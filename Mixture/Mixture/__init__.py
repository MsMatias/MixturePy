#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import os
from Mixture.Mixer import Mixer
import Mixture.Utils as Utils
from joblib import Parallel, delayed

def Mixture (X, Y, cores = 1, iter = 100, nameFile = 'output'):
    
    # Intersection between X and Y
    geneList = X.loc[X['Gene symbol'].isin(Y['Gene symbol'])].sort_values(by=['Gene symbol'])['Gene symbol']

    print('Running mixer with subjects (Count: ' + str(Y.shape[1]) + ')...')
    # Run Mixer Function with original Expressions
    orig = Mixer(X, Y, cores)

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

    if iter > 0:

        print('Creating population (Count: ' + str(iter) + ')...')

        matRand = Parallel(n_jobs=cores, backend='multiprocessing')(delayed(Utils.sampleRandom)(Y = Y, i = i, verbose = 1) for i in range(iter))

        #for i in range(iter):
        #    matRand.append(Utils.sampleRandom(Y, i, 1))

        print('Finish creating population')

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

        pValues = result.Subjects[0].ACCmetrix[0].apply(Utils.getPValues, args=(result.PermutedMetrix[0], ), axis = 1)
        pValues = pd.DataFrame(pValues.values.tolist(), index = pValues.index, columns=['RMSEa', 'RMSEa', 'Ra', 'Rp']) 

        print('Finish')

        Utils.generateXlsx (result, pValues, nameFile)

        return result, pValues
    else:
        
        result = pd.DataFrame([orig, geneList], ['Subjects', 'usedGenes']).T

        result.usedGenes[0] = pd.DataFrame(result.usedGenes[0])
        
        print('Finish')

        Utils.generateXlsx (result, None, nameFile)

        return result, None



