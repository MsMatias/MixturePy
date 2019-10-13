# MIXTUREpy

A v-SVR based noise constrained Recursive Feature Extraction algorithm for robust deconvolution of cell-types mixture from molecular signatures in python

Since the significant impact of immunotherapy in cancer, the estimation of the immune cell-type proportions present in a tumor becomes crucial. Currently, the deconvolution of the cell mixture content of a tumor is carried out by different analytic tools, yet the accuracy of inferred cell type proportions has room for improvement. We improve tumor immune environment characterization developing MIXTURE, an analytical method based on a noise constrained recursive variable selection for a support vector regression

## Getting Started

* [User Guide](https://docs.google.com/presentation/d/1lv8YGpmyuf9n9UUKAm5GavVHrqdSYf9m1UrzU_a0sK8/edit?usp=sharing)

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

The current "functional like" version of the software requires the following libraries, however, this package download automatically yours dependencies
 * pandas
 * numpy
 * sklearn
 * rpy2
 * multiprocessing
 * joblib

### Installing
* [User Guide](https://docs.google.com/presentation/d/1lv8YGpmyuf9n9UUKAm5GavVHrqdSYf9m1UrzU_a0sK8/edit?usp=sharing)

## Running MIXTURE

* [User Guide](https://docs.google.com/presentation/d/1lv8YGpmyuf9n9UUKAm5GavVHrqdSYf9m1UrzU_a0sK8/edit?usp=sharing)

This example tends to estimate the same pure cell-types from LM22 signature matrix from NewMan
```
# Read xlsx files
X = pd.read_excel('data/LM22_signature.xlsx', sheet_name = 0) 
Y = pd.read_excel('data/NewmanFL.xlsx', sheet_name = 0) 

#Number of cores that will work
core = 4

#Number of permutation samples
iter = 500

#Name the output file xlsx (without format)
output = 'Result_Newman'

# Run Mixer Function
if __name__ == '__main__':
    result, pValues = Mixture.Mixture(X, Y , cores, iters, output)

```

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Elmer Andrés Fernández** - *Initial work* - [Profile](https://www.researchgate.net/profile/Elmer_Fernandez)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
