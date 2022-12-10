rm(list=ls())

#"https://formicidae-tracker.github.io/myrmidon/latest/index.html"

######load necessary libraries
library(FortMyrmidon) ####R bindings
library(Rcpp)
library(circular)
library(R.utils)

###source C++ movement direction program
#sourceCpp("/home/eg15396/Documents/R_scripts/Automated_Ant_Orientation_Nathalie/Get_Movement_Angle.cpp")

### directory of data and myrmidon files
dir_data <- '/media/eg15396/EG_DATA-2/NTM/'

### tracking data folder name
#track_data_name <- 'EG_NTM_s30_MODa.0000'

### manually oriented myrmidon file name
defined_capsule_file <- 'manual_ref_leamas.myrmidon'

### automatically oriented myrmidon file name
no_capsule_file <- 'EG_NTM_s25_DEHb.myrmidon'

#################################################################################################################################################################################################################
###########STEP 1 - use manually oriented data to extract important information about AntPose and Capsules
###########          IN YOUR PARTICULAR SPECIES AND EXPERIMENTAL SETTINGS  
###########IMPORTANT: FOR THIS TO WORK YOU NEED TO HAVE DEFINED THE SAME CAPSULES WITH THE SAME NAMES ACROSS ALL YOUR MANUALLY ORIENTED DATA FILES
#################################################################################################################################################################################################################
#data_list         <- list ("/home/eg15396/Documents/Data/NTM/NTM_s30_auto_orient.myrmidon") ###here list all the myrmidon files containing oriented data
data_list         <- list (paste(dir_data,defined_capsule_file,sep=''))
oriented_metadata <- NULL
capsule_list <- list()
for (myrmidon_file in data_list){
  experiment_name <- unlist(strsplit(myrmidon_file,split="/"))[length(unlist(strsplit(myrmidon_file,split="/")))]
  oriented_data <- fmExperimentOpen(myrmidon_file)
  oriented_ants <- oriented_data$ants
  capsule_names <- oriented_data$antShapeTypeNames
  for (ant in oriented_ants){
    ###extract ant length and capsules
    ant_length_px <- mean(fmQueryComputeMeasurementFor(oriented_data,antID=ant$ID)$length_px)
    capsules      <- ant$capsules
    for (caps in 1:length(capsules)){
      capsule_name  <- capsule_names[[capsules[[caps]]$type]]
      capsule_coord <- capsules[[caps]]$capsule
      capsule_info <- data.frame(experiment = experiment_name,
                                 antID      = ant$ID,
                                 c1_ratio_x = capsule_coord$c1[1]/ant_length_px,
                                 c1_ratio_y = capsule_coord$c1[2]/ant_length_px,
                                 c2_ratio_x = capsule_coord$c2[1]/ant_length_px,
                                 c2_ratio_y = capsule_coord$c2[2]/ant_length_px,
                                 r1_ratio   = capsule_coord$r1[1]/ant_length_px,
                                 r2_ratio   = capsule_coord$r2[1]/ant_length_px
      )
      
      if (!capsule_name %in%names(capsule_list)){ ###if this is the first time we encounter this capsule, add it to capsule list...
        capsule_list <- c(capsule_list,list(capsule_info)) 
        if(length(names(capsule_list))==0){
          names(capsule_list) <- capsule_name
        }else{
          names(capsule_list)[length(capsule_list)] <- capsule_name
        }
      }else{###otherwise, add a line to the existing dataframe within capsule_list
        capsule_list[[capsule_name]] <- rbind(capsule_list[[capsule_name]] , capsule_info)
      }
    }
    
    
    ###extract offset btewen tag centre and ant centre
    for (id in ant$identifications){
      oriented_metadata <- rbind(oriented_metadata,data.frame(experiment       = experiment_name,
                                                              antID            = ant$ID,
                                                              tagIDdecimal     = id$tagValue,
                                                              angle            = id$antAngle,
                                                              x_tag_coord      = id$antPosition[1], 
                                                              y_tag_coord      = id$antPosition[2],
                                                              x_ant_coord      = id$antPosition[1]*cos(-id$antAngle) - id$antPosition[2]*sin(-id$antAngle),
                                                              y_ant_coord      = id$antPosition[1]*sin(-id$antAngle) + id$antPosition[2]*cos(-id$antAngle),
                                                              length_px        = ant_length_px,
                                                              stringsAsFactors = F))
    }
  }
}

### Measures of mean ant length and offset between tag centre and ant centre will be heavily influenced by the queen #########
### So we need to remove the queen from the computation
### One way of doing so is to find and remove outliers in the ant length measure (provided there is enough variation between queen and worker size)
interquartile_range <- quantile(oriented_metadata$length_px,probs=c(0.25,0.75))
outlier_bounds      <- c(interquartile_range[1]-1.5*(interquartile_range[2]-interquartile_range[1]),interquartile_range[2]+1.5*(interquartile_range[2]-interquartile_range[1]))
###apply outlier exclusion to oriented_metadata...
oriented_metadata <- oriented_metadata[which(oriented_metadata$length_px>=outlier_bounds[1]&oriented_metadata$length_px<=outlier_bounds[2]),]  
###...and to capsule list
for (caps in 1:length(capsule_list)){
  capsule_list[[caps]] <-capsule_list[[caps]] [ as.character(interaction(capsule_list[[caps]] $experiment,capsule_list[[caps]] $antID))%in%as.character(interaction(oriented_metadata $experiment,oriented_metadata $antID)),]
}

for (caps in 1:length(capsule_list)){
  capsule_list[[caps]] <- colMeans(capsule_list[[caps]][,which(grepl("ratio",names(capsule_list[[caps]])))])
}



# open tracking data which need new capsule
tracking_data <- fmExperimentOpen(paste(dir_data,no_capsule_file,sep='')) 
ants <- tracking_data$ants
for (caps in 1:length(capsule_list)){
  tracking_data$createAntShapeType(names(capsule_list)[caps])
}


for (i in 1:length(ants)){
  
  ant_length_px <- mean(fmQueryComputeMeasurementFor(tracking_data,antID=ants[[i]]$ID)$length_px)
  
  ants[[i]]$clearCapsules()
  for (caps in 1:length(capsule_list)){
    capsule_ratios <- capsule_list[[caps]]; names(capsule_ratios) <- gsub("_ratio","",names(capsule_ratios))
    capsule_coords <- ant_length_px*capsule_ratios
    
    
    ants[[i]]$addCapsule(caps, fmCapsuleCreate(c1 = c(capsule_coords["c1_x"],capsule_coords["c1_y"]), c2 = c(capsule_coords["c2_x"],capsule_coords["c2_y"]), r1 = capsule_coords["r1"], r2 = capsule_coords["r2"] ) )
    
  }
  
}
tracking_data$save(paste(dir_data,no_capsule_file,sep='')) 

##LASTLY!! Go to fort-studio to check things look all right
### AND TO OVERWRITE INFO FOR QUEEN!!! (tag size, manual orientation, manual capsules)
