
save_plot = function(fname) {
  h = read.csv(paste0(fname, ".csv"), T, sep=",", colClasses=rep("numeric", 8))
  N = nrow(h)
  cols = colnames(h)
  
  h2 = NULL
  k = 0
  for(j in 1:ncol(h)) {
    type = substr(cols[j], 1, 4)
    player = substr(cols[j], 8, 8)
    prob = as.numeric(h[,j])
    df_j = data.frame(type=type, player=player, prob=prob)
    h2 = rbind(h2, df_j)
  }
  
  X11(width=8, height=6)
  par(mfrow=c(1,2))
  for(type in c("game", "simu")) {
    boxplot(prob ~ player, data=h2[h2$type==type,], main=type, ylim=c(.2, .3))
    abline(h=0.25, lty=2, lwd=2)
  }
  par(mfrow=c(1,1))
  savePlot(paste0(fname, ".png"), type = "png")
}

save_plot("randomness_check_rand")
save_plot("randomness_check_0")
