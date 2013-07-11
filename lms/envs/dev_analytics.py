"""
This modifies the dev settings to include a secondary database.
This database is used for read-only views which should be tested
against production data

This settings file expects a pw protected MySQL connection to be 
available on 127.0.0.1:3306 and prompts for password on server start
and on code-change restarts.

To make a connection to MySQLserver.com:3306 from proxy.org available
to your local django instance at 127.0.0.1:3306 , you can use ssh port 
forwarding:

    ssh user@proxy.org -L 3306:MySQLserver.com:3306 -N -f 

this command will use your local credentials to establish a connection to
proxy.org.  

When you attempt to connect to a passoword protected MySQL server, you'll be
prompted for a password (if relevant) to the user account specified in 
DATABASES below

"""

from dev import * 

# get the password for the analytics replica
# TODO: ask only once on startup (it's now 3).
# only asks once on code-change restarts
import getpass
analytics_pw = getpass.getpass("Analytics PW: ")

# define a second database for read only analtyics queries
DATABASES["replica"] = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'wwc',
    'USER': 'analytics_ro',
    'PASSWORD': analytics_pw,
    'HOST': '127.0.0.1',
    'PORT': '3306'
}

# Let admin_dashboard know about certificates issued to 6.002x's first run
MITX_FEATURES['LEGACY_CERT_COUNT'] = 7157