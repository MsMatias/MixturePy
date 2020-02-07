#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import os

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import scale
from joblib import Parallel, delayed

# Function Score
# Main Function
# @method Score
# @param [DataFrame] Signature
# @param [DataFrame] Expression
# @param [int] num Cores
# @return -------
def Score(X, Y, cores):

    print('Normalizing data')
    
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

    out = list()
    print('Processing...')

    out = Parallel(n_jobs=cores, backend='threading')(delayed(linearDeconv)(X = X, Y = j) for i, j in Yn.iteritems())
             
    #out = [x.recv() for x in pipe_list]

    print('_____________________________________________________________________')
    
    print('Finish Svm')

    return pd.DataFrame(out)

def linearDeconv (X, Y):
    svr = LinearSVR(random_state=0)
    model = svr.fit(X, Y)
    score = model.coef_
    score[np.where(score<0)] = 0 
    return (score/sum(score))
