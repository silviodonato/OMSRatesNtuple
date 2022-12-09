python3 trigger_plots.py --xsect --vsIntLumi --inputFile /afs/cern.ch/work/s/sdonato/public/OMS_ntuples/v2.0/2018/2018.root --triggers allL1 --selections "2018_PU45_55=pileup>45 && pileup<55 && physics_flag && hbhea && hbhec && hbheb && bpix && fpix" --nbins 10000 >& logAllL1Plots2018 &
python3 trigger_plots.py --xsect --vsIntLumi --inputFile /afs/cern.ch/work/s/sdonato/public/OMS_ntuples/v2.0/2018/2018.root --triggers allHLT --selections "2018_PU45_55=pileup>45 && pileup<55 && physics_flag && hbhea && hbhec && hbheb && bpix && fpix" --nbins 10000 >& logAllHLTPlots2018 &


python3 trigger_plots.py --xsect --vsPU --inputFile /afs/cern.ch/work/s/sdonato/public/OMS_ntuples/v2.0/2018/2018.root --removeOutliers 0.005 --triggers allL1 --selections "2018=physics_flag && hbhea && hbhec && hbheb && bpix && fpix" --lumisPerBin 10 >& logAllL1PlotsVsPU2018 &
python3 trigger_plots.py --xsect --vsPU --inputFile /afs/cern.ch/work/s/sdonato/public/OMS_ntuples/v2.0/2018/2018.root --removeOutliers 0.001 --triggers allHLT --selections "2018=physics_flag && hbhea && hbhec && hbheb && bpix && fpix" --lumisPerBin 100 >& logAllHLTPlotsVsPU2018 &

