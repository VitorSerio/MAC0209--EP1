tempos1 = c( 7.22,  7.09,  6.99,  7.11,  7.51,  7.94,  7.19,  7.53,  7.13,  7.52,  7.46,  6.91,  6.65,  7.52,  7.50)
tempos2 = c(14.49, 14.23, 14.19, 14.29, 14.79, 16.09, 14.45, 14.90, 14.29, 14.81, 14.55, 14.10, 14.02, 14.80, 14.71)
reps = c(1:5)


tempos = numeric(30)

for (i in c(1:15)) {
    tempos[2*i - 1] = tempos1[i]
    tempos[2*i] = tempos2[i]
}

table = data.frame("rep" = rep(reps, each = 6),
                   "theta" = rep(c(1,2), 15),
                   "temps" = tempos)

write.csv(table, file = "mcu.csv", row.names = F)