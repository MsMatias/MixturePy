import pandas as pd
import numpy as np
from sklearn.svm import LinearSVR
from sklearn.datasets import make_regression
import random, math
from joblib import Parallel, delayed

def Score (X, Y, cores):

    # Normalize signature Matrix
    #mean = X.iloc[:, 1:].mean()
    #std = X.iloc[:, 1:].stack().std()
    #X.iloc[:, 1:] = (X.iloc[:, 1:] - mean.mean()) / std

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

    #Yn = pd.DataFrame(scale(Y), index=Y.index, columns=Y.columns)
    Yn = Y

    score_adj = list()
    print('Processing...')

    score_adj = Parallel(n_jobs=cores, backend='threading')(delayed(proccessData)(X = X, Y = j, subject = i, verbose = 1) for i, j in Yn.iteritems())

    matWa = pd.DataFrame()
    matWp = pd.DataFrame()
    matRes = pd.DataFrame()

    for i in score_adj:
        matWa = matWa.append(i.Wa, ignore_index=True)
        matWp = matWp.append(i.Wp, ignore_index=True)
        matRes = matRes.append(pd.DataFrame([[i.RMSEa, i.RMSEp, i.Ra, i.Rp]], columns=['RMSEa', 'RMSEp', 'Ra', 'Rp']), ignore_index=True)
  
    matWa.index = Y.columns.values
    matWa.columns = X.columns.values

    matWp.index = Y.columns.values
    matWp.columns = X.columns.values

    matRes.index = matWp.index.values

    return(pd.DataFrame([[matWa, matWp, matRes]], columns=['MIXabs', 'MIXprop', 'ACCmetrix']))


def proccessData (X, Y, subject, verbose):

    XX = X

    svr = LinearSVR (random_state = 0)
    model = svr.fit(X, Y)
    score = model.coef_

    # The scores less 0 change to 0
    score[np.where(score<0)] = 0

    wAbs = score

    w = score/sum(score)

    w = pd.DataFrame(w, XX.columns).T

    wOut = pd.DataFrame(wAbs, XX.columns).T

    # Create wSel with all values in zero
    wSel = [0 for x in range(len(X.columns))]
    wSel = pd.DataFrame(wSel, X.columns).T
    wSel.loc[:, wSel.columns.isin(wOut.columns)] = wOut

    u = X.apply(lambda x: x * wSel.iloc[0], axis = 1).values
    k = np.sum(u, axis = 1)
    nusvm = math.sqrt(pow((k - Y.values),2).mean())
    corrv = np.corrcoef(k, Y.values)

    w = wSel/wSel.sum().sum()
    uW = X.apply(lambda x: x * w.iloc[0], axis = 1).values
    kW = np.sum(uW, axis = 1)
    nusvmW = math.sqrt(pow((kW - Y.values),2).mean())
    corrvW = np.corrcoef(kW, Y.values)

    result = pd.Series([wSel, w, nusvm, nusvmW, corrv[0][1], corrvW[0][1]], index =['Wa', 'Wp', 'RMSEa', 'RMSEp', 'Ra', 'Rp'])
    return result