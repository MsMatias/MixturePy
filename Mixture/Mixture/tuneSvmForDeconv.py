#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import os, math, sys

from sklearn.svm import LinearSVR

# Function nuSvr (Not import)
# Run NuSvr with expression Matrix and signature Matrix
# @method nuSvr
# @param [DataFrame] Signature
# @param [DataFrame] Expression
# @param [float] nu
# @param [float] delta
# @return [Array] [{ float } RMSEpredict, { objet } model]
def nuSvr(X, Y, nu, delta, verbose = False):

    # Run eSVR
    clf = LinearSVR (random_state = 0, max_iter = 40000)
    model = svr.fit(X, Y)
    
    # Get betas
    w = model.coef_

    # Set values i to zero where i < 0
    w = np.where(w<0, 0, w)    

    # Normalize data
    w = w/np.sum(w)

    # Set values i to zero where i < delta
    w = np.where(w<delta, 0, w)    
    
    # Product betas per rows X
    neww = X.apply(lambda row: row*w[0], axis=1)# Get Predict
    predict = neww.sum(axis=1)

    # Get Rmse predict for nuseq
    RmsePredict = math.sqrt(pow((Y - predict),2).mean())
    return [RmsePredict, clf]

# Function tuneSvmForDeconv
# Create result nuSvr list with nuseq
# @method tuneSvmForDeconv
# @param [DataFrame] Signature
# @param [DataFrame] Expression
# @param [array] nuseq
# @param [float] delta
# @return [DataFrame] [RMSEpredict, model]
def tuneSvmForDeconv(X, Y, nuseq, delta, verbose = False):
    result = list(map(lambda nu: nuSvr(X,Y, nu, delta, verbose), nuseq))
    listNuSvr = pd.DataFrame(result, columns=['RMSEpred', 'model'])
    
    # Get min RMSEPredict
    selector = listNuSvr.index[listNuSvr['RMSEpred'] == listNuSvr.min(axis = 0)[0]]
    return listNuSvr, listNuSvr.iloc[selector[0]]['model']
