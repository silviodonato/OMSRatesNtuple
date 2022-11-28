## Rateplots
This script produce trigger rate plots from the OMS ntuples, which are currently stored in `/eos/user/s/sdonato/public/OMS_rates/v1.0/` (accessible outside cern using `root://eos.cern.ch//eos/user/...`). The OMS ntuples were produced by https://github.com/silviodonato/OMSRatesNtuple/tree/main/OMS_ntuplizer. 

As the size of the OMS nuples in `/eos/user/s/sdonato/public/OMS_rates/v1.0/` is less than 1 GB, it is convenient to copy them locally.


### Install RatePlots
- Get OMSRatesNtuple following https://github.com/silviodonato/OMSRatesNtuple/blob/main/README.md and go in `RatePlots` folder.

### Run Rateplots
- Edit the paramters in `trigger_plots.py`. Most of them are self-explanatory (eg. `folder` and `plotsFolder`)
- Run `python3 trigger_plots.py`
- Check the new plots in `plotsFolder` :-).

### Parameter description
- `folder`: input folder containing the OMS ntuples produced with [OMS_ntuplizer](https://github.com/silviodonato/OMSRatesNtuple/tree/main/OMS_ntuplizer) \
 (default = `/eos/user/s/sdonato/public/OMS_rates/v1.0/`).
- `plotsFolder`: output folder that will contain the plots (default `plots/`)
- `batch`: default `False`. To be activated for debugging/testing
- `testing`: default `False`. To be activated for debugging/testing
- `lumisPerBin`: number of lumi section per bins (default `20`)
- `runMin` and `runMax`: run range
- `removeOutliers`: set the maximum rate/cross-section in the plot with respect to the average. Default: `1.5` means the maximum rate showed is 50% larger than the average rate 
- `folderSelection`: list of output subfolders with the definintion of the selection criteria (eg. PU range)
- `triggers`: list of monitored triggers.
