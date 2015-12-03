__author__ = 'luisangel'

import geodict.geodict_lib
import os
from regionesTweets import get_conecction_neo
from neo4jrestclient import exceptions
BD_DATA = "data/tmp/"


def getUserNodeById(gdb, id):
    try:
        while True:
            query = "MATCH (n:User) WHERE n.id={id} RETURN n LIMIT 25"
            param = {'id': id}
            results = gdb.query(query, params=param, data_contents=True)

            return results.rows[0][0]
    except exceptions.StatusException as e:
        return "Error: "+e.result



def main():
    gdb = get_conecction_neo()

    print getUserNodeById(gdb, 207468255)

def prueba():
    """

    :rtype : object
    """
    return None, 'Luis', None
if __name__ == '__main__':
    main()