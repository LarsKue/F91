
# random canvas ID:
import random

import ROOT

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def list_product(l):
    rv = 1
    for x in l:
        rv *= x
    return rv


class EventData(object):
    def __init__(self, chain):
        self.chain = chain
        self.data = []
        self.index = 0
    
    def acquire_entries(self, entries=None):
        if entries is None:
            entries = range(self.chain.GetEntriesFast())
        
        for i in entries:
            if i % 10000 == 0:
                print 100.0 * (i - entries[0]) / len(entries), r"% complete."
            
            self.data.append(Entry(self.chain, i))
        
        return self
    
    def plot(self, variable, title, xlabel, ylabel, bins, xmin, xmax):
        pass
    
    def filter(self, selector):
        self.data = filter(selector, self.data)
    
    def __iter__(self):
        return self
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value
    
    def __len__(self):
        return len(self.data)
    
    def next(self):
        if self.index >= len(self.data):
            raise StopIteration
        rv = self.data[self.index]
        self.index += 1
        return rv
        


class Entry(object):
    def __init__(self, chain, entry):
        self.entry = entry
        chain.GetEntry(entry)
        self.lep_pt = chain.lep_pt
        self.lep_eta = chain.lep_eta
        self.lep_phi = chain.lep_phi
        self.lep_E = chain.lep_E
        self.lep_n = chain.lep_n
        self.trigE = chain.trigE
        self.trigM = chain.trigM
        self.passGRL = chain.passGRL
        self.hasGoodVertex = chain.hasGoodVertex
        self.lep_charge = chain.lep_charge
        self.lep_ptcone30 = chain.lep_ptcone30
        self.lep_etcone20 = chain.lep_etcone20
        self.lep_type = chain.lep_type
        self.lep_flag = chain.lep_flag
            

class Plot(object):
    def __init__(self, chain, name, is_list, title, xlabel, ylabel, bins, xmin, xmax):
        self.chain = chain
        self.name = name
        self.is_list = is_list
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.bins = bins
        self.xmin = xmin
        self.xmax = xmax
        self.data = []
        self.total_entries = 0

        if self.is_list:
            self.hist = []
        else:
            self.hist = ROOT.TH1D(self.name, self.title + ";" + self.xlabel + ";" + self.ylabel, self.bins, self.xmin, self.xmax)

    def acquire_entries(self, num_entries=-1, selector=None, weight=None):
        if num_entries < 0:
            num_entries = self.chain.GetEntriesFast()

        self.total_entries = num_entries
        for jentry in range(0, num_entries):
            if jentry % 100000 == 0:
                print 100 * jentry / num_entries, r"% complete."

            nb = self.chain.GetEntry(jentry)
            # print "nb:", nb
            if nb <= 0:
                continue

            if weight is None:
                _weight = 1
            else:
                _weight = self.chain.__getattr__(weight)

            data_item = self.chain.__getattr__(self.name)
            if selector is not None:
                data_item = selector(data_item, self.chain)
                if data_item is None:
                    continue

            if not self.is_list:
                self.data.append(data_item)
                self.hist.Fill(data_item, _weight)
            else:
                self.data.append(list(data_item))
                for i, item in enumerate(data_item):
                    if i == len(self.hist):
                        self.hist.append(ROOT.TH1D(self.name + str(i), self.title + ";" + self.xlabel + ";" + self.ylabel, self.bins, self.xmin, self.xmax))
                    self.hist[i].Fill(item, _weight)

    def acquire_from_data(self, data):
        self.data = data
        weight = 1
        for item in data:
            self.hist.Fill(item, weight)


    def acquire_from_dict(self, dict):
        weight = 1
        self.data = []
        for key, value in dict.items():
            for _ in range(value):
                self.data.append(key)
                self.hist.Fill(key, weight)


    def draw(self, which=None):
        canvas = ROOT.TCanvas("".join([chr(random.randint(ord('a'), ord('z'))) for _ in range(512)]), 'Analysis Plots', 200, 10, 700, 500)
        canvas.cd()
        if self.is_list and which is None:
            for histogram in self.hist:
                histogram.Draw("h")
        elif self.is_list:
            for i in which:
                self.hist[i].Draw("h")
        else:
            self.hist.Draw("h")

    def draw_and_save(self, filepath, which=None, log_scale=(0,0)):
        canvas = ROOT.TCanvas("".join([chr(random.randint(ord('a'), ord('z'))) for _ in range(512)]), 'Analysis Plots', 200, 10, 700, 500)
        canvas.SetLogx(log_scale[0])
        canvas.SetLogy(log_scale[1])
        canvas.cd()
        if self.is_list and which is None:
            for histogram in self.hist:
                histogram.Draw("h")
        elif self.is_list:
            for i in which:
                self.hist[i].Draw("h")
        else:
            self.hist.Draw("h")

        canvas.SaveAs(filepath)

    def add_histogram(self, histogram):
        if self.is_list:
            self.hist.append(histogram)
        else:
            self.hist = [self.hist, histogram]

