oms_ntuplizer_dir="/eos/home-s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer/"
#oms_ntuplizer_dir="/DiskIO1OS2/OMSRatesNtuple/OMS_ntuplizer/"
echo 
echo "Running update JIRA and OMS ntuplizer scripts"
echo $(date)

command="cd /DiskIO1OS2/CronJob/ && python3 update_JIRA_google_sheet.py"
echo $command
eval $command

