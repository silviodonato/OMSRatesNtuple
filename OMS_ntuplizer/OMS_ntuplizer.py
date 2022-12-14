#!/usr/bin/env python
from __future__ import print_function
""" This code download the trigger rates using OMS API (https://gitlab.cern.ch/cmsoms/oms-api-client).
Parts of the code have been taken from https://gitlab.cern.ch/cmsoms/oms-api-client/-/blob/master/examples/06-get-max-rate-l1trigger-bit.py
and from https://gitlab.cern.ch/cms-tsg-fog/ratemon/-/tree/master/ .

The output ntuples are stored in /eos/user/s/sdonato/public/OMS_rates
"""

run_min = 355678 ## 355678 ## July 17, before this run the lumi is stored using a different unit
run_max = 999000
#run_min = 362079 # RunG
#run_max = 362782 # RunG
minimum_integratedLumi = 1. # require at least some pb-1 (?) per run 
outputFolder = "."

#missing last json
#run_min = 362439 
#run_max = 362761


#2018
#run_min = 314458 
#run_max = 326004

overwrite = False #overwrite output files
requiredHLTpath = "AlCa_EcalEtaEBonly_v" #require this trigger to be in the menu (ie. require a collision menu)
badRuns = [360088, 357112,357104, 355872, 321775, 318734, 319908, 319698, 321712] #the code crashes on these runs

#load json files from https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions22/
muonJsonFile = "Cert_Collisions2022_355100_362760_Muon.json" 
goldenJsonFile = "Cert_Collisions2022_355100_362760_Golden.json" 

## Max limits in queries, used for testing
minLS = 0
maxLS = 50000
maxHLTPaths = 5000
maxL1Bits = 5000
max_pages = 10000

import sys
import os
import argparse
import re
import ROOT
from array import array

if not os.path.exists( os.getcwd() + 'omsapi.py' ):
    sys.path.append('..')  # if you run the script in the more-examples sub-folder 
from omsapi import OMSAPI

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

#omsapi = OMSAPI('http://cmsoms.cms/agg/api/','v1', cert_verify=False)
omsapi = OMSAPI("https://cmsoms.cern.ch/agg/api", "v1")
#cern-get-sso-cookie -u https://cmsoms.cern.ch/cms/fills/summary -o ssocookies.txt
omsapi.auth_krb()


l1BitMap = {}
l1Bits = []

L1Counts_var = {}

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

query = omsapi.query("runs")
query.set_verbose(False)
query.per_page = max_pages  # to get all names in one go
query.attrs(["run_number","recorded_lumi","components","hlt_key","l1_key"]) #
query.filter("run_number", run_min, "GE")
query.filter("run_number", run_max, "LE")
query.filter("recorded_lumi", minimum_integratedLumi, "GE") ## require at least minimum_integratedLumi [pb-1] of lumi per run

resp = query.data()
oms = resp.json()   # all the data returned by OMS
data = oms['data']

runs = []
for d in reversed(data):
    run = d['attributes']['run_number']
    hltkey = d['attributes']['hlt_key']
    print(run , d['attributes']['recorded_lumi'], len(d['attributes']['components']), d['attributes']['l1_key'])
    if job_i>=0 and job_tot>0:
        if run%job_tot==job_i:
            runs.append(run)
    else:
        runs.append(run)

#get HLT prescale tables
#query = omsapi.query("hltprescalesets")
#query.filter("config_name", "/cdaq/physics/Run2022/2e34/v1.5.0/HLT/V13" )
##query.filter("path_name", 'HLT_PFMETTypeOne140_PFMHT140_IDTight_v13' )
#query.filter("prescale_sequence", "200" )
##query.filter("prescale_index", "4" )
#resp = query.data()
#oms = resp.json()
#data = oms['data']
#for i in data: print(i,"\n")

#    query = omsapi.query("datasetrates/datasets")

#    ## Filter run
#    query.filter("run_number", run )
#    query.attr("datasets")

#    # Execute query and fetch data
#    resp = query.data()
#    oms = resp.json()   # all the data returned by OMS
#    data = oms['data']

#    datasets = data['attributes']['datasets']

print("Doing %d runs="%len(runs),runs)
for run in runs:
    fName = outputFolder+"/"+str(run)+".root"
    if os.path.isfile(fName):
        print(fName+" already existing, skipping.")
        continue
    print(" Run=%d"%run)
    if run in badRuns:
        print("Contained in "+str(badRuns)+ "skipping.")
        continue
    query = omsapi.query("lumisections")
    query.set_verbose(False)
    query.per_page = max_pages  # to get all names in one go
    query.filter("run_number",  run)
    resp = query.data()
    oms = resp.json()   # all the data returned by OMS
    data = oms['data']

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


    from datetime import datetime
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
        lumisections['time'].append(int(datetime(int(yy), int(mm), int(dd), int(HH), int(MM),int(SS)).timestamp()) - int(datetime(2023,1,1).timestamp()))
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

    query = omsapi.query("hltpathinfo")
    query.set_verbose(False)
    query.per_page = max_pages  # to get all names in one go

    # Projection. Specify attributes you want to fetch
    query.attrs(["path_name"])

    # Filter run
    query.filter("run_number", run )

    # Execute query and fetch data
    resp = query.data()
    oms = resp.json()   # all the data returned by OMS
    data = oms['data']
    HLTPaths = []
    for row in data[:maxHLTPaths]:
        HLTPaths.append(row['attributes']['path_name'])

    def stripVersion(name):
        if "_v" in name:
            return name.split("_v")[0]+"_v"
        return name

    HLTpaths_noVersion = [stripVersion(path) for path in HLTPaths]
    if not requiredHLTpath in HLTpaths_noVersion:
        print()
        print(HLTpaths_noVersion)
        print()
        print("Run=%d doesn't contain path %s. Skipping file %s"%(run,requiredHLTpath,fName))
        continue

    ###############
    query = omsapi.query("hltpathrates")
    query.set_verbose(False)
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

    query = omsapi.query("l1algorithmtriggers")
    query.set_verbose(False)
    query.per_page = max_pages  # to get all names in one go

    # Projection. Specify attributes you want to fetch
    query.attrs(["name","bit"])
    query.filter("first_lumisection_number", minLS, "GE")
    query.filter("last_lumisection_number", maxLS, "LE")

    # Filter run
    query.filter("run_number", run )

    # Execute query and fetch data
    resp = query.data()
    oms = resp.json()   # all the data returned by OMS
    data = oms['data']
    for row in data:
        algo = row['attributes']
        l1BitMap[int(algo['bit'])] = algo['name']
    # Create a query.
    query = omsapi.query("l1algorithmtriggers")
    query.set_verbose(False)
    query.per_page = max_pages  # to get all names in one go

#    # Projection. Specify attributes you want to fetch
#    query.attrs(["pre_dt_before_prescale_counter"]) #"name","bit", see https://cmsoms.cern.ch/agg/api/v1/l1algorithmtriggers/362616__1__1

#    #print(l1Bits)
#    lumis = range(0,2)
#    #bit = l1Bits[0]
#    query.filter("run_number", run )
##    query.filter("first_lumisection_number", minLS, operator="GE")
##    query.filter("last_lumisection_number", maxLS, operator="LE")

#    #query.filter("bit", bit)  # returns data per lumisection
#    #query.custom("group[granularity]", "lumisection")
#    data = query.data().json()['data']
#    query.verbose = False
#    max = 0.0
#    lumisection = 4

#    #362616__383__25

    ###############
    query = omsapi.query("l1algorithmtriggers")
    query.set_verbose(False)
    query.per_page = max_pages  # to get all names in one go

    # Projection. Specify attributes you want to fetch
    firstPath = True
    L1_Counters = {}
    L1lumis = []
#    query.attrs(["pre_dt_before_prescale_counter","last_lumisection_number","first_lumisection_number","last_lumisection_number"]) #
    query.attrs(["pre_dt_before_prescale_counter","last_lumisection_number","first_lumisection_number"]) #
    for L1_bit in list(l1BitMap.keys())[:maxL1Bits]:
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
            L1_Counters[L1_bit].append(int(row['attributes']['pre_dt_before_prescale_counter']))
        if L1_bit==0:
            for row in data:
        #        run[0], aaa, new_lumi = [int(el) for el in row['id'].split("__")]
                L1lumis.append(row['attributes']['last_lumisection_number'])
        query.attrs(["pre_dt_before_prescale_counter"]) #
    
    ###############
    
    ### Init root file
    print("Creating ", fName)
    f = ROOT.TFile(fName,"recreate")
    tree = ROOT.TTree("tree","tree")
    
    lumi = SetVariable(tree,"lumi",'i',1,1)
    run_ = SetVariable(tree,"run",'i',1,1)
    run_[0] = run
    
    HLTAccepted = {}
    for path in reversed(HLTPaths):
        HLTAccepted[path] = SetVariable(tree, stripVersion(path),'i',1,1)
    
    for var in det_flags+lhc_flags:
        lumisections_vars[var] = SetVariable(tree,var,'O',1,1)
    
    for var in lhc_int+lhc_int_add:
        var = var.replace("_number","") ## lumisection_number -> lumisection
        lumisections_vars[var] = SetVariable(tree,var,'I',1,1)
    
    for var in lhc_float+lhc_float_add:
        lumisections_vars[var] = SetVariable(tree,var,'f',1,1)
    
    for bit in l1BitMap:
        L1Counts_var[bit] = SetVariable(tree,l1BitMap[bit],'i',1,1)
    
    ##########################################################
    
    # Fill tree
    first_el = True
    for idx_lumi,l in enumerate(lumisections['lumisection_number']):
#        print(l, L1lumis, HLTlumis)
        if l in L1lumis and l in HLTlumis:
            for var in det_flags+lhc_flags+lhc_int+lhc_int_add+lhc_float+lhc_float_add:
                lumisections_vars[var.replace("_number","")][0] = lumisections[var][idx_lumi]  if lumisections[var][idx_lumi] else False
            hlt_lumi = HLTlumis.index(l)
            for path in HLT_Counters:
                HLTAccepted[path][0] = HLT_Counters[path][hlt_lumi]
            l1_lumi = L1lumis.index(l)
            for l1bit in L1_Counters:
                L1Counts_var[l1bit][0] = L1_Counters[l1bit][l1_lumi]
            lumi[0] = l
            tree.Fill()
#            print("tree.Fill()",run, lumi[0])
    ##############################################
    
    print("Closing ",f.GetName())
    f.Write()
    f.Close()

