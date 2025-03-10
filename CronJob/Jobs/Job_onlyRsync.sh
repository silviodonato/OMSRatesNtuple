#oms_ntuplizer_dir="/eos/home-s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer/"
local_plots="/DiskIO1OS2/OMSRatesNtuple/RatePlots/"
eos_plots="/eos/home-s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/RatePlots/"
ntuples_local="/DiskIO1OS2/OMSRatesNtuple/OMS_ntuplizer/"
ntuples_eos="/eos/home-s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer/"

echo 
echo "Processing Rsync of plots from local to EOST"
echo $(date)

#last_file=$(find $rate_plot_dir"plots/2025_CRUZET_allL1" -maxdepth 1 -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)

command="rsync -v -r ${local_plots} ${eos_plots}"
echo $command
eval $command

command="rsync -v -r ${ntuples_local} ${ntuples_eos}"
echo $command
eval $command

