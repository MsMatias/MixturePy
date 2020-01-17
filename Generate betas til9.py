#!/usr/bin/env python
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
import os
import sys
import Mixture
import multiprocessing
from joblib import Parallel, delayed
from random import seed
from random import sample 
from random import randint


# In[2]:


lines = [2, 6]
cpu = multiprocessing.cpu_count()
rango = 1000


# In[3]:


dataFrameSignature = pd.read_excel('data/Pre.proccessor.xlsx', sheet_name = 0) 


# In[4]:


def createBetas (X, a, b, n):

    ns = randint(a, b)
    r = np.random.uniform(1, 0.2, ns)
    rn = r/r.sum()
    id = sample(range(n-1), ns)
    betas = np.repeat(.0, n, axis=0)
    for index, i in enumerate(id, start = 0):
        betas[i] = rn[index]

    vector = X.to_numpy(copy=True)    
    vector = vector.flatten()
        
    A = np.dot(X, betas) + vector[sample(range(len(vector)), len(X.index))]

    return betas, id, A


# In[5]:


X = dataFrameSignature.iloc[:, 1:]

subjects = Parallel(n_jobs=cpu, backend='threading')(delayed(createBetas)(X = X, a = lines[0], b = lines[1], n = len(X.columns)) for i in range(rango))

# Getting expression matrix
vector = [x[2] for x in subjects]
columns = ['V' + str(x+1) for x in range(len(subjects))]
Y2 = pd.DataFrame(np.column_stack(vector), columns=columns)
Y2.insert(0, 'Gene symbol', dataFrameSignature['Gene symbol'])

# Getting Real Betas Matrix
vector = [x[0] for x in subjects]
columns = ['V' + str(x+1) for x in range(len(subjects))]
betas = pd.DataFrame(np.column_stack(vector), columns=columns)

X = dataFrameSignature

vector = [len(x[1]) for x in subjects]
ids = pd.DataFrame(np.column_stack(vector))   


# In[10]:


betas


# In[ ]:


#Generate xlsx
with pd.ExcelWriter('betas.list.TIL9.xlsx') as writer:
    betas.to_excel(writer, sheet_name='beta')
    ids.to_excel(writer, sheet_name='id')
    Y2.to_excel(writer, sheet_name='A')

