import ROOT
import CMS_lumi, tdrstyle #https://twiki.cern.ch/twiki/bin/viewauth/CMS/Internal/FigGuidelines
tdrstyle.setTDRStyle()
import os

lumisPerBin=50
batch = True
#batch = False
testing = False
#testing = True
runMin = 355678 # July 17. Different unit for rec lumi before this run.
runMax = -1
##runMax = 361447
#runMax = 361447
#runMax = 359000
#runMax = 361000
removeOutliers = 1.5
useRates=[False, True] ## useRates = False -> plot cross section , True -> plot rates.

ROOT.gROOT.SetBatch(batch)

chain = ROOT.TChain("tree")

folder = "/eos/user/s/sdonato/public/OMS_rates/"
#folder = "/run/user/1000/gvfs/sftp:host=lxplus.cern.ch,user=sdonato/afs/cern.ch/user/s/sdonato/AFSwork/ratemon/ratemon/"
#folder = "/home/sdonato/CMS/OMS_plots/OMS_ntuples/"
plotsFolder = "plots/"
#useRate = False

folderSelection = {
    "PU50_60": "cms_ready && beams_stable && beam2_stable && pileup>50 && pileup<60",
    "inclusive": "cms_ready && beams_stable && beam2_stable",
#    "RunE": "cms_ready && beams_stable && beam2_stable",
}

triggers = [
    "HLT_DoubleMediumChargedIsoDisplacedPFTauHPS32_Trk1_eta2p1_v",
    "HLT_IsoMu24_v",
    "HLT_Ele30_WPTight_Gsf_v",
    "HLT_QuadPFJet70_50_40_35_PFBTagParticleNet_2BTagSum0p65_v" ,
    "HLT_DoubleEle7p5_eta1p22_mMax6_v",
    "HLT_PFMETNoMu110_PFMHTNoMu110_IDTight_FilterHF_v",
    "AlCa_PFJet40_v",
    "HLT_AK8PFJet250_SoftDropMass40_PFAK8ParticleNetBB0p35_v",
    "HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1_v",
    "HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId_Mass55_v",
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
]

#for tr in triggerColors: triggerColors[tr]= ROOT.kBlue

files = os.listdir(folder)
## Use only few files and few triggers for testing:
if testing:
    folderSelection = {"inclusive":folderSelection["inclusive"]}
    lumisPerBin = 1
#    files = ["362655.root","357900.root"]
#    triggers = ["HLT_DoubleMediumChargedIsoDisplacedPFTauHPS32_Trk1_eta2p1_v", "HLT_IsoMu24_v","AlCa_PFJet40_CPUOnly_v"]
    runMin = 360449 # July 17. Different unit for rec lumi before this run.
    runMax = 361500

runs = [int(f.split(".root")[0]) for f in files  if (f[0]=="3" and f[-5:]==".root")]
#selection = "pileup>53 && pileup<57 && cms_ready && beams_stable && beam2_stable"
#selection = "pileup>54 && pileup<56 && cms_ready && beams_stable && beam2_stable"
#selection = "HLT_DoubleMediumChargedIsoDisplacedPFTauHPS32_Trk1_eta2p1_v>0"


## Load all not-empy files
for run in sorted(runs):
    fName = "%s/%d.root"%(folder,run)
    if runMin>0 and run<runMin: continue
    if runMax>0 and run>runMax: continue
    if os.path.getsize(fName) > 1000 :
        chain.AddFile(fName)

## Constants
secInDay = 24.*60*60
LS_seconds = 2**18 / 11245.5 
LS_duration = LS_seconds/ secInDay #LS in days
#from datetime import datetime
#offset = -(int(datetime(2022,8,31).timestamp()) - int(datetime(2023,1,1).timestamp()))  #since Nov 1, 2022 instead of #since Jan 1, 2023
offset =5270400 ## Nov1 (ie. 0. = Nov1)
offset =5356800 ## Oct31 (ie. 1. = Nov1)
offset =10630800 ## Aug31 
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)

## get fill number from the first event
chain.GetEvent(0)
firstFill = chain.fill

## Skip missing triggers
for trigger in triggers[:]:
    if not hasattr(chain, trigger):
        triggers.remove(trigger)
        print("Trigger %s not found. Removed from the trigger list."%trigger)

## Time varibale
var = "(time + %f)/%f "%(offset, secInDay)

# Loop over selections
if not os.path.exists(plotsFolder):
    os.mkdir(plotsFolder)
for selFolder in folderSelection:
    print("Doing %s"%selFolder)
    outFolder = plotsFolder+"/"+selFolder
    if not os.path.exists(outFolder):
        os.mkdir(outFolder)
    selection = folderSelection[selFolder]

    # get binning
    from tools import getBinning
    bin_size = LS_duration * lumisPerBin
    ntimebins, timemin, timemax = getBinning(chain, var, selection, bin_size)
    binning = "(%s,%s,%s)"%(ntimebins,timemin,timemax)

    # get common histograms
    from tools import getHisto
    fillNumber = getHisto("fill", chain, var, binning, selection)
    delLumi = getHisto("delivered_lumi_per_lumisection", chain, var, binning, "1") #1000 pb-1 = fb-1
    delLumi.Scale(1./1000)# pb-1 -> fb-1
    intLumi = delLumi.GetCumulative()
    intLumi.SetName(intLumi.GetName().replace("_",""))
    count = getHisto("1", chain, var, binning, selection) ## count number of entries per bin
    pileup = getHisto("pileup", chain, var, binning, selection)
    recLumi = getHisto("recorded_lumi_per_lumisection", chain, var, binning, selection) #pb-1 * 1E33 = 1 cm-2
    recLumi.Scale(1E36)# pb-1 -> cm-1
    print("get common histograms: DONE")

    ## take the average value per bin, instead of the sum, for non-cumulative variables
    from tools import dropError
    pileup.Divide(count) 
    fillNumber.Divide(count) 
    dropError(pileup)
    dropError(fillNumber)
    print("A")

    # init canvas
    from style import res_X,res_Y, gridX, gridY
    canv = ROOT.TCanvas("canv","",res_X,res_Y)
    canv.SetGridx(gridX)
    canv.SetGridy(gridY)
    print("B")

    from style import title_vsLumi,intLumiLabel,timeLabel
    intLumiLabel = intLumiLabel%firstFill ## replace %s with the actual first fill number 
    # plot integrated lumi vs time
    intLumi.SetTitle("")
    intLumi.GetXaxis().SetTitle(timeLabel)
    intLumi.GetYaxis().SetTitle(intLumiLabel)
    intLumi.Draw("P")
    canv.Update()
    canv.Modify()
    print("C")
    canv.SaveAs(outFolder+"/AintLumi_vsTime.root")
#    canv.SaveAs(outFolder+"/AintLumi_vsTime.png")
    print("C")

    # plot the fill number vs integrated luminosity
    from style import fillLabel, fillNumberMargin
    lastFill = fillNumber.GetMaximum()
    fillNumber_IntLumi = ROOT.TGraph(len(fillNumber))
    npoints=0
    print("D")
    for i in range(len(fillNumber)):
        if fillNumber[i]>0:
            fillNumber_IntLumi.SetPoint(npoints,intLumi[i],fillNumber[i])
            npoints+=1
    print("D")
    fillNumber_IntLumi.SetMarkerSize(0.5)
    fillNumber_IntLumi.SetMarkerStyle(21)
    fillNumber_IntLumi.SetTitle("")
    #fillNumber_IntLumi.GetXaxis().SetRangeUser(xsec_vsLum.keys()[0].GetXaxis().GetXmin(), pileup.GetXaxis().GetXmax())
    fillNumber_IntLumi.GetXaxis().SetTitle(intLumiLabel)
    fillNumber_IntLumi.GetYaxis().SetTitle(fillLabel)
    fillNumber_IntLumi.SetMinimum(firstFill-fillNumberMargin)
    fillNumber_IntLumi.SetMaximum(fillNumber.GetMaximum()+fillNumberMargin)
    fillNumber_IntLumi.Draw("AP")
    print("E")
    canv.SaveAs(outFolder+"/AfillNumber_vsIntLumi.root")
    canv.SaveAs(outFolder+"/AfillNumber_vsIntLumi.png")
    print("E")
    del canv 
    histos_vsTime = {}
    from tools import setStyle
    from style import getColor
    for i, trigger in enumerate(triggers):
        print("Getting histo for ", trigger)
        histos_vsTime[trigger] = getHisto("%s"%trigger, chain, var, binning, selection) #Alt$(%s,1) ?
        setStyle(histos_vsTime[trigger], getColor(i))
    for useRate in useRates:
        print("Doing useRate %s"%str(useRate))
        if useRate: 
            prefix = "rates_"
        else: ## by default compute xsection
            prefix = "xsec_"
        # get trigger cross sections histograms vs time and fit them with a constant
        from tools import getCrossSection, createFit
        from style import legStyle
        xsec_vsTime = {}
        fits = {}
        for i, trigger in enumerate(triggers):
            print("Getting histo for ", trigger)
            if useRate:  ## get cross sections [events/recolumi]
                xsec_vsTime[trigger] = getCrossSection(histos_vsTime[trigger],count,removeOutliers)
                xsec_vsTime[trigger].Scale(1./LS_seconds)
            else: ## computes rates [events/time]
                xsec_vsTime[trigger] = getCrossSection(histos_vsTime[trigger],recLumi,removeOutliers)
            if not useRate:
                fits[trigger] = createFit(xsec_vsTime[trigger], xsec_vsTime[trigger].Integral()/count.Integral())
        ## re-init canvas
        from style import res_X,res_Y, gridX, gridY
        canv = ROOT.TCanvas("canv","",res_X,res_Y)
        canv.SetGridx(gridX)
        canv.SetGridy(gridY)
        
        # make trigger cross sections plots vs time, showing the pileup on the right axis
        from tools import addPileUp
        from style import title_vsTime, xsecLabel, puColor, createLegend,pileupLabel,ratesLabel
        setStyle(pileup, puColor)
        puScaleMax = 1.1*pileup.GetMaximum()
        for trigger in xsec_vsTime:
            xsec_vsTime[trigger].SetTitle(title_vsTime)
            xsec_vsTime[trigger].GetXaxis().SetTitle(timeLabel)
            if useRate:
                xsec_vsTime[trigger].GetYaxis().SetTitle(ratesLabel)
            else:
                xsec_vsTime[trigger].GetYaxis().SetTitle(xsecLabel)
            xsec_vsTime[trigger].Draw("e1")
    #        puScaleMin = xsec_vsTime[trigger].GetMinimum()/xsec_vsTime[trigger].GetMaximum()*puScaleMax
            pileup_scaled, rightaxis = addPileUp(canv, pileup, puScaleMax, pileupLabel)
            pileup_scaled.Draw("P, same")
    #        xsec_vsTime[trigger].Draw("P") ##keep pileup in backgroup
            rightaxis.Draw("") 
            if not useRate:
                fits[trigger].Draw("same")
            leg = createLegend()
            leg.AddEntry(pileup_scaled,"pileup","p")
            leg.AddEntry(xsec_vsTime[trigger],trigger,legStyle)
            leg.Draw()
            canv.SaveAs(outFolder+"/"+prefix+trigger+"_vsTime.root")
            canv.SaveAs(outFolder+"/"+prefix+trigger+"_vsTime.png")
        
        from tools import getPlotVsNewVar        
        
        # make trigger cross sections plots vs integrated lumi, showing the pileup on the right axis
        xsec_vsLum = {}
        pileup_vsLum = getPlotVsNewVar(pileup, intLumi)
        for trigger in xsec_vsTime:
            leg = createLegend()
            xsec_vsLum[trigger] = getPlotVsNewVar(xsec_vsTime[trigger], intLumi) #convert xsec_vsTime in xsec_vsLum using intLumi
            setStyle(xsec_vsLum[trigger],xsec_vsTime[trigger].GetLineColor())
            xsec_vsLum[trigger].SetTitle(title_vsLumi)
            xsec_vsLum[trigger].GetXaxis().SetTitle(intLumiLabel)
            if useRate:
                xsec_vsLum[trigger].GetYaxis().SetTitle(ratesLabel)
            else:
                xsec_vsLum[trigger].GetYaxis().SetTitle(xsecLabel)
            xsec_vsLum[trigger].Draw("AP")
            if not useRate:
                fits[trigger].Draw("same")
            pileup_scaled, rightaxis = addPileUp(canv, pileup_vsLum, puScaleMax, pileupLabel)
            pileup_scaled.Draw("P, same")
    #        xsec_vsLum[trigger].Draw("P") ##keep pileup in backgroup
            rightaxis.Draw("") 
            leg.AddEntry(pileup_scaled,"pileup","p")
            leg.AddEntry(xsec_vsTime[trigger],trigger,legStyle) # or lep or f</verbatim>
            leg.Draw()
            canv.SaveAs(outFolder+"/"+prefix+trigger+"_vsIntLumi.root")
            canv.SaveAs(outFolder+"/"+prefix+trigger+"_vsIntLumi.png")


        # make trigger cross sections plots vs pileup
        xsec_vsPU = {}
        for trigger in xsec_vsTime:
            leg = createLegend()
            xsec_vsPU[trigger] = getPlotVsNewVar(xsec_vsTime[trigger], pileup) #convert xsec_vsTime in xsec_vsPU using intLumi
            setStyle(xsec_vsPU[trigger],xsec_vsTime[trigger].GetLineColor())
            xsec_vsPU[trigger].SetTitle(title_vsLumi)
            xsec_vsPU[trigger].GetXaxis().SetTitle(pileupLabel)
            if useRate:
                xsec_vsPU[trigger].GetYaxis().SetTitle(ratesLabel)
            else:
                xsec_vsPU[trigger].GetYaxis().SetTitle(xsecLabel)
            xsec_vsPU[trigger].Draw("AP")
            if not useRate:
                fits[trigger].Draw("same")
            leg.AddEntry(xsec_vsTime[trigger],trigger,legStyle) # or lep or f</verbatim>
            leg.Draw()
            canv.SaveAs(outFolder+"/"+prefix+trigger+"_vsPU.root")
            canv.SaveAs(outFolder+"/"+prefix+trigger+"_vsPU.png")
        del canv

