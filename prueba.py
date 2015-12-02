__author__ = 'luisangel'

import geodict.geodict_lib
import os
BD_DATA = "data/tmp/"
def main():
    user_fname = os.path.join(BD_DATA, 'tweets_per_component7307.txt')
    try:
        archivo = open(user_fname)
        resp = list(archivo)
        archivo.close()
        print len(resp)
    except IOError:
        print 'No se pudo abrir el archivo'
    pass

def prueba():
    """

    :rtype : object
    """
    return None, 'Luis', None
if __name__ == '__main__':
    a, b, c = prueba()
    print(a)
    print(b)
    print(c)