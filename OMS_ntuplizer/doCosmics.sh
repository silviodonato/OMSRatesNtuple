cd /afs/cern.ch/work/s/sdonato/public/website/OMSRatesNtuple/OMSRatesNtuple/RatePlots/ && python3 trigger_plots.py --rates  --vsRun --vsFill --vsTime --lumisPerBin 30 --input /afs/cern.ch/work/s/sdonato/public/website/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer/2023/ --triggers allHLT,L1_SingleMuCosmics,L1_SingleMuOpen,L1_SingleMu3,L1_SingleMuCosmics_BMTF,L1_SingleMuCosmics_OMTF,L1_SingleMuCosmics_EMTF,L1_SingleMu7,L1_SingleJet35,L1_SingleJet60,L1_SingleMu18,L1_ETMHF70,L1_HTT120er,L1_DoubleMu0,L1_TripleMu_5_3_3,L1_SingleIsoEG26er2p5  --selections "cosmics=run>363400" --cosmics