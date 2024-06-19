## OMSRatesNtuple

This repository contains two primary tools designed to facilitate the downloading and visualization of trigger rates from the Online Monitoring System (OMS):

- **[OMS_ntuplizer](https://github.com/silviodonato/OMSRatesNtuple/tree/main/OMS_ntuplizer)**: This tool allows you to download trigger rates from OMS and save them as ROOT files. Pre-generated ntuples can be found at the following locations:
  - EOS: `/eos/user/s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer/`;
  - Webiste: https://sdonato.web.cern.ch/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer/;
  - CERN box: https://cernbox.cern.ch/files/spaces/eos/user/s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer.

The latest (2024) OMS ntuple for 13.6 TeV pp collisions (physics) is [2024_physics_merged.root](https://sdonato.web.cern.ch/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer/2024_physics_merged.root).

- **[RatePlots](https://github.com/silviodonato/OMSRatesNtuple/tree/main/RatePlots)**: This script is used to generate plots of trigger rates, such as trigger cross-sections as a function of LHC integrated luminosity, using the OMS ntuples created by [OMS_ntuplizer](https://github.com/silviodonato/OMSRatesNtuple/tree/main/OMS_ntuplizer). The plots are available at the same locations:
  - EOS: `/eos/user/s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/RatePlots/plots/`;
  - Webiste: https://sdonato.web.cern.ch/OMSRatesNtuple/OMSRatesNtuple/RatePlots/plots/;
  - CERN box: https://cernbox.cern.ch/files/spaces/eos/user/s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/RatePlots/plots/.

The latest (2024) plots for 13.6 TeV pp collisions (physics) are available on [2024_physics_allHLT](https://sdonato.web.cern.ch/OMSRatesNtuple/OMSRatesNtuple/RatePlots/plots/2024_physics_allHLT/) folder.

### Getting Started with OMSRatesNtuple

To begin using OMSRatesNtuple, first clone the repository:

```sh
git clone git@github.com:silviodonato/OMSRatesNtuple.git
```

Next, follow the instructions provided in the README files for each specific tool:
- [OMS_ntuplizer README](https://github.com/silviodonato/OMSRatesNtuple/blob/main/OMS_ntuplizer/README.md)
- [RatePlots README](https://github.com/silviodonato/OMSRatesNtuple/blob/main/RatePlots/README.md)
