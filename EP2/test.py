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

def frange(start, stop, step=1.0):
    
    i = start
    while i < stop:
        yield i
        i += step
        
def erro(df, dft1, dft2, x):
    e1 = []
    e2 = []
    
    for i in range(len(df)):
        j = math.floor(df['time'][i] * 1000)
        e1.append(df[x][i] - dft1[x][j])
        e2.append(df[x][i] - dft2[x][j])
        
    df[x + '_e1'] = e1
    df[x + '_e2'] = e2
    
#def plot modelos(df, dft, x, u = 1, v = 1, i = 1, m = 1, label = '', unit = ''):
#    plt.subplot(u, v, i)
#    plt.ylabel(label + ' (' + unit + ')')
#    plt.xlabel('Tempo (s)')
#    plt.scatter(df[x], color = 'black')
#    plt.plot(dft[x], color = 'C' + str(m))
#    
#    plt.subplot(u, v, i+v)
#    plt.ylabel('Erro (' + unit + ')')
#    plt.xlabel('Tempo (s)')
#    plt.scatter(df[x + '_e' + str(m)], color = 'C' + str(m))
#    plt.plot([0, max(df['time'])], [0, 0], color = 'red')
    

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
mp = 0.23                                # massa do pendulo                          (kg)
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
    r[i].columns = ['time', 'a']
    # removendo dados antes do tempo inicial estimado
    r[i] = r[i].loc[r[i]['time'] >= tmin_r[i]]
    r[i] = r[i].reset_index(drop = True)
    # convertendo valores para m/s^2
    r[i].update(pd.Series(r[i]['a'] * g, name = 'a'))  
    # 'zerando' o tempo
    r[i].update(pd.Series(r[i]['time'] - tmin_r[i], name = 'time'))
    # calculando as velocidades experimentais
    r[i]['v'] = integrate(r[i]['time'], r[i]['a'])
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
    p[i].columns = ['time', 'w']
    # removendo dados fora do intervalo alvo
    p[i] = p[i].loc[(p[i]['time'] >= tmin_p[i]) & (p[i]['time'] <= tmin_p[i] + 30)]
    p[i] = p[i].reset_index(drop = True)
    # 'zerando' o tempo
    p[i].update(pd.Series(p[i]['time'] - tmin_p[i], name = 'time'))
    # calculando a inclinação experimental
    p[i]['theta'] = integrate(p[i]['time'], p[i]['w'])
    # estimando a inclinação inicial
    theta0.append(max(p[i]['theta']) / 2)
    # recalculando a inclinação experimental
    p[i].update(pd.Series(integrate(p[i]['time'], p[i]['w'], y0 = -theta0[i]), name = 'theta'))
    # calculando a aceleração angular
    p[i]['a'] = derivate(p[i]['time'], p[i]['w'], y0 = g * math.sin(theta0[i]) / L)

##################################
#     GRAFICOS EXPERIMENTAIS     #
##################################
    
########## Bloco em rampa #########

plt.figure(figsize = (25, 15), facecolor = '#FFFFFF')
plt.suptitle('Valores experimentais para os experimentos de Bloco em Rampa')
for i in range(5):
    plt.subplot(3, 5, i+1)
    plt.plot(r[i]['time'], r[i]['a'])
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

plt.figure(figsize = (25, 12), facecolor = '#FFFFFF')
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
    plt.plot(p[i]['time'], p[i]['w'])
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

Br = par * Ar / mr * 4
Ar = g * math.sin(thetar)

tmax = max(re['time'])

dt = 0.001

eur1 = pd.DataFrame({'time' : list(frange(0.0, tmax, dt)),
                    'd' : 0.0,
                    'v' : 0.0,
                    'a' : 0.0})

eur1['d'][0] = 0.0
eur1['v'][0] = 0.0
eur1['a'][0] = Ar
    
for i in range(1, len(eur1)):
    eur1['d'][i] = eur1['d'][i-1] + eur1['v'][i-1] * dt
    eur1['v'][i] = eur1['v'][i-1] + eur1['a'][i-1] * dt
    eur1['a'][i] = Ar - Br * eur1['v'][i] ** 2

eur2 = pd.DataFrame({'time' : list(frange(0.0, tmax, dt)),
                    'd' : 0.0,
                    'v' : 0.0,
                    'a' : 0.0})

eur2['d'][0] = 0.0
eur2['v'][0] = 0.0
eur2['a'][0] = Ar
    
for i in range(1, len(eur2)):
    vmid = eur2['v'][i-1] + eur2['a'][i-1] * dt / 2
    amid = Ar - Br * vmid ** 2
    eur2['v'][i] = eur2['v'][i-1] + amid * dt
    eur2['d'][i] = eur2['d'][i-1] + vmid * dt
    eur2['a'][i] = Ar - Br * eur2['v'][i] ** 2
    
erro(re, eur1, eur2, 'd')
erro(re, eur1, eur2, 'v')
erro(re, eur1, eur2, 'a')


############### MCU ###############

wc = np.mean(ce['w'])

tmax = max(ce['time'])
    
euc1 = pd.DataFrame({'time' : list(frange(0.0, tmax, dt)),
                    'theta' : 0.0})

euc1['theta'][0] = 0.0
    
for i in range(1, len(euc1)):
    euc1['theta'][i] = euc1['theta'][i-1] + wc * dt
euc1['w'] = wc

euc2 = pd.DataFrame({'time' : list(frange(0.0, tmax, dt)),
                    'theta' : 0.0})

euc2['theta'][0] = 0.0
    
for i in range(1, len(euc2)):
    euc2['theta'][i] = euc2['theta'][i-1] + wc * dt
euc2['w'] = wc
    
erro(ce, euc1, euc2, 'theta')
erro(ce, euc1, euc2, 'w')

############# Pêndulo #############

Bp = par * Ap * L / mp
thetap0 = np.mean(theta0)
Ap = g / L

tmax = max(pe['time'])

eup1 = pd.DataFrame({'time' : list(frange(0.0, tmax, dt)),
                    'theta' : 0.0,
                    'w' : 0.0,
                    'a' : 0.0})

eup1['theta'][0] = -thetap0
eup1['w'][0] = 0.0
eup1['a'][0] = Ap * math.sin(thetap0)
    
for i in range(1, len(eup1)):
    eup1['theta'][i] = eup1['theta'][i-1] + eup1['w'][i-1] * dt
    eup1['w'][i] = eup1['w'][i-1] + eup1['a'][i-1] * dt
    eup1['a'][i] = -Ap * math.sin(eup1['theta'][i]) - Bp * eup1['w'][i] * abs(eup1['w'][i])

eup2 = pd.DataFrame({'time' : list(frange(0.0, tmax, dt)),
                    'theta' : 0.0,
                    'w' : 0.0,
                    'a' : 0.0})

eup2['theta'][0] = -thetap0
eup2['w'][0] = 0.0
eup2['a'][0] = Ap * math.sin(thetap0)
    
for i in range(1, len(eup2)):
    eup2['a'][i] = -Ap * math.sin(eup2['theta'][i-1]) - Bp * eup2['w'][i] * abs(eup2['w'][i-1])
    eup2['w'][i] = eup2['w'][i-1] + eup2['a'][i] * dt
    eup2['theta'][i] = eup2['theta'][i-1] + eup2['w'][i] * dt
    
erro(pe, eup1, eup2, 'theta')
erro(pe, eup1, eup2, 'w')
erro(pe, eup1, eup2, 'a')
    
    
##################################
#            GRAFICOS            #
##################################

########## Bloco em rampa #########

tmax = max(re['time'])

plt.figure(figsize = (15, 10), facecolor = '#FFFFFF')
plt.suptitle('Resultado do modelo com seus respectivos erros para o experimento do Bloco em Rampa')

plt.subplot(2, 3, 1)
plt.title('Aceleração')
plt.scatter(re['time'], re['a'], s = 1)
plt.plot(eur1['time'], eur1['a'], color = 'C2')
plt.plot(eur2['time'], eur2['a'], color = 'C1')
plt.ylabel(r'Aceleração (m/s$^2$)')
plt.xlabel('Tempo (s)')

plt.subplot(2, 3, 2)
plt.title('Velocidade')
plt.scatter(re['time'], re['v'], s = 1)
plt.plot(eur1['time'], eur1['v'], color = 'C2')
plt.plot(eur2['time'], eur2['v'], color = 'C1')
plt.ylabel('Velocidade (m/s)')
plt.xlabel('Tempo (s)')

plt.subplot(2, 3, 3)
plt.title('Distância')
plt.scatter(re['time'], re['d'], s = 1)
plt.plot(eur1['time'], eur1['d'], color = 'C2')
plt.plot(eur2['time'], eur2['d'], color = 'C1')
plt.ylabel('Distância (m)')
plt.xlabel('Tempo (s)')

plt.subplot(2, 3, 4)
plt.scatter(re['time'], re['a_e1'], s = 1)
plt.scatter(re['time'], re['a_e2'], s = 1, color = 'C1')
plt.plot([0, tmax], [0, 0], color = 'C2')
plt.ylabel(r'Erro (m/s$^2$)')
plt.xlabel('Tempo (s)')

plt.subplot(2, 3, 5)
plt.scatter(re['time'], re['v_e1'], s = 1)
plt.scatter(re['time'], re['v_e2'], s = 1, color = 'C1')
plt.plot([0, tmax], [0, 0], color = 'C2')
plt.ylabel('Erro (m/s)')
plt.xlabel('Tempo (s)')

plt.subplot(2, 3, 6)
plt.scatter(re['time'], re['d_e1'], s = 1)
plt.scatter(re['time'], re['d_e2'], s = 1, color = 'C1')
plt.plot([0, tmax], [0, 0], color = 'C2')
plt.ylabel('Erro (m)')
plt.xlabel('Tempo (s)')
plt.show()

############### MCU ###############

tmax = max(ce['time'])

plt.figure(figsize = (10, 5), facecolor = '#FFFFFF')
plt.suptitle('Resultado do modelo com seus respectivos erros para o experimento do Movimento Circular Uniforme')

plt.subplot(1, 2, 1)
plt.scatter(ce['time'], ce['theta'], s = 1)
plt.plot(euc1['time'], euc1['theta'], color = 'C2')
plt.plot(euc2['time'], euc2['theta'], color = 'C1')
plt.ylabel('Distância angular (m)')
plt.xlabel('Tempo (s)')

plt.subplot(1, 2, 2)
plt.scatter(ce['time'], ce['theta_e1'], s = 10)
plt.scatter(ce['time'], ce['theta_e2'], s = 10, color = 'C1')
plt.plot([0, tmax], [0, 0], color = 'C2')
plt.ylabel('Erro (m)')
plt.xlabel('Tempo (s)')
plt.show()

############# Pêndulo #############  

tmax = max(pe['time'])

plt.figure(figsize = (15, 10), facecolor = '#FFFFFF')
plt.suptitle('Resultado do modelo com seus respectivos erros para o experimento do Movimento Pendular')

plt.subplot(2, 3, 1)
plt.title('Aceleração Angular') 
plt.scatter(pe['time'], pe['a'], s = 1)
plt.plot(eup1['time'], eup1['a'], color = 'C2')
plt.plot(eup2['time'], eup2['a'], color = 'C1')
plt.ylabel(r'Aceleração angular (rad/s$^2$)')
plt.xlabel('Tempo (s)')

plt.subplot(2, 3, 2)
plt.title('Velocidade Angular')
plt.scatter(pe['time'], pe['w'], s = 1)
plt.plot(eup1['time'], eup1['w'], color = 'C2')
plt.plot(eup2['time'], eup2['w'], color = 'C1')
plt.ylabel('Velocidade angular (rad/s)')
plt.xlabel('Tempo (s)')

plt.subplot(2, 3, 3)
plt.title('Inclinação')
plt.scatter(pe['time'], pe['theta'], s = 1)
plt.plot(eup1['time'], eup1['theta'], color = 'C2')
plt.plot(eup2['time'], eup2['theta'], color = 'C1')
plt.ylabel('Inclinação (rad)')
plt.xlabel('Tempo (s)')

plt.subplot(2, 3, 4)
plt.scatter(pe['time'], pe['a_e1'], s = 1)
plt.scatter(pe['time'], pe['a_e2'], s = 1, color = 'C1')
plt.plot([0, tmax], [0, 0], color = 'C2')
plt.ylabel(r'Erro (rad/s$^2$)')
plt.xlabel('Tempo (s)')

plt.subplot(2, 3, 5)
plt.scatter(pe['time'], pe['w_e1'], s = 1)
plt.scatter(pe['time'], pe['w_e2'], s = 1, color = 'C1')
plt.plot([0, tmax], [0, 0], color = 'C2')
plt.ylabel('Erro (rad/s)')
plt.xlabel('Tempo (s)')

plt.subplot(2, 3, 6)
plt.scatter(pe['time'], pe['theta_e1'], s = 1)
plt.scatter(pe['time'], pe['theta_e2'], s = 1, color = 'C1')
plt.plot([0, tmax], [0, 0], color = 'C2')
plt.ylabel('Erro (rad)')
plt.xlabel('Tempo (s)')
plt.show()