## CronJob

Here you can find the code used to submit the production of the OMS ntuple after some time, and the production of the plots.
If you need to run this in your own machine, you'll need to fix the folder defined in `cronjob_parallel.sh` and `logStart.sh`

For the submission: `./cronjob_parallel.sh` using screen. 
You might need to use `renewticket.py` to maintain a valid Kerberos token to use EOS for a long period (>1h). 

### Support:
Mattermost channel: https://mattermost.web.cern.ch/cms-tsg/channels/omsratesntuple
