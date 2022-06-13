#Open Experiment

rm(list=ls())

######load necessary libraries
library(FortMyrmidon) 
library(Rcpp)
library(circular)
library(R.utils)

tracking_data <- fmExperimentOpen('/media/eg15396/EG_DATA-7/NTM/EG_NTM_s13_DEHa.myrmidon')
