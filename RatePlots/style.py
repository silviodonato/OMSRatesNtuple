from ROOT import TLegend,kBlue,kMagenta,kRed,kGreen,TStyle

title_vsTime = "Trigger cross-section vs time"
title_vsLumi = "Trigger cross-section vs int lumi"
timeLabel = "days since Apr 30, 2023"
#xsecLabel = "cross section [cm2]"
xsecLabel = "rate at %0.1fE34 cm-2s-1"
ratesLabel = "rate [Hz]"
fillLabel = "fill number"
runLabel = "run number"
pileupLabel = "pileup"
intLumiLabel = "Int. luminosity since fill %d [fb-1]"
legStyle = "lp"
fillLabel = "Fill number"

minY=-1
maxY=-1
fillNumberMargin = 5


#def createLegend(xmin=0.18, ymin=0.15, xmax=0.82, ymax=0.25):
def createLegend(xmin=0.16, ymin=0.88, xmax=0.87, ymax=0.98):
    leg = TLegend(xmin,ymin,xmax,ymax)
#    leg.SetFillStyle(0)
    return leg


def setYRange(histo,maxY=maxY,minY=minY):
    max_, min_ = histo.GetMaximum(), histo.GetMinimum()
    margin = 0.1 * (max_-min_)
    if maxY>0: histo.SetMaximum(maxY)
    else: histo.SetMaximum(max_ + margin)
    if minY>0: histo.SetMinimum(minY)
    else: histo.SetMaximum(min_ - margin)


#def defaultStyle():
#    defaultStyle  = TStyle("default","default")
#    defaultStyle.SetPadLeftMargin(0.16)
#    defaultStyle.SetPadRightMargin(0.02)
#    defaultStyle.SetPadTickY(1)
#    defaultStyle.SetTitleYOffset(1.25)
#    return defaultStyle

#def twoScalesStyle():
#    twoScalesStyle  = TStyle("twoScalesStyle","twoScalesStyle")
#    twoScalesStyle.SetPadLeftMargin(0.12)
#    twoScalesStyle.SetPadRightMargin(0.12)
#    twoScalesStyle.SetPadTickY(0)
#    twoScalesStyle.SetTitleYOffset(0.9)
#    return

res_X,res_Y = 1280, 1024
res_X,res_Y = 600*2, 600*2
gridX, gridY = True, True

puColor = kRed

colors = [ kBlue, kMagenta, kGreen ]

for c in colors [:]:
    colors.append(c+3)

for c in colors [:]:
    colors.append(c-7)

for c in colors [:]:
    colors.append(c+1)

for c in colors [:]:
    colors.append(c-9)

for c in colors [:]:
    colors.append(c-4)

for c in colors [:]:
    colors.append(c+1)

def getColor(i):
    return colors[i%len(colors)]
