import pandas as pd
import Mixture
import Mixture.Utils as mut

# Load Data Signature
# LM22 OR TIL10

X = pd.read_excel('data/LM22Signature.xlsx', sheet_name = 0)

# Read xlsx expression file
#Y = X #pd.read_excel('EPICsig_betas.xlsx', sheet_name = 0)
#Y = pd.read_excel('data/NewmanFL.xlsx', sheet_name = 0)
Y = pd.read_excel('data/Celllines.xlsx', sheet_name = 0)

Y = Y.iloc[: , 1:]
#X = X.iloc[: , 1:]

# Number of cores that will work
cores = 24

# Number of permutation samples
iters = 1000

# Name the output file xlsx (without format)
output = 'Result_Mixture_esvr_celllines_lm22'

# Run Mixer Function
if __name__ == '__main__':
#    result, pValues = Mixture.Mixture(X, Y , cores, iters, output)
#    result, pValues = Mixture.Mixture(X2, Y , cores, iters, output2)
    result, pValues = Mixture.Mixture(X, Y , cores, iters, output)
