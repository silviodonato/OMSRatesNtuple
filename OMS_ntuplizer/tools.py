import os, sys
if not os.path.exists( os.getcwd() + 'omsapi.py' ):
    sys.path.append('..')  # if you run the script in the more-examples sub-folder 
from omsapi import OMSAPI

appName = "cms-tsg-oms-ntuple"
appSecret = "" #keep empty to load secret from appSecretLocation
appSecretLocation = "~/private/oms.sct" #echo "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx" > ~/private/oms.sct

def getOMSAPI_krb():
    print("Calling  getOMSAPI_krb()")
    omsapi = OMSAPI("https://cmsoms.cern.ch/agg/api", "v1")
    omsapi.auth_krb()
    return omsapi

def getOMSAPI_oidc(appSecret):
    print("Calling  getOMSAPI_oidc(appSecret)")
    omsapi = OMSAPI("https://cmsoms.cern.ch/agg/api", "v1", cert_verify=False)
    omsapi.auth_oidc(appName,appSecret)
    return omsapi

def getOMSAPI(appSecret=""):
    if appSecret == "":
        print("### No CERN OpenID secret found. Trying using kerberos, but it will work only from lxplus! ( https://gitlab.cern.ch/cmsoms/oms-api-client#alternative-auth-option )")
        return getOMSAPI_krb()
    else:
        try:
            return getOMSAPI_oidc(appSecret)
        except:
            print("### Problems with CERN OpenID secret found. Trying using kerberos, but it will work only from lxplus! ( https://gitlab.cern.ch/cmsoms/oms-api-client#alternative-auth-option )")
            return getOMSAPI_krb()

def getAppSecret():
    if appSecret == "":
        f = open(os.path.expanduser(appSecretLocation))
        return f.read()[:-1]
    else:
        return appSecret
