from omsapi import OMSAPI
omsapi = OMSAPI("https://cmsoms.cern.ch/agg/api", "v1")
omsapi.auth_krb()
