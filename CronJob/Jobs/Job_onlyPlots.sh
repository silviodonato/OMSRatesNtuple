oms_ntuplizer_dir="/eos/home-s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer/"
#oms_ntuplizer_dir="/DiskIO1OS2/OMSRatesNtuple/OMS_ntuplizer/"
echo 
echo "Running OMS plots"
echo $(date)

# Create an array of words
words=("CRAFT" "CRUZET" "circulating" "special" "physics")
words=("physics" "CRAFT")

echo 
echo 
# Loop through each word
for word in "${words[@]}"; do
    echo 
    echo "Processing: $word"
    # Add your desired actions here
    echo 

    rate_plot_dir="${oms_ntuplizer_dir}/../RatePlots/"

    #if word is "CRAFT" "CRUZET"

    last_allHLT_cosmics_file=$(find $rate_plot_dir"plots/2024_${word}_allHLT" -maxdepth 1 -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    last_allL1_cosmics_file=$(find $rate_plot_dir"plots/2024_${word}_allL1" -maxdepth 1 -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    last_allHLT_physics_file=$(find $rate_plot_dir"plots/2024_${word}_allHLT" -maxdepth 1 -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    last_allL1_physics_file=$(find $rate_plot_dir"plots/2024_${word}_allL1" -maxdepth 1 -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)

    if [ $word == "CRAFT" ] || [ $word == "CRUZET" ] || [ $word == "circulating" ]
    then
        if [ ${oms_ntuplizer_dir}/"2024_"${word}"_merged.root" -nt "$last_allHLT_cosmics_file" ]
        then
            command="cd ${rate_plot_dir} && python3 trigger_plots.py --cosmics --rates  --vsRun --vsFill --vsTime  --lumisPerBin 30 --inputFile \"${oms_ntuplizer_dir}/2024_${word}_merged.root\" --triggers allHLT  --selections \"2024_${word}_allHLT=fill>9517\""
            echo $command
            eval $command
        else
            echo "No new ntuples in 2024_"${word}"_merged.root"
            ls -l ${oms_ntuplizer_dir}/"2024_"${word}"_merged.root"
            ls -l $last_allHLT_cosmics_file
        fi
        if [ ${oms_ntuplizer_dir}/"2024_"${word}"_merged.root" -nt "$last_allL1_cosmics_file" ]
        then
            command="cd ${rate_plot_dir} && python3 trigger_plots.py --cosmics --rates  --vsRun --vsFill --vsTime  --lumisPerBin 30 --inputFile \"${oms_ntuplizer_dir}/2024_${word}_merged.root\" --triggers allL1  --selections \"2024_${word}_allL1=fill>9517\""
            echo $command
            eval $command
        else
            echo "No new ntuples in 2024_"${word}"_merged.root"
            ls -l ${oms_ntuplizer_dir}/"2024_"${word}"_merged.root"
            ls -l $last_allL1_cosmics_file
        fi
    else ## PHYSICS
        if [ ${oms_ntuplizer_dir}/"2024_"${word}"_merged.root" -nt "$last_allHLT_physics_file" ]
        then
            command="cd ${rate_plot_dir} && python3 trigger_plots.py --xsect --rates  --vsRun --vsFill --vsTime --vsIntLumi --vsPU  --lumisPerBin 30 --inputFile \"${oms_ntuplizer_dir}/2024_${word}_merged.root\" --triggers HLT_*,DST_*,AlCa_*,Status_*,Stream*,Dataset*  --selections \"2024_${word}_allHLT=recorded_lumi_per_lumisection>0.2\",\"2024_${word}_allHLT_highPU=recorded_lumi_per_lumisection>0.2&&pileup>60&&pileup<70\""
            echo $command
            eval $command
        else
            echo "No new ntuples in 2024_"${word}"_merged.root"
            ls -l ${oms_ntuplizer_dir}/"2024_"${word}"_merged.root"
            ls -l $last_allHLT_physics_file
        fi

        if [ ${oms_ntuplizer_dir}/"2024_"${word}"_merged.root" -nt "$last_allL1_physics_file" ]
        then
            command="cd ${rate_plot_dir} && python3 trigger_plots.py --xsect --rates  --vsRun --vsFill --vsTime  --vsIntLumi  --vsPU --lumisPerBin 30 --inputFile \"${oms_ntuplizer_dir}/2024_${word}_merged.root\" --triggers allL1  --selections \"2024_${word}_allL1=recorded_lumi_per_lumisection>0.2\",\"2024_${word}_allL1_highPU=recorded_lumi_per_lumisection>0.2&&pileup>60&&pileup<70\""
            echo $command
            eval $command
        else
            echo "No new ntuples in 2024_"${word}"_merged.root"
            ls -l ${oms_ntuplizer_dir}/"2024_"${word}"_merged.root"
            ls -l $last_allL1_physics_file
        fi
    fi
done	
