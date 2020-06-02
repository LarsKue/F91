import os

base_path = "../fp/data/"
data_path = base_path + "Data/"
mc_path = base_path + "MC/"

file_type = ".root"

data_files = ["DataEgamma"]
mc_files = ["mc_147770.Zee"]

for df in data_files:
    os.system("python eventloop.eff.py -f " + data_path + df + file_type)

for mcf in mc_files:
    os.system("python eventloop.eff.py -f " + mc_path + mcf + file_type + " -mc")
