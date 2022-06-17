#Open Experiment

rm(list=ls())

######load necessary libraries
library(FortMyrmidon) 
library(Rcpp)
library(circular)
library(R.utils)

e <- fmExperimentOpen('/media/eg15396/EG_DATA-7/NTM/EG_NTM_s13_DEHa.myrmidon')
time_start <- fmTimeParse("2021-09-12T11:00:00Z")
time_stop <- fmTimeParse("2021-09-12T14:00:00Z")
int <- interaction_detection(e, time_start, time_stop, max_time_gap = 10, max_distance_moved = 201)
write.csv(int,'/home/eg15396/Documents/GitHub/auto_vs_manual_orientation_check/matcher_test_data.csv', row.names = TRUE)
