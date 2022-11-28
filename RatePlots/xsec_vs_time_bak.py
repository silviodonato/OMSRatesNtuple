import ROOT
import os

batch = True
#batch = False
minY=-1
maxY=-1
maxXS = 50.

ROOT.gROOT.SetBatch(batch)

lumisPerBin=100
chain = ROOT.TChain("tree")

folder = "/eos/user/s/sdonato/public/OMS_rates/"
folder = "/run/user/1000/gvfs/sftp:host=lxplus.cern.ch,user=sdonato/afs/cern.ch/user/s/sdonato/AFSwork/ratemon/ratemon/"
folder = "OMS_ntuples/"
outFolder = "plots/"

triggerColors = {
    "HLT_DoubleMediumChargedIsoDisplacedPFTauHPS32_Trk1_eta2p1_v" : ROOT.kBlue,
#    "HLT_IsoMu24_v" : ROOT.kRed,
#    "HLT_Ele30_WPTight_Gsf_v" : ROOT.kGreen+2,
#    "HLT_QuadPFJet70_50_40_35_PFBTagParticleNet_2BTagSum0p65_v" : ROOT.kMagenta,
#    "HLT_DoubleEle7p5_eta1p22_mMax6_v": ROOT.kCyan+3,
#    "HLT_PFMETNoMu110_PFMHTNoMu110_IDTight_FilterHF_v":ROOT.kYellow+3,
#    "AlCa_PFJet40_CPUOnly_v":ROOT.kPink,
#    "AlCa_PFJet40_v":ROOT.kYellow+2,
#    "HLT_AK8PFJet250_SoftDropMass40_PFAK8ParticleNetBB0p35_v":ROOT.kPink+2,
#    "HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1_v":ROOT.kMagenta+2,
#    "HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId_Mass55_v":ROOT.kBlue+2,
#    "HLT_AK8PFJet420_TrimMass30_v":ROOT.kGreen+2,
#    "HLT_PFHT330PT30_QuadPFJet_75_60_45_40_TriplePFBTagDeepJet_4p5_v":ROOT.kRed+2,
}

#for tr in triggerColors: triggerColors[tr]= ROOT.kBlue

files = os.listdir(folder)
#files = ["362657.root","362655.root"]
runs = [int(f.split(".root")[0]) for f in files  if (f[0]=="3" and f[-5:]==".root")]
#selection = "pileup>53 && pileup<57 && cms_ready && beams_stable && beam2_stable"
selection = "pileup>54 && pileup<56"
selectionLoose = "recorded_lumi_per_lumisection>0.0001"
selectionLoose = selection
#selection = "HLT_DoubleMediumChargedIsoDisplacedPFTauHPS32_Trk1_eta2p1_v>0"

for run in sorted(runs):
    fName = "%s/%d.root"%(folder,run)
    if os.path.getsize(fName) > 1000:
        chain.AddFile(fName)


secInDay = 24.*60*60
LS_duration = 2**18 / 11245.5 / secInDay #LS in days
#from datetime import datetime
#offset = -(int(datetime(2022,11,1).timestamp()) - int(datetime(2023,1,1).timestamp()))  #since Nov 1, 2022 instead of #since Jan 1, 2023
offset =5270400 ## Nov1 (ie. 0. = Nov1)
offset =5356800 ## Oct31 (ie. 1. = Nov1)
ROOT.gStyle.SetOptStat(0)

var = "(time + %f)/%f "%(offset, secInDay)
#var = "run"

#1./secInDay * 
chain.Draw(var+" >> tmp",selection,"GOFF")

bin_size = LS_duration * lumisPerBin
tmp = ROOT.gROOT.Get("tmp")
timemax = tmp.GetXaxis().GetXmax()
timemin = tmp.GetXaxis().GetXmin()
ntimebins =  int((timemax-timemin)/bin_size)
timemax = timemin + bin_size*(ntimebins-1)



chain.GetEvent(0)
firstFill = chain.fill

#def getHisto(hName, )
from tools import getHisto
binning = (ntimebins,timemin,timemax)
recLumi = getHisto("recorded_lumi_per_lumisection", chain, var, binning, selection)
count = getHisto("1", chain, var, binning, selectionLoose) ## count number of entries per bin
pileup = getHisto("pileup", chain, var, binning, selectionLoose)
pileup.Divide(count) ## take the average value per bin, instead of the sum
fillNumber = getHisto("fill", chain, var, binning, selection)
fillNumber.Divide(count) ## take the average value per bin, instead of the sum
delLumi = getHisto("delivered_lumi_per_lumisection/1000", chain, var, binning, selection)
intLumi = delLumi.GetCumulative()

#chain.Draw(var + " >> recLumi(%d,%f,%f)"%(ntimebins,timemin,timemax),"recorded_lumi_per_lumisection*(%s)"%selection,"GOFF")
#recLumi = ROOT.gROOT.Get("recLumi")

#chain.Draw(var + " >> pileup(%d,%f,%f)"%(ntimebins,timemin,timemax),"pileup * (%s)"%selectionLoose,"GOFF")
#pileup = ROOT.gROOT.Get("pileup")

#chain.Draw(var + " >> count(%d,%f,%f)"%(ntimebins,timemin,timemax),"(%s)"%selectionLoose,"GOFF")
#count = ROOT.gROOT.Get("count")

#chain.Draw(var + " >> delLumi(%d,%f,%f)"%(ntimebins,timemin,timemax),"delivered_lumi_per_lumisection/1000","GOFF") ## no selection 
#delLumi = ROOT.gROOT.Get("delLumi")
#intLumi = delLumi.GetCumulative()

#chain.Draw(var + " >> fillNumber(%d,%f,%f)"%(ntimebins,timemin,timemax),"1.*fill*(%s)"%selectionLoose,"GOFF")
#fillNumber = ROOT.gROOT.Get("fillNumber")
#fillNumber.Divide(count)


from tools import getCrossSection
xsec_vsTime = {}
fits = {}
for trigger in triggerColors:
    chain.Draw(var + " >> %s(%d,%f,%f)"%(trigger,ntimebins,timemin,timemax),"%s*(%s)"%(trigger,selection),"GOFF")
    xsec_vsTime[trigger] = ROOT.gROOT.Get(trigger)
    
    getCrossSection(xsec_vsTime[trigger],recLumi)
    
    xsec_vsTime[trigger].SetLineColor(triggerColors[trigger])
    xsec_vsTime[trigger].Scale(maxXS/xsec_vsTime[trigger].GetMaximum())
    xsec_vsTime[trigger].SetLineWidth(2)
    fits[trigger] = ROOT.TF1(trigger+"fit","[0]",timemin,timemax)
    fits[trigger].SetLineColor(triggerColors[trigger])
    xsec_vsTime[trigger].Fit(fits[trigger])
#    print(xsec_vsTime, trigger)

pileup.SetLineColor(ROOT.kBlack)

#recLumi.Scale(maxXS/recLumi.GetMaximum())

pileup = ROOT.TGraph(pileup)
pileup.SetTitle("Trigger cross-section vs time")
pileup.GetXaxis().SetTitle("days since Oct 31, 2022")
pileup.GetYaxis().SetTitle("cross-section [AU] or pileup")
#for i in range(len(pileup)): pileup.SetBinError(i,0)
if maxY>0: pileup.SetMaximum(maxY)
if minY>0: pileup.SetMinimum(minY)
pileup.SetMarkerSize(0.3)
pileup.SetMarkerStyle(21)

c1 = ROOT.TCanvas("c1","",1280,1024)
c1.SetGridx()
c1.SetGridy()
#leg.SetHeader("")
for trigger in xsec_vsTime:
    leg = ROOT.TLegend(0.55,0.1,0.9,0.25)
    pileup.Draw("AP")
    leg.AddEntry(pileup,"pileup","p") # or lep or f</verbatim>
    xsec_vsTime[trigger].Draw("e1,same")
    fits[trigger].Draw("same")
#    print(xsec_vsTime[trigger].Integral())
    leg.AddEntry(xsec_vsTime[trigger],trigger,"lep") # or lep or f</verbatim>
    leg.Draw()
    c1.SaveAs(outFolder+"/"+trigger+"_vsTime.png")
    c1.SaveAs(outFolder+"/"+trigger+"_vsTime.root")
leg = ROOT.TLegend(0.55,0.1,0.9,0.25)
#leg.SetHeader("")
pileup.Draw("AP")
leg.AddEntry(pileup,"pileup","l") # or lep or f</verbatim>
for trigger in xsec_vsTime:
    xsec_vsTime[trigger].Draw("e1,same")
    fits[trigger].Draw("same")
#    print(xsec_vsTime[trigger].Integral())
    leg.AddEntry(xsec_vsTime[trigger],trigger,"lep") # or lep or f</verbatim>


c1.Clear()
c1.SetGridx()
c1.SetGridy()
#leg.SetHeader("")
xsec_vsLum = {}
for trigger in xsec_vsTime:
    leg = ROOT.TLegend(0.55,0.1,0.9,0.25)
    xsec_vsLum[trigger] = ROOT.TGraphErrors()
    npoints = 0
    for i in range(len(xsec_vsTime[trigger])):
        if xsec_vsTime[trigger][i]>0:
            xsec_vsLum[trigger].SetPoint(npoints,intLumi[i],xsec_vsTime[trigger][i])
            xsec_vsLum[trigger].SetPointError(npoints,0,xsec_vsTime[trigger].GetBinError(i))
            npoints+=1
#        print(pileup_int[i],xsec_vsTime[trigger][i])
    xsec_vsLum[trigger].SetMarkerSize(0.5)
    xsec_vsLum[trigger].SetMarkerStyle(21)
    xsec_vsLum[trigger].SetLineColor(triggerColors[trigger])
    xsec_vsLum[trigger].SetMarkerColor(triggerColors[trigger])
    xsec_vsLum[trigger].SetTitle("Trigger cross-section vs int lumi")
    xsec_vsLum[trigger].GetXaxis().SetTitle("Integrated luminosity since fill %d [fb-1]"%(firstFill))
    xsec_vsLum[trigger].GetYaxis().SetTitle("Cross-section")
    xsec_vsLum[trigger].Draw("AP")
    fits[trigger].Draw("same")
    leg.AddEntry(xsec_vsTime[trigger],trigger,"lep") # or lep or f</verbatim>
    leg.Draw()
    c1.SaveAs(outFolder+"/"+trigger+"_vsIntLumi.png")
    c1.SaveAs(outFolder+"/"+trigger+"_vsIntLumi.root")

c1.Clear()
c1.SetGridx()
c1.SetGridy()
intLumi.SetTitle("Trigger cross-section vs time")
intLumi.GetXaxis().SetTitle("days since Nov 1, 2022")
intLumi.GetYaxis().SetTitle("cross-section [AU] or pileup")
intLumi.Draw("HIST")
c1.SaveAs(outFolder+"/0_intLumi_vsTime.png")
c1.SaveAs(outFolder+"/0_intLumi_vsTime.root")

c1.Clear()
c1.SetGridx()
c1.SetGridy()
lastFill = fillNumber.GetMaximum()
fillNumber_IntLumi = ROOT.TGraph(len(fillNumber))
npoints=0
for i in range(len(fillNumber)):
    if fillNumber[i]>0:
        fillNumber_IntLumi.SetPoint(npoints,intLumi[i],fillNumber[i])
        npoints+=1
fillNumber_IntLumi.SetMarkerSize(0.5)
fillNumber_IntLumi.SetMarkerStyle(21)
fillNumber_IntLumi.SetTitle("Trigger cross-section vs time")
#fillNumber_IntLumi.GetXaxis().SetRangeUser(xsec_vsLum.keys()[0].GetXaxis().GetXmin(), pileup.GetXaxis().GetXmax())
fillNumber_IntLumi.GetXaxis().SetTitle("days since Nov 1, 2022")
fillNumber_IntLumi.GetYaxis().SetTitle("cross-section [AU] or pileup")
fillNumber_IntLumi.SetMinimum(firstFill)
fillNumber_IntLumi.SetMaximum(fillNumber.GetMaximum())
fillNumber_IntLumi.Draw("AP")
c1.SaveAs(outFolder+"/0_fillNumber_vsIntLumi.png")
c1.SaveAs(outFolder+"/0_fillNumber_vsIntLumi.root")


#chain.Scan("run_number:year:month:day:hour:minute:second:lumi:"+var,"lumi==1")
#recLumi.Integral()


#recorded_lumi_per_lumisection


#chain.Draw("time:Alt$(HLT_IsoMu20_v,0)","","profg")

