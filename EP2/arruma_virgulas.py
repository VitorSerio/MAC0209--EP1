#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 10:39:16 2018

@author: vitor
"""

import os
import re

for r in range(1, 6):
                
    filename = 'r' + str(r)
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