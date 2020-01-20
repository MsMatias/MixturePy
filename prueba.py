def funcion(x):
    for i in x:
        print(i)
    return 'termino'

def inicio(y, func = funcion):
    r = func(y)
   # print(r)

inicio([1,2,3,4])