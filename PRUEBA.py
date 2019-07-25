#!/usr/bin/env python
# coding: utf-8

# ---------------------------------------------------
# -------------------- WARNING ----------------------
# ---------------------------------------------------
# Do you need run this commands:
# unlimit -n 8192
# sudo sysctl -w fs.file-max=100000


import pandas as pd
import numpy as np
import os
import sys
from Mixture import Mixture

if len(sys.argv) < 2:
	print('Write first the dataset and output name file')
	print('Example: TCGA output_TCGA')
	sys.exit()

# Read xlsx files
X = pd.read_excel('LM22Signature.xlsx', sheet_name = 0)
Y = pd.read_excel(sys.argv[1] + '.xlsx', sheet_name = 0)

# Run Mixer Function
if __name__ == '__main__':
	data = Mixture(X, Y , 4, 2, sys.argv[2])
