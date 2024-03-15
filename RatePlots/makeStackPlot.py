#!/usr/bin/python3
import ROOT
import os
from fnmatch import fnmatch
import tdrstyle #https://twiki.cern.ch/twiki/bin/viewauth/CMS/Internal/FigGuidelines

tdrstyle = tdrstyle.setTDRStyle()
tdrstyle.cd()

ROOT.gROOT.SetBatch(0)

plotsMap = {
    "Prompt": (ROOT.kGreen-9, "Physics*"),
    "ParkingDoubleMuon": (ROOT.kMagenta, "ParkingDoubleMuonLowMass*"),
    "ParkingLLP": (ROOT.kBlue, "ParkingLLP*"),
    "ParkingHH": (ROOT.kYellow, "ParkingHH*"),
    "ParkingDoubleElectron": (ROOT.kCyan, "ParkingDoubleElectron*"),
    "ParkingVBF": (ROOT.kGreen, "ParkingVBF*"),
#    "Scouting": (ROOT.kBlue-9, "Scouting*"),
#    "Commissioning": (ROOT.kGreen, "Prompt*"),
}

def getHistoFromFile(fName):
    f = ROOT.TFile.Open(fName)
    canvas = f.Get("canv")
    histos = [p for p in canvas.GetListOfPrimitives() if type(p)==ROOT.TH1F]
    f.Close()
    return histos[0]


folder = "plots/Stream22"
for kind in ["vsFill","vsTime","vsRun"]:
    files = [f for f in os.listdir(folder) if ".root" in f and kind in f]
    
    c2 = ROOT.TCanvas("c2","")
    
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
            groupHisto.SetLineWidth(0)
            groupHisto.SetLineColor(ROOT.kBlack)
            groupHisto.SetFillColor(color)
            print(group)
            stack.Add(groupHisto)
            leg.AddEntry(groupHisto, group, "f")
    
    c2.Modify()
    c2.Update()
    
    stack.Draw("HIST")
    
#    1/0
    
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

    ### build stack
    #if group == "main" or group == 'lumi':
    #else:
    #    leg = ROOT.TLegend(0.12,0.45,0.35,0.98)
    #    
    #for group in plotsMap:
    #    if leg.GetNRows()>30: leg.SetNColumns(2)
    #    leg.AddEntry(stacks[d],d) # or lep or f
    
    stack.Draw("HIST")
    leg.Draw("same")
    stack.SetMaximum(stack.GetMaximum()*1.1)
    
    c2.SaveAs(folder+"_"+kind+".root")
    c2.SaveAs(folder+"_"+kind+".png")
    c2.SaveAs(folder+"_"+kind+".C")

