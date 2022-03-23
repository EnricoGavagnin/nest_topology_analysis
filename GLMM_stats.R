rm(list=ls())
library(lme4)
library(car)

prop_list <- c('cMOD','wDIA','cwDEH','wDEN')
dat <- read.csv("NTM_df_stats.csv",header=T,stringsAsFactors = F)
pv_list <- integer(0)

rf <- ' ~ exp +(1|rep)+(1|h)'

for (prop in prop_list){
  model <- lmer(formula(paste(prop, rf)), data = dat)
  print(summary(model))
  pv_list <- c(pv_list, as.numeric(Anova(model)["exp","Pr(>Chisq)"]))}

pv_adj <- p.adjust(pv_list, method="BH")
names(pv_adj) <- prop_list

print(pv_adj)
