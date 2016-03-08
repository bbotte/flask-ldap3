an authentication example using ldap3, flask and logging

quick instructions

# create virtualenv and install
1) pip install virtualenv
2) virtualenv -p /usr/bin/python3 ./virtualenv
3) source ./virtualenv/bin/activate
4) python setup.py develop

# run
5) flask_ldap3

# log in with curl (or via your browser)
6) curl localhost:5000 --user your_username
