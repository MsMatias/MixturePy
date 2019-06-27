#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import os
from multiprocessing import Pool
from Mixer import Mixer
import random

def sampleRandom (Y, n):
    Y = Y.iloc[:, 1:]
    vector = Y.to_numpy(copy=True)
    vector = vector.flatten()
    return vector[[random.randrange(Y.shape[0] * Y.shape[1]) for x in range(Y.shape[0])]]

def getPValues (x, i):
    return pd.DataFrame([sum(i.loc[:,'RMSEa'] < x.RMSEa),
            sum(i.loc[:,'RMSEp'] < x.RMSEp), 
            sum(i.loc[:,'Ra'] > x.Ra), 
            sum(i.loc[:,'Rp'] > x.Rp)]).T/len(i)

def generateXlsx (result, pValues, nameFile):
    with pd.ExcelWriter( nameFile + '.xlsx') as writer:
        result.Subjects[0].MIXabs[0].to_excel(writer, sheet_name='Absolute')
        result.Subjects[0].MIXprop[0].to_excel(writer, sheet_name='Proportions')
        result.Subjects[0].ACCmetrix[0].to_excel(writer, sheet_name='Metrics')
        result.usedGenes[0].to_excel(writer, sheet_name='UsedGenes')
        pValues.to_excel(writer, sheet_name='Pvalues')

def Mixture (X, Y, cores, iter = 100, nameFile = 'output'):

    # Intersection between X and Y
    geneList = X.loc[X['Gene symbol'].isin(Y['Gene symbol'])].sort_values(by=['Gene symbol'])['Gene symbol']

    print('Running mixer with subjects (Count: ' + str(Y.shape[1]) + ')...')
    # Run Mixer Function with original Expressions
    orig = Mixer(X, Y , cores)

    print(orig)

    print('Finish mixer')
    
    print('Get Medias')
    # Get Media by subject
    totalMediaBySubject = Y.median(axis = 0, skipna = True)

    # Get Media by subject with intersect signatureMatrix
    totalMediaBySubjectLm22 = Y.loc[Y['Gene symbol'].isin(X['Gene symbol'])].median(axis = 0, skipna = True)
    
    # Get Media
    maxMediaFullCohort = max(np.median(Y.iloc[:, 1:]), 1)

    temp = pd.DataFrame([totalMediaBySubjectLm22/totalMediaBySubject, totalMediaBySubjectLm22/maxMediaFullCohort], index=['IscBySbj', 'IscPob']).T
    orig.ACCmetrix[0] = pd.concat([orig.ACCmetrix[0], temp], sort = False, axis = 1) 
  
    matRand = list()

    #matRand = [pd.apply(sampleRandom, args=(Y, Y.shape[0])) for i in range(iter)]
    for i in range(iter):
            matRand.append(sampleRandom(Y, Y.shape[0]))

    matRand = map(list, zip(*matRand))
    matRand = pd.DataFrame(matRand, Y['Gene symbol'])
    matRand.reset_index(drop=True, inplace=True)
    matRand = pd.concat([Y['Gene symbol'], matRand], sort = False, axis = 1)

    print('Finish')

    print('Running mixer with porpulationBased (Count: ' + str(matRand.shape[1]) + ')')
    # Run Mixer Function with Random Matrix
    outMix = Mixer(X, matRand, cores)

    #geneList = pd.DataFrame(geneList)

    result = pd.DataFrame([orig, outMix.ACCmetrix[0], geneList], ['Subjects', 'PermutedMetrix', 'usedGenes']).T

    result.usedGenes[0] = pd.DataFrame(result.usedGenes[0])

    pValues = list()

    pValues = result.Subjects[0].ACCmetrix[0].apply(getPValues, args=(result.PermutedMetrix[0], ), axis = 1)
    pValues = pd.DataFrame(pValues.values.tolist(), index = pValues.index, columns=['RMSEa', 'RMSEa', 'Ra', 'Rp']) 

    print('Finish')

    generateXlsx (result, pValues, nameFile)

    return result, pValues



