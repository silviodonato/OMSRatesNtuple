'''
This code is used to produce a Google sheet  with the list of open JIRA ticket.
1) download the JIRA tickets from https://its.cern.ch/jira
2) preparare the file to be uploaded
3) update the google sheet with the new file
Example:
python3 queryJIRA.py STEAM
'''

# JIRA username and password
token = "XXXXX"
tokenFile = open("/eos/home-s/sdonato/private/jira.txt")
token = tokenFile.read()[:-1]

maxResults = 100000 # max results in JIRA query
dateLimit = "2020-01-01" # get JIRA tickets created after dateLimit

deleteAll = False ##delete all worksheets, useful for use the same style among all worksheets

# JIRA ticket query
jql_query = "project = CMSHLT AND status != Closed AND createdDate >%s"%dateLimit

# JIRA ticket API url, corresponding to https://its.cern.ch/jira
url = "https://its.cern.ch/jira/rest/api/2/search?jql=" + jql_query + "&maxResults=%d"%maxResults

# Google API credentials:
api_json_credentials = '/eos/home-s/sdonato/private/sdonato-tsg-d2a8d20b682c.json'
## Credentials done from https://console.cloud.google.com/apis/credentials -> Service Accounts -> Keys -> Add key -> Create keys -> JSON


# spreadsheet to be edited
spreadsheetId = '16zfg5fJXey9li4z7MJB9qonVTKfRKTtOHDNY-lrrhZg'  # Please set spreadsheet ID. (tsg-jira@sdonato-tsg.iam.gserviceaccount.com needs to have the rights to edit it)


##################################################################

import requests
import json

import sys


## get selected groups. [] = all
selectedGroups = []
if __name__ == "__main__":
    if len(sys.argv)>1:
        selectedGroups = ' '.join(sys.argv[1:])
        selectedGroups = selectedGroups.split(",")

print(selectedGroups)


excludeComponents = ["FOG Completed"]


# Run JIRA Ticket API query
print("Query: %s"%url)
response = requests.get(url, headers={"Authorization": "Bearer " + token})
#response.headers.update({"Authorization", "Bearer " + token})

# Check the response
if response.status_code != 200:
    raise ValueError("Failed to retrieve results from JIRA: {}".format(response.text))

# Convert json in list of jira tickets
data = json.loads(response.text)
print(len(data['issues']), " JIRA tickets found.")

JIRAs = {}

# make a list of JIRA tickets per each component. Save [key , status, created , lastView, summary, ", ".join(components)] per each JIRA
for issue in data['issues']:
    components = issue['fields']['components']
    components = [i['name'] for i in components]
    lastView = issue['fields']['lastViewed']
    created = issue['fields']['created']
    summary = issue['fields']['summary']
    status = issue['fields']['status']['name']
    created = created.split("T")[0]
    key = issue['key']
    key = '=hyperlink("https://its.cern.ch/jira/browse/%s", "%s")'%(key, key)
    if not lastView: lastView = str(created)
    else:
        lastView = lastView.split("T")[0]
    for component in components:
        if not component in JIRAs: JIRAs[component] = list()
        JIRAs[component].append([key , status, created , lastView, summary, ", ".join(components)])

################ prepare worksheets #########################################

## each group will have a worksheet. This is the list of components corresponding to each group
groups = {
    "STEAM": ['STEAM tasks', 'PerformancePlots', 'HLT prescales'],
    "STORM": ['HLT configurations', 'STORM tasks', 'ConfDB GUI Updates'],
    "FOG": ['FOG', 'L1 prescales', 'RateMon'],
    "L1T": ['L1 trigger', 'L1 prescales'],
    "DPG": ['ECAL DPG',  'HCAL DPG', 'PPS DPG', 'Tracker DPG', 'CT-PPS PAG', 'FSQ PAG'],
    "AlCa": ['AlCa'],
    "Scouting": ['Scouting'],
    }
for comp in JIRAs:
    if "POG" in comp or "PAG" in comp:
        groups[comp] = [comp]

## remove minor/old PAGs
if 'CT-PPS PAG' in groups: del groups['CT-PPS PAG']
if 'FSQ PAG' in groups: del groups['FSQ PAG']

## define "Others group"
groups['Others'] = []
for comp in JIRAs:
    if not (comp in [i for a in groups.values() for i in a]):
        groups['Others'].append(comp)

## first row of the worksheet:
labelRow = ["JIRA", "Status", "Created", "Modified", "Title", "Components"]

#make worksheets
sheets = {}
for group in groups:
    jiras = []
    sheets[group]=[labelRow]
    for comp in groups[group]:
        JIRAs[component].sort(key=lambda x: x[0], reverse=True)
        if comp in JIRAs:
            for jira in JIRAs[comp]:
                if not (jira in jiras):
                    jiras.append(jira)
                    sheets[group] .append(jira)


################ upload on Google Drive #########################################

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Utilizzare le credenziali dell'account di servizio per autenticarsi con Google Sheets API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(api_json_credentials, scope)
gc = gspread.authorize(credentials)

sh = gc.open_by_key(spreadsheetId)
worksheets = [w.title for w in sh.worksheets()]

if deleteAll: ## delete all sheets except the first one.
    for w in sh.worksheets()[1:]:
        sh.del_worksheet(w)
    worksheets = [w.title for w in sh.worksheets()]

## edit all worksheets, create them if missing
for group in sheets.keys():
    if selectedGroups and not (group in selectedGroups): 
#        print(group, " not selected")
        continue
    if not (group in worksheets): 
        print("Creating "+group)
        sh.duplicate_sheet(sh.worksheets()[0].id,new_sheet_name=group)
    else:
        print("Updating "+group)
    ws = sh.worksheet(group)
    ws.clear()
    sh.values_update(
        group,
        params={'valueInputOption': 'USER_ENTERED'},
        body={'values': sheets[group]}
    )

## order worksheets
order = ['STORM', 'FOG', 'STEAM', 'Scouting', 'AlCa', 'L1T', 'DPG', 'Tracking POG', 'B-Tagging POG', 'E/Gamma POG', 'Jets/MET POG', 'Muons POG', 'Taus POG', 'B and Quarkonia PAG', 'Exotica PAG', 'B2G PAG', 'Higgs PAG', 'Standard Model PAG', 'SUSY PAG', 'Top PAG', 'Heavy Ions PAG', 'Others']

sorting = []
for el in order:
    if el in worksheets:
        sorting.append(sh.worksheet(el))

sh.reorder_worksheets(sorting)

print(sh.url)

