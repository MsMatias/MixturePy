#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import os
from Mixture import Mixture
from multiprocessing import Pool
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

# Read xlsx files
X = pd.read_excel('LM22Signature.xlsx', sheet_name = 0)
Y = pd.read_excel('BRCA.TCGA.xlsx', sheet_name = 0)

# Run Mixer Function
data = Mixture(X, Y , 1, 2, nameFile = 'Salida_Cancer')


data

