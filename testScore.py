import pandas as pd
import Mixture
import Mixture.Utils as mut
import score

# Load Data Signature
# LM22 OR TIL10
X = pd.read_excel('data/TIL9_signature.xlsx', sheet_name = 0)

# Read xlsx expression file
Y = pd.read_excel('data/TIL9_signature.xlsx', sheet_name = 0) 

# Number of cores that will work
cores = 8

# Number of permutation samples
iters = 1000

# Name the output file xlsx (without format)
output = 'Result_TIL9_TIL9'

# Run Mixer Function
if __name__ == '__main__':
    result, pValues = Mixture.Mixture(X, Y, cores, iters, output, score.Score)