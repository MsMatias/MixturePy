import pyreadr

result = pyreadr.read_r('betas.list.rds')

print(result.keys()) # let's check what objects we got: there is only None
df1 = result[None]
print(df1)