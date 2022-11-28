# OMS ntuplizer
This code download the trigger rates using OMS API (https://gitlab.cern.ch/cmsoms/oms-api-client)

1. (only the first time) Install OMS API client. 
You need to follow the recipes in https://gitlab.cern.ch/cmsoms/oms-api-client.
You might need to download the CERN cookies from lxplus using `cern-get-sso-cookie -u https://cmsoms.cern.ch/cms/fills/summary -o ssocookies.txt`.

2. Test the correct installation of OMS API using: `python3 OMSAPI_test.py`. If get any error, please check your OMS API installation.

3. Edit the parameters in `OMS_ntuplizer.py` (eg. `outputFolder` or `run_max`).

4. Run `python3 OMS_ntuplizer.py`.
