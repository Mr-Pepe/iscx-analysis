import pickle
import os
import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import svm

p_files_path = "../datasets/flows"
save_dir_path = "../datasets/flows"

paths = []
filenames = []

all_flows = []
labels = []
i_file = 0

for dirpath, dirnames, filenames in os.walk(p_files_path):
    for filename in filenames:
        path = os.path.join(dirpath, filename)

        with open(path, 'rb') as file:
            flows = pickle.load(file)



        for flow in flows:
            labels.append(i_file)
            all_flows.append(flow)



        i_file += 1


df = {'label': labels,
      'sip': [flow[0] for flow in all_flows],
      'dip': [flow[1] for flow in all_flows],
      'sport': [flow[2] for flow in all_flows],
      'dport': [flow[3] for flow in all_flows],
      'prot': [flow[4] for flow in all_flows]
      }

df = pd.DataFrame(df)
df = df[['label', 'sip', 'dip', 'sport', 'dport', 'prot']]

reduced_df = df[['sport', 'dport', 'prot']]





print("Test")
