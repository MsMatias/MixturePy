import pandas as pd
import numpy as np
import random
import multiprocessing

def sampleRandom (Y, i, verbose = 0):
        
    if verbose == 1:
        print('--------------------------------------------------')
        print('Creating Subject: ' + str(i) + ' Nro. Processor: ' + str(multiprocessing.current_process()))
        print('--------------------------------------------------')

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
        pValues.to_excel(writer, sheet_name='Pvalues')
        result.usedGenes[0].to_excel(writer, sheet_name='UsedGenes')