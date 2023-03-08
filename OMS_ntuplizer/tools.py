max_pages = 10000
verbose = False
import os, sys
if not os.path.exists( os.getcwd() + 'omsapi.py' ):
    sys.path.append('..')  # if you run the script in the more-examples sub-folder 
from omsapi import OMSAPI

appName = "cms-tsg-oms-ntuple"
appSecret = "" #keep empty to load secret from appSecretLocation
appSecretLocation = "~/private/oms.sct" #echo "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx" > ~/private/oms.sct

def getOMSAPI_krb():
    if verbose: print("Calling  getOMSAPI_krb()")
    omsapi = OMSAPI("https://cmsoms.cern.ch/agg/api", "v1")
    omsapi.auth_krb()
    return omsapi

def getOMSAPI_oidc(appSecret):
    if verbose: print("Calling  getOMSAPI_oidc(appSecret)")
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
        fName = os.path.expanduser(appSecretLocation)
        if os.path.exists(fName):
            f = open(fName)
            return f.read()[:-1]
    return appSecret ## return "" if appSecret is not found
    

def getOMSdata(omsapi,table, attributes, filters, max_pages=max_pages, verbose=verbose):
    query = omsapi.query(table)
    query.set_verbose(verbose)
    query.per_page = max_pages  # to get all names in one go
    if attributes:
        query.attrs(attributes)
    for var in filters:
        if len(filters[var])==2:
            if  filters[var][0]!=None: query.filter(var, filters[var][0], "GE")
            if  filters[var][1]!=None: query.filter(var, filters[var][1], "LE")
        elif len(filters[var])==1:
            query.filter(var, filters[var][0])
    resp = query.data()
    oms = resp.json()   # all the data returned by OMS
    return oms['data']

from array import array
### Define tree variables, option https://root.cern.ch/doc/master/classTTree.html 
def SetVariable(tree,name,option='F',lenght=1,maxLenght=100):
    if option == 'F': arraytype='f'
    elif option == 'f': arraytype='f'
    elif option == 'O': arraytype='i'
    elif option == 'I': arraytype='l'
    elif option == 'i': arraytype='l'
    else:
        print('option ',option,' not recognized.')
        return

    if not type(lenght) == str:
        maxLenght = lenght
        lenght = str(lenght)
    variable = array(arraytype,[0]*maxLenght)
    if maxLenght>1: name = name + '['+lenght+']'
    tree.Branch(name,variable,name+'/'+option)
    return variable

def stripVersion(name):
    if "_v" in name:
        return name.split("_v")[0]+"_v"
    return name
