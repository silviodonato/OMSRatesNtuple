#!/usr/bin/env python
from __future__ import print_function
""" This code download the trigger rates using OMS API (https://gitlab.cern.ch/cmsoms/oms-api-client).
Parts of the code have been taken from https://gitlab.cern.ch/cmsoms/oms-api-client/-/blob/master/examples/06-get-max-rate-l1trigger-bit.py
and from https://gitlab.cern.ch/cms-tsg-fog/ratemon/-/tree/master/ .

The output ntuples are stored in /eos/user/s/sdonato/public/OMS_rates
"""

max_pages = 10000 #10000

import ROOT, argparse, os

parser = argparse.ArgumentParser( 
    description='python script to check the kind of run (eg. cosmics, HIon) and propose a renaming', 
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

#parser.add_argument( 'run', type = int, help = 'run for which rates should be retrieved' )
parser.add_argument( '--folder', default='-1', help = 'select a input folder')

args = parser.parse_args()

from tools import getOMSAPI, getAppSecret, SetVariable, getOMSdata, stripVersion

try:
    omsapi = getOMSAPI(getAppSecret())
except:
    import time
    time.sleep(3)
    omsapi = getOMSAPI(getAppSecret())

def fromHltKeyToKey(hltkey, run_db):
#    print(hltkey)
    b_field = run_db["attributes"]["b_field"]
    energy = run_db["attributes"]["energy"]
    
    key = ""
    if "firstCollision" in hltkey:
        key = "firstCollisions"
    elif "collision" in hltkey:
        key = "collisions"
    elif "Run2024HI" in hltkey:
        key = "HIon"
    elif "Run2023HI" in hltkey:
        key = "HIon"
    elif "Run2022HI" in hltkey:
        key = "HIon"
    elif "PRef" in hltkey:
        key = "PRef"
    elif "circulating" in hltkey:
        key = "circulating"
    elif "CRAFT" in hltkey:
        key = "CRAFT"
    elif "CRUZET" in hltkey:
        key = "CRUZET"
    elif "cosmic" in hltkey:
        if b_field<1:
            key = "CRUZET"
        elif b_field>3:
            key = "CRAFT"
        else:
            key = "cosmics"
    elif "special" in hltkey:
        key = "special"
    elif "physics" in hltkey and energy>5000:
        key = "physics"
    else:
        key = "other"
    return key

def selectRun(data_runs, run):
    run_db = [r for r in data_runs if r['id']==str(run)]
    if len(run_db)!=1: print(data_runs, "\n", run, "\n", run_db)
    assert(len(run_db)==1)
    run_db = run_db[0]
    return run_db


folder = args.folder
runs = []
for r in os.listdir(folder):
    r_ = r.split(".")[0].split("_")[-1]
    try:
        runs.append(int(r_))
    except:
        print("Skipping %s"%r)
        pass

data_runs = getOMSdata(omsapi, "runs", 
    attributes = ["run_number","recorded_lumi","components","hlt_key","l1_key","b_field","energy"], #+perRunVariables_int+perRunVariables_float, 
    filters = {
        "run_number":[min(runs),max(runs)], 
    }, 
    max_pages=max_pages
)

print("Doing %s"%folder)
for run in runs:
    oldFileName = folder+"/"+[f for f in os.listdir(folder) if str(run) in f][0]
    run_db = selectRun(data_runs, run)
    hltkey = run_db['attributes']['hlt_key']
    key = fromHltKeyToKey(hltkey, run_db)
    newFileName = folder+"/"+key+"_"+str(run)+".root"
    if oldFileName!=newFileName:
        print("mv %s %s"%(oldFileName,newFileName))


#runs = []
#for d in reversed(data_runs):
#    run = d['attributes']['run_number']
#    hltkey = d['attributes']['hlt_key']
#    print(run , d['attributes']['recorded_lumi'], len(d['attributes']['components']), d['attributes']['l1_key'])
#    run_db = selectRun(data_runs, run)
#    if job_i>=0 and job_tot>0:
#        if run%job_tot==job_i:
#            runs.append((run, fromHltKeyToKey(hltkey, run_db)))
#    else:
#        runs.append((run, fromHltKeyToKey(hltkey, run_db)))

