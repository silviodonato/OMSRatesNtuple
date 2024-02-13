## Rateplots
This script produce trigger rate plots from the OMS ntuples, which are currently stored in `/eos/cms/store/group/dpg_trigger/comm_trigger/TriggerStudiesGroup/OMSRatesNtuple/` (accessible outside cern using `root://eoscms.cern.ch//eos/cms/...` and at https://sdonato.web.cern.ch/sdonato/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer). The OMS ntuples were produced using https://github.com/silviodonato/OMSRatesNtuple/tree/main/OMS_ntuplizer. 

As the size of the OMS nuples in `/eos/user/s/sdonato/public/OMS_rates/v2.0/` is less than 2 GB, it might be convenient to copy it locally.
The folder contains also some other merged ntuples (eg. goldejson_skim.root, physics_merged.root).

### Installation of RatePlots

#### Method 1: Link to an existing copy of RatePlots (quickest method)
```
mkdir RatePlots
cd RatePlots
ln -s /afs/cern.ch/work/s/sdonato/public/website/OMSRatesNtuple/OMSRatesNtuple/RatePlots/*.py .
python3 trigger_plots.py --help
```
Note that you can even use directly the remote file:
```
python3 /afs/cern.ch/work/s/sdonato/public/website/OMSRatesNtuple/OMSRatesNtuple/RatePlots/trigger_plots.py --help
```

#### Method 2: Get RatePlots from GitHub (recommended)
- Get OMSRatesNtuple following https://github.com/silviodonato/OMSRatesNtuple/blob/main/README.md and the:
```
cd RatePlots
python3 trigger_plots.py --help
```

#### Method 3: Copy RatePlots from lxplus (if you don't have a GitHub account)
- Copy RatePlots from an existing folder:
```
mkdir RatePlots
cd RatePlots
cp /afs/cern.ch/work/s/sdonato/public/website/OMSRatesNtuple/OMSRatesNtuple/RatePlots/*py
python3 trigger_plots.py --help
```

### Run Rateplots
- Check some parameters in `python3 trigger_plots.py --help`. You can find some example in doAll.sh.
- Run `python3 trigger_plots.py` (example: `python3 trigger_plots.py --xsect --vsPU --vsIntLumi --lumisPerBin 30 --inputFile
root://eoscms.cern.ch//eos/cms/store/group/dpg_trigger/comm_trigger/TriggerStudiesGroup/OMSRatesNtuple/2023/physics_merged.root --triggers L1_DoubleEG_LooseIso25_LooseIso12_er1p5,HLT_IsoMu24_v --selections "PU50_60=cms_ready && beams_stable && beam2_stable
&& pileup>50 && pileup<60,inclusive=cms_ready && beams_stable && beam2_stable"`)
- Check the new plots in `plots` :-).

### Parameter description
```
python3 trigger_plots.py --help
```

```
usage: trigger_plots.py [-h] [--cosmics] [--rates] [--xsect] [--vsFill] [--vsRun] [--vsPU] [--vsIntLumi] [--vsTime] [--runMin RUNMIN] [--runMax RUNMAX] [--triggers TRIGGERS] [--selections SELECTIONS]
                        [--input INPUT] [--inputFile INPUTFILE] [--output OUTPUT] [--refLumi REFLUMI] [--lumisPerBin LUMISPERBIN] [--nbins NBINS] [--removeOutliers REMOVEOUTLIERS] [--nobatch]
                        [--testing]

https://github.com/silviodonato/OMSRatesNtuple. Example: python3 trigger_plots.py --rates --xsect --vsFill --vsPU --vsIntLumi --vsTime --lumisPerBin 30 --inputFile
/afs/cern.ch/work/s/sdonato/public/OMS_ntuples/v2.0/goldejson_skim.root --triggers L1_DoubleEG_LooseIso25_LooseIso12_er1p5,HLT_IsoMu24_v --selections "PU50_60=cms_ready && beams_stable && beam2_stable
&& pileup>50 && pileup<60,inclusive=cms_ready && beams_stable && beam2_stable" Example cosmics: python3 trigger_plots.py --rates --vsRun --vsFill --vsTime --lumisPerBin 30 --input
/afs/cern.ch/work/s/sdonato/public/website/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer/2023/ --triggers HLT_L1SingleMuOpen_v --selections "cosmics=1" --cosmics

options:
  -h, --help            show this help message and exit
  --cosmics             Run cosmics rates (no pileup, no lumi) (default: False)
  --rates               Make rates plots (default: False)
  --xsect               Make cross sections plots. Selected by default if no --rates nor --rates are defined (default: False)
  --vsFill              Make plots vs fill number (default: False)
  --vsRun               Make plots vs run number (default: False)
  --vsPU                Make plots vs pileup (default: False)
  --vsIntLumi           Make plots vs integrated luminosity. Selected by default if any --vs* flag is defined (default: False)
  --vsTime              Make plots vs days (default: False)
  --runMin RUNMIN       Select files with run>runMin. This option will be ignored when used with --inputFile. The minimum run possible run is 355678 (July 17, 2022) (default: 362104)
  --runMax RUNMAX       Run max (default: 1000000)
  --triggers TRIGGERS   List of trigger used in the plots, separated by ",". If undefined, the triggerList defined in trigger_plots.py will be used. Example: --triggers HLT_IsoMu24_v,AlCa_PFJet40_v.
                        Use --triggers allHLT,allL1 option to run on all HLT and L1 triggers. (default: )
  --selections SELECTIONS
                        List of selections used in the plots, separated by ",". If undefined, the triggerList defined in trigger_plots.py will be used. (default: )
  --input INPUT         Input folder containing the OMS ntuples. Cannot be used with --inputFile option. [Eg. /afs/cern.ch/work/s/sdonato/public/OMS_ntuples/v2.0/] (default: )
  --inputFile INPUTFILE
                        Input file containing the OMS ntuples. Cannot be used with --input option. [Eg. /afs/cern.ch/work/s/sdonato/public/OMS_ntuples/v2.0/goldejson_skim.root] (default: )
  --output OUTPUT       Folder of the output plots (default: plots/)
  --refLumi REFLUMI     Reference rate used in the cross-section plots. (default: 2e+34)
  --lumisPerBin LUMISPERBIN
                        Number of lumisections that will be merged in the plots. Cannot work with --nbins (default: -1)
  --nbins NBINS         Number of max bins. Cannot work with --lumisPerBin. Default=1000 (default: -1)
  --removeOutliers REMOVEOUTLIERS
                        Percentile of data points that will excluded from the plots. This is necessary to remove the rates spikes from the plots. (default: 0.01)
  --nobatch             Disable ROOT batch mode (default: False)
  --testing             Used for debugging/development (default: False)
```

### Plots

- The plots obtained centrally are available at https://sdonato.web.cern.ch/OMSRatesNtuple
