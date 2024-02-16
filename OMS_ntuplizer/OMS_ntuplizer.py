#!/usr/bin/env python
from __future__ import print_function
""" This code download the trigger rates using OMS API (https://gitlab.cern.ch/cmsoms/oms-api-client).
Parts of the code have been taken from https://gitlab.cern.ch/cmsoms/oms-api-client/-/blob/master/examples/06-get-max-rate-l1trigger-bit.py
and from https://gitlab.cern.ch/cms-tsg-fog/ratemon/-/tree/master/ .

The output ntuples are stored in /eos/user/s/sdonato/public/OMS_rates
"""

#run_min = 355678 ## 355678 ## July 17, before this run the lumi is stored using a different unit
lastNdays = 7 ## look only at the runs of the last N days
run_min = 376808 # first cosmics run of cosmics 2024
#run_min = 3????? # first stable beam 2024 ???
run_max = 999000
#run_min = 362079 # RunG
#run_max = 362782 # RunG
#run_min= 367574-10
#run_max= 367574+10
minimum_integratedLumi = -1.E-3 # require at least some pb-1 (?) per run 
minimum_hltevents = -1 # require a minimum of events passing HLT
outputFolder = "2024"

#missing last json
#run_min = 362439 
#run_max = 362761

#run_min = 362758 
#run_max = 362760

#2018
#run_min = 314458 
#run_max = 326004
from tools import verbose
overwrite = False #overwrite output files
#requiredHLTpath = "AlCa_EcalEtaEBonly_v" #require this trigger to be in the menu (ie. require a collision menu)
requiredHLTpath = "HLT_EcalCalibration_v" #require this trigger to be in the menu (ie. require a collision menu)
badRuns = [360088, 357112,357104, 355872, 321775, 318734, 319908, 319698, 321712] #the code crashes on these runs

#load json files from https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions22/
muonJsonFile = "Cert_Collisions2022_355100_362760_Muon.json" 
goldenJsonFile = "Cert_Collisions2022_355100_362760_Golden.json" 

## Max limits in queries, used for testing
minLS = 0
maxLS = 50000
maxHLTPaths = 5000
maxL1Bits = 5000
max_pages = 10000 #10000

import sys
import os
import argparse
import re
import ROOT
from array import array

parser = argparse.ArgumentParser( 
    description='python script using OMS API to get maximum rate of L1 trigger algos', 
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

#parser.add_argument( 'run', type = int, help = 'run for which rates should be retrieved' )
#group = parser.add_mutually_exclusive_group(required=True)
#group.add_argument( '--pattern', help = 'regexp pattern for algos for which max rate will be retrieved, example: ".*EG.*"' )
parser.add_argument( '--split', default="-1/-1", help = 'split runs for simultaneous queries . Example: "5/10" will run only runs with run%10==5' )
#group.add_argument( '--bits', nargs='+', help = 'list of algo bits for which max rate will be retrieved')

args = parser.parse_args()
job_i, job_tot = [int(v) for v in args.split.split("/")]

from tools import getOMSAPI, getAppSecret, SetVariable, getOMSdata, stripVersion
omsapi = getOMSAPI(getAppSecret())


l1BitMap = {}
l1Bits = []

L1Counts_var = {}
run_recLumi = 0.

import json
muonJsonDict = json.load(open(muonJsonFile))
goldenJsonDict = json.load(open(goldenJsonFile))

def json( dic, run , lumi):
    if str(run) in dic:
        if lumi>=dic[str(run)][0][0] and lumi<=dic[str(run)][0][1]:
            return True 
    return False

#print(l1BitMap)


###############################################
perRunVariables_int = []
perRunVariables_float = ["b_field", "energy","energy"]

from datetime import datetime, timedelta
day_start = datetime.today()-timedelta(days=lastNdays)
data_runs = getOMSdata(omsapi, "runs", 
    attributes = ["run_number","recorded_lumi","components","hlt_key","l1_key"]+perRunVariables_int+perRunVariables_float, 
    filters = {
        "run_number":[run_min, run_max], 
        "recorded_lumi":[minimum_integratedLumi, None], 
        "hlt_physics_counter":[minimum_hltevents, None],
        "end_time":[day_start.isoformat(), "3000-01-01T00:00:00Z"], ## exclude ongoing runs (end_time=None)
    }, 
    max_pages=max_pages
)


def fromHltKeyToKey(hltkey, run_db):
    print(hltkey)
    b_field = run_db["attributes"]["b_field"]
    energy = run_db["attributes"]["energy"]
    
    key = ""
    if "firstCollision" in hltkey:
        key = "firstCollisions"
    elif "collision" in hltkey:
        key = "collisions"
    elif "Run2024HI" in hltkey:
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

runs = []
for d in reversed(data_runs):
    run = d['attributes']['run_number']
    hltkey = d['attributes']['hlt_key']
    print(run , d['attributes']['recorded_lumi'], len(d['attributes']['components']), d['attributes']['l1_key'])
    run_db = selectRun(data_runs, run)
    if job_i>=0 and job_tot>0:
        if run%job_tot==job_i:
            runs.append((run, fromHltKeyToKey(hltkey, run_db)))
    else:
        runs.append((run, fromHltKeyToKey(hltkey, run_db)))


print("Doing %d runs="%len(runs),runs)
for (run, key) in runs:
    fName = outputFolder+"/"+key+"_"+str(run)+".root"
    if os.path.isfile(fName):
        print(fName+" already existing, skipping.")
        continue
    print(" Run=%d"%run)
    if run in badRuns:
        print("Contained in "+str(badRuns)+ "skipping.")
        continue
    
    filters ={
        "run_number":[run],
    }
    data = getOMSdata(omsapi, "lumisections", 
        attributes = [], 
        filters = {
            "run_number": [run],
        }, 
        max_pages=max_pages
    )
    
    run_db = selectRun(data_runs, run)
    
    lumisections = {}
    det_flags = ['bpix', 'fpix', 'tob', 'tecp', 'tecm', 'tibtid', 'esm', 'ebp', 'esp', 'eep', 'ebm', 'eem', 'ho', 'hbhea', 'hbhec', 'hbheb', 'hf', 'gemm', 'gemp', 'gem', 'dt0', 'dtm', 'dtp', 'rpc', 'cscm', 'cscp', 'rp_sect_45', 'rp_sect_56', 'rp_time']
    lhc_flags = ['beams_stable','beam_present','beam2_stable','beam2_present','physics_flag']
    lhc_int = ['run_number','fill_number','lumisection_number']
    lhc_float = ['recorded_lumi_per_lumisection','delivered_lumi_per_lumisection','pileup']
    lhc_int_add = ["year","month","day","hour","minute","second","time","cms_ready","golden_json","muon_json"]
    lhc_float_add = ["deadtime"]
    cms_ready_vars = [flag for flag in det_flags if not flag in ['rp_sect_45', 'rp_sect_56', 'rp_time','gem']]


    lumisections_vars = {}
    for var in det_flags+lhc_flags+lhc_int+lhc_int_add+lhc_float+lhc_float_add:
        lumisections[var] = []


    for row in data:
        for var in det_flags:
            lumisections[var].append(row['attributes'][var+"_ready"])
        for var in lhc_flags+lhc_int+lhc_float:
            lumisections[var].append(row['attributes'][var])
        dtime = row['attributes']['start_time'] #format: '2022-11-24T08:45:47Z'
        date, time = dtime.split('T')
        yy,mm,dd = date.split('-')
        HH,MM,SS = time[:-1].split(':')
        lumisections['year'].append(int(yy))
        lumisections['month'].append(int(mm))
        lumisections['day'].append(int(dd))
        lumisections['hour'].append(int(HH))
        lumisections['minute'].append(int(MM))
        lumisections['second'].append(int(SS))
        lumisections['time'].append(int(datetime(int(yy), int(mm), int(dd), int(HH), int(MM),int(SS)).timestamp()) - int(datetime(2024,1,1).timestamp()))
        lumisections['deadtime'] = [ r/d if d>0 else 1 for r, d in zip(lumisections['recorded_lumi_per_lumisection'], lumisections['delivered_lumi_per_lumisection'])]
        run_recLumi = sum(lumisections["recorded_lumi_per_lumisection"])
        cms_ready = True
        for var in cms_ready_vars:
            if not row['attributes'][var+"_ready"]:
                cms_ready = False
        lumisections['cms_ready'].append(cms_ready)
        lumisections['muon_json'].append(json(muonJsonDict, run, row['attributes']['lumisection_number']))
        lumisections['golden_json'].append(json(goldenJsonDict, run, row['attributes']['lumisection_number']))


    if run_recLumi<minimum_integratedLumi:
        print()
        print("Run=%d integrated lumi %f, below %f. Skipping file %s"%(run,run_recLumi,minimum_integratedLumi,fName))
        print()
        continue

    #q.filter("lumisection_number", minLS, operator="GE")
    #q.filter("lumiseciton_number", maxLS, operator="LE")
    #q.custom("include", "meta")

    ####################################################################

    data = getOMSdata(omsapi, "hltpathinfo", 
        attributes = ["path_name"], 
        filters = {
            "run_number": [run],
        }, 
        max_pages=max_pages
    )
    HLTPaths = []
    for row in data[:maxHLTPaths]:
        HLTPaths.append(row['attributes']['path_name'])

    HLTpaths_noVersion = [stripVersion(path) for path in HLTPaths]
    if not requiredHLTpath in HLTpaths_noVersion:
        print()
        print(HLTpaths_noVersion)
        print()
        print("Run=%d doesn't contain path %s. Skipping file %s"%(run,requiredHLTpath,fName))
        continue

    ###############
    query = omsapi.query("hltpathrates")
    query.set_verbose(verbose)
    query.per_page = max_pages  # to get all names in one go

    # Projection. Specify attributes you want to fetch
    firstPath = True
    HLT_Counters = {}
    HLTlumis = []
    query.attrs(["counter",'last_lumisection_number']) #
    for HLT_path in reversed(HLTPaths):
    #    print(HLT_path)
        HLT_Counters[HLT_path] = []
        query.clear_filter()

        # Filter run
        query.filter("run_number", run )

        query.filter("path_name", HLT_path)
        query.filter("first_lumisection_number", minLS, "GE")
        query.filter("last_lumisection_number", maxLS, "LE")

        # Execute query and fetch data
        resp = query.data()
        oms = resp.json()   # all the data returned by OMS
        data = oms['data']
        HLTCounters = {}
        for row in data:
    #        run[0], aaa, new_lumi = [int(el) for el in row['id'].split("__")]
            HLT_Counters[HLT_path].append(row['attributes']['counter'])
        if 'last_lumisection_number' in row['attributes']:
            for row in data:
        #        run[0], aaa, new_lumi = [int(el) for el in row['id'].split("__")]
                HLTlumis.append(row['attributes']['last_lumisection_number'])
        query.attrs(["counter"]) #

    #print(HLT_Counters[HLT_path])
    #################################################################

    data = getOMSdata(omsapi, "l1algorithmtriggers", 
        attributes = ["name","bit"], 
        filters = {
            "first_lumisection_number": [minLS, None],
            "last_lumisection_number": [None, maxLS],
            "run_number" : [run],
        }, 
        max_pages=max_pages
    )


    for row in data:
        algo = row['attributes']
        l1BitMap[int(algo['bit'])] = algo['name']
    # Create a query.
    query = omsapi.query("l1algorithmtriggers")
    query.set_verbose(verbose)
    query.per_page = max_pages  # to get all names in one go

    ###############
    query = omsapi.query("l1algorithmtriggers")
    query.set_verbose(verbose)
    query.per_page = max_pages  # to get all names in one go

    # Projection. Specify attributes you want to fetch
    firstPath = True
    L1_Counters = {}
    L1lumis = []
#    query.attrs(["pre_dt_before_prescale_counter","last_lumisection_number","first_lumisection_number","last_lumisection_number"]) #
    query.attrs(["pre_dt_before_prescale_counter","last_lumisection_number","first_lumisection_number"]) #
    for L1_bit in list(l1BitMap.keys())[:maxL1Bits]:
        if type(L1_bit)!=int: 
            print("Something wrong with %d. Skipping"%L1_bit)
            print("l1BitMap[L1_bit] = %s"%l1BitMap[L1_bit])
            continue
    #    print(L1_bit)
        L1_Counters[L1_bit] = []
        query.clear_filter()

        # Filter run
        query.filter("run_number", run )
        query.filter("bit", L1_bit )
        query.filter("first_lumisection_number", minLS, "GE")
        query.filter("last_lumisection_number", maxLS, "LE")

        # Execute query and fetch data
        resp = query.data()
        oms = resp.json()   # all the data returned by OMS
        data = oms['data']
        for row in data:
    #        run[0], aaa, new_lumi = [int(el) for el in row['id'].split("__")]
            if row['attributes']['pre_dt_before_prescale_counter']==None: row['attributes']['pre_dt_before_prescale_counter']=0
            L1_Counters[L1_bit].append(int(row['attributes']['pre_dt_before_prescale_counter']))
        if L1_bit==0:
            for row in data:
        #        run[0], aaa, new_lumi = [int(el) for el in row['id'].split("__")]
                L1lumis.append(row['attributes']['last_lumisection_number'])
        ## See examples with empty entries https://cmsoms.cern.ch/cms/triggers/l1_algo?cms_run=367474&cms_l1_bit=110&cms_l1_bit_name=
        ## https://cmsoms.cern.ch/agg/api/v1/l1algorithmtriggers/?fields=pre_dt_before_prescale_counter&filter[run_number][EQ]=367474&filter[bit][EQ]=368&filter[first_lumisection_number][GE]=0&filter[last_lumisection_number][LE]=50000&page[offset]=0&page[limit]=10000
        if len(L1_Counters[L1_bit]) == 0:
            print("Problems with %s"%query.data_query(), L1_bit, run)
            print("Setting it to zero.")
            L1_Counters[L1_bit] = len(L1lumis)*[0]
        query.attrs(["pre_dt_before_prescale_counter"]) #
    
    ###############
    
    if HLTlumis!=L1lumis:
        print("HLTlumis!=L1lumis")
        print("HLTlumis=", len(HLTlumis), HLTlumis)
        print("L1lumis=", len(L1lumis), L1lumis)
#        continue
    
    ### Init root file
    print("Creating ", fName)
    f = ROOT.TFile(fName,"recreate")
    tree = ROOT.TTree("tree","tree")
    
    ### fill constant value (eg. B_field)
    for var in perRunVariables_float:
        lumisections_vars[var] = SetVariable(tree,var,'f',1,1)
    
    for var in perRunVariables_int:
        lumisections_vars[var] = SetVariable(tree,var,'I',1,1)
    
    for var in perRunVariables_float+perRunVariables_int:
        lumisections_vars[var][0] = run_db["attributes"][var]
    
    ### fill lumi dependent variables value (eg. pileup per lumi)
    lumi = SetVariable(tree,"lumi",'i',1,1)
    run_ = SetVariable(tree,"run",'i',1,1)
    run_[0] = run
    
    HLTAccepted = {}
    for path in reversed(HLTPaths):
        HLTAccepted[path] = SetVariable(tree, stripVersion(path),'i',1,1)
    
    for var in det_flags+lhc_flags:
        lumisections_vars[var] = SetVariable(tree,var,'O',1,1)
    
    for var in lhc_float+lhc_float_add:
        lumisections_vars[var] = SetVariable(tree,var,'f',1,1)
    
    for var in lhc_int+lhc_int_add:
        var = var.replace("_number","") ## lumisection_number -> lumisection
        lumisections_vars[var] = SetVariable(tree,var,'I',1,1)
    
    for bit in l1BitMap:
        L1Counts_var[bit] = SetVariable(tree,l1BitMap[bit],'i',1,1)
    
    ##########################################################
    
    # Fill tree
    first_el = True
    for idx_lumi,l in enumerate(lumisections['lumisection_number']):
        if l in L1lumis and l in HLTlumis:
            for var in det_flags+lhc_flags+lhc_int+lhc_int_add+lhc_float+lhc_float_add:
                lumisections_vars[var.replace("_number","")][0] = lumisections[var][idx_lumi]  if lumisections[var][idx_lumi] else False
            hlt_lumi = HLTlumis.index(l)
            for path in HLT_Counters:
                HLTAccepted[path][0] = HLT_Counters[path][hlt_lumi]
            l1_lumi = L1lumis.index(l)
            for l1bit in L1_Counters:
                if l1_lumi>=0 and l1_lumi<len(L1_Counters[l1bit]):
                    L1Counts_var[l1bit][0] = L1_Counters[l1bit][l1_lumi]
                else:
                    print("Something wrong, no l1_lumi in L1_Counters[l1bit]. Forcing L1Counts_var[l1bit][0] = 0")
                    print(l1_lumi, l1bit, len(L1_Counters[l1bit]))
                    print(l, idx_lumi, hlt_lumi, l1_lumi, L1lumis, HLTlumis)
                    L1Counts_var[l1bit][0] = 0
                ###
            lumi[0] = l
            tree.Fill()
#            print("tree.Fill()",run, lumi[0])
    ##############################################
    
    print("Closing ",f.GetName())
    f.Write()
    f.Close()

