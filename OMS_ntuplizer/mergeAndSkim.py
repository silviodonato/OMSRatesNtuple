from ROOT import TFile, TChain
fileout = TFile("goldejson_skim.root","recreate")
chain = TChain("tree")
#chain.Add("36*.root")
#chain.Add("35*.root")
chain.Add("31*.root")
chain.Add("32*.root")

fileout.cd()
newTree = chain.CloneTree(0)
for entry in chain:
#    if chain.golden_json:
        newTree.Fill()

fileout.Write()
fileout.Close()

