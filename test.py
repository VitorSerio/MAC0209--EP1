#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 20:22:12 2018

@author: vitor
"""

"""
1011
1012
1111
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

###############################################################################
###############################################################################

###########
# FUNÇÕES #
###########

###############################################################################
# Funções para ajustar os dados

def arruma_tempos(raw_data):
    # Calculando as médias dos pontos que possuem duas medidas de tempo
    data = raw_data[raw_data['Deslocado'] == False].copy()
    
    for row in data.index.values:
        try:
            t1 = data.at[row, 'Tempo']
            t2 = data.at[row + 1, 'Tempo']
            data.at[row, 'Tempo'] = ((t1 + t2)/2)
            data = data.drop(row + 1)
            pass
        except:
            continue
    
    data = pd.concat([data, raw_data[raw_data['Deslocado'] == True]])
    
    data = data.reset_index(drop = True)
            
    return data

def calc_vel_ac_1(data):
    # Calculando, ponto a ponto, as variações de espaço (ds), tempo (dt)
    # e velocidade (dv) e as velocidade e aceleração médias (vm e am)
    data['v'] = 0.0
    data['vm'] = 0.0
    data['a'] = 0.0
    data['am'] = 0.0
    data['agm'] = 0.0

    movimentos = data['Tipo'].unique()
    deslocado = data['Deslocado'].unique()
    pessoa = data['Pessoa'].unique()
    travessia = data['Travessia'].unique()

    for m in movimentos:
        for p in pessoa:
            for d in deslocado:
                for t in travessia:

                    if d and t == 'T2':
                        continue

                    M = data['Tipo'] == m
                    D = data['Deslocado'] == d
                    P = data['Pessoa'] == p
                    T = data['Travessia'] == t

                    index = data[M & D & P & T].index.values

                    for i in index:
                        data.at[i, 'v'] = data.at[i, 'Distancia'] / data.at[i, 'Tempo']
                        data.at[i, 'a'] = 2 * data.at[i, 'Distancia'] / (data.at[i, 'Tempo'] ** 2)
                    
            index = data[M & P].index.values
            
            vm = data.loc[index, 'v'].mean()
            data.loc[index, 'vm'] = vm
            am = data.loc[index, 'a'].mean()
            data.loc[index, 'am'] = am
            
        index = data[M].index.values
        
        agm = data.loc[index, 'a'].mean()
        data.loc[index, 'agm'] = agm
    
    
    return data

def calc_vel_ac_3(data):
     # Calculando, ponto a ponto, as variações de espaço (ds), tempo (dt)
    # e velocidade (dv) e as velocidade e aceleração médias (vm e am)
    data['v'] = 0.0
    data['vm'] = 0.0
    data['a'] = 0.0
    data['am'] = 0.0
    data['agm'] = 0.0

    movimentos = data['Tipo'].unique()
    deslocado = data['Deslocado'].unique()
    pessoa = data['Pessoa'].unique()
    travessia = data['Travessia'].unique()

    for m in movimentos:
        for p in pessoa:
            for d in deslocado:
                for t in travessia:

                    if d and t == 'T2':
                        continue

                    M = data['Tipo'] == m
                    D = data['Deslocado'] == d
                    P = data['Pessoa'] == p
                    T = data['Travessia'] == t

                    index = data[M & D & P & T].index.values

                    for i in index:
                        data.at[i, 'v'] = data.at[i, 'Distancia'] / data.at[i, 'Tempo']
                        data.at[i, 'a'] = 2 * data.at[i, 'Distancia'] / (data.at[i, 'Tempo'] ** 2)
                    
            index = data[M & P].index.values
            
            vm = (data.loc[index, 'v'] * data.loc[index, 'Tempo']).sum() / data.loc[index, 'Tempo'].sum()
            data.loc[index, 'vm'] = vm
            am = (data.loc[index, 'a'] * data.loc[index, 'Tempo']).sum() / data.loc[index, 'Tempo'].sum()
            data.loc[index, 'am'] = am
            
        index = data[M].index.values
        
        agm = (data.loc[index, 'a'] * data.loc[index, 'Tempo']).sum() / data.loc[index, 'Tempo'].sum()
        data.loc[index, 'agm'] = agm
    
    
    return data
    
###############################################################################
# Funções para plotar os gráficos
def plot_mru_pos(x, y, v, show = True):
    
    xmax = x.max()
    
    ymax = v * xmax
    
    plt.scatter(x, y)
    plt.plot([0, xmax], [0, ymax], '--')
    if show: plt.show()

def plot_mruv_pos(x, y, a, show = True):
    
    xmax = x.max()
    
    tx = np.linspace(0, xmax, 1000)
    ty = (a * (tx ** 2)) / 2
    
    plt.scatter(x, y)
    plt.plot(tx, ty, '--')
    if show: plt.show()    

def plot_pos(data, x, y, tipo = 0, p = 1, show = True):
    
    mov = ['MRU', 'MRUV'][tipo]
    pes = ['Geral', 'P1', 'P2', 'P3'][p]
    
    P = data['Pessoa'] == pes if p > 0 else True
    M = data['Tipo'] == mov
      
    df = data[M & P].loc[:, ['Distancia', 'Tempo', 'v', 'a', 'vm', 'am', 'agm']].copy()
    df = df.reset_index(drop = True)
    
    coef = df.at[0, 'vm'] if not tipo else df.at[0, 'am'] if p > 0 else df.at[0, 'agm']
    
    plt.title(('Espaço x Tempo', mov, pes))
    plt.xlabel('Tempo')
    plt.ylabel('Posição')
    if tipo: plot_mruv_pos(df[x], df[y], coef, show)
    else: plot_mru_pos(df[x], df[y], coef, show)

def plot_vel(data, x, y, pes = 1, show = True):
    
    pes = ['Geral', 'P1', 'P2', 'P3'][pes]
    
    P = data['Pessoa'] == pes if p > 0 else True
    M = data['Tipo'] == 'MRUV'
    
    df = data[M & P].copy()
    df = df.reset_index(drop = True)
    
    df['Tempo'] = df['Tempo'] / 2
    
    coef = df.at[0, 'am'] if p > 0 else df.at[0, 'agm']
    
    tmax = df['Tempo'].max()
    vmax = coef * tmax
    
    plt.title(('Velocidade x Tempo', 'MRUV', pes))
    plt.xlabel('Tempo')
    plt.ylabel('Velocidade')
    plt.scatter(df[x], df[y])
    plt.plot([0, tmax], [0, vmax], '--')
    if show: plt.show()
    
def plot_erros(data, x, y, tipo = 0, p = 1, vel = False, show = True):
    
    mov = ['MRU', 'MRUV'][tipo]
    pes = ['Geral', 'P1', 'P2', 'P3'][p]
    
    P = data['Pessoa'] == pes if p > 0 else True
    M = data['Tipo'] == mov
    
    df = data[M & P].copy()
    df = df.reset_index(drop = True)
    
    coef = df.at[0, 'vm'] if not tipo else df.at[0, 'am'] if p > 0 else df.at[0, 'agm']
    
    if vel:
        df[x] = df[x] / 2
        df['teor'] = coef * df[x]
    else:
        df['teor'] = coef * (df[x] ** 2) / 2 if tipo else coef * df[x] 
    
    df['e'] = df[y] - df['teor']
    
    xmax = df[x].max()
    
    plt.xlabel('Tempo')
    plt.ylabel('Erro')
    plt.scatter(df[x], df['e'])
    plt.plot([0, xmax], [0, 0], '--')
    if show: plt.show()

###############################################################################
###############################################################################

raw_data = pd.read_csv("tempos.csv")

# Arrumando os dados
data = arruma_tempos(raw_data)
data = calc_vel_ac_3(data)

# Plotando todos os gráficos de espaço por tempo

plt.figure(figsize = (15, 10), facecolor = '#FFFFFF')

i = 1
m = 0
for t in [0, 1]:
    for p in [1, 2, 3]:
        
        plt.subplot(2, 3, i)
        if t: plot_erros(data, 'Tempo', 'Distancia', m, p, show = False)
        else: plot_pos(data, 'Tempo', 'Distancia', m, p, show = False)
        i += 1

plt.show()


plt.figure(figsize = (15, 10), facecolor = '#FFFFFF')

i = 1
m = 1
for t in [0, 1]:
    for p in [1, 2, 3]:
        
        plt.subplot(2, 3, i)
        if t: plot_erros(data, 'Tempo', 'Distancia', m, p, show = False)
        else: plot_pos(data, 'Tempo', 'Distancia', m, p, show = False)
        i += 1

plt.show()

plt.figure(figsize = (15, 10), facecolor = '#FFFFFF')

i = 1
for t in [0, 1]:
    for p in [1, 2, 3]:
        
        plt.subplot(2, 3, i)
        if t: plot_erros(data, 'Tempo', 'v', 1, p, True, False)
        else: plot_vel(data, 'Tempo', 'v', p, False)
        i += 1

plt.show()