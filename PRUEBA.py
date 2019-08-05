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
import Mixture

if len(sys.argv) < 5:
	print('Write first the dataset and output name file')
	print('Example: [num cores] [iterators] [signature file] [expression file] [output file]')	
	sys.exit()
	
cores = int(sys.argv[1])
iters = int(sys.argv[2])
signature = sys.argv[3]
expression = sys.argv[4]
output = sys.argv[5]

# Read xlsx files
X = pd.read_excel(signature + '.xlsx', sheet_name = 0)
Y = pd.read_excel(expression + '.xlsx', sheet_name = 0)

# Run Mixer Function
if __name__ == '__main__':
	data = Mixture.Mixture(X, Y , cores, iters, output)
