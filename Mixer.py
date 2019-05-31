#!/usr/bin/env python
# coding: utf-8

# In[3]:


import numpy as np
import pandas as pd
import os

from multiprocessing import Pool
# from ipynb.fs.full.nuSvrR import nuSvrR
from nuSvmRobust import nuSvmRobust
from sklearn.preprocessing import StandardScaler


# In[2]:


# Function Mixer
# Main Function
# @method Mixer
# @param [DataFrame] Signature
# @param [DataFrame] Expression
# @param [int] num Cores
# @return -------
def Mixer(X, Y, cores):
    # Normalize signature Matrix
    mean = X.iloc[:, 1:].mean()
    std = X.iloc[:, 1:].stack().std()
    X.iloc[:, 1:] = (X.iloc[:, 1:] - mean.mean()) / std
    
    # Intersection between X and Y
    X = X.loc[X['Gene symbol'].isin(Y['Gene symbol'])]
    Y = Y.loc[Y['Gene symbol'].isin(X['Gene symbol'])]
    
    # Ordering by GeneSymbol
    X = X.sort_values(by=['Gene symbol'])
    Y = Y.sort_values(by=['Gene symbol'])

    # Slice Gene symbol column
    X = X.iloc[:, 1:]
    Y = Y.iloc[:, 1:]
    X.reset_index(drop=True, inplace=True)
    
    # Normalize features Matrix
    scaler = StandardScaler()
    scaler.fit(Y)
    Yn = pd.DataFrame(scaler.transform(Y.values), columns=Y.columns, index=Y.index)

    out = list()

    for i, j in Yn.iteritems():
            print(i)
            print(j)
            print('-------------------------')
            out.append(nuSvmRobust(X = X, Y = j, nuseq = [0.25,0.5,0.75], delta = 0.007))

    return out
    
    # Run function Multiples cores
#     num_processors = 3
#     print(num_processors)
#     p=Pool(processes = num_processors)
#     out = list(p.map(lambda Yi: nuSvrR(X = X, Y = Yi, nuseq = [0.25,0.5,0.75], delta = 0.007), Yn))
#     print(out)
#     print('asd')
#     return out