#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import os
import sys
from Mixture import Mixture
from multiprocessing import Pool
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

if len(sys.argv) < 2:
	print('Write first the dataset and output name file')
	print('Example: TCGA output_TCGA')
	sys.exit()

# Read xlsx files
X = pd.read_excel('LM22Signature.xlsx', sheet_name = 0)
Y = pd.read_excel(sys.argv[1] + '.xlsx', sheet_name = 0)

# Run Mixer Function
data = Mixture(X, Y , 1, 2, nameFile = sys.argv[2])


data

