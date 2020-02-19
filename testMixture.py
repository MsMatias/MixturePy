import pandas as pd
import Mixture
import Mixture.Utils as mut

# Load Data Signature
# LM22 OR TIL10
X = pd.read_excel('data/TIL9_signature.xlsx', sheet_name = 0)
X2 = pd.read_excel('data/TIL10_signature.xlsx', sheet_name = 0)
X3 = pd.read_excel('data/LM22Signature.xlsx', sheet_name = 0)

# Read xlsx expression file
Y = pd.read_excel('data/Celllines.xlsx', sheet_name = 0) 

Y = Y.iloc[: , 1:]

# Number of cores that will work
cores = 24

# Number of permutation samples
iters = 1

# Name the output file xlsx (without format)
output = 'Result_Cellines_TIL9_Mixture'
output2 = 'Result_Cellines_TIL10_Mixture'
output3 = 'Result_Cellines_LM22_2_Mixture'

# Run Mixer Function
if __name__ == '__main__':
#    result, pValues = Mixture.Mixture(X, Y , cores, iters, output)
#    result, pValues = Mixture.Mixture(X2, Y , cores, iters, output2)
    result, pValues = Mixture.Mixture(X3, Y , cores, iters, output3)
