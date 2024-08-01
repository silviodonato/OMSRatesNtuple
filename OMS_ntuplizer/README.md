## OMS Ntuplizer

This code downloads trigger rates from the OMS using the [OMS API](https://gitlab.cern.ch/cmsoms/oms-api-client) and creates flat ntuples (TTree). These ntuples include the number of events accepted by each L1 and HLT trigger per lumisection, along with other useful information (e.g., luminosity, pileup, number of fills, DCS detector bits, etc.). All variables are stored per lumisection (23.31 seconds).

Originally designed by the TSG group, this tool facilitates trigger studies (e.g., plotting trigger cross-sections vs. integrated luminosity) but can be extended for other purposes as well.

### Installing OMS_ntuplizer and OMS API

1. **Clone OMSRatesNtuple**
   - Follow the instructions [here](https://github.com/silviodonato/OMSRatesNtuple/blob/main/README.md).

2. **Install the OMS API Client**
   - Follow the README instructions at [OMS API Client](https://gitlab.cern.ch/cmsoms/oms-api-client).
   - Install the OMS API client in a separate folder.
   - Download CERN cookies from lxplus using (not mandatory):
     ```sh
     cern-get-sso-cookie -u https://cmsoms.cern.ch/cms/fills/summary -o ssocookies.txt
     ```

3. **Test the OMS API Installation**
   - Navigate to the `OMSRatesNtuple/OMS_ntuplizer` folder.
   - Test the OMS API installation:
     ```sh
     python3 OMSAPI_test.py
     ```
   - If you encounter any errors, check your OMS API installation.

### Running OMS Ntuplizer

1. **Edit Parameters**
   - Modify the parameters in `OMS_ntuplizer.py` (e.g., select a different `outputFolder`).

2. **Run the Ntuplizer**
   - Execute the following command:
     ```sh
     python3 OMS_ntuplizer.py
     ```

3. **Check the Output**
   - Verify the ntuples produced in your specified `outputFolder` :-).


### Support:
Mattermost channel: https://mattermost.web.cern.ch/cms-tsg/channels/omsratesntuple
