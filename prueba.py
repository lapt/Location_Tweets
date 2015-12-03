__author__ = 'luisangel'

import geodict.geodict_lib
import os
from regionesTweets import get_conecction_neo
from neo4jrestclient import exceptions
BD_DATA = "data/tmp/"


def set_chile_user(gdb, id_user, screen_name):
    with gdb.transaction(for_query=True) as tx:
        try:
            query = "MATCH(n:User) where n.id={id} set n+={region:'Chile', screen_name: {sn}} " \
                    "set n.chile=true remove n:Extranjero set n:Chile;"
            param = {'id': id_user, 'sn': screen_name}
            gdb.query(query, params=param)
            return "Victoria!!!"
        except exceptions.StatusException as e:
            print "Error in update user: " + e.result
            tx.rorollback()
            return "Derrota !!! "


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

    gdb = get_conecction_neo()
    print set_chile_user(gdb, 207468255, 'pablitocachureo')
if __name__ == '__main__':
    prueba()