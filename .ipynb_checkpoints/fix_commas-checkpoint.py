#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 17:22:57 2018

@author: vitor
"""

import os
import re

aux = [0, 1]
pessoas = [1, 2, 3]
travessias = [1, 2]

for m in aux:
    for d in aux:
        for p in pessoas:
            for t in travessias:
                
                if d == 1 and t == 2:
                    continue
                
                filename = 'ac' + str(m) + str(d) + str(p) + str(t) + '.csv'
                file = open(filename, 'r')
                
                line = file.readline()
                
                if not re.match('^time;', line):
                    file.close()
                    break
                
                tempname = 'temp.csv'
                temp = open(tempname, 'w')
                
                line = line.replace(';', ',')
                temp.write(line)
                    
                for line in file:
                    line = line.replace(',', '.')
                    line = line.replace(';', ',')
                    temp.write(line)
                
                temp.close()
                file.close()
                
                os.remove(filename)
                os.rename(tempname, filename)
                    