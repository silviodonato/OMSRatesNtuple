#oms_ntuplizer_dir="/eos/home-s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer/"
oms_ntuplizer_dir="/DiskIO1OS2/OMSRatesNtuple/OMS_ntuplizer/"
echo 
echo "Processing OMS plots allL1_CRUZET"
echo $(date)

rate_plot_dir="${oms_ntuplizer_dir}/../RatePlots/"

#if word is "CRUZET" "CRUZET"

last_file=$(find $rate_plot_dir"plots/2025_CRUZET_allL1" -maxdepth 1 -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)

if [ ${oms_ntuplizer_dir}/"2025_CRUZET_merged.root" -nt "$last_file" ]
then
    command="cd ${rate_plot_dir} && python3 trigger_plots.py --cosmics --rates  --vsRun --vsFill --vsTime  --lumisPerBin 30 --inputFile \"${oms_ntuplizer_dir}/2025_CRUZET_merged.root\" --triggers allL1  --selections \"2025_CRUZET_allL1=fill>9517\""
    echo $command
    eval $command
else
    echo "No new ntuples in 2025_CRUZET_merged.root"
    ls -l ${oms_ntuplizer_dir}/"2025_CRUZET_merged.root"
    ls -l $last_file
fi
