from flask import request,session,Response
from ldap3 import Server, Connection, AUTH_SIMPLE, STRATEGY_SYNC, ALL
from functools import wraps
import logging_config
import logging

auth_logger = logging.getLogger('verbose')

def ldap_authenticate(request,username,password,groups_allowed=False):
  
  #change these values to what is appropriate for your environment
  id_name="samaccountname"
  ldap_host="ldap.example.net"
  ldap_port="389"
  bind_dn="CN=ldap,CN=users,DC=ldap,DC=example,DC=net"
  bind_pass="example_pass"
  user_base="ou=Users,dc=ldap,dc=example,dc=net"
  
  #bind with service account
  s = Server(ldap_host, port=int(ldap_port), get_info=ALL)
  c = Connection(
    s,
    authentication=AUTH_SIMPLE, 
    user=bind_dn,
    password=bind_pass,
    check_names=True, 
    lazy=False, 
    client_strategy=STRATEGY_SYNC, 
    raise_exceptions=False)
  c.open()
  c.bind()
  if c.bound:
    
    #once bound, check username provided and get cn, memberOf list and mail
    # get cn_name
    c.search(user_base,'(%s=%s)'%(id_name,username),attributes=['cn','mail','memberOf'])
   
    try: 
      cn_name=c.entries[0]._dn
    except:
      print("user cn cannot be found")
      auth_logger.error("user cn cannot be found")
      
    try:
      cn_memberof=c.entries[0].memberOf.values
    except:
      print("user groups cannot be found")
      auth_logger.error("user groups cannot be found")
    
    #log back with the appropriate cn
    try:
      c.unbind()
      c = Connection(
        s,
        authentication=AUTH_SIMPLE, 
        user=cn_name,
        password=password,
        check_names=True, 
        lazy=False, 
        client_strategy=STRATEGY_SYNC, 
        raise_exceptions=True)    
      c.bind()
      c.unbind
      auth_logger.debug("checking group authorization")
      auth_logger.debug("%s is a member of %s" %(username,cn_memberof) )
      if isinstance(groups_allowed,list) and len(groups_allowed)>=0:
        for group in groups_allowed:
          if any(str(group) in s for s in cn_memberof):
            auth_logger.debug("allowed groups for %s on %s:%s"%(request.method,request.url_rule.rule,groups_allowed))
            auth_logger.debug("user %s is authorized for access"%username)
            session['username']=username
            auth_logger.debug("login as %s completed"%session['username'])
            return True
          else:
            auth_logger.error("login succeeded but %s is not in any allowed groups"%username)
            return False
      elif not groups_allowed:
        auth_logger.debug("This endpoint has no group restrictions, %s has been given access"%username)
        session['username']=username
        auth_logger.debug("login as %s completed"%session['username'])
        return True
      else:
        session['error_message']="login succeeded but user %s is not in any allowed groups"%username
        auth_logger.error(session['error_message'])
        return False
    except:
      auth_logger.error("Authentication Failed")
      return False
  else:
    auth_logger.debug('ldap bind failed')
    c.unbind()
    return False

def auth_401():
  """Sends a 401 response that enables basic auth"""
  return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def ldap_protected(f):
  @wraps(f)
  def decorated(*args, **kwargs):

    # this can be configured and taken from elsewhere
    # path, method, groups_allowed (users in Allowed Users group will be allowed to access / with a GET method)
    authorization_config = {
      "/": {
         "GET": ["Allowed Users"]
      }
    }

    auth_endpoint_rule = authorization_config.get(request.url_rule.rule)
    if auth_endpoint_rule is not None:
      groups_allowed = auth_endpoint_rule.get(request.method) or True
    else:
      groups_allowed = True
    
    auth = request.authorization
    if not ('username' in session):
      if not auth or not ldap_authenticate(request,auth.username, auth.password, groups_allowed):
        return auth_401()
    else:
      auth_logger.debug("%s calling %s endpoint"%(session['username'],f.__name__))
    return f(*args, **kwargs)
  return decorated

