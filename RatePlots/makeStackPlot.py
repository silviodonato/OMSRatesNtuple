#!/usr/bin/python3
import ROOT
import os, array
from fnmatch import fnmatch
import tdrstyle #https://twiki.cern.ch/twiki/bin/viewauth/CMS/Internal/FigGuidelines
from pprint import pprint
from datetime import datetime

tdrstyle = tdrstyle.setTDRStyle()
tdrstyle.cd()

ROOT.gROOT.SetBatch(1)

plotsMap = {
    "Prompt": (ROOT.kRed, "Physics*"),
    "ParkingDoubleMuon": (ROOT.kBlue, "ParkingDoubleMuonLowMass*"),
    "ParkingLLP": (ROOT.kMagenta, "ParkingLLP*"),
    "ParkingHH": (ROOT.kYellow, "ParkingHH*"),
    "ParkingDoubleElectron": (ROOT.kGreen, "ParkingDoubleElectron*"),
    "ParkingVBF": (ROOT.kGreen-9, "ParkingVBF*"),
#    "Scouting": (ROOT.kBlue-9, "Scouting*"),
#    "Commissioning": (ROOT.kGreen, "Prompt*"),
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
        if x>keys[0]:
            newHisto.GetXaxis().SetBinLabel(new_i, xLabels[keys[0]])
            print("XXX", new_i, xLabels[keys[0]], keys[0])
            del keys[0]
        else:
            newHisto.GetXaxis().SetBinLabel(new_i, "")
    newHisto.GetXaxis().SetTitle("")
    return newHisto

folder = "plots/Stream22"

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

for kind in ["vsFill","vsTime","vsRun"]:
    if kind == "vsFill":
        xLabels = fillLabel
    elif kind == "vsTime":
        xLabels = timeLabel
    elif kind == "vsRun":
        xLabels = runLabel

    files = [f for f in os.listdir(folder) if ".root" in f and kind in f]
    
    c2 = ROOT.TCanvas("c2","",1960,1080)
    c2.SetGridx()
    c2.SetGridy()
    
    leg = ROOT.TLegend(0.12,0.88,0.87,0.97)
    stack = ROOT.THStack("stack", "")
    
    for group in plotsMap:
        color, rule = plotsMap[group]
        groupHisto = None
        for fName in files:
            if not "Stream_" in fName: continue
            streamName = fName.split(".root")[0].split("Stream_")[1]
            if fnmatch(streamName, rule):
                print(streamName)
                histo = getHistoFromFile("%s/%s"%(folder, fName))
                if not groupHisto: groupHisto = histo.Clone(group)
                else: groupHisto.Add(histo)
        if groupHisto and groupHisto.Integral()>0: 
            groupHisto = removeEmptyBins(groupHisto, xLabels)
            groupHisto.SetLineWidth(1)
            groupHisto.SetLineColor(ROOT.kBlack)
            groupHisto.SetFillColor(color)
            print(group)
            stack.Add(groupHisto)
            leg.AddEntry(groupHisto, group, "f")
    
    c2.Modify()
    c2.Update()
    
    stack.Draw("HIST")

    
    stack.SetTitle(histo.GetTitle())
    stack.GetXaxis().SetTitle(histo.GetXaxis().GetTitle())
    stack.GetYaxis().SetTitle(histo.GetYaxis().GetTitle())
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
    
    c2.SaveAs(folder+"_"+kind+".root")
    c2.SaveAs(folder+"_"+kind+".png")
    c2.SaveAs(folder+"_"+kind+".C")

