import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
base = importr('base')

# evaluate locally a remote R script
base.source("http://www.bioconductor.org/biocLite.R")
bioclite = robjects.globalenv['biocLite']

# download and install a bioconductor package
bioclite("limma")
