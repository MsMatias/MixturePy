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
    return pd.DataFrame([sum(x.RMSEa < i.loc[:,'RMSEa']),
            sum(x.RMSEp < i.loc[:,'RMSEp']), 
            sum(x.Ra > i.loc[:,'Ra']), 
            sum(x.Rp > i.loc[:,'Rp'])]).T/i.shape[0]

def generateXlsx (result, pValues, nameFile):
    with pd.ExcelWriter( nameFile + '.xlsx') as writer:
        result.Subjects[0].MIXabs[0].to_excel(writer, sheet_name='Absolute')
        result.Subjects[0].MIXprop[0].to_excel(writer, sheet_name='Proportions')
        result.Subjects[0].ACCmetrix[0].to_excel(writer, sheet_name='Metrics')        
        pValues.to_excel(writer, sheet_name='Pvalues')
        result.usedGenes[0].to_excel(writer, sheet_name='UsedGenes')