#!/usr/bin/python3

#Plots done with: python3 trigger_plots.py --rate --xsec --vsTime --vsFill --vsRun --lumisPerBin 30 --inputFile /home/sdonato/CMS/PlotDellaDiscordia/2023_rereco_physics_merged.root --triggers StreamBandwidth_*,Stream_* --selections "Stream23NoFirstFills=cms_ready && beams_stable && beam2_stable && fill>8645 "

#folder = "plots/Stream23NoFirstFills"
folder = "plots/Stream18"
plotPatterns = ["rates_Stream_", "xsec_Stream_", "rates_StreamBandwidth_", "xsec_StreamBandwidth_"]
kinds = ["vsFill","vsTime","vsRun"]
kinds = ["vsFill"]
plotPatterns = ["rates_Stream_"]

# plotPatterns = ["rates_StreamBandwidth_", "xsec_StreamBandwidth_"]
# kinds = ["vsFill"]

import ROOT
import os, array
from fnmatch import fnmatch
import tdrstyle #https://twiki.cern.ch/twiki/bin/viewauth/CMS/Internal/FigGuidelines
from pprint import pprint
from datetime import datetime

tdrstyle = tdrstyle.setTDRStyle()
tdrstyle.cd()

ROOT.gROOT.SetBatch(1)

vetos = [
    "PhysicsCommissioning",
    "PhysicsHLTPhysics0",
    "PhysicsHLTPhysics1",
    "PhysicsHLTPhysics2",
    "PhysicsHLTPhysics3",
    "PhysicsHLTPhysics4",
    "PhysicsHLTPhysics5",
    "PhysicsHLTPhysics6",
    "PhysicsHLTPhysics7",
    "PhysicsHLTPhysics8",
    "PhysicsHLTPhysics9",
    "PhysicsZeroBias0",
    "PhysicsZeroBias1",
    "PhysicsZeroBias2",
    "PhysicsZeroBias3",
    "PhysicsZeroBias4",
    "PhysicsZeroBias5",
    "PhysicsZeroBias6",
    "PhysicsZeroBias7",
    "PhysicsZeroBias8",
    "PhysicsZeroBias9"

]

plotsMap = {
#    "Prompt": (ROOT.kRed, "Physics*"),
    "PhysicsMuon": (ROOT.kRed-10, ["PhysicsMuo*"]),
    "PhysicsEGamma": (ROOT.kRed-9, ["PhysicsEGamm*"]),
    "PhysicsScoutingPFMonitor": (ROOT.kRed-7, ["PhysicsScoutingPFMonito*","PhysicsScoutingMonito*"]),
    "PhysicsHadronsTaus": (ROOT.kRed-4, ["PhysicsDispJetBTagMuEGTau","PhysicsJetMET*","PhysicsHadronsTau*"]),
    "PhysicsReservedDoubleMuonLowMass": (ROOT.kRed+0, ["PhysicsReservedDoubleMuonLowMass"]),

    "ParkingDoubleMuon": (ROOT.kBlue-7, ["ParkingDoubleMuonLowMas**"]),
    "ParkingSingleMuon": (ROOT.kBlue-4, ["ParkingSingleMuon*"]),
    "ParkingLLP": (ROOT.kBlue, ["ParkingLLP*"]),
    "ParkingHH": (ROOT.kBlue+1, ["ParkingHH*"]),
    "ParkingDoubleElectron": (ROOT.kBlue+2, ["ParkingDoubleElectron*"]),
    "ParkingVBF": (ROOT.kBlue+3, ["ParkingVBF*"]),
    "ParkingBPH": (ROOT.kBlue, ["ParkingBPH*"]),
    # "PhysicsParkingScoutingMonitor": (ROOT.kBlue-9, ["PhysicsParkingScoutingMonito*"]),


    "PhysicsCommissioning": (ROOT.kGreen-9, ["PhysicsCommissioning"]),
    "PhysicsZeroBias": (ROOT.kGreen, ["PhysicsZeroBia*"]),
    "PhysicsHLTPhysics": (ROOT.kGreen+2, ["PhysicsHLTPhysic*"]),


    # "Physics": (ROOT.kRed, ["Physics*"]),
    # "Parking": (ROOT.kBlue, ["Parking*"]),

#    "Scouting": (ROOT.kBlue-9, ["ScoutingPF*"]),
#    "Commissioning": (ROOT.kGreen, ["Prompt*"]),
}

def getHistoFromFile(fName):
    f = ROOT.TFile.Open(fName)
    canvas = f.Get("canv")
#    print( type(canvas.GetListOfPrimitives()[0]))
    histos = [p for p in canvas.GetListOfPrimitives() if (type(p)==ROOT.TH1F or type(p)==ROOT.TGraph)]
    f.Close()
    return histos[0]

def removeEmptyBins(histo, xLabels):
    keys = list(xLabels)
    xs = []
    bins = []
    for i in range(0, histo.GetNbinsX()):
        if histo.GetBinContent(i)>0:
            bins.append(i)
            xs.append(histo.GetBinLowEdge(i))
    xs = xs + [xs[-1]+1]
    newHisto = ROOT.TH1F(histo.GetName()+"_new",histo.GetTitle(),len(bins),0,len(bins))
    for new_i, old_i in enumerate(bins):
        x = xs[new_i]
        new_i = new_i + 1 ## TH1F bins starts from 1
        newHisto.SetBinContent(new_i, histo.GetBinContent(old_i))
        if len(keys)>0 and x>keys[0]:
            newHisto.GetXaxis().SetBinLabel(new_i, xLabels[keys[0]])
            del keys[0]
        else:
            newHisto.GetXaxis().SetBinLabel(new_i, "")
    newHisto.GetXaxis().SetTitle("")
    return newHisto


intLumi_vsTime = getHistoFromFile(folder+"/AintLumi_vsTime.root")
fillNumber_vsLumi = getHistoFromFile(folder+"/AfillNumber_vsLumi.root")
runNumber_vsLumi = getHistoFromFile(folder+"/ArunNumber_vsLumi.root")

timeLabel = {}
intLumiLabel = {}
fillLabel = {}
runLabel = {}

currentMonth = None
for i in range(intLumi_vsTime.GetNbinsX()):
    date = datetime.fromtimestamp(intLumi_vsTime.GetBinLowEdge(i))
    newMonth = date.year*12+date.month
    if currentMonth != newMonth and currentMonth!= None:
        label = "%d/%d"%(date.month, date.year) 
        timeLabel[intLumi_vsTime.GetBinLowEdge(i)] = label
        intLumiLabel[intLumi_vsTime.GetBinContent(i)] = label
    currentMonth = newMonth 

lumiKeys = list(intLumiLabel)[:] ## exclude last bin

for i, intLumi in enumerate(fillNumber_vsLumi.GetX()):
    if intLumi==0: break ## skip empty bin at the end of the plot
    matches = [key for key in lumiKeys if (intLumi-key)>=0] ## take the first fill with a lumi greater than the current one
    if len(matches)>1: raise Exception("Matches %d"%len(matches))
    if len(matches)==1:
        fillLabel[int(fillNumber_vsLumi.GetY()[i])] = intLumiLabel[matches[0]]
        runLabel[int(runNumber_vsLumi.GetY()[i])] = intLumiLabel[matches[0]]
        lumiKeys.remove(matches[0])

pprint(timeLabel)
pprint(fillLabel)
pprint(runLabel)
pprint(intLumiLabel)

c2 = ROOT.TCanvas("c2","",1960,1080)
c2.SetGridx()
c2.SetGridy()

plotPattern = plotPatterns[0]

files = [f for f in os.listdir(folder) if ".root" in f and kinds[0] in f]
assigned = set()

for group in plotsMap:
    print()
    print("### %s ###"%group)
    color, rules = plotsMap[group]
    for fName in files[:]:
        if not plotPattern in fName: continue
        streamName = fName.split(".root")[0].split(plotPattern)[1]
        matches = [fnmatch(streamName, rule) for rule in rules]
        if max(matches)>0:
            print(streamName)
            if streamName in assigned:
                raise Exception("%s already assigned.")
            assigned.add(streamName)
            files.remove(fName)

print()
print("Unassigned files: ")
for fName in files:
    if not plotPattern in fName: continue
    streamName = fName.split(".root")[0].split(plotPattern)[1].split("_")[0]
    print(streamName)
print()
print("Assigned: ")
print(assigned)
print()
print()


for plotPattern in plotPatterns:
    for kind in kinds:
        files = [f for f in os.listdir(folder) if ".root" in f and kind in f]
        if kind == "vsFill":
            xLabels = fillLabel
        elif kind == "vsTime":
            xLabels = timeLabel
        elif kind == "vsRun":
            xLabels = runLabel
        if len(xLabels)==0:
            raise Exception("No xLabels found for %s"%kind)
        
        leg = ROOT.TLegend(0.12,0.88,0.87,0.97)
        stack = ROOT.THStack("stack", "")
        
        groupHistos = {}
        for group in plotsMap:
            color, rules = plotsMap[group]
            groupHisto = None
            for fName in files:
                if not plotPattern in fName: continue
                streamName = fName.split(".root")[0].split(plotPattern)[1].split("_")[0]
                if streamName in vetos:
    #                print("Skipping %s"%streamName)
                    continue
                if max([fnmatch(streamName, rule) for rule in rules])>0:
    #                print(streamName)
                    histo = getHistoFromFile("%s/%s"%(folder, fName))
                    if not groupHisto: groupHisto = histo.Clone(group+"_"+kind+"_"+plotPattern)
                    else: 
                        if groupHisto.GetNbinsX()!=histo.GetNbinsX():
                            raise Exception("Bins mismatch for %s: %d vs %d. HistoName = %s"%(group, groupHisto.GetNbinsX(), histo.GetNbinsX(), histo.GetName()))
                    groupHisto.Add(histo)
            if groupHisto and groupHisto.Integral()>0: 
                groupHisto.SetName(groupHisto.GetName()+"_%s"%kind)
                # print(xLabels)
                groupHisto = removeEmptyBins(groupHisto, xLabels)
                groupHisto.SetLineWidth(1)
                groupHisto.SetLineColor(ROOT.kBlack)
                groupHisto.SetFillColor(color)
    #            print(group)
                 ## convert file size to bandwidth
                if "StreamBandwidth" in plotPattern:
                    groupHisto.Scale(23.31) ## fix 1/23.31 (bug: bandwidth instead of file size) 
                    # groupHisto.Scale(1./1000) ## fix 1/1000 (from MB/s instead of GB/s)
                    if "rates" in plotPattern:
                        groupHisto.Scale(1./1000) ## fix 1/1000 (from MB/s instead of GB/s)
                    elif "xsec" in plotPattern:
                        groupHisto.Scale(20.) ## convert MB/s @2.E34 cm-2 s-1 (ie GB/20 fb-1) to TB/fb-1
                else:
                    if "rates" in plotPattern:
                        groupHisto.Scale(1./1000) ## from Hz to kHz
                ## add histo to stack
                stack.Add(groupHisto)
                groupHistos[group] = groupHisto
        for group in reversed(plotsMap):
            if group in groupHistos:
                if leg.GetNRows()>3: leg.SetNColumns(1+int(leg.GetNRows()/3))
                leg.AddEntry(groupHistos[group], group, "f")
        
        for group in groupHistos:
            histo = groupHistos[group]
            print(group, histo.GetXaxis().GetNbins())

        c2.Modify()
        c2.Update()
        
        stack.Draw("HIST")
        
        stack.SetTitle(histo.GetTitle())
        stack.GetXaxis().SetTitle(histo.GetXaxis().GetTitle())
        if "StreamBandwidth" in plotPattern:
            if "rates" in plotPattern:
                stack.GetYaxis().SetTitle("stream bandwidth [GB/s]")
            elif "xsec" in plotPattern:
                stack.GetYaxis().SetTitle("data cross section [TB/fb^{-1} or MB/s @ 1E33 cm^{-2} s^{-1}]")
        else:
            if "rates" in plotPattern:
                stack.GetYaxis().SetTitle("rate [Hz]")
            elif "xsec" in plotPattern:
                stack.GetYaxis().SetTitle("rate @ 2E34 cm^{-2} s^{-1} [Hz]")
        #stack.SetLineWidth(histo.GetLineWidth())
        
        if kind == "vsTime":
            timeAxis = stack.GetXaxis()
            timeAxis.SetTimeDisplay(1)
            timeAxis.SetTimeFormat(timeAxis.ChooseTimeFormat(timeAxis.GetXmax()-timeAxis.GetXmin()))
            #timeAxis.SetTimeFormat("%Y-%m-%d %H:%M:%S")
            timeAxis.SetTimeOffset(0)
        
        stack.Draw("HIST")
        leg.Draw("same")
        stack.SetMaximum(stack.GetMaximum()*1.1)
        
        c2.SaveAs(folder+"_"+plotPattern+"_"+kind+".root")
        c2.SaveAs(folder+"_"+plotPattern+"_"+kind+".png")

















    