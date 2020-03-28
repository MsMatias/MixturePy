# !/usr/bin/env python
# coding: utf-8

from __future__ import print_function
import numpy as np
import pandas as pd
import os, math, sys
import multiprocessing
# from ipynb.fs.full.tuneSvmForDeconv import tuneSvmForDeconv
from Mixture import tuneSvmForDeconv

#pd.set_option('display.max_columns', None)
#pd.set_option('display.max_rows', None)
#pd.set_option('display.max_colwidth', -1)

# Function nuSvmRobust
# ----------------
# @method nuSvmRobust
# @param [DataFrame] Signature
# @param [DataFrame] Expression
# @param [array] nuseq
# @param [float] delta
# @return -------------
def nuSvmRobust(X, Y, subject, nuseq = [0.25,0.5,0.75], delta = 0.007, maxIter = 6, verbose = 0):

    wSel = [1 for x in range(len(X.columns))]
    wSel = pd.DataFrame(wSel, X.columns).T
    ok = True
    i = 0
    model = 0

    salida = list()

    np.seterr(divide='ignore', invalid='ignore')

    if verbose == 1:
        print('--------------------------------------------------')
        print('Subject: ' + str(subject) + ' Nro. Processor: ' + str(multiprocessing.current_process()))
        print('--------------------------------------------------')

    while ok:
        i = i + 1
        # Run function
        XX = X.loc[:, X.columns.isin(wSel.columns[wSel.values[0] > 0])]
        r, model = tuneSvmForDeconv.tuneSvmForDeconv(X = XX, Y = Y.values, nuseq = [0.25,0.5,0.75], delta = 0.007)

        if i == 1:
            salida.append(r)
        
        if verbose == 1:
            print('Iter: ' + str(i) + ' Subject: ' + str(subject), flush=True)

        # Get betas
        w = model.coef_

        w.setflags(write=1)
        
        # Set values i to zero where i < 0
        #w[w < 0] = 0
        w = np.where(w<0, 0, w)

        # Save new betas backup
        wAbs = w
        
        # Normalize data
        w = w/np.sum(w)

        # Set values i to zero where i < delta
        #w = np.where(w<delta, 0, w)

        # Convert array to df
        #print(w)
        w = pd.DataFrame(w, XX.columns).T
        
        # Checking if all the values are NaN
        if w.isnull().all().all():
            wNan = np.empty(len(X.columns))#[0 for x in range(len(X.columns))]
            wNan.fill(np.nan)
            wNan = pd.DataFrame(wNan, X.columns).T
            result = pd.Series([wNan, wNan, float('NaN'), float('NaN'), float('NaN'), float('NaN'), i], index =['Wa', 'Wp', 'RMSEa', 'RMSEp', 'Ra', 'Rp', 'Iter'])
            return result

        # Checking if any value is < delta
        if w.apply(lambda x: x < delta).any().any():
            if(w.apply(lambda x: x > 0).sum().sum() == 1):
                break
            wSel.loc[:, wSel.columns.isin(w.loc[:, (w.values < delta).any(axis=0)].columns)] = 0
        else:
            ok = False
        
        if i >= maxIter and maxIter > -1:
            ok = False

    wOut = pd.DataFrame(wAbs, XX.columns).T

    # Create wSel with all values in zero
    wSel = [0 for x in range(len(X.columns))]
    wSel = pd.DataFrame(wSel, X.columns).T
    wSel.loc[:, wSel.columns.isin(wOut.columns)] = wOut

    u = X.apply(lambda x: x * wSel.iloc[0], axis = 1).values
    k = np.sum(u, axis = 1)
    #k = u.sum(axis = 1, skipna = True)
    nusvm = math.sqrt(pow((k - Y.values),2).mean())
    corrv = np.corrcoef(k, Y.values)
    #corrv = k.corr(Y.values)

    w = wSel/wSel.sum().sum()
    uW = X.apply(lambda x: x * w.iloc[0], axis = 1).values
    kW = np.sum(uW, axis = 1)
    #kW = uW.sum(axis = 1, skipna = True)
    nusvmW = math.sqrt(pow((kW - Y.values),2).mean())
    corrvW = np.corrcoef(kW, Y.values)
    #corrvW = kW.corr(Y.values)

    #wSel = wSel.where(wSel>delta).fillna(0)
    #w = w.where(w>delta).fillna(0).round(1)

    result = pd.Series([wSel, w, nusvm, nusvmW, corrv[0][1], corrvW[0][1], i], index =['Wa', 'Wp', 'RMSEa', 'RMSEp', 'Ra', 'Rp',  'Iter'])
    return result
