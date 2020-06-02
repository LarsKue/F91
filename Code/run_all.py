import os

base_path = "../fp/data/"
data_path = base_path + "Data/"
mc_path = base_path + "MC/"

file_type = ".root"

data_files = {"DataEgamma": "e", "DataMuons": "m"}
mc_files = {"mc_147770.Zee": "e", "mc_147771.Zmumu": "m", "mc_147772.Ztautau": "t"}

# for df, tp in data_files.items():
#     os.system("python eventloop.py -f " + data_path + df + file_type + " -p " + df + " -t " + tp)

for mcf, tp in mc_files.items():
    os.system("python eventloop.py -f " + mc_path + mcf + file_type + " -p " + mcf + " -t " + tp + " -mc")
