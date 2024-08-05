#!/usr/bin/python3
import ROOT
import tdrstyle #https://twiki.cern.ch/twiki/bin/viewauth/CMS/Internal/FigGuidelines

skipFit = True
tdrstyle = tdrstyle.setTDRStyle()
tdrstyle.cd()
import os

chain = ROOT.TChain("tree")

selectionDefault = {
    "PU50_60": "cms_ready && beams_stable && pileup>50 && pileup<60",
    "inclusive": "cms_ready && beams_stable",
}

triggerDefault = [
    "HLT_HT200_L1SingleLLPJet_DisplacedDijet35_Inclusive1PtrkShortSig5_v3",
    "HLT_L1Tau_DelayedJet40_DoubleDelay1p25nsInclusive_v1",
    "HLT_HT430_DelayedJet40_SingleDelay1nsTrackless_v3",
    "HLT_HT270_L1SingleLLPJet_DisplacedDijet40_DisplacedTrack_v3",
    "HLT_Photon200_v16",
    "HLT_Photon110EB_TightID_TightIso_v4",


    ## since  355678
    "HLT_DoubleMediumChargedIsoDisplacedPFTauHPS32_Trk1_eta2p1_v",
    "HLT_IsoMu24_v",
    "HLT_Ele30_WPTight_Gsf_v",
    "HLT_QuadPFJet70_50_40_35_PFBTagParticleNet_2BTagSum0p65_v" ,
    "HLT_AK8PFJet250_SoftDropMass40_PFAK8ParticleNetBB0p35_v",
    "HLT_AK8PFJet420_TrimMass30_v",
    "HLT_PFHT330PT30_QuadPFJet_75_60_45_40_TriplePFBTagDeepJet_4p5_v",
    "L1_SingleIsoEG30er2p5",
    "L1_SingleEG36er2p5",
    "L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p6",
    "L1_DoubleIsoTau34er2p1",
    "L1_LooseIsoEG30er2p1_HTT100er",
    "L1_SingleMu22",
    "L1_HTT360er",
    "L1_ETMHF90",
    "L1_DoubleEG_LooseIso25_LooseIso12_er1p5",

    ## since  356409
    "HLT_DoubleEle7p5_eta1p22_mMax6_v",
    "HLT_PFMETNoMu110_PFMHTNoMu110_IDTight_FilterHF_v",
    "AlCa_PFJet40_v",
    "HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1_v",
    "HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId_Mass55_v",

    ## since 359530
]


#for tr in triggerColors: triggerColors[tr]= ROOT.kBlue


###################################################
import argparse

parser = argparse.ArgumentParser( 
    description='''https://github.com/silviodonato/OMSRatesNtuple. 
Example:
python3 /eos/home-s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/RatePlots/trigger_plots.py --xsect --vsIntLumi --triggers HLT_IsoMu24_v --inputFile /eos/home-s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer//2024_physics_merged.root --output plots/   --selections "2024_physics_allHLT"="fill>9517&&recorded_lumi>0.2" 

Example cosmics:
python3 trigger_plots.py --xsect --vsIntLumi --triggers HLT_IsoMu24_v --inputFile /eos/home-s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer//2024_physics_merged.root --output plots/   --selections "2024_physics_allHLT"="fill>9517&&recorded_lumi_per_lumisection>0.2"
''', 
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

parser.add_argument('--cosmics', action='store_const', const=True, default=False, help='Run cosmics rates (no pileup, no lumi)')
parser.add_argument('--rates', action='store_const', const=True, default=False, help='Make rates plots')
parser.add_argument('--xsect', action='store_const', const=True, default=False, help='Make cross sections plots. Selected by default if no --rates nor --rates are defined')
parser.add_argument('--vsFill', action='store_const', const=True, default=False, help='Make plots vs fill number')
parser.add_argument('--vsRun', action='store_const', const=True, default=False, help='Make plots vs run number')
parser.add_argument('--vsPU', action='store_const', const=True, default=False, help='Make plots vs pileup')
parser.add_argument('--vsIntLumi', action='store_const', const=True, default=False, help='Make plots vs integrated luminosity. Selected by default if any --vs* flag is defined')
parser.add_argument('--vsTime', action='store_const', const=True, default=False, help='Make plots vs days')
parser.add_argument('--runMin', default=362104 , help='Select files with run>runMin. This option will be ignored when used with --inputFile. The minimum run possible run is 355678 (July 17, 2022)')
parser.add_argument('--runMax', default=1000000 , help='Run max')
parser.add_argument('--triggers', default="" , help='List of trigger used in the plots, separated by ",". If undefined, the triggerList defined in trigger_plots.py will be used. Example: --triggers HLT_IsoMu24_v,AlCa_PFJet40_v. Use --triggers allHLT,allL1 option to run on all HLT and L1 triggers.')
parser.add_argument('--selections', default="" , help='List of selections used in the plots, separated by ",". If undefined, the triggerList defined in trigger_plots.py will be used.')
parser.add_argument('--input', default="" , help='Input folder containing the OMS ntuples. Cannot be used with --inputFile option. [Eg. /afs/cern.ch/work/s/sdonato/public/OMS_ntuples/v2.0/]')
parser.add_argument('--inputFile', default="" , help='Input file containing the OMS ntuples. Cannot be used with --input option. [Eg. /afs/cern.ch/work/s/sdonato/public/OMS_ntuples/v2.0/goldejson_skim.root]')
parser.add_argument('--output', default="plots/" , help='Folder of the output plots')
parser.add_argument('--refLumi', default=2E34 , help='Reference rate used in the cross-section plots.')
parser.add_argument('--lumisPerBin', default=-1 , help='Number of lumisections that will be merged in the plots. Cannot work with --nbins')
parser.add_argument('--nbins', default=-1 , help='Number of max bins. Cannot work with --lumisPerBin. Default=1000')
parser.add_argument('--removeOutliers', default="0.01" , help='Percentile of data points that will excluded from the plots. This is necessary to remove the rates spikes from the plots.')
parser.add_argument('--nobatch', action='store_const', const=True, default=False, help='Disable ROOT batch mode')
parser.add_argument('--postDeadtime', action='store_const', const=True, default=False, help='Do not apply deadtime correction (ie. get post-DT rates)')
parser.add_argument('--testing', action='store_const', const=True, default=False, help='Used for debugging/development')

args = parser.parse_args()

from tools import readOptions
useRates, vses, triggers, inputFolder, inputFile, plotsFolder, removeOutliers, runMin, runMax, collisions, batch, deadtimeCorrection, testing, lumisPerBin, refLumi, selections, nbins = readOptions(parser.parse_args(), triggerDefault, selectionDefault)

print("##### Options #####")
print ("trigger_plots.py will produce %d x %d x %d x %d = %d plots in %s using OMS ntuples from %s,"%(len(useRates),len(vses),len(triggers),len(selections),len(useRates)*len(vses)*len(triggers)*len(selections), plotsFolder, inputFolder if inputFolder else inputFile))
if lumisPerBin>0: print("using %d lumisection per bin"%nbins)
if nbins>0: print("using %d bins"%nbins)
print(vses)
print("useRates=",useRates)
print("triggers=",triggers)
print("selections=",selections)
print()
print("Runs %d - %d"%(runMin,runMax))
print("removeOutliers = %f (percentile)"%removeOutliers)
print("refLumi = %f"%refLumi)
print("batch = %s"%str(batch))
print("deadtimeCorrection = %s"%str(deadtimeCorrection))
print("testing = %s"%str(testing))
print("###################")



###################################################

if inputFile:
    chain = ROOT.TChain("tree")
    chain.Add(inputFile)
else:
    try:
        files = os.listdir(inputFolder)
    except:
        print("#"*100)
        print("Input folder %s not found. Please check your --input option."%inputFolder)
        print("You can download the OMS ntuple from OMS using:")
        print("xrdcp --recursive root://eosuser.cern.ch//eos/home-s/sdonato/www/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer/2023_rereco_physics_merged.root  .")
        print("#"*100)


    ## Use only few files and few triggers for testing:
    if testing:
        import shutil
        selections = {"testing":selections["inclusive"]}
        for f in selections:
            shutil.rmtree(plotsFolder+"/"+f)
        lumisPerBin = 1
    #    files = ["362655.root","357900.root"]
    #    triggers = ["HLT_DoubleMediumChargedIsoDisplacedPFTauHPS32_Trk1_eta2p1_v", "HLT_IsoMu24_v","AlCa_PFJet40_CPUOnly_v"]
        runMin = 360449 # July 17. Different unit for rec lumi before this run.
        runMax = 361500
        vses = ["vsFill"]
        useRates = [False]
        inputFolder = "/home/sdonato/CMS/OMS_plots/OMS_ntuples/"
    #    batch=False

    runs = [int(f.split(".root")[0]) for f in files  if (f[0]=="3" and f[-5:]==".root")]
    #selection = "pileup_vs>53 && pileup_vs<57 && cms_ready && beams_stable && beam2_stable"
    #selection = "pileup_vs>54 && pileup_vs<56 && cms_ready && beams_stable && beam2_stable"
    #selection = "HLT_DoubleMediumChargedIsoDisplacedPFTauHPS32_Trk1_eta2p1_v>0"


    ## Load all not-empy files
    for run in sorted(runs):
        fName = "%s/%d.root"%(inputFolder,run)
        if runMin>0 and run<runMin: continue
        if runMax>0 and run>runMax: continue
        if os.path.getsize(fName) > 1000 :
            chain.AddFile(fName)

## Constants
#timeUnit = 24.*60*60  ## 1 day
timeUnit = 1 ## 1 sec

LS_seconds = 2**18 / 11245.5 
LS_duration = LS_seconds/ timeUnit #LS in days
from datetime import datetime
from datetime import timedelta
#offset = int(datetime(2023,1,1).timestamp()) - int(datetime(2022,8,31).timestamp())  #since Nov 1, 2022 instead of #since Jan 1, 2023
#daysSince = datetime(2024,1,31)
try: ## python3 - reccomended
    offset = int(datetime(2024,1,1).timestamp())  #since Feb 29, 2024
#    offset = int(datetime(2024,1,1).timestamp())  #since Feb 29, 2024
#    offset = int(datetime(2024,1,1).timestamp()) - int(daysSince.timestamp())  #since Feb 29, 2024
except: ## python
    offset = 23850000 ## Mar31, 2023 
    print("Please use 'python3' instead of 'python',")
    print("using offset %d. This should be equal to int(datetime(2023,1,1).timestamp()) - int(datetime(2022,3,31).timestamp()) in python3 [from datetime import datetime] ")
#offset += -4294967296 ## bug fix ntuple v2.0
#offset =5270400 ## Nov1 (ie. 0. = Nov1)
#offset =5356800 ## Oct31 (ie. 1. = Nov1)
#offset =10630800 ## Aug31 

#1/0

ROOT.gROOT.SetBatch(batch)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)

## get fill number from the first event
#chain.GetEvent(0)
#firstFill = chain.fill
#firstRun = chain.run

chain.Draw("fill >> tmpFill","","GOFF")
tmpFill = ROOT.gROOT.Get("tmpFill")
firstFill, lastFill = tmpFill.GetXaxis().GetXmin(), tmpFill.GetXaxis().GetXmax()

chain.Draw("run >> tmpRun","","GOFF")
tmpRun = ROOT.gROOT.Get("tmpRun")
firstRun, lastRun = tmpRun.GetXaxis().GetXmin(), tmpRun.GetXaxis().GetXmax()

import fnmatch

branches = [a.GetName() for a in chain.GetListOfLeaves()]

## Skip missing triggers and use wildcards
triggers_expanded = []
for entry in [0, chain.GetEntries()-1]: #check only the first and last event
    chain.GetEvent(entry)
    for trigger in triggers[:]:
        trigger_matched = fnmatch.filter(branches, trigger) ## expands trigger matching (eg. HLT_IsoMu*)
        triggers_expanded += [ t for t in trigger_matched if not t in triggers_expanded] ## avoid duplicates
        if len(trigger_matched)==0:
            print("##### Trigger %s not found in run %d. Removed from the trigger list. #####"%(trigger,chain.run))
        if trigger == "allHLT": 
            triggers += [a.GetName() for a in chain.GetListOfLeaves() if a.GetName()[:4]=="HLT_"]
        if trigger == "allL1": 
            triggers += [a.GetName() for a in chain.GetListOfLeaves() if a.GetName()[:3]=="L1_"]
triggers = triggers_expanded


## Time varibale
timeVar = "(time + %f)/%f "%(offset, timeUnit)

# Loop over selections
if not os.path.exists(plotsFolder):
    os.mkdir(plotsFolder)
for selFolder in selections:
    print("Doing %s"%selFolder)
    outFolder = plotsFolder+"/"+selFolder
    if not os.path.exists(outFolder):
        os.mkdir(outFolder)
    selection = selections[selFolder]

    # get binning
    from tools import getBinning, getBinningFromMax
    if lumisPerBin>0:
        bin_size = LS_duration * lumisPerBin
        ntimebins, timemin, timemax = getBinning(chain, timeVar, selection, bin_size)
        binning = "(%s,%s,%s)"%(ntimebins,timemin,timemax)
    elif nbins>0:
        ntimebins, timemin, timemax = getBinningFromMax(chain, timeVar, selection, LS_duration, nbins)
        binning = "(%s,%s,%s)"%(ntimebins,timemin,timemax)
    

    # get common histograms
    from tools import getHisto
    fillNumber_vsTime = getHisto("fill", chain, timeVar, binning, selection, deadtimeCorrection=False)
    runNumber_vsTime = getHisto("run", chain, timeVar, binning, selection, deadtimeCorrection=False)
    if collisions:
        deliveredLumi_vsTime = getHisto("delivered_lumi_per_lumisection", chain, timeVar, binning, "1",deadtimeCorrection=False) #1000 pb-1 = fb-1
        deliveredLumi_vsTime.Scale(1./1000)# pb-1 -> fb-1
        intLumi_vsTime = deliveredLumi_vsTime.GetCumulative()
        intLumi_vsTime.SetName(intLumi_vsTime.GetName().replace("_",""))
    count_vsTime = getHisto("1", chain, timeVar, binning, selection, deadtimeCorrection=False) ## count_vs number of entries per bin
    if collisions:
        pileup_vsTime = getHisto("pileup", chain, timeVar, binning, selection, deadtimeCorrection=False) ##co
        delLumi_vsTime = getHisto("delivered_lumi_per_lumisection", chain, timeVar, binning, selection, deadtimeCorrection=False) #pb-1 * 1E33 = 1 cm-2
        ## loop on bin and set bin error to zero
        for i in range(delLumi_vsTime.GetNbinsX()):
            delLumi_vsTime.SetBinError(i+1,0) 
    print("get common histograms: DONE")

    ## take the average value per bin, instead of the sum, for non-cumulative variables
    from tools import dropError
    fillNumber_vsTime.Divide(count_vsTime) 
    runNumber_vsTime.Divide(count_vsTime) 
    dropError(fillNumber_vsTime)
    dropError(runNumber_vsTime)
    fillNumber_vsTime.SetMinimum(firstFill)
    runNumber_vsTime.SetMinimum(firstRun)


    ## compute the histograms binned per fillNumber instead of run number
    from tools import getHistoVsFillNumber
    count_vsFill = getHistoVsFillNumber(count_vsTime, fillNumber_vsTime)
    if collisions:
        delLumi_vsFill = getHistoVsFillNumber(delLumi_vsTime, fillNumber_vsTime)
        intLumi_vsFill = getHistoVsFillNumber(intLumi_vsTime, fillNumber_vsTime)
    count_vsRun = getHistoVsFillNumber(count_vsTime, runNumber_vsTime)
    if collisions:
        delLumi_vsRun = getHistoVsFillNumber(delLumi_vsTime, runNumber_vsTime)
        intLumi_vsRun = getHistoVsFillNumber(intLumi_vsTime, runNumber_vsTime)
#    pileup_vsTime.Divide(count_vsTime) 
#    pileup_vsFill = getHistoVsFillNumber(pileup_vsTime, fillNumber_vsTime)
#    delLumi_vsFill.Draw()
    
    if collisions:
        pileup_vsRun = getHistoVsFillNumber(pileup_vsTime, runNumber_vsTime)
        pileup_vsFill = getHistoVsFillNumber(pileup_vsTime, fillNumber_vsTime)
        pileup_vsTime.Divide(count_vsTime) 
        pileup_vsFill.Divide(count_vsFill) 
        pileup_vsRun.Divide(count_vsRun) 
        dropError(pileup_vsTime)
        dropError(pileup_vsFill)
        dropError(pileup_vsRun)
    
    # init canvas
    from style import res_X,res_Y, gridX, gridY
    canv = ROOT.TCanvas("canv","",res_X,res_Y)
    canv.UseCurrentStyle()
    canv.SetGridx(gridX)
    canv.SetGridy(gridY)
    
    from style import title_vsLumi,intLumiLabel,timeLabel
    if collisions:
        intLumiLabel = intLumiLabel%firstFill ## replace %s with the actual first fill number 
        # plot integrated lumi vs time
        intLumi_vsTime.SetTitle("")
        intLumi_vsTime.GetXaxis().SetTitle(timeLabel)
        intLumi_vsTime.GetYaxis().SetTitle(intLumiLabel)
        intLumi_vsTime.Draw("HIST")
        canv.Update()
        canv.Modify()
        
        canv.SaveAs(outFolder+"/AintLumi_vsTime.root")
        canv.SaveAs(outFolder+"/AintLumi_vsTime.png")
    
    # plot the fill number vs integrated luminosity
    from style import fillLabel, fillNumberMargin, runLabel
    for var in ['fill','run']:
        if var == 'fill':
            xlabel = fillLabel
            plotNumber_vsTime = fillNumber_vsTime
            firstNumber = firstFill
        elif var == 'run':
            xlabel = runLabel
            plotNumber_vsTime = runNumber_vsTime
            firstNumber = firstRun
        lastFill = plotNumber_vsTime.GetMaximum()
        if collisions:
            plotNumber_vsLumi = ROOT.TGraph(len(plotNumber_vsTime))
            npoints=0
            for i in range(len(plotNumber_vsTime)):
                if plotNumber_vsTime[i]>0:
                    plotNumber_vsLumi.SetPoint(npoints,intLumi_vsTime[i],plotNumber_vsTime[i])
                    npoints+=1
            plotNumber_vsLumi.SetMarkerSize(0.5)
            plotNumber_vsLumi.SetMarkerStyle(21)
            plotNumber_vsLumi.SetTitle("")
            #plotNumber_vsLumi.GetXaxis().SetRangeUser(xsec_vsLum.keys()[0].GetXaxis().GetXmin(), pileup_vs.GetXaxis().GetXmax())
            plotNumber_vsLumi.GetXaxis().SetTitle(intLumiLabel)
            plotNumber_vsLumi.GetYaxis().SetTitle(xlabel)
            plotNumber_vsLumi.SetMinimum(firstNumber-fillNumberMargin)
            plotNumber_vsLumi.SetMaximum(plotNumber_vsTime.GetMaximum()+fillNumberMargin)
            plotNumber_vsLumi.Draw("AP")
            canv.SaveAs(outFolder+"/A%sNumber_vsLumi.root"%var)
            canv.SaveAs(outFolder+"/A%sNumber_vsLumi.png"%var)
            del plotNumber_vsLumi
    del canv 
    
    ## re-init canvas
    from style import res_X,res_Y, gridX, gridY
    canv = ROOT.TCanvas("canv","",res_X,res_Y)
    canv.SetGridx(gridX)
    canv.SetGridy(gridY)
    
    histos_vsTime = {}
    histos_vsFill = {}
    histos_vsRun = {}
    from tools import setStyle, getCrossSection, createFit, addPileUp, getPlotVsNewVar, saveSh
    from style import title_vsTime, xsecLabel, puColor, createLegend,pileupLabel,ratesLabel,fillLabel,runLabel,legStyle,getColor
    if deadtimeCorrection or "L1_" in trigger: ##L1 bits are already pre-DT
        ratesLabel = ratesLabel + " (pre-DT)"
        xsecLabel = xsecLabel + " (pre-DT)"
    else:
        ratesLabel = ratesLabel + " (post-DT)"
        xsecLabel = xsecLabel + " (post-DT)"
    xsecLabel = xsecLabel%(refLumi/1E34)
    for i, trigger in enumerate(triggers[:]):
        print("Getting histo for ", trigger)
        outFolderWithTrigger = "%s/%s"%(outFolder, trigger)
        if not os.path.exists(outFolderWithTrigger):
            os.mkdir(outFolderWithTrigger)
        histos_vsTime = getHisto("%s"%trigger, chain, timeVar, binning, selection, deadtimeCorrection if not "L1_" in trigger else False) ##L1 bits are already pre-DT
        histos_vsFill = getHistoVsFillNumber(histos_vsTime, fillNumber_vsTime)
        histos_vsRun = getHistoVsFillNumber(histos_vsTime, runNumber_vsTime)
        setStyle(histos_vsTime, getColor(i))
        setStyle(histos_vsFill, getColor(i))
        if histos_vsTime.Integral()==0:
            triggers.remove(trigger)
        for useRate in useRates:
            for vs in vses:
    #        for vs in ["vsTime","vsFill","vsPU"]:
                ## Consider "vsTime" as default and the other option as an "hack"
                if vs in ["vsTime","vsPU","vsIntLumi"]:
                    histos_vs = histos_vsTime
                    count_vs = count_vsTime
                    if collisions:
                        delLumi_vs = delLumi_vsTime
                        intLumi_vs = intLumi_vsTime
                        pileup_vs = pileup_vsTime
                elif vs == "vsFill":
                    histos_vs = histos_vsFill
                    count_vs = count_vsFill
                    if collisions:
                        delLumi_vs = delLumi_vsFill
                        intLumi_vs = intLumi_vsFill
                        pileup_vs = pileup_vsFill
                elif vs == "vsRun":
                    histos_vs = histos_vsRun
                    count_vs = count_vsRun
                    if collisions:
                        delLumi_vs = delLumi_vsRun
                        intLumi_vs = intLumi_vsRun
                        pileup_vs = pileup_vsRun
                else:
                    raise Exception("Problem with vs = %s"%vs)
                
                print("Doing useRate %s. Trigger=%s"%(str(useRate), trigger))
                if histos_vs.Integral() == 0:
                    print()
                    print("WARNING: Empty plot. Skipping %s."%trigger)
                    print()
                    continue
                if useRate: 
                    prefix = "rates_"
                else: ## by default compute xsection
                    prefix = "xsec_"
                # get trigger cross sections histograms vs time and fit them with a constant
                xsec_vs = {}
                fit = {}
                print("DOING ",vs,useRate,selFolder,trigger)
#                for i, trigger in enumerate(triggers):
                print("Getting histo for ", trigger)
                if vs == "vsFill":
                    histos_vs = histos_vsFill
                elif vs == "vsRun":
                    histos_vs = histos_vsRun
                if useRate: ## computes rates [events/time]
                    xsec_vs = getCrossSection(histos_vs,count_vs,1./LS_seconds, removeOutliers)
#                    print("scaling")
#                    xsec_vs.Scale(1./LS_seconds)
#                    print("scaled")
                elif collisions:  ## get cross sections [events/recolumi]
                    xsec_vs = getCrossSection(histos_vs,delLumi_vs,1, removeOutliers)
                    max_, min_ = xsec_vs.GetMaximum(), xsec_vs.GetMinimum()
                    xsec_vs.Scale(refLumi/1E36)# pb -> cm^2 -> rates at 2E34 cm-2s-1
                    xsec_vs.SetMaximum(max_*refLumi/1E36)
                    xsec_vs.SetMinimum(min_*refLumi/1E36)

                if not useRate and not skipFit:
                    fit = createFit(xsec_vs, xsec_vs.Integral()/count_vs.Integral())
#                print("B")
                
                if collisions:
                    puScaleMax = 1.1*pileup_vs.GetMaximum()
                    setStyle(pileup_vs, puColor)
                print("Making plots for %s %s %s"%(prefix, vs, trigger))
                filePath = os.path.abspath(__file__)
                saveSh(outFolderWithTrigger+"/"+prefix+trigger+"_"+vs+".sh", filePath, useRate, vs, trigger, inputFolder, inputFile, plotsFolder, removeOutliers, runMin, runMax, collisions, batch, deadtimeCorrection, testing, lumisPerBin, refLumi, '"%s"="%s"'%(selFolder,selection), nbins)
                if vs in ["vsTime","vsFill","vsRun"]: 
                    # make trigger cross sections plots vs time, showing the pileup_vs on the right axis
                    print("xsecLabel %s"%xsecLabel)
                    xsec_vs.SetTitle(title_vsTime)
                    if vs == "vsFill":
                        xsec_vs.GetXaxis().SetTitle(fillLabel)
                    elif vs == "vsRun":
                        xsec_vs.GetXaxis().SetTitle(runLabel)
                    elif vs == "vsTime":
                        xsec_vs.GetXaxis().SetTitle(timeLabel)
                    if useRate:
                        xsec_vs.GetYaxis().SetTitle(ratesLabel)
                    else:
                        xsec_vs.GetYaxis().SetTitle(xsecLabel)
                    xsec_vs.GetYaxis().SetRangeUser(xsec_vs.GetMinimum(),xsec_vs.GetMaximum())
                    print("Y-range: %f - %f"%(xsec_vs.GetMaximum(),xsec_vs.GetMinimum()))
                    xsec_vs.Draw("e1")
            #        puScaleMin = xsec_vs.GetMinimum()/xsec_vs.GetMaximum()*puScaleMax
                    if collisions:
                        pileup_vs_scaled, rightaxis = addPileUp(canv, pileup_vs, puScaleMax, pileupLabel)
                        pileup_vs_scaled.Draw("P, same")
                        rightaxis.Draw("") 
                    xsec_vs.Draw("e1,same") ##keep pileup_vs in backgroup
                    if not useRate and not skipFit:
                        fit.SetRange(xsec_vs.GetXaxis().GetXmin(),xsec_vs.GetXaxis().GetXmax())
                        fit.Draw("same")
                    leg = createLegend()
                    if collisions:
                        leg.AddEntry(pileup_vs_scaled,"pileup","p")
                    leg.AddEntry(xsec_vs,trigger,legStyle)
                    leg.Draw()
                    outputFile = outFolderWithTrigger+"/"+prefix+trigger+"_"+vs+".root"
                    canv.SaveAs(outputFile)
                    canv.SaveAs(outputFile.replace(".root",".png"))
    #                1/0 vs, xsec_vs, 
                
                
                # make trigger cross sections plots vs integrated lumi, showing the pileup_vs on the right axis
                if vs == "vsIntLumi" and collisions: 
                    xsec_vsLum = {}
                    if collisions:
                        pileup_vsLum = getPlotVsNewVar(pileup_vs, intLumi_vs)
                    leg = createLegend()
                    xsec_vsLum = getPlotVsNewVar(xsec_vs, intLumi_vs) #convert xsec_vs in xsec_vsLum using intLumi_vs
                    setStyle(xsec_vsLum,xsec_vs.GetLineColor())
                    xsec_vsLum.SetTitle(title_vsLumi)
                    xsec_vsLum.GetXaxis().SetTitle(intLumiLabel)
                    if useRate:
                        xsec_vsLum.GetYaxis().SetTitle(ratesLabel)
                    else:
                        xsec_vsLum.GetYaxis().SetTitle(xsecLabel)
                    xsec_vsLum.GetYaxis().SetRangeUser(xsec_vs.GetMinimum()*0.9,xsec_vs.GetMaximum()*1.1)
                    xsec_vsLum.Draw("AP")
                    if not useRate and not skipFit:
                        fit.SetRange(xsec_vsLum.GetXaxis().GetXmin(),xsec_vsLum.GetXaxis().GetXmax())
                        fit.Draw("same")
                    if collisions:
                        pileup_vs_scaled, rightaxis = addPileUp(canv, pileup_vsLum, puScaleMax, pileupLabel)
                        pileup_vs_scaled.Draw("P, same")
                    rightaxis.Draw("") 
                    xsec_vsLum.Draw("P") ##keep pileup_vs in backgroup
                    if collisions:
                        leg.AddEntry(pileup_vs_scaled,"pileup","p")
                    leg.AddEntry(xsec_vs,trigger,legStyle) # or lep or f</verbatim>
                    leg.Draw()
                    outputFile = outFolderWithTrigger+"/"+prefix+trigger+"_vsIntLumi.root"
                    canv.SaveAs(outputFile)
                    canv.SaveAs(outputFile.replace(".root",".png"))

                
                
                # make trigger cross sections plots vs pileup_vs
                if vs == "vsPU" and collisions: 
                    xsec_vsPU = {}
                    leg = createLegend()
                    xsec_vsPU = getPlotVsNewVar(xsec_vs, pileup_vs) #convert xsec_vs in xsec_vsPU using intLumi_vs
                    setStyle(xsec_vsPU,xsec_vs.GetLineColor())
                    xsec_vsPU.SetTitle(title_vsLumi)
                    xsec_vsPU.GetXaxis().SetTitle(pileupLabel)
                    if useRate:
                        xsec_vsPU.GetYaxis().SetTitle(ratesLabel)
                    else:
                        xsec_vsPU.GetYaxis().SetTitle(xsecLabel)
                    xsec_vsPU.GetYaxis().SetRangeUser(xsec_vs.GetMinimum()*0.9,xsec_vs.GetMaximum()*1.1)
                    xsec_vsPU.Draw("AP")
                    if not useRate and not skipFit:
                        fit.SetRange(xsec_vsPU.GetXaxis().GetXmin(),xsec_vsPU.GetXaxis().GetXmax())
                        fit.Draw("same")
                    leg.AddEntry(xsec_vs,trigger,legStyle) # or lep or f</verbatim>
                    xsec_vsPU.Draw("P") ##keep pileup_vs in backgroup
                    leg.Draw()
                    outputFile = outFolderWithTrigger+"/"+prefix+trigger+"_vsPU.root"
                    canv.SaveAs(outputFile)
