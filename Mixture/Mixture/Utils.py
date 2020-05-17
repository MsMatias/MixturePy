import pkg_resources
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

def loadSignature(sig):
    if sig == 'LM22' or sig == 'lm22':        
        resource_path = pkg_resources.resource_filename(__name__, '/data/LM22Signature.xlsx')
        signature = pd.read_excel(resource_path, sheet_name = 0)
    elif sig == 'TIL10' or sig == 'til10':      
        resource_path = pkg_resources.resource_filename(__name__, '/data/TIL10_signature.xlsx')
        signature = pd.read_excel(resource_path, sheet_name = 0)
    elif sig == 'TIL9' or sig == 'til9':      
        resource_path = pkg_resources.resource_filename(__name__, '/data/TIL9_signature.xlsx')
        signature = pd.read_excel(resource_path, sheet_name = 0)
    else:
        signature = None
        print('Error, Type "LM22", "TIL10" or "TIL9')    
    
    return signature

def getPValues (x, i):
    return pd.DataFrame([sum(x.RMSEa < i.loc[:,'RMSEa']),
            sum(x.RMSEp < i.loc[:,'RMSEp']), 
            sum(x.Ra > i.loc[:,'Ra']), 
            sum(x.Rp > i.loc[:,'Rp'])]).T/i.shape[0]

def generateXlsx (result, pValues, nameFile):
    if len(nameFile) > 0:
        with pd.ExcelWriter( nameFile + '.xlsx') as writer:
            result.Subjects[0].MIXabs[0].to_excel(writer, sheet_name='Absolute')
            result.Subjects[0].MIXprop[0].to_excel(writer, sheet_name='Proportions')
            result.Subjects[0].ACCmetrix[0].to_excel(writer, sheet_name='Metrics')    
            if pValues is not None:
                pValues.to_excel(writer, sheet_name='Pvalues')
            result.usedGenes[0].to_excel(writer, sheet_name='UsedGenes', index=False)