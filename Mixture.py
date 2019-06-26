#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import os
from multiprocessing import Pool
from Mixer import Mixer
import random

def sampleRandom(Y, n):
    Y = Y.iloc[:, 1:]
    vector = Y.to_numpy(copy=True)
    vector = vector.flatten()
    return vector[[random.randrange(Y.shape[0] * Y.shape[1]) for x in range(Y.shape[0])]]

def Mixture(X, Y, cores, iter = 100):

    # Run Mixer Function with original Expressions
    #orig = Mixer(X, Y , cores)

    #Get Media by subject
    totalMediaBySubject = Y.median(axis = 0, skipna = True)

    #Get Media by subject with intersect signatureMatrix
    totalMediaBySubjectLm22 = Y.loc[Y['Gene symbol'].isin(X['Gene symbol'])].median(axis = 0, skipna = True)
    
    #Get Media
    maxMediaFullCohort = max(np.median(Y.iloc[:, 1:]), 1)

    matRand = list()

    p=Pool(processes = cores)
    matRand = [p.apply(sampleRandom, args=(Y, Y.shape[0])) for i in range(iter)]
    matRand = map(list, zip(*matRand))
    matRand = pd.DataFrame(matRand, Y['Gene symbol'])
    return matRand



