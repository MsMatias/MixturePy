import pandas as pd
import numpy as np
import random
import multiprocessing

def sampleRandom (Y, verbose = 0):
        
    if verbose == 1:
        print('--------------------------------------------------')
        print('Creating Subject Nro. Processor: ' + str(multiprocessing.current_process()))
        print('--------------------------------------------------')

    Y = Y.iloc[:, 1:]
    vector = Y.to_numpy(copy=True)    

    return vector

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