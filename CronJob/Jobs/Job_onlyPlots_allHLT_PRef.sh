oms_ntuplizer_dir="/eos/home-s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer/"
#oms_ntuplizer_dir="/DiskIO1OS2/OMSRatesNtuple/OMS_ntuplizer/"
echo 
echo "Processing OMS plots allHLT_PRef"
echo $(date)

rate_plot_dir="${oms_ntuplizer_dir}/../RatePlots/"

#if word is "CRAFT" "CRUZET"

last_file=$(find $rate_plot_dir"plots/2024_PRef_allHLT" -maxdepth 1 -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)

if [ ${oms_ntuplizer_dir}/"2024_PRef_merged.root" -nt "$last_file" ]
then
    command="cd ${rate_plot_dir} && python3 trigger_plots.py --xsect --rates  --vsRun --vsFill --vsTime  --vsIntLumi  --vsPU  --lumisPerBin 30 --inputFile \"${oms_ntuplizer_dir}/2024_PRef_merged.root\" --triggers HLT_*,DST_*,AlCa_*,Status_*,Stream*,Dataset*  --selections \"2024_PRef_allHLT=recorded_lumi_per_lumisection>0.0002\""
    echo $command
    eval $command
else
    echo "No new ntuples in 2024_PRef_merged.root"
    ls -l ${oms_ntuplizer_dir}/"2024_PRef_merged.root"
    ls -l $last_file
fi
