# README - Data Analysis

This folder contains a series of scripts and notebook to perform the data post-processing and data analysis of the Nest Topology Manipulation (NTM) experiments. 

## Post-processing

### Requirements
Post-processing requires the folowing software to be installed:

* [Fort-myrmidon](https://anaconda.org/formicidae-tracker/libfort-myrmidon)
* [Fort-Studio (v0.8.3)](https://github.com/formicidae-tracker/myrmidon) 
* [Fort-myrmidon R-bindings](https://anaconda.org/formicidae-tracker/r-fort-myrmidon) 

The post-processing is performed using R and Fort-Studio and consists of the following steps:

* For each tracking box used (Esterhase, Leamas, Polyakov and Karla), manually create a myrmidon file with manually oriented ants. These files can be found in the data HHD with names **"manual_ref_*name_tracking_box*.myrmidon"**. The capsule definition can be cloned from one myrmidon file to an other by using the R script "clone_capsule_manual_to_manual_R".

* For all the traxking data in the HDD, automatically create a myrmidon file, create ant identities and assign capsule and automatically orient tags based on the ant trajectories. This can be doen using the script **"auto_orientation_loop.R"**

## Data Analysis

The data analysis is performed in Python as Jupyter notebooks and comprises four fundamental parts:

1. Create social interaction network from raw data on collision
2. Compute network properties for each social network
3. Perform statistical analysis on the properties of interest 
4. Visualise the results by plotting relevant distributions

These four parts are performed in two steps. Step 1 and step 2 are performed in the notebook **"Data_analysis_complete_(social_net&prop).ipynb"**. Steps 3 and 4 are performed in **"Data_analysis_complete_(stats&plotting).ipynb"**.


### Requirements
The data analysis requires the following software to be installed: 

* [Fort-myrmidon](https://anaconda.org/formicidae-tracker/libfort-myrmidon)
* [Fort-myrmidon Python-bindings](https://anaconda.org/formicidae-tracker/py-fort-myrmidon) (only for **"Data_analysis_complete_(social_net&prop).ipynb"**)

