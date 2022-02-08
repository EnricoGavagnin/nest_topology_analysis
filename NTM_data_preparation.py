# NTM_data preparation

# Created by Enrico Gavagnin 17/01/2022

# %%
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import seaborn as sns
import py_fort_myrmidon as fm
from circular_hist import circular_hist
from angles import normalize
from prime_generator import nth_prime_number
import datetime
import scipy.sparse as sparse
from matplotlib.colors import ListedColormap
import networkx as nx
import community
import statistics

# link to folder with data and myrmidon files
working_dir = '/media/eg15396/EG_DATA-2/NTM/'
#working_dir = '/home/eg15396/Documents/Data/NTM/'
#working_dir = '/home/eg15396/Documents/Data/Adriano/'

# name auto-oriented myrmidon file
auto_orient = 'NTM_s27_auto_orient.myrmidon'
#auto_orient = 'R3SP_13-03-21_automatically_oriented.myrmidon'

# name auto-oriented myrmidon file
manual_orient = 'NTM_s27_man_orient.myrmidon'
#manual_orient = 'R3SP_13-03-21_Capsule_Zones_defined.myrmidon'

# plot scale factor
plt_sf = 1

box_name = ''

frm_rate = 6
# % Load experiment

# open experiments
e_auto = fm.Experiment.Open(working_dir + auto_orient)
e_manual = fm.Experiment.Open(working_dir + manual_orient)

# open ants
ants_auto = e_auto.Ants
ants_manual = e_manual.Ants

N_ants = len(ants_auto)


# start and end time of data processing
start = fm.Query.GetDataInformations(e_manual).Start.Add(fm.Duration(0*3600*10**9))
end = start.Add(fm.Duration(2*3600*10**9))
#end = fm.Query.GetDataInformations(e_manual).End


#%%

# treshold of minimum number of ants (otherwise treat as skipped frame)
tresh = N_ants * 0.7

# Read number of detected ants in each frame
frames = pd.DataFrame.from_dict({fm.Time.ToDateTime(frm.FrameTime): len(frm.Positions) if len(frm.Positions) > tresh else np.nan 
                                 for frm in fm.Query.IdentifyFrames(e_auto,start=start,end=end)
                                 }, orient='index').reset_index().rename(columns={0: "detection", 'index': "time"})


# moving avarege 
win_size = 6*60*10 
frames['detection_MA'] = frames['detection'].rolling(win_size, min_periods=round(win_size*0.8), center=True).mean()

#%%
fig = plt.figure(figsize=(8,6),dpi=144)
ax = fig.add_subplot(111)
ax2 = ax.twinx()
colors = sns.color_palette()

sns.lineplot(data=frames, x='time', y='detection', color=colors[0], ax=ax)
sns.lineplot(data=frames, x='time', y='detection_MA', color=colors[1], ax=ax2)
fig.legend(['Detection', 'moving_avarege'],loc="upper left", bbox_to_anchor=(0.01, 0.95), bbox_transform=ax.transAxes)
ax.grid(axis='both', lw=0.5)

#plt.xlim([362000,372500])























