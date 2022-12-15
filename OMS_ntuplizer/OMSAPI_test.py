## Other simple test available in https://gitlab.cern.ch/cmsoms/oms-api-client/-/blob/master/examples/01-query.py

from tools import getOMSAPI, getAppSecret

omsapi = getOMSAPI(getAppSecret())

query = omsapi.query("runs")
query.set_verbose(False)
query.per_page = 1000  # to get all names in one go
query.attrs(["run_number","recorded_lumi"]) #
query.filter("run_number", 362691, "GE")
query.filter("run_number", 362698, "LE")
query.filter("recorded_lumi", 1., "GE")

resp = query.data()
oms = resp.json()   # all the data returned by OMS
data = oms['data']

runs = []
print()
print("Test: print all runs with >1pb-1 of Fill 8489 [362691 - 362698]")
print("(https://cmsoms.cern.ch/cms/fills/report?cms_fill=8489)")
print()
print("Expected runs: 362698, 362696, 362695")
print()
print("Run\tIntegratedLumi")
for d in reversed(data):
    print(d['attributes']['run_number'], d['attributes']['recorded_lumi'])
    runs.append(d['attributes']['run_number'])

print()
if len(runs) == 3:
    print("Test SUCCESSFUL.")
else:
    print("Test FAILED.")
    raise Exception("Test FAILED. Please check your OMS API installation: https://gitlab.cern.ch/cmsoms/oms-api-client ")
print()


