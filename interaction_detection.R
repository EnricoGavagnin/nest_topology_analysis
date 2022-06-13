collapse_collisions <- function(collisions){
  ###bring collisions metadata and zone/x-y/time info to same dataframe
  ###first, merge collisions$collisions with collisions$frames
  collisions$collisions <- cbind(collisions$collisions,collisions$frames[collisions$collisions$frames_row_index,])
  
  ###second, add information from positions to collisions$collisions
  collisions$collisions <- cbind(collisions$collisions,t(apply (collisions$collisions,1,get_positional_data,collisions=collisions)))
  
  return(collisions$collisions)
}

get_positional_data <- function (x,frames_row_index="frames_row_index",ant_pair = c("ant1","ant2"),collisions){
  pos_data <- unlist(collisions$positions[[as.numeric(x[frames_row_index])]][match(as.numeric(x[ant_pair]),as.numeric(collisions$positions[[as.numeric(x[frames_row_index])]]$antID)),])
  return(pos_data[which(!names(pos_data)%in%c("antID1","antID2"))])
}

filter_capsules     <- function(collisions,capsule_matcher){
  ###first, list types of interactions which we want to keep
  to_include <- c()
  for (caps in 1:length(capsule_matcher)){
    to_include <- c(to_include,c(paste(capsule_matcher[[caps]],collapse="-"),paste(rev(capsule_matcher[[caps]]),collapse="-")))
  }
  to_include <- sort(unique(to_include))
  
  ###use to_include and the content of collisions$types to list the interactions we ARE NOT INTERESTED IN
  all_types <- unique(unlist(strsplit((collisions$types),split=",")))  ###all types of interactions listed in collisions
  to_remove <- all_types [which(!all_types%in%to_include)]
  
  ##use the to_remove object to erase from collision$types the collisions we are not interested in, as well as the commas
  collisions_types <- collisions$types
  for (type in c(to_remove,",")){
    collisions_types <- gsub(type,"",collisions_types)
  }
  lines_to_remove <- which(nchar(collisions_types)==0)
  
  
  ##finally,remove lines with empty collisions$types
  collisions      <- collisions[-lines_to_remove,]
  
  return(collisions)
}

filter_ants         <- function(collisions,desired_ants,logical_link){
  if (logical_link == "or"){
    collisions <- collisions[which(collisions$ant1%in%desired_ants | collisions$ant2%in%desired_ants),]
  }
  if (logical_link == "and"){
    collisions <- collisions[which(collisions$ant1%in%desired_ants & collisions$ant2%in%desired_ants),]   
  }
 return(collisions) 
}

filter_distance     <- function(collisions,distance,logical_link){
  if (logical_link == "smaller"){
    collisions <- collisions[which(sqrt((collisions$x1-collisions$x2)^2+(collisions$y1-collisions$y2)^2)<=distance),]
  }
  if (logical_link == "greater"){
    collisions <- collisions[which(sqrt((collisions$x1-collisions$x2)^2+(collisions$y1-collisions$y2)^2)>=distance),]
  }
  return(collisions) 
}

filter_angle     <- function(collisions,angle_threshold,logical_link){
  ant_angle_diff  <-  (collisions$angle1-collisions$angle2) - (2*pi)*round((collisions$angle1-collisions$angle2)/(2*pi))
  angle_threshold <- (angle_threshold) - (2*pi)*round((angle_threshold)/(2*pi))
    
  if (logical_link == "smaller"){
    collisions <- collisions[which(abs(ant_angle_diff)<=angle_threshold),]
  }
  if (logical_link == "greater"){
    collisions <- collisions[which(abs(ant_angle_diff)>=angle_threshold),]  }
  return(collisions) 
}


interaction_detection <- function (e
                                   ,time_start
                                   ,time_stop
                                   , max_time_gap
                                   , max_distance_moved
                                   , capsule_matcher=NULL
                                   , desired_ants_OR = NULL
                                   , desired_ants_AND = NULL
                                   , distance_smaller_than = NULL
                                   , distance_greater_than = NULL
                                   , angle_smaller_than = NULL
                                   , angle_greater_than = NULL
){
  ###e: experiment
  ###time start: fmTime
  ###time_stop: fmTime
  ###capsule_matcher: list of vectors - each vector containing 2 capsule IDs that we want to see collide
  ###desired_ants_OR: vector of (any number) of ant IDs that we are interested in (any interaction involving at least one of these ants)
  ###desired_ants_AND: vector of (any number) of ant IDs that we are interested in (any interaction involving two ants from this list)
  ###distance_smaller_than: only collisions in which the distance between the two ants tag is less than distance_smaller_than will be kept
  ###distance_greater_than: only collisions in which the distance between the two ants tag is more than distance_greater_than will be kept
  ###angle_smaller_than: only collisions in which the angle between the two ants is less than angle_smaller_than will be kept
  ###angle_greater_than: only collisions in which the angle between the two ants is more than angle_greater_than will be kept
  
  
  #######################################
  ###query all collisions ###############
  #######################################
  collisions          <- fmQueryCollideFrames(e, start=time_start, end=time_stop, showProgress = FALSE)
  
  #######################################
  ###filter on capsules #################
  #######################################
  if (!is.null(capsule_matcher)){
    collisions$collisions <- filter_capsules (collisions$collisions,capsule_matcher)
  }

  #######################################
  ###filter on ant ids #################
  #######################################
  if (!is.null(desired_ants_OR)){
    collisions$collisions <- filter_ants (collisions$collisions,desired_ants_OR,"or")
  }
  if (!is.null(desired_ants_AND)){
    collisions$collisions <- filter_ants (collisions$collisions,desired_ants_AND,"and")
  }
  
  #################################################################################################
  ###collpase collisions into single dataframe (necessary for next filtering step) ################
  #################################################################################################
  collisions          <-  collapse_collisions(collisions)
  
  #######################################
  ###filter on ant distances ############
  #######################################
  if (!is.null(distance_smaller_than)){
    collisions <- filter_distance (collisions,distance_smaller_than,"smaller")
  }
  if (!is.null(distance_greater_than)){
    collisions <- filter_distance (collisions,distance_greater_than,"greater")
  }
  
  #######################################
  ###filter on ant angles ###############
  #######################################
  if (!is.null(angle_smaller_than)){
    collisions <- filter_angle (collisions,angle_smaller_than,"smaller")
  }
  if (!is.null(angle_greater_than)){
    collisions <- filter_angle (collisions,angle_greater_than,"greater")
  }
  
  ###################################################################
  ###assemble successive collisions into interactions ###############
  ###################################################################
  ###prepare collisions to be loaded into cpp function
  collisions$time_second <- round(as.numeric(collisions$time),3)
 
  collisions$pair        <- apply(collisions[,c("ant1","ant2")],1,function(x){paste(sort(x),collapse = "_") })
  collisions$pair        <- match(collisions$pair,sort(unique(collisions$pair)))-1
  pair_list              <- sort(unique(collisions$pair))
  interactions           <- merge_interactions(collisions, pair_list, max_distance_moved=max_distance_moved, max_time_gap=max_time_gap)
  # interactions       <- interactions[order(interactions$end,interactions$start,interactions$ant1,interactions$ant2),]
  interactions$start <- as.POSIXct(interactions$start,  origin="1970-01-01", tz="GMT" )
  interactions$end   <- as.POSIXct(interactions$end,  origin="1970-01-01", tz="GMT" )

  return(interactions)
}

