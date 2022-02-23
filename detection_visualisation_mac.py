# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import seaborn as sns
import datetime
import networkx as nx
from os import listdir
import pickle

# %%


# Save
# a_file = open("detection_data.pkl", "wb")
# pickle.dump(detection_data, a_file)
# a_file.close()


# Open
a_file = open("detection_data_1-32.pkl", "rb")
data = pickle.load(a_file)



# %% PLOT


for rep in data:
    #rep = 'EG_NTM_s23_DENb.myrmidon'
    print(rep)
    sns.set(font_scale = 0.8)
    sns.lineplot(data=data[rep][1], x='time', y='detection')
    plt.xticks(rotation=45)
    plt.title(rep[7:15] + ' - modes = ' + str(data[rep][0]))
    plt.tight_layout()
    plt.savefig('plots/detection_analysis/'+  rep[7:15] + '.png', dpi=190)
    plt.close()