## RatePlots

This script produces trigger rate plots from OMS ntuples, which are currently stored in `/eos/user/s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer/` (eg. [2024_physics_merged.root](https://sdonato.web.cern.ch/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer/2024_physics_merged.root), see [OMSRatesNtuple](https://github.com/silviodonato/OMSRatesNtuple/blob/main/README.md) for more info). These ntuples were generated using [OMS_ntuplizer](https://github.com/silviodonato/OMSRatesNtuple/tree/main/OMS_ntuplizer). 

As the size of the OMS ntuples is less than 2 GB, it might be convenient to copy them locally.

### Installation of RatePlots
Prerequisite: test that ROOT and python3 are correctly installed: `python3 -c "import ROOT"`.
You should not get any error. 

#### Method 1: Use an Existing Copy of RatePlots (Quickest Method from Lxplus)
```sh
ln -s /eos/user/s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/RatePlots/trigger_plots.py .
python3 trigger_plots.py --help
```
Note that you can even use the remote file directly:
```sh
python3 /eos/user/s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/RatePlots/trigger_plots.py --help
```

#### Method 2: Get RatePlots from GitHub (Recommended)
- Follow the instructions [here](https://github.com/silviodonato/OMSRatesNtuple/blob/main/README.md) to get OMSRatesNtuple, then:
```sh
cd RatePlots
python3 trigger_plots.py --help
```

#### Method 3: Copy RatePlots from lxplus (if you don't have a GitHub account)
- Copy RatePlots from an existing folder:
```sh
wget https://github.com/silviodonato/OMSRatesNtuple/archive/refs/heads/main.zip 
unzip  main.zip
cd OMSRatesNtuple-main/RatePlots/
python3 trigger_plots.py --help
```

### Running RatePlots

1. **Check Parameters**
   - Review available parameters using:
     ```sh
     python3 trigger_plots.py --help
     ```

2. **Run the Script**
   - Example command:
     ```sh
     python3 /eos/home-s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/RatePlots/trigger_plots.py --xsect --vsIntLumi --triggers HLT_IsoMu24_v --inputFile /eos/home-s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer//2024_physics_merged.root --output plots/   --selections "2024_physics_allHLT"="fill>9517&&recorded_lumi>0.2" 
     ```

3. **Check the Output**
   - Review the generated plots in the `plots` directory.

### Parameter Description
To understand all available options and their descriptions, run:
```sh
python3 trigger_plots.py --help
```

```
usage: trigger_plots.py [-h] [--cosmics] [--rates] [--xsect] [--vsFill] [--vsRun] [--vsPU] [--vsIntLumi] [--vsTime] [--runMin RUNMIN] [--runMax RUNMAX] [--triggers TRIGGERS] [--selections SELECTIONS]
                        [--input INPUT] [--inputFile INPUTFILE] [--output OUTPUT] [--refLumi REFLUMI] [--lumisPerBin LUMISPERBIN] [--nbins NBINS] [--removeOutliers REMOVEOUTLIERS] [--nobatch] [--postDeadtime]
                        [--testing]

https://github.com/silviodonato/OMSRatesNtuple. Example: python3 trigger_plots.py --rates --xsect --vsFill --vsPU --vsIntLumi --vsTime --lumisPerBin 30 --inputFile /afs/cern.ch/work/s/sdonato/public/OMS_ntuples/v2.0/goldejson_skim.root --triggers L1_DoubleEG_LooseIso25_LooseIso12_er1p5,HLT_IsoMu24_v --selections "PU50_60=cms_ready && beams_stable && beam2_stable && pileup>50 && pileup<60,inclusive=cms_ready && beams_stable && beam2_stable"
Example for cosmics: python3 trigger_plots.py --rates --vsRun --vsFill --vsTime --lumisPerBin 30 --input /afs/cern.ch/work/s/sdonato/public/website/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer/2023/ --triggers HLT_L1SingleMuOpen_v --selections "cosmics=1" --cosmics

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
  --postDeadtime        Do not apply deadtime correction (ie. get post-DT rates) (default: False)
  --testing             Used for debugging/development (default: False)
```

### Accessing Plots

The centrally generated plots are available at [2024_physics_allHLT]([https://sdonato.web.cern.ch/OMSRatesNtuple](https://sdonato.web.cern.ch/OMSRatesNtuple/OMSRatesNtuple/RatePlots/plots/2024_physics_allHLT/)).
