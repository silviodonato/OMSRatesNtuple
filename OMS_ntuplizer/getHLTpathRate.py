#!/usr/bin/python3
max_pages = 10000

import argparse

parser = argparse.ArgumentParser( 
    description='''https://github.com/silviodonato/OMSRatesNtuple. 
Example:
python3 getHLTpathRate.py --path HLT_L1SingleMu5_v --run 363534 --lsMin -1 --lsMax 10000 --removeDeadtime
''', 
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

parser.add_argument('--removeDeadtime', action='store_const', const=True, default=False, help='Increase the trigger rate by 1./(1.-deadtime)')
parser.add_argument('--path', default='HLT_L1SingleMu5_v' , help='HLT path, without version number')
parser.add_argument('--run', default=363534 , help='run number')
parser.add_argument('--lsMin', default=-1 , help='lumi section minimum')
parser.add_argument('--lsMax', default=10000 , help='lumi section maximum')
parser.add_argument('--verbose', action='store_const', const=True, default=False, help='OMS query verbose')

args = parser.parse_args()

from pprint import pprint

from tools import getOMSAPI, getAppSecret, getOMSdata, stripVersion
omsapi = getOMSAPI(getAppSecret())

minLS = args.lsMin
maxLS = args.lsMax
run = args.run
path = args.path
removeDeadtime = args.removeDeadtime
verbose = args.verbose

LS_lenght = 2**18 / 11245.5  #23.31 s

def getHLTpaths(omsapi, run):
    data = getOMSdata(omsapi, "hltpathinfo", 
        attributes = ["path_name"], 
        filters = {
            "run_number": [run],
        }, 
        verbose=verbose
    )
    
    HLTPaths = []
    for row in data[:]:
        HLTPaths.append(row['attributes']['path_name'])
    return HLTPaths

def getDeadtime(omsapi, run, minLS, maxLS):
    data = getOMSdata(omsapi, "deadtimes", 
        attributes = ['overall_total_deadtime'], 
        filters = {
            "run_number": [run],
            "first_lumisection_number": [minLS, None],
            "last_lumisection_number": [None, maxLS],
        }, 
        verbose=verbose
    )
    return data[0]['attributes']['overall_total_deadtime']['percent']/100

def getPathNameWithVersion(path, HLTPaths):
    for p in HLTPaths:
        if path in p:
            return p


def getTriggerRate(omsapi, run, path, minLS, maxLS):
    data = getOMSdata(omsapi, "hltpathrates", 
    #    attributes = ["fill_number","rate","counter","last_lumisection_number","first_lumisection_number","run_number","path_name"], 
        attributes = ["counter","last_lumisection_number"], 
        filters = {
            "run_number": [run],
            "first_lumisection_number": [minLS, None],
            "last_lumisection_number": [None, maxLS],
            "path_name": [HLT_path],
        }, 
        max_pages=max_pages,
        verbose=verbose
    )
    triggerRate = 0
    for d in data:
        ls = d['attributes']['last_lumisection_number']
        triggerRate += d['attributes']['counter']/LS_lenght
    return triggerRate/len(data)

HLTPaths = getHLTpaths(omsapi, run)
HLT_path = getPathNameWithVersion(path, HLTPaths)
if not HLT_path in HLTPaths:
    pprint(HLTPaths)
    raise Exception("%s not found in the HLT menu of run %s."%(path, run))
rate = getTriggerRate(omsapi, run, HLT_path, minLS, maxLS)
if removeDeadtime: 
    rate = rate / (1.-getDeadtime(omsapi, run, minLS, maxLS))

pprint(rate)

