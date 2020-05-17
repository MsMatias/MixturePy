import pandas as pd
import Mixture
import Mixture.Utils as mut

# Load Data Signature
# LM22 OR TIL10
X = mut.loadSignature('LM22')

# Read xlsx expression file
Y = pd.read_excel('data/NewmanFL.xlsx', sheet_name = 0) 

# Number of cores that will work
cores = 24

# Number of permutation samples
iters = 50

# Name the output file xlsx (without format)
output = 'Result_Newman'

# Run Mixer Function
if __name__ == '__main__':
    result, pValues = Mixture.Mixture(X, Y , cores, iters, output)
