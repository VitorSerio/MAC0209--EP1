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

def calc_vel(data):
    # Calculando, ponto a ponto, as variações de espaço (ds), tempo (dt)
    # e velocidade (dv) e as velocidade e aceleração médias (vm e am)
    data['Velocidade'] = 0.0

    index = data.index.values

    for i in index:
        data.at[i, 'Velocidade'] = data.at[i, 'Distancia'] / data.at[i, 'Tempo']

    return data

def calc_res(data):
    def calc_vel_mru(data):
        data = data[data['Tipo'] == 'MRU'].copy()
        
        data['v'] = 0.0
        
        pessoa = data['Pessoa'].unique()
    
        vel = []
        for p in pessoa:
            
            df = data[data['Pessoa'] == p]
            
            vm = df['Velocidade'].mean()
                
            vel.append(vm)
            
        return vel
    
    def calc_ac_mruv(data, res):
        data = data[data['Tipo'] == 'MRUV'].copy()
        
        #data['dv'] = 0.0
        data['a'] = 0.0
        data['v0'] = 0.0
        res['v0'] = [0.55, 0.6, 0.7]
        
        
        pessoa = data['Pessoa'].unique()
    
        for p in pessoa:
            
            P = data['Pessoa'] == p
            
            index = data[P].index.values
                
            v0 = res.at[p, 'v0']
            
            for i in index:
                
                si = data.at[i, 'Distancia']
                ti = data.at[i, 'Tempo']
                data.at[i, 'a'] = 2 * (si - v0 * ti) / (ti ** 2)
                
            res.at[p, 'am'] = data.loc[index, 'a'].mean()
            
        return res
    
    res = pd.DataFrame(index = data['Pessoa'].unique(), columns = ['vm', 'am', 'v0'])
    
    res['vm'] = calc_vel_mru(data)
    res = calc_ac_mruv(data, res)
    
    res.loc['Geral'] = res.mean()
    
    return res
    
    
###############################################################################
# Funções para plotar os gráficos

def plot(data, res, m = 0, p = 1, v = 0, erro = True, show = False):
    
    def plot_data(x, y, a, b = 0, parab = False, show = True):
    
        def plot_line(x, y, a, b, show = True):
            
            xmax = x.max() + 5
            ymax = a * xmax + b
            
            plt.scatter(x, y)
            plt.plot([0, xmax], [b, ymax], '--')
            if show: plt.show()
            
            return
    
        def plot_parab(x, y, a, b, show = True):
            
            xmax = x.max() + 5
            
            tx = np.linspace(0, xmax, 1000)
            ty = (a * (tx ** 2)) / 2 + b * tx
            
            plt.scatter(x, y)
            plt.plot(tx, ty, '--')
            if show: plt.show()
            
            return   
    
        if parab: plot_parab(x, y, a, b, show)
        else: plot_line(x, y, a, b, show)
        
        return
    
    def plot_erro(x, y, a, b, parab = False, show = True):
        
        xmax = x.max() + 5
        
        if parab:
            e = y - ((a * (x ** 2)) / 2 + (b * x))
        else:
            e = y - (a * x + b)
        
        plt.xlabel('Tempo')
        plt.ylabel('Erro')
        plt.scatter(x, e)
        plt.plot([0, xmax], [0, 0], '--')
        if show: plt.show()
        
        return
    
    mov = ['MRU', 'MRUV'][m]
    pes = ['Geral', 'P1', 'P2', 'P3'][p]
    
    P = data['Pessoa'] == pes if p > 0 else True
    M = data['Tipo'] == mov
    
    df = data[M & P].copy()
    df = df.reset_index(drop = True)
    
    x = 'Tempo'
    plt.xlabel(x)
    x = df[x] / 2 if v else df[x]
    
    y = 'Velocidade' if v else 'Distancia'
    plt.ylabel(y)
    y = df[y]
    
    a = res.at[pes, 'am'] if m else res.at[pes, 'vm']
    b = res.at[pes, 'v0'] if m else 0
    
    parab = True if m and not v else False
    
    if erro:
        plot_erro(x, y, a, b, parab, show)
        
    else:
        plt.title('Pessoa ' + str(p))
        plot_data(x, y, a, b, parab, show)
        
    return
    

###############################################################################
###############################################################################

raw_data = pd.read_csv("tempos.csv")

# Arrumando os dados
data = arruma_tempos(raw_data)
data = calc_vel(data)
res = calc_res(data)

# Plotando todos os gráficos de espaço por tempo

plt.figure(figsize = (15, 10), facecolor = '#FFFFFF')

i = 1
m = 0
for erro in [False, True]:
    for p in [1, 2, 3]:
        
        plt.subplot(2, 3, i)
        plot(data, res, m, p, 0, erro)
        i += 1

plt.show()


plt.figure(figsize = (15, 10), facecolor = '#FFFFFF')

i = 1
m = 1
for erro in [False, True]:
    for p in [1, 2, 3]:
        
        plt.subplot(2, 3, i)
        plot(data, res, m, p, 0, erro)
        i += 1

plt.show()

plt.figure(figsize = (15, 10), facecolor = '#FFFFFF')

i = 1
for erro in [False, True]:
    for p in [1, 2, 3]:
        
        plt.subplot(2, 3, i)
        plot(data, res, m, p, 1, erro)
        i += 1

plt.show()