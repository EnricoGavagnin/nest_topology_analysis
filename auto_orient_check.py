# Auto vs manual orientation check

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
#working_dir = '/media/eg15396/EG_DATA-2/NTM/'
working_dir = '/home/eg15396/Documents/Data/NTM/'
#orking_dir = '/home/eg15396/Documents/Data/Adriano/'

# name auto-oriented myrmidon file
auto_orient = 'NTM_s30_auto_orient.myrmidon'
#auto_orient = 'R3SP_13-03-21_automatically_oriented.myrmidon'

# name auto-oriented myrmidon file
manual_orient = 'NTM_s30_man_orient.myrmidon'
#manual_orient = 'R3SP_13-03-21_Capsule_Zones_defined.myrmidon'


# % Load experiment

# open experiments
e_auto = fm.Experiment.Open(working_dir + auto_orient)
e_manual = fm.Experiment.Open(working_dir + manual_orient)

# open ants
ants_auto = e_auto.Ants
ants_manual = e_manual.Ants

N_ants = len(ants_auto)

#%% Tag Angle

# save tag-position angles
angles_auto = [ants_auto[a].Identifications[0].AntAngle for a in ants_auto]
angles_manual = [ants_manual[a].Identifications[0].AntAngle for a in ants_manual]

# compute angles errors module [-pi, pi)
angles_err = [normalize(angles_auto[i] - angles_manual[i], -np.pi, np.pi) for i in range(len(angles_manual))]

# plot angles difference
ax = circular_hist(angles_err, title='Tag-position angle error\n (leamas)')


# %% Ant offset

# save offest from tag reference
offset_auto_tag = [ants_auto[a].Identifications[0].AntPosition for a in ants_auto]
offset_manual_tag = [ants_manual[a].Identifications[0].AntPosition for a in ants_manual]

# compute offset from ant refence 
offset_manual_ant = np.array([np.array([offset_manual_tag[i][0]*np.cos(-angles_manual[i])-
                                        offset_manual_tag[i][1]*np.sin(-angles_manual[i]),
                                        offset_manual_tag[i][0]*np.sin(-angles_manual[i])+
                                        offset_manual_tag[i][1]*np.cos(-angles_manual[i])]) for i in range(len(angles_manual))])
offset_auto_ant = np.array([np.array([offset_auto_tag[i][0]*np.cos(-angles_auto[i])-
                                      offset_auto_tag[i][1]*np.sin(-angles_auto[i]),
                                      offset_auto_tag[i][0]*np.sin(-angles_auto[i])+
                                      offset_auto_tag[i][1]*np.cos(-angles_auto[i])]) for i in range(len(angles_manual))])

# compute offset error from the ant reference
offset_err = np.array([offset_auto_ant[i] - offset_manual_ant[i] for i in range(len(angles_manual))])

# plot offset error
data = pd.DataFrame({
    'x-offset (pixel)': offset_err[:,0],
    'y-offset (pixel)': offset_err[:,1],})
lim = np.max(abs(offset_err))*1.1
ax1 = sns.jointplot(data=data,x='x-offset (pixel)',y='y-offset (pixel)', xlim=(-lim,lim), ylim=(-lim,lim))
plt.text(0.8*lim,-0.9*lim,'y-mean={:.2f}\n'.format(offset_err[:,1].mean()) + 'y-var={:.2f}'.format(offset_err[:,1].var()), rotation=-90)
plt.text(-2.5*lim,1.3*lim,'x-mean={:.2f}\n'.format(offset_err[:,0].mean()) + 'x-var={:.2f}'.format(offset_err[:,0].var()))


# %% Ant length

# read length of ants in pixel
length_pxl_manual = {a: np.mean([fm.Query.ComputeMeasurementFor(e_manual,antID=ants_manual[a].ID,measurementTypeID=1)[i].LengthPixel for i in range(2)])  for a in ants_manual}

# plot ant length distribution
ax2 = sns.histplot(length_pxl_manual)
ax2.set(xlabel='Head-Tail measurement (pixel)', ylabel='count')
plt.text(170,30,'mean={:.1f}\n'.format(np.mean(list(length_pxl_manual.values()))) + ' var={:.1f}\n'.format(np.var(list(length_pxl_manual.values()))))


# %% Collision pattern

# start and end time of interaction computed
start = fm.Query.GetDataInformations(e_manual).Start.Add(fm.Duration(23*3600*10**9))
end = start.Add(fm.Duration(2*3600*10**9))

#%%
# compute ant interaction
#[trj_man, coll_list_manual] = fm.Query.ComputeAntInteractions(e_manual, start=start, end=end)
#[trj_auto, coll_list_auto] = fm.Query.ComputeAntInteractions(e_auto, start=start, end=end)


# copute interactions per each frame coll_frame
# access via coll_frame[#frame_num][1].Collisions[#interaction_num].IDs
# interaction between ID1 and ID2 is uniquily represented as ID1 * 10*4 + ID2
coll_frame_manual = [[i.IDs[0] * 10**4 + i.IDs[1] for i in frame[1].Collisions] for frame in fm.Query.CollideFrames(e_manual,start=start,end=end)]
coll_frame_auto = [[i.IDs[0] * 10**4 + i.IDs[1] for i in frame[1].Collisions] for frame in fm.Query.CollideFrames(e_auto,start=start,end=end)]

#compute difference
coll_m_a = [list(set.difference(set(coll_frame_manual[f]),set(coll_frame_auto[f]))) for f in range(len(coll_frame_auto))]
coll_a_m = [list(set.difference(set(coll_frame_auto[f]),set(coll_frame_manual[f]))) for f in range(len(coll_frame_auto))]
coll_aum = [list(set.union(set(coll_frame_manual[f]),set(coll_frame_auto[f]))) for f in range(len(coll_frame_auto))]

coll_relative_err = [100 * (len(coll_m_a[i]) + len(coll_a_m[i])) / len(coll_aum[i]) for i in range(len(coll_aum)) if len(coll_aum[i])>0]


# %% plot ant length distribution
ax = sns.histplot(coll_relative_err,bins=50)
ax.set(xlabel='Mismatched interactions per frame (%)', ylabel='frames')
plt.title(' from: ' + str(start) + '\n to: ' +str(end) + '\n mean={:.1f}, '.format(np.mean(coll_relative_err)) + ' var={:.1f} '.format(np.var(coll_relative_err)))

# %% Correlation ant length and collision mismatch

# collision detection scores per individual ants
# List of all interactions, grouped by manual\auto, auto\manual and manual U auto
all_coll_m_a = [item for sublist in coll_m_a for item in sublist]
all_coll_a_m = [item for sublist in coll_a_m for item in sublist]
all_coll_aum = [item for sublist in coll_aum for item in sublist]


##  to do==> run the following for loop throught the all_init_* lists
coll_ant = {id:[((np.array(all_coll_m_a) // 10**4)==id).sum() + ((np.array(all_coll_m_a) % 10**4)==id).sum(), # number of interactions in manual, but not in auto
                ((np.array(all_coll_a_m) // 10**4)==id).sum() + ((np.array(all_coll_a_m) % 10**4)==id).sum(), # number of interactions in auto, but not in manual
                ((np.array(all_coll_aum) // 10**4)==id).sum() + ((np.array(all_coll_aum) % 10**4)==id).sum()]       # number of interactions in both auto and manual
           for id in range(1,len(ants_auto)+1)}


# compute relative detection in auto and manual
coll_ant_relative_err = pd.DataFrame([[ant, 100 * coll_ant[ant][0] / coll_ant[ant][2], 100 * coll_ant[ant][1] / coll_ant[ant][2], length_pxl_manual[ant]] for ant in coll_ant if coll_ant[ant][2]>0], columns=['ID', 'manual_collisions (%)', 'auto_collisions (%)', 'HT-length (pixels)'])

# scatter plot with color gradient as HT length
fig, ax = plt.subplots()
sns.set(font_scale = 2)
sns.scatterplot(data=coll_ant_relative_err, x='manual_collisions (%)',y='auto_collisions (%)',hue='HT-length (pixels)', s=120, palette=('rocket'), ax=ax)
ax.set(ylim=(0,None), xlim=(0,None))
plt.title(' from: ' + str(start) + '\n to: ' +str(end) )

# add colorbar
norm = plt.Normalize(coll_ant_relative_err['HT-length (pixels)'].min(), coll_ant_relative_err['HT-length (pixels)'].max())
sm = plt.cm.ScalarMappable(cmap="rocket", norm=norm)
sm.set_array([])

# Remove the legend and add a colorbar
ax.get_legend().remove()
cax = fig.add_axes([0.27, 0.8, 0.5, 0.05])
ax.figure.colorbar(sm, shrink=0.8, label='HT-length (pixels)', cax=cax,orientation='horizontal')


# %% Interaction comparison

# start and end time of interaction computed
start = fm.Query.GetDataInformations(e_manual).Start.Add(fm.Duration(23*3600*10**9))
end = start.Add(fm.Duration(0.5*3600*10**9))


# Dictionary to convert timestamp of frame into corresponding frame number starting from 1 (with frame#1 at 'start' time)
TimeToFrame = {fm.Time.ToTimestamp(frm[0].FrameTime): i + 1 for i,frm in enumerate(fm.Query.CollideFrames(e_manual,start=start,end=end))}
N_frm = len(TimeToFrame)

# maximum gap (s) for interaction computation
max_gap = 20
int_err_per_frame = []

for mg_i, max_gap in enumerate(range(1,200,3)):
    print(max_gap)

    # pointer to list of all the possible ids pairs ordered 
    ids_pairs = [id1*10**4 + id2 for id1 in range(1,len(ants_auto)) for id2 in range(id1 + 1,len(ants_auto) + 1)]
    ids_pairs = {k: i for i,k in enumerate(ids_pairs)} #NOT VERY NICE!! YOU CAN DO THIS IN ONE GO WITH PREVIOUS LINE (TO DO)
    
    
    # inisialize interaction matrix each rows represent a binary array, one for each ids pairs, with 1s on the interactions and 0s elsewhere
    int_mat_manual = np.zeros((len(ids_pairs), N_frm + 2), dtype=bool)
    int_mat_auto = np.zeros((len(ids_pairs), N_frm + 2), dtype=bool)
    
    
    # Manual              <---- to improve: merge in one for loop!!
    for i in fm.Query.ComputeAntInteractions(e_manual,start=start,end=end,maximumGap=fm.Duration(max_gap*10**9))[1]:
        ids = i.IDs[0]*10**4 + i.IDs[1]
        int_mat_manual[ids_pairs[ids]] += np.concatenate([np.zeros((1,TimeToFrame[fm.Time.ToTimestamp(i.Start)])), 
                                                   np.ones((1,TimeToFrame[fm.Time.ToTimestamp(i.End)] - TimeToFrame[fm.Time.ToTimestamp(i.Start)] + 1)),
                                                   np.zeros((1,N_frm - TimeToFrame[fm.Time.ToTimestamp(i.End)] + 1))], 1)[0].astype(bool)
    
    # Auto
    for i in fm.Query.ComputeAntInteractions(e_auto,start=start,end=end,maximumGap=fm.Duration(max_gap*10**9))[1]:
        ids = i.IDs[0]*10**4 + i.IDs[1]
        int_mat_auto[ids_pairs[ids]] += np.concatenate([np.zeros((1,TimeToFrame[fm.Time.ToTimestamp(i.Start)])), 
                                                   np.ones((1,TimeToFrame[fm.Time.ToTimestamp(i.End)] - TimeToFrame[fm.Time.ToTimestamp(i.Start)] + 1)),
                                                   np.zeros((1,N_frm - TimeToFrame[fm.Time.ToTimestamp(i.End)] + 1))], 1)[0].astype(bool)
        
    int_mat_err = sparse.csr_matrix(int_mat_manual.astype(int) - int_mat_auto.astype(int))
    
    int_err_per_frame.append([(int_mat_err==1).sum() / N_frm, (int_mat_err==-1).sum() / N_frm])


# %% plot interaction matrix
# max interaction to show
ylim = 2000

# show yticks every
ytick_span = 70
plt.imshow(200*int_mat_auto[:ylim,:], cmap='cividis')
plt.grid(None)
plt.xlabel('Frame')
plt.ylabel('ant_pair')
plt.title('AUTO - max gap = ' + str(max_gap) + 's \n from: ' + str(start) + '\n to: ' +str(end) )
plt.yticks(range(0, ylim, ytick_span), ['(' + str(ids // 10**4) + ', ' + str(ids % 10**4) + ')' for ids in ids_pairs][:ylim:ytick_span])


# %% plot interaction patter error
# max interaction to show
ylim = 2000

# show yticks every
ytick_span = 70
plt.imshow(200*int_mat_err[:ylim,:4000], cmap='cividis')
plt.grid(None)
plt.xlabel('Frame')
plt.ylabel('ant_pair')
plt.title('DIFFERENCE - max gap = ' + str(max_gap) + 's \n from: ' + str(start) + '\n to: ' +str(end) )
plt.yticks(range(0, ylim, ytick_span), ['(' + str(ids // 10**4) + ', ' + str(ids % 10**4) + ')' for ids in ids_pairs][:ylim:ytick_span])



# %% CUMULATIVE NETWORK VISUAL COMPARISON

# ------- parameters -----------

# cumulative time window (s)
time_win = 60 * 30

# maximum gap (s) for interaction computation
max_gap = 20

# minimum cumulative interaction duration (s)
min_cum_duration = 100

# -----------------------------



# start and end time of interaction computed
start = fm.Query.GetDataInformations(e_manual).Start.Add(fm.Duration(23*3600*10**9))
end = start.Add(fm.Duration(time_win * 10**9))

# Dictionary to convert timestamp of frame into corresponding frame number starting from 1 (with frame#1 at 'start' time)
TimeToFrame = {fm.Time.ToTimestamp(frm[0].FrameTime): i + 1 for i,frm in enumerate(fm.Query.CollideFrames(e_manual,start=start,end=end))}
N_frm = len(TimeToFrame)

#initialise adj-matrix
adj_manual = np.zeros((N_ants, N_ants))
adj_auto = np.zeros((N_ants, N_ants))


# Manual
for i in fm.Query.ComputeAntInteractions(e_manual,start=start,end=end,maximumGap=fm.Duration(max_gap*10**9))[1]:
    adj_manual[i.IDs[0]-1, i.IDs[1]-1] += TimeToFrame[fm.Time.ToTimestamp(i.End)] - TimeToFrame[fm.Time.ToTimestamp(i.Start)]

# Auto
for i in fm.Query.ComputeAntInteractions(e_auto,start=start,end=end,maximumGap=fm.Duration(max_gap*10**9))[1]:
    adj_auto[i.IDs[0]-1, i.IDs[1]-1] += TimeToFrame[fm.Time.ToTimestamp(i.End)] - TimeToFrame[fm.Time.ToTimestamp(i.Start)]

# trimming 
adj_manual[adj_manual < min_cum_duration] = 0
adj_auto[adj_auto < min_cum_duration] = 0

# network build
G_manual = nx.Graph(adj_manual)
G_auto = nx.Graph(adj_auto)

# select connencted components
Gcc_manual = sorted(nx.connected_components(G_manual), key=len, reverse=True)
Gcc_auto = sorted(nx.connected_components(G_auto), key=len, reverse=True)

GC_manual = G_manual.subgraph(Gcc_manual[0])
GC_auto = G_auto.subgraph(Gcc_auto[0])


#%% PLOTTING network comparison
# starting node position for spring layout
start_pos = nx.random_layout(G_manual)

# manual 
pos = nx.spring_layout(GC_manual,  iterations=100, pos=start_pos)
ax = plt.subplot(121)
nx.draw(GC_manual, ax=ax, pos=pos)
plt.title('MANUAL - CC = ' +str(len(Gcc_manual)))


# auto
pos = nx.spring_layout(GC_auto,  iterations=100, pos=start_pos)
ax = plt.subplot(122)
nx.draw(GC_auto, ax=ax, pos=pos)
plt.title('AUTO - CC = ' +str(len(Gcc_auto)))

plt.suptitle('max gap = ' + str(max_gap) + 's, min edge = ' +str(min_cum_duration) + 's  \n from: ' + str(start) + '\n to: ' +str(end))

# %% CUMULATIVE NETWORK PROPERTIES COMPARISON

# ------- parameters -----------

# cumulative time window (s)
time_win = 60 * 30

# number of networks computed
num_net = 20

# maximum gap (s) for interaction computation
max_gap = 20

# minimum cumulative interaction duration (frames)
min_cum_duration = 10*6

# -----------------------------

# properties dataframe
prop_df = pd.DataFrame(columns=[])

# start and end time of interaction computed
t0 = fm.Query.GetDataInformations(e_manual).Start.Add(fm.Duration(23*3600*10**9))


for net in range(num_net):
    start = t0.Add(fm.Duration(time_win * net * 10**9))

    end = t0.Add(fm.Duration(time_win * (net+1) * 10**9))

    # Dictionary to convert timestamp of frame into corresponding frame number starting from 1 (with frame#1 at 'start' time)
    TimeToFrame = {fm.Time.ToTimestamp(frm[0].FrameTime): i + 1 for i,frm in enumerate(fm.Query.CollideFrames(e_manual,start=start,end=end))}
    N_frm = len(TimeToFrame)

    #initialise adj-matrix
    adj_manual = np.zeros((N_ants, N_ants))
    adj_auto = np.zeros((N_ants, N_ants))


    # Manual
    for i in fm.Query.ComputeAntInteractions(e_manual,start=start,end=end,maximumGap=fm.Duration(max_gap*10**9))[1]:
        adj_manual[i.IDs[0]-1, i.IDs[1]-1] += TimeToFrame[fm.Time.ToTimestamp(i.End)] - TimeToFrame[fm.Time.ToTimestamp(i.Start)]

    # Auto
    for i in fm.Query.ComputeAntInteractions(e_auto,start=start,end=end,maximumGap=fm.Duration(max_gap*10**9))[1]:
        adj_auto[i.IDs[0]-1, i.IDs[1]-1] += TimeToFrame[fm.Time.ToTimestamp(i.End)] - TimeToFrame[fm.Time.ToTimestamp(i.Start)]
    
    # trimming 
    adj_manual[adj_manual < min_cum_duration] = 0
    adj_auto[adj_auto < min_cum_duration] = 0
    
    # network build
    G_manual = nx.Graph(adj_manual)
    G_auto = nx.Graph(adj_auto)
    
    # set attribute of inverse of cumulative weight (for path distance props)
    nx.set_edge_attributes(G_manual, {(i,j): 1/adj_manual[j,i] if adj_manual[j,i]>0 else 0 for i in range(len(adj_manual)) for j in range(i)}, 'inv_weight')
    nx.set_edge_attributes(G_auto, {(i,j): 1/adj_auto[j,i] if adj_auto[j,i]>0 else 0 for i in range(len(adj_auto)) for j in range(i)}, 'inv_weight')
    
    # select connencted components
    cc_manual = sorted(nx.connected_components(G_manual), key=len, reverse=True)
    cc_auto = sorted(nx.connected_components(G_auto), key=len, reverse=True)
    GC_manual = G_manual.subgraph(cc_manual[0])
    GC_auto = G_auto.subgraph(cc_auto[0])
    
    # save properties
    def G_prop(G,start,end,name):
        best_partition = community.best_partition(G,weight='weight', randomize=False)
        return {'type': name,
                'start': fm.Time.ToDateTime(start), 
                'end': end, 
                'MOD': community.modularity(best_partition, G), 
                '#part': np.max(list(best_partition.values())) + 1,
                'DEN': nx.density(G), 
                'wDIA': nx.diameter(G, e=nx.eccentricity(G, sp=dict(nx.shortest_path_length(G,weight='inv_weight')))), 
                'DIA': nx.diameter(G),
                'DEH': statistics.pvariance([G.degree(n) for n in G.nodes()])}
    
    prop_df = prop_df.append(G_prop(GC_manual, start, end, 'manual'), ignore_index=True)
    prop_df = prop_df.append(G_prop(GC_auto, start, end, 'auto'), ignore_index=True)

# NETWORK PROP PLOTTING
#%%%


sns.lineplot(data=prop_df, x="start", y="MOD", markers=True, hue='type', marker=True, style='type',markersize=20)
plt.title(' from: ' + str(start) + ',\n cumulated time : ' +str(time_win) + ' s, max_gap: ' + str(max_gap) + ' s, interaction tresh:'+str(min_cum_duration)+' s' )






























































