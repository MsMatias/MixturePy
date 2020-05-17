#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import os

from Mixture.nuSvmRobust import nuSvmRobust
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import scale
from joblib import Parallel, delayed

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
    print('Processing...')

    out = Parallel(n_jobs=cores, backend='multiprocessing')(delayed(nuSvmRobust)(X = X, Y = j, subject = i, nuseq = [0.25,0.5,0.75], delta = 0.007, maxIter = -1, verbose = 1) for i, j in Yn.iteritems())
             
    #out = [x.recv() for x in pipe_list]

    print('_____________________________________________________________________')
    
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

    matWa.index.name = 'SubjectID'
    matWp.index.name = 'SubjectID'

    matRes.index = matWp.index.values
    matRes.index.name = 'CellTypes'

    return(pd.DataFrame([[matWa, matWp, matRes]], columns=['MIXabs', 'MIXprop', 'ACCmetrix']))
