# MIXTUREpy

A v-SVR based noise constrained Recursive Feature Extraction algorithm for robust deconvolution of cell-types mixture from molecular signatures in python

Since the significant impact of immunotherapy in cancer, the estimation of the immune cell-type proportions present in a tumor becomes crucial. Currently, the deconvolution of the cell mixture content of a tumor is carried out by different analytic tools, yet the accuracy of inferred cell type proportions has room for improvement. We improve tumor immune environment characterization developing MIXTURE, an analytical method based on a noise constrained recursive variable selection for a support vector regression

## Getting Started

* [User Guide](https://github.com/MsMatias/MixturePy/wiki)

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

The current "functional like" version of the software requires the following libraries, however, this package download automatically yours dependencies
 * python3 >= 3.6
 * pip3
 * xlrd
 * scikit-learn
 * openpyxl
 * pandas
 * numpy
 * multiprocessing
 * joblib
 

### Installing
* [User Guide](https://github.com/MsMatias/MixturePy/wiki)

## Running MIXTURE

* [User Guide](https://github.com/MsMatias/MixturePy/wiki)

This example tends to estimate the same pure cell-types from LM22 signature matrix from [Newman et al.](http://www.nature.com/nmeth/journal/v12/n5/abs/nmeth.3337.html)
```
import pandas as pd
import Mixture
import Mixture.Utils as mut

# Load Data Signature
# LM22 OR TIL10
X = mut.loadSignature('LM22')

# Read xlsx expression file
Y = pd.read_excel('data/NewmanFL.xlsx', sheet_name = 0) 

# Number of cores that will work
cores = 4

# Number of permutation samples
iters = 500

# Name the output file xlsx (without format)
output = 'Result_Newman'

# Run Mixer Function
if __name__ == '__main__':
    result, pValues = Mixture.Mixture(X, Y , cores, iters, output)
```

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Elmer Andrés Fernández** - *Initial work* - CONICET, Catholic University of Cordoba - [Profile](https://www.researchgate.net/profile/Elmer_Fernandez)
* **Miranda Matias Samuel** - *Developer* - Catholic University of Cordoba

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
