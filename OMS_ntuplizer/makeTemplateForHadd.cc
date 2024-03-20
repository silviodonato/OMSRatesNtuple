#include <iostream>
#include <TFile.h>
#include <TTree.h>
#include <TBranch.h>
#include <TObjArray.h>

int main(int argc, char **argv) {
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--help") {
            std::cout << "This program takes command line arguments representing input files and creates a template TTree by combining the TTree structures of the input files." << std::endl;
            std::cout << "The template TTree is then written to an output file named \"template.root\"." << std::endl;
            std::cout << "To be compiled with: g++ -o makeTemplateForHadd makeTemplateForHadd.cc $(root-config --cflags --libs) && ./makeTemplateForHadd outputfile.root file1.root file2.root file3.root" << std::endl;
            return 0;
        }
    }
    if (argc < 3) {
        std::cout << "Usage: " << argv[0] << " outputfile.root file1.root file2.root ... fileN.root" << std::endl;
        return 1;
    }

    TFile *outFile = new TFile(argv[1], "RECREATE");
    TTree *outTree = new TTree("tree","");

    for (int i = 2; i < argc; ++i) {
        TFile *inFile = TFile::Open(argv[i]);
        if (!inFile) {
            std::cout << "Cannot open file: " << argv[i] << std::endl;
            continue;
        }

        TTree *inTree = (TTree*)inFile->Get("tree")->Clone();
        if (!inTree) {
            std::cout << "Cannot find TTree in file: " << argv[i] << std::endl;
            inFile->Close();
            continue;
        }

        if (i == 1) {
            // For the first file, clone the TTree structure to the output TTree
            outFile->cd();
            outTree = inTree->CloneTree(0);
        }
        else {
            // For the subsequent files, add the new TBranches to the output TTree
            TObjArray *branches = inTree->GetListOfBranches();
            for (int j = 0; j < branches->GetEntries(); ++j) {
                TBranch *branch = (TBranch*)branches->At(j)->Clone();
                // Add the branch if it is not already in the output TTree
                if (!outTree->GetBranch(branch->GetName()))
                    outTree->Branch(branch->GetName(), branch->GetAddress(), branch->GetTitle());
            }
        }
        inFile->Close();
    }

    outFile->cd();
    if (outTree) {
        outTree->Write();
    }

    outFile->Close();

    return 0;
}