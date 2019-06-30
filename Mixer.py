#!/usr/bin/env python
# coding: utf-8

# In[3]:


import numpy as np
import pandas as pd
import os

#import  multiprocessing
from multiprocessing import Process, Pipe
# from ipynb.fs.full.nuSvrR import nuSvrR
from nuSvmRobust import nuSvmRobust
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import scale


# In[2]:


# Function Mixer
# Main Function
# @method Mixer
# @param [DataFrame] Signature
# @param [DataFrame] Expression
# @param [int] num Cores
# @return -------
def Mixer(X, Y, cores):

    print('Normalizing data')

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
    
    Yn = pd.DataFrame(scale(Y), index=Y.index, columns=Y.columns)

    out = list()
    processes = []
    pipe_list = []
    print('Processing...')

    if __name__ == 'Mixer':
        for i, j in Yn.iteritems():
            recv_end, send_end = Pipe(False)
            p = Process(target=nuSvmRobust, args=(X, j, i, [0.25, 0.5, 0.75], 0.007, 6, 0, send_end))
            processes.append(p)
            p.start()
            pipe_list.append(recv_end)

        for p in processes:
            p.join()

    out = [x.recv() for x in pipe_list]
    
    print('Finish nuSvm')

    matWa = pd.DataFrame()
    matWp = pd.DataFrame()
    matRes = pd.DataFrame()

    for i in out:
        matWa = matWa.append(i.Wa, ignore_index=True)
        matWp = matWp.append(i.Wp, ignore_index=True)
        matRes = matRes.append(pd.DataFrame([[i.RMSEa, i.RMSEp, i.Ra, i.Rp,  i.BestParams, i.Iter]], columns=['RMSEa', 'RMSEp', 'Ra', 'Rp',  'BestParams', 'Iter']), ignore_index=True)

    matWa.index = Y.columns.values
    matWa.columns = X.columns.values

    matWp.index = Y.columns.values
    matWp.columns = X.columns.values

    matRes.index = matWp.index.values

    return(pd.DataFrame([[matWa, matWp, matRes]], columns=['MIXabs', 'MIXprop', 'ACCmetrix']))
