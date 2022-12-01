#!/usr/bin/python3

import ROOT
import tdrstyle #https://twiki.cern.ch/twiki/bin/viewauth/CMS/Internal/FigGuidelines

tdrstyle = tdrstyle.setTDRStyle()
tdrstyle.cd()
import os

chain = ROOT.TChain("tree")

selectionDefault = {
    "PU50_60": "golden_json && pileup>50 && pileup<60",
    "inclusive": "golden_json",
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
    description='https://github.com/silviodonato/OMSRatesNtuple', 
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

parser.add_argument('--rates', action='store_const', const=True, default=False, help='Make rates plots')
parser.add_argument('--xsect', action='store_const', const=True, default=False, help='Make cross sections plots. Selected by default if no --rates nor --rates are defined')
parser.add_argument('--vsFill', action='store_const', const=True, default=False, help='Make plots vs fill number')
parser.add_argument('--vsRun', action='store_const', const=True, default=False, help='Make plots vs run number')
parser.add_argument('--vsPU', action='store_const', const=True, default=False, help='Make plots vs pileup')
parser.add_argument('--vsIntLumi', action='store_const', const=True, default=False, help='Make plots vs integrated luminosity. Selected by default if any --vs* flag is defined')
parser.add_argument('--vsTime', action='store_const', const=True, default=False, help='Make plots vs days')
parser.add_argument('--runMin', default=362104 , help='Run min. The minimum run possible run is 355678 (July 17, 2022)')
parser.add_argument('--runMax', default=1000000 , help='Run max')
parser.add_argument('--triggers', default="" , help='List of trigger used in the plots, separated by ",". If undefined, the triggerList defined in trigger_plots.py will be used. Example: --triggers HLT_IsoMu24_v,AlCa_PFJet40_v')
parser.add_argument('--selections', default="" , help='List of selections used in the plots, separated by ",". If undefined, the triggerList defined in trigger_plots.py will be used.')
parser.add_argument('--input', default="/afs/cern.ch/work/s/sdonato/public/OMS_ntuples/v2.0/" , help='Input folder containing the OMS ntuples')
parser.add_argument('--output', default="plots/" , help='Folder of the output plots')
parser.add_argument('--refLumi', default=2E34 , help='Reference rate used in the cross-section plots.')
parser.add_argument('--lumisPerBin', default=1 , help='Number of lumisections that will be merged in the plots. Cannot work with --nbins')
parser.add_argument('--nbins', default=-1 , help='Number of max bins. Cannot work with --lumisPerBin')
parser.add_argument('--removeOutliers', default="0.01" , help='Percentile of data points that will excluded from the plots. This is necessary to remove the rates spikes from the plots.')
parser.add_argument('--nobatch', action='store_const', const=True, default=False, help='Disable ROOT batch mode')
parser.add_argument('--testing', action='store_const', const=True, default=False, help='Used for debugging/development')

args = parser.parse_args()

from tools import readOptions
useRates, vses, triggers, folder, plotsFolder, removeOutliers, runMin, runMax, batch, testing, lumisPerBin, refLumi, selections, nbins = readOptions(parser.parse_args(), triggerDefault, selectionDefault)

print("##### Options #####")
print ("trigger_plots.py will produce %d x %d x %d x %d = %d plots in %s using OMS ntuples from %s,"%(len(useRates),len(vses),len(triggers),len(selections),len(useRates)*len(vses)*len(triggers)*len(selections), plotsFolder, folder))
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
print("testing = %s"%str(testing))
print("###################")



###################################################

try:
    files = os.listdir(folder)
except:
    print("#"*100)
    print("Input folder %s not found. Please check your --input option."%folder)
    print("You can download the OMS ntuple from OMS using:")
    print("xrdcp --recursive root://eosuser.cern.ch//eos/user/s/sdonato/public/OMS_rates/v1.0/  .")
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
    folder = "/home/sdonato/CMS/OMS_plots/OMS_ntuples/"
#    batch=False

runs = [int(f.split(".root")[0]) for f in files  if (f[0]=="3" and f[-5:]==".root")]
#selection = "pileup_vs>53 && pileup_vs<57 && cms_ready && beams_stable && beam2_stable"
#selection = "pileup_vs>54 && pileup_vs<56 && cms_ready && beams_stable && beam2_stable"
#selection = "HLT_DoubleMediumChargedIsoDisplacedPFTauHPS32_Trk1_eta2p1_v>0"


## Load all not-empy files
for run in sorted(runs):
    fName = "%s/%d.root"%(folder,run)
    if runMin>0 and run<runMin: continue
    if runMax>0 and run>runMax: continue
    if os.path.getsize(fName) > 1000 :
        chain.AddFile(fName)

#chain = ROOT.TChain("tree")
#chain.AddFile("/afs/cern.ch/work/s/sdonato/public/OMS_ntuples/v2.0/goldejson_skim.root")

## Constants
secInDay = 24.*60*60
LS_seconds = 2**18 / 11245.5 
LS_duration = LS_seconds/ secInDay #LS in days
from datetime import datetime
#offset = int(datetime(2023,1,1).timestamp()) - int(datetime(2022,8,31).timestamp())  #since Nov 1, 2022 instead of #since Jan 1, 2023
try:
    offset = int(datetime(2023,1,1).timestamp()) - int(datetime(2022,8,31).timestamp())  #since Nov 1, 2022 instead of #since Jan 1, 2023
except:
    offset = 10630800
    print("Please use 'python3' instead of 'python',")
    print("using offset %d. This should be equal to int(datetime(2023,1,1).timestamp()) - int(datetime(2022,8,31).timestamp()) in python3 [from datetime import datetime] ")
offset += -4294967296 ## bug fix ntuple v2.0
#offset =5270400 ## Nov1 (ie. 0. = Nov1)
#offset =5356800 ## Oct31 (ie. 1. = Nov1)
#offset =10630800 ## Aug31 

#1/0

ROOT.gROOT.SetBatch(batch)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)

## get fill number from the first event
chain.GetEvent(0)
firstFill = chain.fill
firstRun = chain.run

chain.Draw("fill")

## Skip missing triggers
for entry in [0, chain.GetEntries()-1]: #check only the first and last event
    chain.GetEvent(entry)
    for trigger in triggers[:]:
        if not hasattr(chain, trigger):
            triggers.remove(trigger)
            print("##### Trigger %s not found in run %d. Removed from the trigger list. #####"%(trigger,chain.run))

## Time varibale
timeVar = "(time + %f)/%f "%(offset, secInDay)

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
    fillNumber_vsTime = getHisto("fill", chain, timeVar, binning, selection)
    runNumber_vsTime = getHisto("run", chain, timeVar, binning, selection)
    delLumi_vsTime = getHisto("delivered_lumi_per_lumisection", chain, timeVar, binning, "1") #1000 pb-1 = fb-1
    delLumi_vsTime.Scale(1./1000)# pb-1 -> fb-1
    intLumi_vsTime = delLumi_vsTime.GetCumulative()
    intLumi_vsTime.SetName(intLumi_vsTime.GetName().replace("_",""))
    count_vsTime = getHisto("1", chain, timeVar, binning, selection) ## count_vs number of entries per bin
    pileup_vsTime = getHisto("pileup", chain, timeVar, binning, selection)
    recLumi_vsTime = getHisto("recorded_lumi_per_lumisection", chain, timeVar, binning, selection) #pb-1 * 1E33 = 1 cm-2
    recLumi_vsTime.Scale(1E36/refLumi)# pb-1 -> cm-2 -> rates at 2E34 cm-2s-1
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
    recLumi_vsFill = getHistoVsFillNumber(recLumi_vsTime, fillNumber_vsTime)
    intLumi_vsFill = getHistoVsFillNumber(intLumi_vsTime, fillNumber_vsTime)
    count_vsRun = getHistoVsFillNumber(count_vsTime, runNumber_vsTime)
    recLumi_vsRun = getHistoVsFillNumber(recLumi_vsTime, runNumber_vsTime)
    intLumi_vsRun = getHistoVsFillNumber(intLumi_vsTime, runNumber_vsTime)
#    pileup_vsTime.Divide(count_vsTime) 
#    pileup_vsFill = getHistoVsFillNumber(pileup_vsTime, fillNumber_vsTime)
#    recLumi_vsFill.Draw()
    
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
    histos_vsTime = {}
    histos_vsFill = {}
    histos_vsRun = {}
    from tools import setStyle
    from style import getColor
    for i, trigger in enumerate(triggers[:]):
        print("Getting histo for ", trigger)
        histos_vsTime[trigger] = getHisto("Alt$(%s,1)"%trigger, chain, timeVar, binning, selection) #Alt$(%s,1) ?
        histos_vsFill[trigger] = getHistoVsFillNumber(histos_vsTime[trigger], fillNumber_vsTime)
        histos_vsRun[trigger] = getHistoVsFillNumber(histos_vsTime[trigger], runNumber_vsTime)
        setStyle(histos_vsTime[trigger], getColor(i))
        setStyle(histos_vsFill[trigger], getColor(i))
        if histos_vsTime[trigger].Integral()==0:
            triggers.remove(trigger)
    for useRate in useRates:
        for vs in vses:
#        for vs in ["vsTime","vsFill","vsPU"]:
            ## Consider "vsTime" as default and the other option as an "hack"
            if vs in ["vsTime","vsPU","vsIntLumi"]:
                histos_vs = histos_vsTime
                count_vs = count_vsTime
                recLumi_vs = recLumi_vsTime
                intLumi_vs = intLumi_vsTime
                pileup_vs = pileup_vsTime
            elif vs == "vsFill":
                histos_vs = histos_vsFill
                count_vs = count_vsFill
                recLumi_vs = recLumi_vsFill
                intLumi_vs = intLumi_vsFill
                pileup_vs = pileup_vsFill
            elif vs == "vsRun":
                histos_vs = histos_vsRun
                count_vs = count_vsRun
                recLumi_vs = recLumi_vsRun
                intLumi_vs = intLumi_vsRun
                pileup_vs = pileup_vsRun
            else:
                raise Exception("Problem with vs = %s"%vs)
            
            ## re-init canvas
            from style import res_X,res_Y, gridX, gridY
            canv = ROOT.TCanvas("canv","",res_X,res_Y)
            canv.SetGridx(gridX)
            canv.SetGridy(gridY)
            
            print("Doing useRate %s"%str(useRate))
            if useRate: 
                prefix = "rates_"
            else: ## by default compute xsection
                prefix = "xsec_"
            # get trigger cross sections histograms vs time and fit them with a constant
            from tools import getCrossSection, createFit
            from style import legStyle
            xsec_vs = {}
            fits = {}
            print("DOING ",vs,useRate,selFolder,triggers)
            for i, trigger in enumerate(triggers):
                print("Getting histo for ", trigger)
                if vs == "vsFill":
                    histos_vs = histos_vsFill
                elif vs == "vsRun":
                    histos_vs = histos_vsRun
                if useRate:  ## get cross sections [events/recolumi]
                    xsec_vs[trigger] = getCrossSection(histos_vs[trigger],count_vs,removeOutliers)
                    xsec_vs[trigger].Scale(1./LS_seconds)
                else: ## computes rates [events/time]
                    xsec_vs[trigger] = getCrossSection(histos_vs[trigger],recLumi_vs,removeOutliers)
                if not useRate:
                    fits[trigger] = createFit(xsec_vs[trigger], xsec_vs[trigger].Integral()/count_vs.Integral())
            
            from tools import addPileUp
            from style import title_vsTime, xsecLabel, puColor, createLegend,pileupLabel,ratesLabel,fillLabel,runLabel
            puScaleMax = 1.1*pileup_vs.GetMaximum()
            setStyle(pileup_vs, puColor)
            xsecLabel = xsecLabel%(refLumi/1E34)
            if vs in ["vsTime","vsFill","vsRun"]: 
                # make trigger cross sections plots vs time, showing the pileup_vs on the right axis
                print("xsecLabel %s"%xsecLabel)
                for trigger in xsec_vs:
                    xsec_vs[trigger].SetTitle(title_vsTime)
                    if vs == "vsFill":
                        xsec_vs[trigger].GetXaxis().SetTitle(fillLabel)
                    elif vs == "vsRun":
                        xsec_vs[trigger].GetXaxis().SetTitle(runLabel)
                    elif vs == "vsTime":
                        xsec_vs[trigger].GetXaxis().SetTitle(timeLabel)
                    if useRate:
                        xsec_vs[trigger].GetYaxis().SetTitle(ratesLabel)
                    else:
                        xsec_vs[trigger].GetYaxis().SetTitle(xsecLabel)
                    xsec_vs[trigger].GetYaxis().SetRangeUser(xsec_vs[trigger].GetMinimum()*0.9,xsec_vs[trigger].GetMaximum()*1.1)
                    xsec_vs[trigger].Draw("e1")
            #        puScaleMin = xsec_vs[trigger].GetMinimum()/xsec_vs[trigger].GetMaximum()*puScaleMax
                    pileup_vs_scaled, rightaxis = addPileUp(canv, pileup_vs, puScaleMax, pileupLabel)
                    pileup_vs_scaled.Draw("P, same")
                    rightaxis.Draw("") 
                    xsec_vs[trigger].Draw("e1,same") ##keep pileup_vs in backgroup
                    if not useRate:
                        fits[trigger].Draw("same")
                    leg = createLegend()
                    leg.AddEntry(pileup_vs_scaled,"pileup","p")
                    leg.AddEntry(xsec_vs[trigger],trigger,legStyle)
                    leg.Draw()
                    canv.SaveAs(outFolder+"/"+prefix+trigger+"_"+vs+".root")
                    canv.SaveAs(outFolder+"/"+prefix+trigger+"_"+vs+".png")
    #                1/0
            
            from tools import getPlotVsNewVar        
            
            # make trigger cross sections plots vs integrated lumi, showing the pileup_vs on the right axis
            if vs == "vsIntLumi": 
                xsec_vsLum = {}
                pileup_vsLum = getPlotVsNewVar(pileup_vs, intLumi_vs)
                for trigger in xsec_vs:
                    leg = createLegend()
                    xsec_vsLum[trigger] = getPlotVsNewVar(xsec_vs[trigger], intLumi_vs) #convert xsec_vs in xsec_vsLum using intLumi_vs
                    setStyle(xsec_vsLum[trigger],xsec_vs[trigger].GetLineColor())
                    xsec_vsLum[trigger].SetTitle(title_vsLumi)
                    xsec_vsLum[trigger].GetXaxis().SetTitle(intLumiLabel)
                    if useRate:
                        xsec_vsLum[trigger].GetYaxis().SetTitle(ratesLabel)
                    else:
                        xsec_vsLum[trigger].GetYaxis().SetTitle(xsecLabel)
                    xsec_vsLum[trigger].GetYaxis().SetRangeUser(xsec_vs[trigger].GetMinimum()*0.9,xsec_vs[trigger].GetMaximum()*1.1)
                    xsec_vsLum[trigger].Draw("AP")
                    if not useRate:
                        fits[trigger].Draw("same")
                    pileup_vs_scaled, rightaxis = addPileUp(canv, pileup_vsLum, puScaleMax, pileupLabel)
                    pileup_vs_scaled.Draw("P, same")
                    rightaxis.Draw("") 
                    xsec_vsLum[trigger].Draw("P") ##keep pileup_vs in backgroup
                    leg.AddEntry(pileup_vs_scaled,"pileup","p")
                    leg.AddEntry(xsec_vs[trigger],trigger,legStyle) # or lep or f</verbatim>
                    leg.Draw()
                    canv.SaveAs(outFolder+"/"+prefix+trigger+"_vsIntLumi.root")
                    canv.SaveAs(outFolder+"/"+prefix+trigger+"_vsIntLumi.png")
            
            
            # make trigger cross sections plots vs pileup_vs
            if vs == "vsPU": 
                xsec_vsPU = {}
                for trigger in xsec_vs:
                    leg = createLegend()
                    xsec_vsPU[trigger] = getPlotVsNewVar(xsec_vs[trigger], pileup_vs) #convert xsec_vs in xsec_vsPU using intLumi_vs
                    setStyle(xsec_vsPU[trigger],xsec_vs[trigger].GetLineColor())
                    xsec_vsPU[trigger].SetTitle(title_vsLumi)
                    xsec_vsPU[trigger].GetXaxis().SetTitle(pileupLabel)
                    if useRate:
                        xsec_vsPU[trigger].GetYaxis().SetTitle(ratesLabel)
                    else:
                        xsec_vsPU[trigger].GetYaxis().SetTitle(xsecLabel)
                    xsec_vsPU[trigger].GetYaxis().SetRangeUser(xsec_vs[trigger].GetMinimum()*0.9,xsec_vs[trigger].GetMaximum()*1.1)
                    xsec_vsPU[trigger].Draw("AP")
                    if not useRate:
                        fits[trigger].Draw("same")
                    leg.AddEntry(xsec_vs[trigger],trigger,legStyle) # or lep or f</verbatim>
                    xsec_vsPU[trigger].Draw("P") ##keep pileup_vs in backgroup
                    leg.Draw()
                    canv.SaveAs(outFolder+"/"+prefix+trigger+"_vsPU.root")
                    canv.SaveAs(outFolder+"/"+prefix+trigger+"_vsPU.png")
            del canv

