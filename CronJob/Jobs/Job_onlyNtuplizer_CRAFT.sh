oms_ntuplizer_dir="/eos/home-s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer/"
#oms_ntuplizer_dir="/DiskIO1OS2/OMSRatesNtuple/OMS_ntuplizer/"
echo 
echo "Running update OMS ntuplizer scripts"
echo $(date)

echo 
echo 
command="cd ${oms_ntuplizer_dir} && python3 OMS_ntuplizer.py"
echo $command
eval $command

# Create an array of words
words=("CRAFT" "CRUZET" "circulating" "special" "physics")
words=("CRAFT")

echo 
echo 
# Loop through each word
for word in "${words[@]}"; do
    echo 
    echo "Processing: $word"
    # Add your desired actions here
    echo 

    if [ "2024_"${word}"_merged.root" -nt "$(find 2024/*${word}* -maxdepth 1 -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)" ]
    then
        echo "Skipping "${word}" rate plots"
        echo "No new ntuples in 2024/*"${word}"*"
    else
        echo "Running "${word}" rate plots"

        command="cd ${oms_ntuplizer_dir} && ./makeTemplateForHadd 2024_"${word}"_template.root 2024/"${word}"_3*.root && hadd -f9 2024_${word}_merged.root 2024_${word}_template.root 2024/${word}_3*.root"
        echo $command
        eval $command

        ## If there are more than 1 files (was 100 files), merge them, move all other files in "partialMerge" folder 
        nFiles=$(ls -1 ${oms_ntuplizer_dir}/2024/${word}_3*.root | wc -l)
        echo "Number of files = ",$nFiles

        if [ $nFiles -gt 1 ]
        then
            echo "More than 1 files, merging and moving to partialMerge folder"

            command="cd ${oms_ntuplizer_dir}/2024 && mkdir -p partialMerge && mv ${word}_3*.root partialMerge/"
            echo $command
            eval $command

            ##get last run number
            lastrun=$(ls -1 ${oms_ntuplizer_dir}/2024/partialMerge/${word}_3*.root | tail -1 | awk -F"_" '{print $3}' | awk -F"." '{print $1}')
            echo "Last run number = ",$lastrun
            
            command="cd ${oms_ntuplizer_dir} && cp 2024_${word}_merged.root 2024/${word}_${lastrun}_partialMerged.root"
            echo $command
            eval $command
        fi

        #if word is "CRAFT" "CRUZET"

        rate_plot_dir="${oms_ntuplizer_dir}/../RatePlots/"

    fi
done	
