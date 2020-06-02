# Lines beginning with "#" are comments in python.
# Start your program by importing Root and some other handy modules
import ROOT
import math
import sys
import os
import os.path

# The argparse module makes it easy to write user-friendly command-line interfaces.
import argparse

# other modules
from plotwrapper import *
from numpyarray import numpyarray


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


# we add the flags -f and -n to the scripts, so we can pass arguments in the command line:
# e.g.   python eventloop.py -f someFile.root -n 10
parser = argparse.ArgumentParser(description='Analysis of Z events.')
parser.add_argument('-f', metavar='inputFile', type=str, nargs=1, help='Input ROOT file', required=True)
parser.add_argument('-n', metavar='numEvents', type=int, nargs=1, help='Number of events to process (default all)')
parser.add_argument('-p', metavar='plotDirectory', type=str, nargs=1, help='Directory Name for the final Plot Image')
parser.add_argument('-t', metavar='lepton_type', type=str, nargs=1, help='The type of lepton to be analyzed')
parser.add_argument('-mc', action="store_true", help='Indicates the processed file is a monte-carlo file')

args = parser.parse_args()
fileName = str(args.f[0])
numEvents = -1
if args.n != None :
    numEvents = int(args.n[0])

plotDirectory = str(args.p[0])

print "Plot Directory:", plotDirectory

save_path = "../plots_filtered/" + plotDirectory

if save_path[-1] != "/":
    save_path += "/"

os.mkdir(save_path)


analyze_type = args.t[0]


# from now on, fileName contains the string with the path to our input file and
# numEvents the integer of events we want to process

# Some ROOT global settings and styling
ROOT.TH1.SetDefaultSumw2()

# The execution starts here
print "Starting the analysis"

# Open the input file. The name can be hardcoded, or given from commandline as argument
myfile = None
if os.path.isfile(fileName) and os.access(fileName, os.R_OK):
    myfile = ROOT.TFile(fileName)
else:
    sys.exit("Error: Input file does not exist or is not readable")

print "Opened file %s"%myfile.GetName()

# Now you have access to everything you can also see by using the TBrowser
# Load the tree containing all the variables
myChain = ROOT.gDirectory.Get( 'mini' )

# Open an output file to save your histograms in (we build the filename such that it contains the name of the input file)
# RECREATE means, that an already existing file with this name would be overwritten
outfile = ROOT.TFile.Open("analysis_"+myfile.GetName().split('/')[-1], "RECREATE")
outfile.cd()

# Book histograms within the output file

# max_entries = myChain.GetEntriesFast()
# segment_entries = max_entries // 100

weight = "mcWeight" if args.mc else None

# entries_left = []

# def append_or_add(l, i, val):
#     if len(l) <= i:
#         l.append(val)
#     else:
#         l[i] += val

# for i in range(100):
#     print "overall progress: ", i, "%"
#     entries = range(i * segment_entries, (i + 1) * segment_entries)
    
#     data = EventData(myChain).acquire_entries(entries)
    
#     # all values
#     append_or_add(entries_left, 0, len(data))
#     # trigger
#     data.filter(lambda entry: entry.trigE)
#     append_or_add(entries_left, 1, len(data))
#     # good run list
#     data.filter(lambda entry: entry.passGRL)
#     append_or_add(entries_left, 2, len(data))
#     # good vertex
#     data.filter(lambda entry: entry.hasGoodVertex)
#     append_or_add(entries_left, 3, len(data))
#     # 2 leptons
#     data.filter(lambda entry: entry.lep_n >= 2)
#     append_or_add(entries_left, 4, len(data))
#     # electron or muon (PDGID)
#     data.filter(lambda entry: entry.lep_type[0] in (11,) and entry.lep_type[1] in (11,))
#     append_or_add(entries_left, 5, len(data))
#     # opposite charge
#     data.filter(lambda entry: isclose(entry.lep_charge[0] * entry.lep_charge[1], -1.0))
#     append_or_add(entries_left, 6, len(data))
#     # pt cut
#     data.filter(lambda entry: entry.lep_pt[0] > 25e3 and entry.lep_pt[1] > 25e3)
#     append_or_add(entries_left, 7, len(data))
#     # et isolation
#     data.filter(lambda entry: entry.lep_etcone20[0] / entry.lep_E[0] < 0.15 and entry.lep_etcone20[1] / entry.lep_E[1] < 0.15)
#     append_or_add(entries_left, 8, len(data))
#     # pt isolation
#     data.filter(lambda entry: entry.lep_ptcone30[0] / entry.lep_pt[0] < 0.15 and entry.lep_ptcone30[1] / entry.lep_pt[1] < 0.15)
#     append_or_add(entries_left, 9, len(data))
#     # tight id
#     data.filter(lambda entry: entry.lep_flag[0] & 1 << 9 and entry.lep_flag[1] & 1 << 9)
#     append_or_add(entries_left, 10, len(data))
    
#     print entries_left

# print entries_left

plots = [
    Plot(myChain, "lep_pt", True, "lep_pt", "x", "y", 100, 0, 300e3),
    Plot(myChain, "lep_eta", True, "lep_eta", "x", "y", 50, -3.5, 3.5),
    Plot(myChain, "lep_phi", True, "lep_phi", "x", "y", 50, -3.5, 3.5),
    Plot(myChain, "lep_E", True, "lep_E", "x", "y", 100, 0, 500e3),
    Plot(myChain, "vxp_z", False, "vxp_z", "x", "y", 1000, -500, 500),
    Plot(myChain, "lep_n", False, "lep_n", "x", "y", 10, 0, 10),
    Plot(myChain, "lep_ptcone30", True, "lep_ptcone30", "x", "y", 500, 0, 170e4),
    Plot(myChain, "lep_etcone20", True, "lep_etcone20", "x", "y", 100, 0, 500e3)
]

def opposite_charges(c1, c2):
    return math.is_close(c1, -c2)


def selector(data_item, chain):
    def data_pass():
        return data_item

    def data_fail():
        return None

    if analyze_type == "e" and not chain.trigE:
        return data_fail()

    if analyze_type == "m" and not chain.trigM:
        return data_fail()

    if not chain.passGRL:
        return data_fail()

    if not chain.hasGoodVertex:
        return data_fail()

    # two leptons
    if chain.lep_n < 2:
        return data_fail()

    # two highest energy leptons must be electron (11), muon (13) or tau (15)
    allowed_type = None
    if analyze_type == "e":
        allowed_type = 11
    elif analyze_type == "m":
        allowed_type = 13
    elif analyze_type == "t":
        allowed_type = 15
    else:
        raise ValueError("Invalid Type")

    types = list(chain.lep_type)
    if types[0] != allowed_type or types[1] != allowed_type:
        return data_fail()

    # two highest energy leptons must have opposite charge
    charges = list(chain.lep_charge)
    if not math.is_close(charges[0], -charges[1]):
        return data_fail()

    # transverse momentum of the first two leptons must be at least 25GeV
    pt = list(chain.lep_pt)
    if pt[0] < 25e3 or pt[1] < 25e3:
        return data_fail()

    # Momentum Isolation
    ptcone = list(chain.lep_ptcone30)
    if ptcone[0] / pt[0] > 0.15 or ptcone[1] / pt[1] > 0.15:
        return data_fail()

    # Energy Isolation
    etcone = list(chain.lep_etcone20)
    E = list(chain.lep_E)
    if etcone[0] / E[0] > 0.15 or etcone[1] / E[1] > 0.15:
        return data_fail()

    # check the 9th bit flag (tight detector selection)
    flags = list(chain.lep_flag)
    if not flags[0] & (1 << 9) or not flags[1] & (1 << 9):
        return data_fail()

    return data_pass()
    
num_entries = -1


plots[0].acquire_entries(num_entries=num_entries, selector=selector, weight=weight)
plots[0].draw_and_save(save_path + "lep_pt.png", which=(0,1), log_scale=(0, 1))

# plots[0].draw(which=(0,))
# plots[0].draw(which=(1,))
# plots[0].draw(which=(0,))
# plots[0].draw(which=(1
# pt1 = numpyarray([x[0] for x in plots[0].data if len(x) >= 2])
#
# plots[0].draw(False, which=(1,))

pt1 = numpyarray([x[0] for x in plots[0].data])

# for i in range(100):
#     print pt1[i]

pt1_plot = Plot(myChain, "pt1", False, "pt1", "x", "y", 500, 0, 170e3)
pt1_plot.acquire_from_data(pt1)

pt1_plot.draw(which=(0,))

plots[6].acquire_entries(num_entries=num_entries, selector=selector, weight=weight)

pt1_cone30 = numpyarray([x[0] for x in plots[6].data])
pt1_iso = pt1_cone30 / pt1
pt1_iso_plot = Plot(myChain, "pt1_iso", False, "pt1 isolation", "x", "y", 500, 0, 1)
pt1_iso_plot.acquire_from_data(pt1_iso)
pt1_iso_plot.draw_and_save(save_path + "pt1_iso.png", log_scale=(0, 1))

# print(plots[0].data[0:100])

pt2 = numpyarray([x[1] for x in plots[0].data])

pt2_cone30 = numpyarray([x[1] for x in plots[6].data])
pt2_iso = pt2_cone30 / pt2
pt2_iso_plot = Plot(myChain, "pt2_iso", False, "pt2 isolation", "x", "y", 500, 0, 1)
pt2_iso_plot.acquire_from_data(pt2_iso)
pt2_iso_plot.draw_and_save(save_path + "pt2_iso.png", log_scale=(0, 1))

print "pt1 =", pt1.mean()
print "pt2 =", pt2.mean()

# raw_input()

plots[1].acquire_entries(num_entries=num_entries, selector=selector, weight=weight)
plots[1].draw_and_save(save_path + "lep_eta.png", which=(0,1), log_scale=(0, 0))

eta1 = numpyarray([x[0] for x in plots[1].data])
eta2 = numpyarray([x[1] for x in plots[1].data])

print "eta1 =", eta1.mean()
print "eta2 =", eta2.mean()

# raw_input()

plots[2].acquire_entries(num_entries=num_entries, selector=selector, weight=weight)
plots[2].draw_and_save(save_path + "lep_phi.png", which=(0,1), log_scale=(0, 0))

phi1 = numpyarray([x[0] for x in plots[2].data])
phi2 = numpyarray([x[1] for x in plots[2].data])

print "phi1 =", phi1.mean()
print "phi2 =", phi2.mean()

# raw_input()

M = numpyarray.sqrt(2 * pt1 * pt2 * (numpyarray.cosh(eta1 - eta2) - numpyarray.cos(phi1 - phi2)))

# mass selection
temp = len(M)
M = numpyarray(filter(lambda x: 70e3 <= x <= 110e3, M))
del temp

# print "Len M:", len(M)

m_plot = Plot(None, "M", False, "Invariant Mass M of two leading Leptons", "M_ll / MeV", "counts", 300, 70e3, 130e3)
m_plot.acquire_from_data(M)

plots[3].acquire_entries(num_entries=num_entries, selector=selector, weight=weight)
# plots[3].draw_and_save(save_path + "lep_E.png")

plots[4].acquire_entries(num_entries=num_entries, selector=selector, weight=weight)
plots[4].draw_and_save(save_path + "vxp_z.png")


plots[5].acquire_entries(num_entries=num_entries, selector=selector, weight=weight)
plots[5].draw_and_save(save_path + "lep_n.png", log_scale=(0, 1))


E1 = numpyarray([x[0] for x in plots[3].data])
E2 = numpyarray([x[1] for x in plots[3].data])

plots[7].acquire_entries(num_entries=num_entries, selector=selector, weight=weight)

Et1_cone20 = numpyarray([x[0] for x in plots[7].data])
Et2_cone20 = numpyarray([x[1] for x in plots[7].data])

Et1_iso = Et1_cone20 / E1
Et2_iso = Et2_cone20 / E2

Et1_iso_plot = Plot(myChain, "Et1_iso", False, "Et1 isolation", "x", "y", 500, 0, 1)
Et2_iso_plot = Plot(myChain, "Et2_iso", False, "Et2 isolation", "x", "y", 500, 0, 1)

Et1_iso_plot.acquire_from_data(Et1_iso)
Et2_iso_plot.acquire_from_data(Et2_iso)


Et1_iso_plot.draw_and_save(save_path + "Et1_iso.png", which=(0,), log_scale=(0, 1))
Et2_iso_plot.draw_and_save(save_path + "Et2_iso.png", which=(0,), log_scale=(0, 1))


vec1 = numpyarray([])
vec2 = numpyarray([])


for i in range(len(pt1)):
    pt = pt1[i]
    eta = eta1[i]
    phi = phi1[i]
    E = E1[i]
    lorentz_vec = ROOT.TLorentzVector()
    lorentz_vec.SetPtEtaPhiE(pt, eta, phi, E)
    vec1.append(lorentz_vec)

for i in range(len(pt2)):
    pt = pt2[i]
    eta = eta2[i]
    phi = phi2[i]
    E = E2[i]
    lorentz_vec = ROOT.TLorentzVector()
    lorentz_vec.SetPtEtaPhiE(pt, eta, phi, E)
    vec2.append(lorentz_vec)

M_vec = numpyarray([])

for i in range(len(vec1)):
    v1 = vec1[i]
    v2 = vec2[i]

    M_vec.append((v1 + v2).M())

print "M_vec =", M_vec.mean()

M_vec_plot = Plot(None, "M_vec", False, "Invariant Mass M_vec of two leading Leptons", "M_ll / MeV", "counts", 300, 70e3, 130e3)
M_vec_plot.acquire_from_data(M_vec)
M_vec_plot.draw_and_save(save_path + "M_vec.png", log_scale=(0, 0))


m_plot.draw_and_save(save_path + "M.png", log_scale=(0, 0))

print M.mean()

    # Some entries are stored in vectors, meaning they have several entries themselves
    # another loop is needed for these objects
    # e.g.:
#    print "lep_pt:", myChain.lep_pt
#    print "lep_n:",   myChain.lep_n


    # might be helpful, to access all 32 bits of a 32 bit integer flag individually:

    # for bit in range ( 32 ):
    #     flagBit = lep_flag & (1 << bit)
    #     print flagBit


##########################################################################
#end of the event loop
##########################################################################


### The Wrap-up code (writing the files, etc) goes here
# Let's look at the histogram; create a canvas to draw it
# for var_name, hist in histograms.items():
#     canvas = ROOT.TCanvas(var_name + "canvas", 'Analysis Plots', 200, 10, 700, 500 )
#     canvas.cd()
#     hist.Draw()
#     ROOT.TPython.Prompt()
# hVertexDist.Draw()

#########################################################################

outfile.cd()
print "Writing output to %s"%outfile.GetName()
outfile.Write()

#useful command to pause the execution of the code. Allows to see the plot before python finishes
# ROOT.TPython.Prompt()

# raw_input("Press Enter to Quit.")
