# script to determine the Z boson mass
import ROOT
import math
import sys


def sq(x):
    return x * x


def gauss(x,par):
    N = par[0]
    m = par[1]
    s = par[2]

    try:
        chi2 = (x[0]-m)*(x[0]-m) / (s*s)

        return N / math.sqrt(2*math.pi*s*s) * math.exp(-0.5*chi2)
    except:
        return 0

# you can use https://en.wikipedia.org/wiki/Relativistic_Breit%E2%80%93Wigner_distribution
# with two free parameters: M and Gamma.
# You will need an additional one N for normalization like in the Gaussian
def bw(x,par):
    N = par[0]
    M = par[1]
    Gamma = par[2]

    try:
        gamma = math.sqrt(sq(M) * (sq(M) + sq(Gamma)))
        k = 2 * math.sqrt(2) * M * Gamma * gamma / (math.pi * math.sqrt(sq(M) + gamma))

        return N * k / (sq(sq(x[0]) - sq(M)) + sq(M) * sq(Gamma))
    except:
        return 0



mMin = 70.0e3
mMax = 130.0e3

yMin = -1.0e2
yMax = 18.0e3

# this removes the statics box from the plot
ROOT.gStyle.SetOptStat(0)

# Create a canvas to draw on later
canvas = ROOT.TCanvas("myCanvas", 'Analysis Plots', 200, 10, 1050, 750)
canvas.cd()

#open the input histogram
rootfile = ROOT.TFile.Open(sys.argv[1], "READ")
tmpHist = rootfile.Get("M")
tmpHist.SetStats(False)
tmpHist.GetXaxis().SetRangeUser(mMin,mMax)
tmpHist.GetYaxis().SetRangeUser(yMin, yMax)
tmpHist.Draw("h")

# Create a legend to label the different components of the plot
# https://root.cern.ch/doc/master/classTLegend.html
legend = ROOT.TLegend(0.12, 0.87, 0.3, 0.75)
legend.SetFillColor(0)
legend.SetLineColor(0)

# define a TF1 Gaussian according to our own python function gauss
# https://root.cern.ch/doc/master/classTF1.html
fGauss = ROOT.TF1("fGauss", gauss, mMin, mMax, 3)

fGauss.SetParameters(tmpHist.Integral(), 90.0e3, 4.0e3)

fGauss.SetLineColor(ROOT.kMagenta)
fGauss.SetNpx(10000) # sets the amount of sampling points in x range. Do not choose too small for convolution later on
legend.AddEntry(fGauss, "Gauss", "l")


# do the same thing for a Breit-Wigner distribution
fBw = ROOT.TF1("fBw", bw, mMin, mMax, 3)

# fBw.SetParameters(tmpHist.Integral(), 90.0e3, 2.0e3)
fBw.SetParameters(1.75e8, 90.0e3, 6.0e3)

fBw.SetLineColor(ROOT.kRed)
fBw.SetNpx(10000)
legend.AddEntry(fBw, "Breit-Wigner", "l")



# let root perform a convolution of the two functions. It does so by a Fourier transform
# need to set negative x minimum, because Gauss will be centered at 0 and the same range is used on both functions in the convolution
# in principle the order would not matter, but the fit will converge more easily if the distribution centered at 0 comes second
conv = ROOT.TF1Convolution(fBw, fGauss)
conv.SetRange(-20.e3,mMax)

# convert the TF1Convolution back into a regular TF1 to continue our fitting
# it now has 6 parameters: 0,1,2 from bw and 3,4,5 from gauss
# for the fitting it can make sense to fix some parameters. Both 
# parameters for the mean will shift the result along the x axis
# and both for the normalization will scale it along the y axis.
fConv = ROOT.TF1("fConv", conv, mMin, mMax, conv.GetNpar())
legend.AddEntry(fConv, "Convolution", "l")

fConv.SetParameter(0, tmpHist.Integral())
fConv.SetParameter(1, 90.0e3)
fConv.SetParameter(2, 6.0e3)
fConv.FixParameter(3,1.0) # this would be the normalization of the gauss
fConv.FixParameter(4,0.0) # this would be the mean of the gauss
fConv.SetParameter(5, 4.0e3)



tmpHist.SetLineWidth(3)
tmpHist.Draw("E")

tmpHist.Fit("fGauss")
print ("chi2/NDF = %f / %f = %f")%(fGauss.GetChisquare(), fGauss.GetNDF(), fGauss.GetChisquare()/fGauss.GetNDF())
fGauss.Draw("SAME")

tmpHist.Fit(fBw)
fBw.Draw("SAME")

tmpHist.Fit(fConv)
fConv.Draw("SAME")


tex = ROOT.TLatex(); tex.SetNDC(True); tex.SetTextSize(0.025); tex.SetTextColor(ROOT.kBlack)

tex.DrawLatex(0.70, 0.85, "Gauss Fit")
tex.DrawLatex(0.70, 0.80, "M_{Z} = (%.3f #pm %.3f) GeV" %  (fGauss.GetParameter(1) * 1e-3, fGauss.GetParError(1) * 1e-3))
tex.DrawLatex(0.70, 0.75, "#sigma = (%.3f #pm %.3f) GeV" % (fGauss.GetParameter(2) * 1e-3, fGauss.GetParError(2) * 1e-3))
tex.DrawLatex(0.70, 0.70, "#chi^{2}_{red} = %.1f" %  (fGauss.GetChisquare() / fGauss.GetNDF()))


tex.DrawLatex(0.70, 0.60, "Breit-Wigner Fit")
tex.DrawLatex(0.70, 0.55, "M_{Z} = (%.3f #pm %.3f) GeV" % (fBw.GetParameter(1) * 1e-3, fBw.GetParError(1) * 1e-3))
tex.DrawLatex(0.70, 0.50, "#Gamma = (%.3f #pm %.3f) GeV" % (fBw.GetParameter(2) * 1e-3, fBw.GetParError(2) * 1e-3))
tex.DrawLatex(0.70, 0.45, "#chi^{2}_{red} = %.1f" %  (fBw.GetChisquare() / fBw.GetNDF()))


tex.DrawLatex(0.70, 0.40, "Convolution Fit")
tex.DrawLatex(0.70, 0.35, "M_{Z} = (%.3f #pm %.3f) GeV" % (fConv.GetParameter(1) * 1e-3, fConv.GetParError(1) * 1e-3))
tex.DrawLatex(0.70, 0.30, "#Gamma = (%.3f #pm %.3f) GeV" % (fConv.GetParameter(2) * 1e-3, fConv.GetParError(2) * 1e-3))
tex.DrawLatex(0.70, 0.25, "#chi^{2}_{red} = %.1f" %  (fConv.GetChisquare() / fConv.GetNDF()))

legend.AddEntry(tmpHist, "Data")
legend.Draw("SAME")        


canvas.Update()      
canvas.SaveAs("fits.png")
ROOT.TPython.Prompt()  

rootfile.Close()
