## OMS ntuplizer
This code downloads the trigger rates from OMS using OMS API (https://gitlab.cern.ch/cmsoms/oms-api-client) and makes flat ntuples (TTree) which include the number of events accepted by each L1 and HLT trigger per lumisection and other use full infos (eg. luminosity, pileup, number of fill, DCS detector bits, ...). All the variables are stored per lumisection (23.31 s).
This code was originally designed in TSG group to allow people performing trigger studies (eg. plots of trigger cross-section vs integrated luminosity) but it can be even used/extended to other purposes.

### Install OMS_ntuplizer and OMS API
- Get OMSRatesNtuple following https://github.com/silviodonato/OMSRatesNtuple/blob/main/README.md.

- Install OMS API client following the README in https://gitlab.cern.ch/cmsoms/oms-api-client. \
Please note that OMS API client should be installed in a separated folder. \
You might need to download the CERN cookies from lxplus \
```cern-get-sso-cookie -u https://cmsoms.cern.ch/cms/fills/summary -o ssocookies.txt```.

- Go in the `OMSRatesNtuple/OMS_ntuplizer` folder and test the correct installation of OMS API using `python3 OMSAPI_test.py`.  \
If you get any error, please check your OMS API installation.

### Run OMS ntuplizer

- Edit the parameters in `OMS_ntuplizer.py` (eg. select a different `outputFolder`, default is `.`).

- Run `python3 OMS_ntuplizer.py`.

- Check the nutuples produced in your outputFolder :-)

