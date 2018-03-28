tipos <- c("MRU", "MRUV")
deslocado <- c(FALSE, TRUE)
pessoas <- c("P1", "P2", "P3")
travessias <- c("T1", "T2")
distancias <- list("não_deslocado" = c(10, 20, 30), "deslocado" = c(5, 10, 15, 20, 25, 30))

data <- data.frame(Tipo = as.factor(rep(tipos, each = 54)),
                   Deslocado = rep(rep(deslocado, c(36, 18)), 2),
                   Pessoa = as.factor(rep(c(rep(pessoas, each = 12),
                                            rep(pessoas, each = 6)), 2)),
                   Travessia = as.factor(rep(c(rep(rep(travessias, each = 6), 3),
                                               rep(travessias[1], 18)), 2)),
                   Distancia = rep(c(rep(rep(distancias[["não_deslocado"]], each = 2), 6),
                                     rep(distancias[["deslocado"]], 3)), 2),
                   Tempo = numeric(108))


write.csv(data, file = "tempos.csv", row.names = F, col.names = T)