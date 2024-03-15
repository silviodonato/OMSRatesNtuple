import ROOT

def getCrossSection(histo, recLumi, scale=1, removeOutliers=0.98):
    print("getCrossSection START")
    print(histo, recLumi, scale, removeOutliers)
    npointsMedian = 10000000
    average = 0
    count = 0
    nhisto = histo.Clone(histo.GetName()+recLumi.GetName())
    if histo.Integral() == 0: raise Exception("getCrossSection: %s is empty"%histo.GetName())
    if recLumi.Integral() == 0: raise Exception("getCrossSection: %s is empty"%recLumi.GetName())
    maxAllowedValue = histo.GetMaximum()
    minAllowedValue = histo.GetMinimum()
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
        if len(ys)>1:
            maxAllowedValue = sorted(ys)[maxAllowedIdx]
            minAllowedValue = sorted(ys)[minAllowedIdx]
        else:
            maxAllowedValue = ys[0]
            minAllowedValue = ys[0]
#        print ( len(ys), minAllowedIdx, maxAllowedIdx, minAllowedValue, maxAllowedValue, [sorted(ys)[i] for i in range(len(ys))])
        print("getCrossSection",histo.GetName(),recLumi.GetName(),minAllowedValue, maxAllowedValue, removeOutliers, len(ys), maxAllowedIdx, minAllowedIdx,  histo.Integral(), recLumi.Integral(), jump)
    for i in range(len(histo)):
        val = float(histo[i]) 
        lum = float(recLumi[i])
        if lum>0 and val>=0:
            nhisto.SetBinContent(i, val/lum*scale)
            nhisto.SetBinError(i, val**0.5/lum*scale)
            if removeOutliers>0:
                if val/lum>maxAllowedValue: 
                    nhisto.SetBinContent(i, maxAllowedValue*scale)
                    nhisto.SetBinError(i, 0) ## to avoid huge errors from crazy rates
                elif val/lum<minAllowedValue: 
                    nhisto.SetBinContent(i, minAllowedValue*scale)
                    nhisto.SetBinError(i, 0) ## to avoid huge errors from crazy rates
        else:
            nhisto.SetBinContent(i, 0)
            nhisto.SetBinError(i, 0)
            if lum<0: print("getCrossSection: lum<0 in %s bin %d"%(recLumi.GetName(), i))
            if val<0: print("getCrossSection: val<0 in %s bin %d"%(histo.GetName(), i))
#            print(i,val,lum)
        nhisto.SetMaximum(maxAllowedValue*1.05*scale)
        nhisto.SetMinimum(minAllowedValue*0.5*scale)
    print("getCrossSection STOP", nhisto.GetMaximum(), nhisto.GetMinimum())
    return nhisto

import copy
def getHisto(weight, chain, var, binning, selection, option="GOFF"):
    hName = "hist_"+weight+selection
    hName = ''.join([l for l in hName if (l.isalpha() or l.isnumeric()) ])
    print ("Calling chain.Draw: with",("%s >> %s%s"%(var,hName,binning),"%s*(%s)"%(weight,selection),option))
    chain.Draw("%s >> %s"%(var,hName) + binning,"%s*(%s)"%(weight,selection),option)
    histo = ROOT.gROOT.Get(hName)
    print ("%s %f"%(histo.GetName(),histo.Integral()))
    assert(type(histo)==ROOT.TH1F)
    if "time" in var and histo!=None:
        print(histo)
        print(histo!=None)
        print(histo.GetName())
        timeAxis = histo.GetXaxis()
        timeAxis.SetTimeDisplay(1)
        timeAxis.SetTimeFormat(timeAxis.ChooseTimeFormat(timeAxis.GetXmax()-timeAxis.GetXmin()))
#        timeAxis.SetTimeFormat("%Y-%m-%d %H:%M:%S")
        timeAxis.SetTimeOffset(0)
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
    return ntimebins, timemin, timemax

def setColor(plot, color):
    plot.SetLineColor(color)
    plot.SetMarkerColor(color)

def setStyle(plot, color):
#    print("setStyle START")
    setColor(plot, color)
    plot.SetLineWidth(2)
    plot.SetMarkerStyle(21)
    plot.SetMarkerSize(0.6)
#    print("setStyle STOP")

def createFit(histo, initVal,  function = "[0]"):
#    print("createFit START")
    min_,max_ = histo.GetXaxis().GetXmin(), histo.GetXaxis().GetXmax()
    fit = ROOT.TF1(histo.GetName()+"_fit",function,min_,max(max_,100))
    setColor(fit, histo.GetLineColor())
    fit.SetLineWidth(4)
    fit.SetLineStyle(4)
    fit.SetParameter(0, initVal)
    histo.Fit(fit,"WW","",min_,max_)
#    print("createFit STOP")
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
    if args.vsRun: vses.append("vsRun")
    if args.vsPU: vses.append("vsPU")
    if args.vsIntLumi: vses.append("vsIntLumi")
    if args.vsTime: vses.append("vsTime")
    if len(useRates) == 0:
        print("adding default --xsect flag (--xsect or --rates is required)")
        useRates.append(False)
    if len(vses) == 0:
        print("adding default --vsIntLumi flag (at least one --vs* is required)")
        vses.append("vsIntLumi")
    runMin = int(args.runMin)
    runMax = int(args.runMax)
    removeOutliers = float(args.removeOutliers)
    inputFolder = args.input
    inputFile = args.inputFile
    plotFolder = args.output
    if args.triggers: triggers = args.triggers.split(",")
    if args.selections:
        selections = {}
        for s in args.selections.split(","):
            (direct, sel) = s.split("=")
            selections[direct] = sel
    collisions = not args.cosmics
    batch = not args.nobatch
    testing = args.testing
    refLumi = float(args.refLumi)
    lumisPerBin = int(args.lumisPerBin)
    nbins = int(args.nbins)
    if nbins<0 and lumisPerBin<0: nbins=1000
    if nbins>0 and lumisPerBin>0: raise Exception("You have to use one and only one option between --lumisPerBin and --nbins.")
    if not inputFile and not inputFolder: 
        inputFile = "/afs/cern.ch/work/s/sdonato/public/website/OMSRatesNtuple/OMSRatesNtuple/OMS_ntuplizer/2023/physics_merged.root"
        #inputFile = "/afs/cern.ch/work/s/sdonato/public/OMS_ntuples/v2.0/goldejson_skim.root"
        print ("Using default inputFile = %s"%inputFile)
    if inputFolder and inputFile:  raise Exception("You cannot --input and --inputFolder at the same time.")
    print(args)
    return useRates, vses, triggers, inputFolder, inputFile, plotFolder, removeOutliers, runMin, runMax, collisions, batch, testing, lumisPerBin, refLumi, selections, nbins


def saveSh(outputFile, filePath, useRate, vs, trigger, inputFolder, inputFile, plotsFolder, removeOutliers, runMin, runMax, collisions, batch, testing, lumisPerBin, refLumi, selection, nbins):
    out_ = open(outputFile, 'w')
    command = "python3 %s "%(filePath)
    if useRate: command += "--rates "
    else: command += "--xsect "
    if not collisions: command += "--cosmics "
    command += "--%s "%vs
    command += "--triggers %s "%trigger
    if len(inputFolder)>0: command += "--input %s "%inputFolder
    if len(inputFile)>0: command += "--inputFile %s "%inputFile
    command += "--output %s "%plotsFolder
    command += "--runMin %s "%runMin
    command += "--runMax %s "%runMax
    command += "--refLumi %s "%refLumi
    command += "--lumisPerBin %s "%lumisPerBin
    command += "--nbins %s "%nbins
    command += "--selections %s "%selection
    out_.write(command)
    out_.close()

