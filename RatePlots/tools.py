import ROOT

def getCrossSection(histo, recLumi,removeOutliers=0.95):
    npointsMedian = 10000000
    average = 0
    count = 0
    nhisto = histo.Clone(histo.GetName()+recLumi.GetName())
    if histo.Integral() == 0: raise Exception("getCrossSection: %s is empty"%histo.GetName())
    if recLumi.Integral() == 0: raise Exception("getCrossSection: %s is empty"%recLumi.GetName())
    if removeOutliers>0: ##compute the quantile of histo/recLumi using only npointsMedian points
        y1 = histo.GetArray()
        y2 = recLumi.GetArray()
        ys = []
        npointsMedian = min(npointsMedian,histo.GetNbinsX())
        jump = max(1., float(histo.GetNbinsX())/ npointsMedian)
        for x in range(1, npointsMedian):
            i = int(x*jump)
            if y1[i]>0 and y2[i]>0:
                ys.append(y1[i]/y2[i])
        maxAllowedIdx = min(int(len(ys) * (1.0-removeOutliers))-1, len(ys)-2)
        minAllowedIdx = max(int(len(ys) * (removeOutliers))+1, 0)
        print(len(ys), minAllowedIdx, maxAllowedIdx)
        maxAllowedValue = sorted(ys)[maxAllowedIdx]
        minAllowedValue = sorted(ys)[minAllowedIdx]
#        print ( [sorted(ys)[i] for i in range(len(ys))])
        print("getCrossSection",histo.GetName(),recLumi.GetName(),minAllowedValue, maxAllowedValue, removeOutliers, len(ys), maxAllowedIdx, minAllowedIdx,  histo.Integral(), recLumi.Integral(), jump)
    for i in range(len(histo)):
        val = float(histo[i]) 
        lum = float(recLumi[i])
        if lum>0 and val>=0:
            nhisto.SetBinContent(i, val/lum)
            nhisto.SetBinError(i, val**0.5/lum)
            if removeOutliers>0:
                if val/lum>maxAllowedValue: 
                    nhisto.SetBinContent(i, maxAllowedValue)
                    nhisto.SetBinError(i, 0) ## to avoid huge errors from crazy rates
                elif val/lum<minAllowedValue: 
                    nhisto.SetBinContent(i, minAllowedValue)
                    nhisto.SetBinError(i, 0) ## to avoid huge errors from crazy rates
        else:
            nhisto.SetBinContent(i, 0)
            nhisto.SetBinError(i, 0)
            if lum<0: print("getCrossSection: lum<0 in %s bin %d"%(recLumi.GetName(), i))
            if val<0: print("getCrossSection: val<0 in %s bin %d"%(histo.GetName(), i))
#            print(i,val,lum)
        nhisto.SetMaximum(maxAllowedValue*1.05)
        nhisto.SetMinimum(minAllowedValue*0.5)
    return nhisto

import copy
def getHisto(weight, chain, var, binning, selection, option="GOFF"):
    hName = "hist_"+weight+selection
    hName = ''.join([l for l in hName if l.isalpha()])
    print ("Calling chain.Draw: with",("%s >> %s%s"%(var,hName,binning),"%s*(%s)"%(weight,selection),option))
    chain.Draw("%s >> %s"%(var,hName) + binning,"%s*(%s)"%(weight,selection),option)
    histo = ROOT.gROOT.Get(hName)
    assert(type(histo)==ROOT.TH1F)
    return histo


def getBinning(chain, var, selection,bin_size):
    tmp =  getHisto("1", chain, var, "", selection)
    timemax = tmp.GetXaxis().GetXmax()
    timemin = tmp.GetXaxis().GetXmin()
    ntimebins =  int((timemax-timemin)/bin_size)
    timemax = timemin + bin_size*(ntimebins-1)
    del tmp
    return ntimebins, timemin, timemax

def getBinningFromMax(chain, var, selection, LS_duration, nbins):
    tmp =  getHisto("1", chain, var, "", selection)
    timemax = tmp.GetXaxis().GetXmax()
    timemin = tmp.GetXaxis().GetXmin()
    bin_size =  int((timemax-timemin)/nbins/LS_duration)*LS_duration
    ntimebins =  int((timemax-timemin)/bin_size)
    timemax = timemin + bin_size*(ntimebins-1)
    del tmp
    print("HELLO ", ntimebins, timemin, timemax)
    return ntimebins, timemin, timemax

def setColor(plot, color):
    plot.SetLineColor(color)
    plot.SetMarkerColor(color)

def setStyle(plot, color):
    setColor(plot, color)
    plot.SetLineWidth(2)
    plot.SetMarkerStyle(21)
    plot.SetMarkerSize(0.6)

def createFit(histo, initVal,  function = "[0]"):
    min_,max_ = histo.GetXaxis().GetXmin(), histo.GetXaxis().GetXmax()
    fit = ROOT.TF1(histo.GetName()+"_fit",function,min_,max(max_,100))
    setColor(fit, histo.GetLineColor())
    fit.SetLineWidth(4)
    fit.SetLineStyle(4)
    fit.SetParameter(0, initVal)
    histo.Fit(fit,"WW","",min_,max_)
    return fit

def dropError(histo):
    for i in range(len(histo)): histo.SetBinError(i, 0)

def addPileUp(canvas, pileup, rightmax, pileupLabel):
    pileup_scaled = pileup.Clone(pileup.GetName()+"_scaled")
    canvas.Update()
    canvas.Modify()
    rightmin = canvas.GetUymin() / canvas.GetUymax() * rightmax
    scale = (canvas.GetUymax()-canvas.GetUymin())/(rightmax-rightmin)
    if hasattr(pileup_scaled,"Scale"):
        pileup_scaled.Scale(scale)
    else: ##Assume it is a TGraphErrors
        for i in range(pileup_scaled.GetN()):
            pileup_scaled.GetY()[i] = pileup_scaled.GetY()[i]*scale
            pileup_scaled.GetEY()[i] = pileup_scaled.GetEY()[i]*scale
    axis = ROOT.TGaxis(canvas.GetUxmax(),canvas.GetUymin(), canvas.GetUxmax(), canvas.GetUymax(),rightmin,rightmax,510,"+L");
    axis.SetLineColor(pileup.GetLineColor())
    axis.SetLabelColor(pileup.GetLineColor())
    axis.SetTitleColor(pileup.GetLineColor())
    axis.SetTitle(pileupLabel)
    axis.SetTitleFont(pileup.GetYaxis().GetTitleFont())
    axis.SetTitleSize(pileup.GetYaxis().GetTitleSize())
    axis.SetTitleOffset(pileup.GetYaxis().GetTitleOffset())
    
    return pileup_scaled, axis
#    axis.Draw()
#    del pileup_scaled


## Input: histo A vs B  and histo C vs B  Output: graph A vs C [eg. from rate vs time and lumi vs time --> rate vs lumi]
def getPlotVsNewVar(plot_vsOldVar, newVar_vsOldVar):
    plot_vsLum = ROOT.TGraphErrors()
    npoints = 0
    for i in range(len(plot_vsOldVar)):
        if plot_vsOldVar[i]>0:
            plot_vsLum.SetPoint(npoints,newVar_vsOldVar[i],plot_vsOldVar[i])
            plot_vsLum.SetPointError(npoints,0,plot_vsOldVar.GetBinError(i))
            npoints+=1
    setStyle(plot_vsLum, plot_vsOldVar.GetLineColor())
    return plot_vsLum


def getHistoVsFillNumber(histo, fill):
    min_ = int(fill.GetMinimum()-1)
    max_ = int(fill.GetMaximum()+2)
    nHisto = ROOT.TH1F(histo.GetName() + fill.GetName(),"" , max_-min_, min_, max_)
    for i in range(len(histo)):
        if histo.GetBinContent(i)>0 and fill.GetBinContent(i):
            nHisto.Fill(fill.GetBinContent(i), histo.GetBinContent(i))
#            print(fill.GetBinContent(i), histo.GetBinContent(i))
    nHisto.Sumw2()
    return nHisto

def readOptions(args, triggers, selections):
    useRates = []
    vses = []
    if args.rates: useRates.append(True)
    if args.xsect: useRates.append(False)
    if args.vsFill: vses.append("vsFill")
    if args.vsPU: vses.append("vsPU")
    if args.vsIntLumi: vses.append("vsIntLumi")
    if args.vsTime: vses.append("vsTime")
    runMin = int(args.runMin)
    runMax = int(args.runMax)
    removeOutliers = float(args.removeOutliers)
    folder = args.input
    plotFolder = args.output
    if args.triggers: triggers = args.triggers.split(",")
    if args.selections: 
        selections = {}
    batch = not args.nobatch
    testing = args.testing
    refLumi = float(args.refLumi)
    lumisPerBin = int(args.lumisPerBin)
    nbins = int(args.nbins)
    if nbins>0 and lumisPerBin>0: raise Exception("You have to use one and only one option between --lumisPerBin and --nbins.")
    print(args)
    print(useRates, vses, triggers, folder, plotFolder, removeOutliers, runMin, runMax, batch, testing, lumisPerBin, refLumi, selections, nbins)
    return useRates, vses, triggers, folder, plotFolder, removeOutliers, runMin, runMax, batch, testing, lumisPerBin, refLumi, selections, nbins

