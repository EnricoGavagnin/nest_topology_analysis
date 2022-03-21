rm(list=ls())
library(lme4)
library(car)
setwd('/home/eg15396/Documents/GitHub/auto_vs_manual_orientation_check')
prop_list <- c('MOD','wDIA','wDEH','wDEN')
dat <- read.csv("NTM_df_stats.csv",header=T,stringsAsFactors = F)
# list of properties for the LMER test
pv_list <- integer(0)


for (prop in prop_list){
  model <- lmer(formula(paste(prop,' ~ exp +(1|rep)+(1|h)')), data = dat)
  pv_list <- c(pv_list, print(as.numeric(Anova(model)["exp","Pr(>Chisq)"])))
}

pv_adj <- p.adjust(pv_list, method="BH")
names(pv_adj) <- prop_list

print(pv_adj)
#----------------------

setwd("/home/eg15396/Documents/GitHub/auto_vs_manual_orientation_check")

dat <- read.csv("NTM_df_stats.csv",header=T,stringsAsFactors = F)
dat <- dat[,c("rep","date_exp","h","MODa","MODb")]

dat_a <- data.frame(nest="A",dat[,c("rep","date_exp","h","MODa")])
dat_b <- data.frame(nest="B",dat[,c("rep","date_exp","h","MODb")])

names(dat_a)[grepl("MOD",names(dat_a))] <- "MOD"
names(dat_b)[grepl("MOD",names(dat_b))] <- "MOD"
dat <- rbind(dat_a,dat_b)

dat$colony <- dat$rep
dat[which(dat$rep==54),"colony"] <- 14

model <- lmer(MOD ~ nest + (1|colony)+(1|rep)+(1|h), data = dat)
summary(model)
Anova(model)
p_value_modularity <- as.numeric(Anova(model)["nest","Pr(>Chisq)"])

p_value_list <- c(p_value_modularity, 0.2, 0.1, 0.045)
p_values_adjusted <- p.adjust(p_value_list, method="BH")
