#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 10:58:49 2018

@author: vitor
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display
import math

##################################
#           FUNCOES              #
##################################

    
def integrate(x, y, y0 = 0):
    yi = [y0]
    print(yi)
    
    for i in range(1, min(len(x), len(y))):
        dy = ((y[i-1] + y[i]) / 2) * (x[i] - x[i-1])
        yi.append(yi[i-1] + dy)
        
    return yi

def derivate(x, y, y0 = 0):
    yi = [y0]
    
    for i in range(1, min(len(x), len(y))):
        dy = y[i] - y[i-1]
        dx = x[i] - x[i-1]
        yi.append(dy / dx)
        
    return yi

##################################
#            DADOS               #
##################################
#
#
## 00000 = dados faltando
## 'CHUTE' = valores que esquecemos (Vitor, principalmente) de coletar, então estão estimados e podem precisar de ajustes
#
#
## A plotagem dos gráficos não é definitiva e está aí mais pra visualizarmos e fazermos testes

## Constantes

g = 9.8                 # aceleração da gravidade (m/s^2)
par = 1.2               # densidade do ar (kg/m^3)

## Bloco em rampa
tr = 6 * math.pi / 180  # inclinacao (rad)
D = 3.64                # distância percorrida (m)
mr = 00000              # massa do bloco (g)
Ar = 00000              # área frontal do bloco (m^2)
r = []
tmin_r = [4.7, 2.9, 6.2, 4.6, 4.5]

plt.figure(figsize = (25, 15), facecolor = '#FFFFFF')
plt.suptitle('Aceleração vs. Tempo')
for i in range(5):
    r.append(pd.read_csv('r' + str(i+1) + '.csv'))          # lendo dados do acelerometro
    r[i] = r[i].filter(items=['time', 'gFx'])               # removendo variáveis que não serão utilizadas
    r[i] = r[i].loc[r[i]['time'] >= tmin_r[i]]
    r[i] = r[i].reset_index()
    r[i].update(pd.Series(r[i]['gFx'] * g, name = 'gFx'))   # convertendo valores para m/s^2
    r[i].update(pd.Series(r[i]['time'] - tmin_r[i], name = 'time'))
    r[i]['v'] = integrate(r[i]['time'], r[i]['gFx'])
    r[i]['d'] = integrate(r[i]['time'], r[i]['v'])
    r[i] = r[i].loc[r[i]['d'] <= D]
    
    plt.subplot(3, 5, i+1)
    plt.plot(r[i]['time'], r[i]['gFx'])
    #plt.plot([tmin_r[i], tmin_r[i]], [min(r[i]['gFx']), max(r[i]['gFx'])], color = 'C1')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Aceleração (m/s^2)')
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
    

## MCU
R = 2.1                 # raio (m)
t = pd.read_csv('mcu.csv')

## Pendulo
tp = 45 * math.pi / 180 # inclinacao (rad) - CHUTE!!
l = 0.65                # comprimento das cordas (m) - CHUTE!!
a = 0.051               # largura do cesto (m)
b = 0.144               # comprimento do cesto (m)
mp = 0.2                # massa do pendulo (kg) - CHUTE!!
Ap = 00000              # área frontal do pêndulo (m^2)
p = []
labels = ['wx', 'wy', 'wz']
tmin_p = [7.05, 5.15, 5.2, 5.15, 5.3]
theta0 = []


plt.figure(figsize = (25, 15), facecolor = '#FFFFFF')
plt.suptitle('Velocidade Angular vs. Tempo')
for i in range(5):
    p.append(pd.read_csv('p' + str(i+1) + '.csv'))  # lendo dados do acelerometro
    p[i] = p[i].filter(items=['time', 'wx'])        # removendo variáveis que não serão utilizadas
    p[i] = p[i].loc[(p[i]['time'] >= tmin_p[i]) & (p[i]['time'] <= tmin_p[i] + 30)]
    p[i] = p[i].reset_index()
    p[i].update(pd.Series(p[i]['time'] - tmin_p[i], name = 'time'))
    p[i]['a'] = derivate(p[i]['time'], p[i]['wx'])
    p[i]['theta'] = integrate(p[i]['time'], p[i]['wx'])
    theta0.append(max(p[i]['theta']) / 2)
    p[i].update(pd.Series(integrate(p[i]['time'], p[i]['wx'], y0 = -theta0[i]), name = 'theta'))
    
    plt.subplot(3, 5, i+1)
    plt.plot(p[i]['time'], p[i]['a'])
    plt.xlabel('Tempo (s)')
    plt.ylabel('Aceleração Angular (rad/s^2)')
    plt.title('p' + str(i+1))
    
    plt.subplot(3, 5, i+6)
    plt.plot(p[i]['time'], p[i]['wx'])
    #plt.plot([tmin_p[i], tmin_p[i]], [min(p[i]['wx']), max(p[i]['wx'])], color = 'C1')
    #plt.plot([tmax_p[i], tmax_p[i]], [min(p[i]['wx']), max(p[i]['wx'])], color = 'C1')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Velocidade Angular (rad/s)')
    
    plt.subplot(3, 5, i+11)
    plt.plot(p[i]['time'], p[i]['theta'])
    plt.xlabel('Tempo (s)')
    plt.ylabel('Distância Angular (rad)')
plt.show()

