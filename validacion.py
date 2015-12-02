__author__ = 'luisangel'

from regionesTweets import *



def get_user_node_n(gdb, n):
    query = "MATCH (n) WHERE n.location <> '' RETURN n LIMIT {n}"
    param = {'n': n}
    results = gdb.query(query, params=param, data_contents=True)
    if results.rows is not None:
        return results.rows
    return None


def get_user_node_chilean(gdb, n):
    query = "MATCH (n) WHERE n.location <> '' AND n.chile=true RETURN n LIMIT {n}"
    param = {'n': n}
    results = gdb.query(query, params=param, data_contents=True)
    if results.rows is not None:
        return results.rows
    return None


def get_user_node_foreign(gdb, n):
    query = "MATCH (n) WHERE n.location <> '' AND n.chile=false RETURN n LIMIT {n}"
    param = {'n': n}
    results = gdb.query(query, params=param, data_contents=True)
    if results.rows is not None:
        return results.rows
    return None


def main():
    gdb = get_conecction_neo()
    for n in range(200, 1001, 100):
        users = get_user_node_chilean(gdb, n/2)
        users.extend(get_user_node_foreign(gdb, n/2))
        with open('validate_%d.csv' % n, 'w') as outf:
            for user in users:
                usr = user[0]
                id_user, user_locate, frequency = user_locate_by_tweets(user)
                outf.write('%d\t%d\t%d\t%s\n' % (usr['id'], (1 if usr['chile'] is True else 0),
                                                 -1 if user_locate is None else (1 if user_locate == 'cl' else 0),
                                                 -1 if frequency is None else str(frequency)))
        print "Write validate_%d" % n

    pass


if __name__ == '__main__':
    main()
