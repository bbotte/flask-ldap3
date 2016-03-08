from flask import request,Response,session,Flask
import os
import json
import logging_config
import logging
import auth_ldap3

app_logger = logging.getLogger('verbose')

app = Flask(__name__)

if "WINGDB_ACTIVE" in os.environ:
  app.debug= False
else:
  app.debug=True

@app.route("/")
@auth_ldap3.ldap_protected #this makes this endpoint protected
def root():
  message = "logged in as %s"% session["username"]
  app_logger.debug("%s"%message)
  return Response(json.dumps("%s"%message), mimetype="application/json")

@app.route("/logout")
def logout():
  try:
    app_logger.debug("logging out %s"%session["username"])
    session.pop('username', None)
    message = "logged out"
  except:
    message = "not logged in"
  return Response(json.dumps("%s"%message), mimetype="application/json")

def run():
  app.secret_key = os.urandom(24)
  app_logger.debug("application started")
  app.run()

if __name__=="__main__":
  app.secret_key = os.urandom(24)
  app_logger.debug("application started")
  app.run()
