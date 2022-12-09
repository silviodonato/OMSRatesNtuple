python3 trigger_plots.py --xsect --vsIntLumi --inputFile /afs/cern.ch/work/s/sdonato/public/OMS_ntuples/v2.0/goldejson_skim.root --triggers allL1 --selections "PU45_55=pileup>45 && pileup<55" --nbins 10000 >& logAllL1Plots &
python3 trigger_plots.py --xsect --vsIntLumi --inputFile /afs/cern.ch/work/s/sdonato/public/OMS_ntuples/v2.0/goldejson_skim.root --triggers allHLT --selections "PU45_55=pileup>45 && pileup<55" --nbins 10000 >& logAllHLTPlots &


python3 trigger_plots.py --xsect --vsPU --inputFile /afs/cern.ch/work/s/sdonato/public/OMS_ntuples/v2.0/goldejson_skim.root --removeOutliers 0.005 --triggers allL1 --selections "RunFG=run>360389" --lumisPerBin 10 >& logAllL1PlotsVsPU &
python3 trigger_plots.py --xsect --vsPU --inputFile /afs/cern.ch/work/s/sdonato/public/OMS_ntuples/v2.0/goldejson_skim.root --removeOutliers 0.001 --triggers allHLT --selections "RunFG=run>360389" --lumisPerBin 100 >& logAllHLTPlotsVsPU &

