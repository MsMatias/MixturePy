#!/usr/bin/env python
# coding: utf-8

# ---------------------------------------------------
# -------------------- WARNING ----------------------
# ---------------------------------------------------
# Do you need run this commands:
# ulimit -n 8192
# sudo sysctl -w fs.file-max=100000


import pandas as pd
import numpy as np
import os
import sys
import Mixture
import multiprocessing

#Library to read RDS format
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter

def convertRDS (X):
    readRDS = robjects.r['readRDS']
    df = readRDS(X)    
    with localconverter(robjects.default_converter + pandas2ri.converter):
        df = robjects.conversion.rpy2py(df)
        vector = np.array(df[0])
        pd.DataFrame(vector, index = brcapd[0].rownames, columns = brcapd[0].colnames)
        return pd

if len(sys.argv) < 5:
	print('Write first the dataset and output name file')
	print('Example: [num cores] [iterators] [signature file] [expression file] [output file]')	
	sys.exit()
	
cores = int(sys.argv[1])
iters = int(sys.argv[2])
signature = sys.argv[3]
expression = sys.argv[4]
output = sys.argv[5]

print('Num cores: ' + str(multiprocessing.cpu_count()))

if cores > multiprocessing.cpu_count():
	cores = multiprocessing.cpu_count()
    
# Verify file format (XLS or XLSX)    
#if X.find('.xls') != -1:
    #X = pd.read_excel(signature, sheet_name = 0)
#else if X.find('.rds') != -1:
    #X = convertRDS(signature)
        
    
#if Y.find('.xls') != -1:
    #Y = pd.read_excel(expression, sheet_name = 0)
#else if X.find('.rds') != -1:
    #Y = convertRDS(expression)
    
readRDS = robjects.r['readRDS']
    
X = pd.read_excel(signature, sheet_name = 0)
    
df = readRDS(Y)
with localconverter(robjects.default_converter + pandas2ri.converter):
    df = robjects.conversion.rpy2py(df)
    
vector = [x[2] for x in df]
Y = pd.DataFrame(np.column_stack(vector), index=df[0][2].rownames)

# Run Mixer Function
if __name__ == '__main__':
	data = Mixture.Mixture(X, Y , cores, iters, output)
