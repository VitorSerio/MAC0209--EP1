import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import display
import math

pd.options.mode.chained_assignment = None

##################################
#           FUNCOES              #
##################################

    
def integrate(x, y, y0 = 0):
    yi = [y0]
    
    for i in range(1, min(len(x), len(y))):
        dy = ((y[i-1] + y[i]) / 2) * (x[i] - x[i-1])
        yi.append(yi[i-1] + dy)
        
    return yi

def derivate(x, y, y0 = 0):
    '''
    array, array, object -> array
    
    Recebe dois vetores com dados e retorna um vetor de mesmo tamanho, que seria o resultado da derivada de y em x.
    y0 é o valor inicial da derivada.
    '''
    yi = [y0]
    
    for i in range(1, min(len(x), len(y))):
        dy = y[i] - y[i-1]
        dx = x[i] - x[i-1]
        if dx == 0:
            yi.append(dy)
        else:
            yi.append(dy / dx)
        
    return yi

##################################
#            DADOS               #
##################################
#
## 'CHUTE' = valores que esquecemos (Vitor, principalmente) de coletar, então estão estimados e podem precisar de ajustes
#
#
## A plotagem dos gráficos não é definitiva e está aí mais pra visualizarmos e fazermos testes

############ Constantes ###########

g = 9.8                 # aceleração da gravidade (m/s^2)
par = 1.2               # densidade do ar         (kg/m^3)

########## Bloco em rampa #########
thetar = 6 * math.pi / 180  # inclinacao              (rad)
D = 3.64                    # distância percorrida    (m)
mr = 0.34                   # massa do bloco          (g)
Ar = 0.008                  # área frontal do bloco   (m^2)
r = []                      # lista para armazenar os dados do acelerometro

for i in range(5):
    # lendo dados do acelerometro
    r.append(pd.read_csv('r' + str(i+1) + '.csv'))
    

############### MCU ###############
R = 2.1                     # raio (m)
t = pd.read_csv('mcu.csv')  # tabela com os dados dos tempos das voltas
c = []                      # lista para armazenar os tempos medidos pra cada experimento

for i in range(5):
    c.append(t.loc[t['rep'] == i+1])
    c[i] = c[i].reset_index()
    c[i] = c[i].filter(items=['time', 'theta'])

############# Pêndulo #############
l = 0.823                                # comprimento das cordas                    (m)
a = 0.051                               # largura do cesto                           (m)
b = 0.144                               # comprimento do cesto                       (m)
L = math.sqrt(l**2 - (a/2)**2 - (b/2)**2)  # comprimento da corda imaginária do pêndulo (m)
mp = 0.2                                # massa do pendulo                           (kg) - CHUTE!!
Ap = 0.0059                             # área frontal do pêndulo                    (m^2)
p = []                                  # lista para armazenar os dados do giroscópio
tmin_p = [7.05, 5.15, 5.2, 5.15, 5.3]   # tempos iniciais (s)
theta0 = []                             # inclinação inicial

for i in range(5):
    # lendo dados do giroscópio
    p.append(pd.read_csv('p' + str(i+1) + '.csv'))
    
    
##################################
#       LIMPEZA DOS DADOS        #
##################################
    
########## Bloco em rampa #########
    
tmin_r = [4.7, 2.9, 6.2, 4.6, 4.5]  # tempos iniciais estimados (s)

for i in range(5):
    # removendo variáveis que não serão utilizadas        
    r[i] = r[i].filter(items=['time', 'gFx']) 
    # removendo dados antes do tempo inicial estimado              
    r[i] = r[i].loc[r[i]['time'] >= tmin_r[i]]
    r[i] = r[i].reset_index()
    # convertendo valores para m/s^2
    r[i].update(pd.Series(r[i]['gFx'] * g, name = 'gFx'))  
    # 'zerando' o tempo
    r[i].update(pd.Series(r[i]['time'] - tmin_r[i], name = 'time'))
    # calculando as velocidades experimentais
    r[i]['v'] = integrate(r[i]['time'], r[i]['gFx'])
    # calculando o deslocamento experimental
    r[i]['d'] = integrate(r[i]['time'], r[i]['v'])
    # filtrando dados com deslocamento maior que o tamanho total da rampa
    r[i] = r[i].loc[r[i]['d'] <= D]
    
############### MCU ###############
    
for i in range(5):
    c[i]['theta'][0] = 1*math.pi
    c[i]['theta'][1] = 2*math.pi
    for j in [2, 4]:
        c[i]['theta'][j] = (j+1)*math.pi
        c[i]['theta'][j+1] = (j+2)*math.pi
        c[i]['time'][j] += c[i]['time'][j-1]
        c[i]['time'][j+1] += c[i]['time'][j-1]
    c[i]['w'] = derivate(c[i]['time'], c[i]['theta'], y0 = c[i]['theta'][0] / c[i]['time'][0])
    
############# Pêndulo #############
    
tmin_p = [7.05, 5.15, 5.2, 5.15, 5.3]   # tempos iniciais estimados (s)

for i in range(5):
    # removendo variáveis que não serão utilizadas
    p[i] = p[i].filter(items=['time', 'wx'])
    # removendo dados fora do intervalo alvo
    p[i] = p[i].loc[(p[i]['time'] >= tmin_p[i]) & (p[i]['time'] <= tmin_p[i] + 30)]
    p[i] = p[i].reset_index()
    # 'zerando' o tempo
    p[i].update(pd.Series(p[i]['time'] - tmin_p[i], name = 'time'))
    # calculando a inclinação experimental
    p[i]['theta'] = integrate(p[i]['time'], p[i]['wx'])
    # estimando a inclinação inicial
    theta0.append(max(p[i]['theta']) / 2)
    # recalculando a inclinação experimental
    p[i].update(pd.Series(integrate(p[i]['time'], p[i]['wx'], y0 = -theta0[i]), name = 'theta'))
    # calculando a aceleração angular
    p[i]['a'] = derivate(p[i]['time'], p[i]['wx'], y0 = g * math.sin(theta0[i]) / L)

##################################
#     GRAFICOS EXPERIMENTAIS     #
##################################
    
########## Bloco em rampa #########

plt.figure(figsize = (25, 15), facecolor = '#FFFFFF')
plt.suptitle('Valores experimentais para os experimentos de Bloco em Rampa')
for i in range(5):
    plt.subplot(3, 5, i+1)
    plt.plot(r[i]['time'], r[i]['gFx'])
    plt.xlabel('Tempo (s)')
    plt.ylabel(r'Aceleração (m/s$^2$)')
    plt.title('r' + str(i+1))
    
    plt.subplot(3, 5, i+6)
    plt.plot(r[i]['time'], r[i]['v'])
    plt.xlabel('Tempo (s)')
    plt.ylabel('Velocidade (m/s)')
    
    plt.subplot(3, 5, i+11)
    plt.plot(r[i]['time'], r[i]['d'])
    plt.xlabel('Tempo (s)')
    plt.ylabel('Distância (m)')
plt.show()

############### MCU ###############

plt.figure(figsize = (25, 10), facecolor = '#FFFFFF')
plt.suptitle('Valores experimentais para os experimentos de Movimento Circular Uniforme')
for i in range(5):
    plt.subplot(3, 5, i+1)
    plt.scatter(c[i]['time'], c[i]['theta'])
    plt.xlabel('Tempo (s)')
    plt.ylabel('Deslocamento (rad)')
    plt.title('c' + str(i+1))
    
    plt.subplot(3, 5, i+6)
    plt.scatter(c[i]['time'], c[i]['w'])
    plt.xlabel('Tempo (s)')
    plt.ylabel('Velocidade Angular (rad/s)')
plt.show()

############# Pêndulo #############

plt.figure(figsize = (25, 15), facecolor = '#FFFFFF')
plt.suptitle('Valores experimentais para os experimentos de Movimento Pendular')
for i in range(5):
    plt.subplot(3, 5, i+1)
    plt.plot(p[i]['time'], p[i]['a'])
    plt.xlabel('Tempo (s)')
    plt.ylabel(r'Aceleração Angular (rad/s$^2$)')
    plt.title('p' + str(i+1))
    
    plt.subplot(3, 5, i+6)
    plt.plot(p[i]['time'], p[i]['wx'])
    plt.xlabel('Tempo (s)')
    plt.ylabel('Velocidade Angular (rad/s)')
    
    plt.subplot(3, 5, i+11)
    plt.plot(p[i]['time'], p[i]['theta'])
    plt.xlabel('Tempo (s)')
    plt.ylabel('Distância Angular (rad)')
plt.show()

##################################
#             MODELO             #
##################################

re = r[0]
ce = c[0]
pe = p[0]

for i in range(1,5):
    re = re.append(r[i], ignore_index = True)
    ce = ce.append(c[i], ignore_index = True)
    pe = pe.append(p[i], ignore_index = True)

########## Bloco em rampa #########

Br = 0.2 * par * Ar / mr
Ar = g * math.sin(thetar)

############### MCU ###############

wc = np.mean(ce['w'])

############# Pêndulo #############

Bp = 0.2 * par * Ap * L / mp
thetap0 = np.mean(theta0)
Ap = g / L

