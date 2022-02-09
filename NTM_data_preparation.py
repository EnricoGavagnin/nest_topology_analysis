# NTM_data preparation

# Created by Enrico Gavagnin 17/01/2022

# %%
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import seaborn as sns
import py_fort_myrmidon as fm
from circular_hist import circular_hist
import datetime
import networkx as nx
import community
import statistics
import scipy.stats as stats
from unidip import UniDip

# link to folder with data and myrmidon files
working_dir = '/media/eg15396/EG_DATA-2/NTM/'
#working_dir = '/home/eg15396/Documents/Data/NTM/'


# summary of detection analysis
detection_data = dict()

# name auto-oriented myrmidon file
myrm_list = ['NTM_s28_auto_orient.myrmidon','NTM_s21_auto_orient.myrmidon']

for myrm_file in myrm_list:
    
    # open experiments
    exp = fm.Experiment.Open(working_dir + myrm_file)
    
    # open ants
    ants = exp.Ants
    N_ants = len(ants)
    
    # start and end time of data processing
    start = fm.Query.GetDataInformations(exp).Start
    end = start.Add(fm.Duration(4*3600*10**9))
    #end = fm.Query.GetDataInformations(exp).End
    
    
    #
    
    # treshold of minimum number of ants (otherwise treat as skipped frame)
    tresh = N_ants * 0.2
    
    # Read number of detected ants in each frame
    frames = pd.DataFrame.from_dict({fm.Time.ToDateTime(frm.FrameTime): len(frm.Positions) if len(frm.Positions) > tresh else np.nan 
                                     for frm in fm.Query.IdentifyFrames(exp,start=start,end=end)
                                     }, orient='index').reset_index().rename(columns={0: "detection", 'index': "time"})
    
    # moving avarege 
    win_size = 6*60*10 
    frames['detection_MA'] = frames['detection'].rolling(win_size, min_periods=round(win_size*0.8), center=True).mean()
    
    # %
    # sns.lineplot(x='time', y='value', hue='variable', data=pd.melt(frames, ['time']))
    # plt.grid(visible=True)
    
    # fig = plt.figure(figsize=(8,6),dpi=144)
    # frames.detection_MA.hist(bins=100)
    
    intervals = UniDip(frames.detection_MA.iloc[::6*60].dropna(), mrg_dst = 7).run()
    
    detection_data[myrm_file] = [len(intervals), frames.iloc[::6*60,0:2]]








