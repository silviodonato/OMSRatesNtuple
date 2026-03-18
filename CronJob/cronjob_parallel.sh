#!/bin/bash
#export CRON_FOLDER=/eos/home-s/sdonato/www/CronJob/

/cvmfs/cms.cern.ch/cmsset_default.sh
cd /DiskIO1OS2/CMSSW_15_0_0/src
cmsenv

export OMSRATENTUPLE_FOLDER=/DiskIO1OS2/OMSRatesNtuple/
export CRON_FOLDER=$OMSRATENTUPLE_FOLDER/CronJob
#export CRON_NAME=SilvioCronJob
#export HOME_FOLDER=/DiskIO1OS2/SilvioCronJob

run_cron_job() {
  local script=$1
  local filename=$(basename "$script")
  local time=$2
  local log_file="${filename%.sh}.log"
  
  while true
  do
    kinit -R
    mkdir -p "$CRON_FOLDER/log"
    echo "Running $script . Log: $CRON_FOLDER/log/$log_file"
    ( 
      source $CRON_FOLDER/logStart.sh > $CRON_FOLDER/log/$log_file 2>&1
      kinit -R
      cp -f $CRON_FOLDER/log/$log_file $CRON_FOLDER/log/$log_file".old"
      source $CRON_FOLDER/$script >> $CRON_FOLDER/log/$log_file 2>&1
      source $CRON_FOLDER/logEnd.sh >> $CRON_FOLDER/log/$log_file 2>&1
    )
    sleep $time
  done
}

echo "Environment size: $(env | wc -c) bytes"

# Run four instances of the cron job in parallel
#files=("Jobs/Job_onlyNtuplizer.sh")
run_cron_job Jobs/Job_onlyNtuplizer.sh 60 &
#run_cron_job Jobs/Job_onlyUpdateJIRA.sh 60 &
#run_cron_job Jobs/Job_onlyPlots.sh 10 &
#run_cron_job Jobs/Job_onlyPlots_allHLT_CRUZET.sh 3600 &
#run_cron_job Jobs/Job_onlyPlots_allL1_CRUZET.sh 3600 &
run_cron_job Jobs/Job_onlyPlots_allHLT_CRAFT.sh 3600 &
run_cron_job Jobs/Job_onlyPlots_allL1_CRAFT.sh 3600 &
run_cron_job Jobs/Job_onlyPlots_allHLT_physics.sh 3600 &
run_cron_job Jobs/Job_onlyPlots_allL1_physics.sh 3600 &
#run_cron_job Jobs/Job_onlyPlots_allHLT_special.sh 3600 &
#run_cron_job Jobs/Job_onlyPlots_allL1_special.sh 3600 &
run_cron_job Jobs/Job_onlyPlots_allHLT_physics_highPU.sh 3600 &
run_cron_job Jobs/Job_onlyPlots_allL1_physics_highPU.sh 3600 &
run_cron_job Jobs/Job_onlyPlots_allHLT_physics_lowPU.sh 3600 &
run_cron_job Jobs/Job_onlyPlots_allL1_physics_lowPU.sh 3600 &

#run_cron_job Jobs/Job_onlyPlots_allHLT_HIon.sh 3600 &
#run_cron_job Jobs/Job_onlyPlots_allL1_HIon.sh 3600 &

#run_cron_job Jobs/Job_onlyPlots_allHLT_PRef.sh 3600 &
#run_cron_job Jobs/Job_onlyPlots_allL1_PRef.sh 3600 &

run_cron_job Jobs/Job_onlyRsync.sh 3600 &

#for script in "${files[@]}"
#do
#  run_cron_job $script &
#done

# Wait for all background processes to finish
wait

### nohup ./cronjob_parallel.sh >& logParallel &

