# -*- coding: utf-8 -*-

__author__ = 'luisangel'

import sys
from collections import defaultdict
import time
import os
import codecs

import MySQLdb
import tweepy
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import exceptions

import credentials as k
import geodict.geodict_lib
from geolocation_method1 import *

REGIONES = {'2': 'Antofagasta',
            '3': 'Atacama',
            '4': 'Coquimbo',
            '10': 'Los Lagos',
            '7': 'Maule',
            '11': 'Aysen',
            '15': 'Arica y Parinacota',
            '9': 'Araucania',
            '14': 'Los Rios',
            '12': 'Magallanes',
            '1': 'Tarapaca',
            '5': 'Valparaiso',
            '8': 'Biobio',
            '6': 'O\'Higgins',
            '13': 'RM Santiago'
            }

BD_DATA = "data/tmp/"
users = defaultdict(lambda: {'followers': 0})
MIN_TWEETS = 3000
# Twitter API credentials
consumer_key = "dDA0nZHAw5mMWZt4YdVg4Uz1C"
consumer_secret = "YpQq0KI3hbR24rBmCHgwojPMdfUBP3WFhHKInoqjqCt7l4ZaoE"
access_key = "2559575756-AYu7FySmFcTGCP69cNr1YF0k0oJJySB5GKZdMTd"
access_secret = "MFyWfTO8nkTI03Y6cMh5oDnIJJzYxrvdbnRwt16CPdTZy"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)


def get_conecction_neo():
    gdb = GraphDatabase("http://neo4j:123456@localhost:7474/db/data/")
    return gdb


def set_chile_user(gdb, id_user, screen_name):
    with gdb.transaction(for_query=True) as tx:
        try:
            query = "MATCH(n) where n.id={id} set n+={region:'Chile', screen_name: {sn}} " \
                    "set n.chile=true remove n:Extranjero set n:Chile;"
            param = {'id': id_user, 'sn': screen_name}
            gdb.query(query, params=param)
        except exceptions.StatusException as e:
            print "Error in update user: " + e.result
            tx.rorollback()
            return


def getUserNodeById(gdb, id):
    query = "MATCH (n:Chile) WHERE n.id={id} RETURN n LIMIT 25"
    param = {'id': id}
    results = gdb.query(query, params=param, data_contents=True)

    return results.rows[0][0]


def get_connection():
    # Returns a connection object whom will be given to any DB Query function.

    try:
        connection = MySQLdb.connect(host=k.GEODB_HOST, port=3306, user=k.GEODB_USER,
                                     passwd=k.GEODB_KEY, db=k.GEODB_NAME)
        return connection
    except MySQLdb.DatabaseError, e:
        print 'Error %s' % e
        sys.exit(1)


# cleanTweet(tweet.text.encode("utf-8")).encode('utf-8')
def count_word_tweet(tw):
    w = tw.entities
    count = {'aroa': len(w['user_mentions']), 'gato': len(w['hashtags']), 'URL': len(w['urls']),
             'RT': int(hasattr(tw, 'retweeted_status'))}
    return count


def create_txt_tweets(alltweets, id_user):
    out_tweets = [tweet.id_str + "***,***" + delete_tildes(tweet.text).replace('\n', '') + "\n" for tweet in alltweets]
    with codecs.open('%stweets_per_component%s.txt' % (BD_DATA, id_user), encoding='utf-8', mode='w+') as f:
        f.writelines(out_tweets)
    pass


def get_id_region(name_region, connection):
    query = "SELECT idRegion FROM Region where name=%s;"
    try:
        cursor = connection.cursor()
        cursor.execute(query, (name_region,))
        data = cursor.fetchone()
        if data is None:
            return None
        else:
            return data[0]
    except MySQLdb.Error:
        print "Error: unable to fetch data"
        return -1
    pass


def close_connection(connection):
    connection.close()


def execute(connection, q_script):
    # executes a mysql script

    try:
        cursor = connection.cursor()
        cursor.execute(q_script)
    except MySQLdb.Error:
        print "Error: unable to execute"
        return -1


def get_all_tweets(id_user):
    # Twitter only allows access to a users most recent 3240 tweets with this method

    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    while True:
        try:
            new_tweets = api.user_timeline(user_id=id_user, count=200)
            break
        except tweepy.TweepError, e:
            if str(e.message) == 'Not authorized.':
                print "Not authorized id: " + str(id_user)
                return None
            if e.message[0]['code'] == 34:
                print "Not found ApiTwitter id: " + str(id_user)
                return
            if e.message[0]['code'] == 63:
                print 'Usuario suspendido:' + str(id_user)
                return None
            else:
                # hit rate limit, sleep for 15 minutes
                print 'Rate limited. Dormir durante 15 minutos. ' + e.reason
                time.sleep(15 * 60 + 15)
                continue
        except StopIteration:
            return

    if len(new_tweets) == 0:
        return None

    # save most recent tweets
    alltweets.extend(new_tweets)

    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print "getting tweets before %s" % (oldest)

        while True:
            try:
                # all subsiquent requests use the max_id param to prevent duplicates
                new_tweets = api.user_timeline(user_id=id_user, count=200, max_id=oldest)
                break
            except tweepy.TweepError, e:
                if str(e.message) == 'Not authorized.':
                    print "Not authorized id: " + str(id_user)
                    return None
                if e.message[0]['code'] == 34:
                    print "Not found ApiTwitter id: " + str(id_user)
                    return None
                if e.message[0]['code'] == 63:
                    print 'Usuario suspendido:' + str(id_user)
                    return None
                else:
                    # hit rate limit, sleep for 15 minutes
                    print 'Rate limited. Dormir durante 15 minutos. ' + e.reason
                    time.sleep(15 * 60 + 15)
                    continue
            except StopIteration:
                return None

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print "...%s tweets downloaded so far" % (len(alltweets))

    create_txt_tweets(alltweets, id_user)
    return len(alltweets)


def get_since_id(connection, idUser):
    query = "SELECT idTweet FROM Tweet where idUser=%s order by idTweet desc limit 1;"
    try:
        cursor = connection.cursor()
        cursor.execute(query, (idUser,))
        data = cursor.fetchone()
        if data is None:
            return None
        else:
            return data[0]
    except MySQLdb.Error:
        print "Error: unable to fetch data"
        return -1
    pass


def count_tweets(connection, idUser):
    query = "select count(*) from Tweet where idUser=%s;"
    try:
        cursor = connection.cursor()
        cursor.execute(query, (idUser,))
        data = cursor.fetchone()
        if data is None:
            return None
        else:
            return data[0]
    except MySQLdb.Error:
        print "Error: unable to fetch data"
        return -1
    pass


##### inicio limpieza de datos #####

def delete_tildes(s=''):
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))


def clean_tweet(text):
    # remove retweets
    text = re.sub('(RT|via)((?:\\b\\W*@\\w+)+)', '', text)
    # remove @otragente
    text = re.sub('@\\w+', '', text)
    # remueve simbolos de puntuacion
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    # remove números
    text = re.sub('\d', '', text)
    # remueve links
    text = re.sub("http([…]+|[\w]+)", '', text)
    # remueve htt...
    text = re.sub("ht[t]?…", "", text)
    # Convierte a minuscula
    text = text.lower()
    # remueve tildes
    text = delete_tildes(text.decode('utf-8'))
    return text


def get_user_foreign(gdb):
    query = "MATCH (n:Extranjero) RETURN n Limit 10"
    results = gdb.query(query, data_contents=True)
    return results.rows


def user_locate_by_tweets(user):
    date = user[0]
    location = unicode(date['location']).encode('utf-8')
    if len(location) != 0:
        resp = geodict.geodict_lib.find_chilean_locations_in_text(location)
        if len(resp) != 0:
            ub = resp[0]['found_tokens'][0]
            if ub['country_code'] != 'cl':
                return None, None, None
    user_f_name = os.path.join(BD_DATA, 'tweets_per_component' + str(date['id']) + '.txt')

    if os.path.exists(user_f_name) is False:
        nro_tweets = get_all_tweets(int(date['id']))
    else:
        archive = codecs.open(user_f_name, encoding='utf-8')
        tweets_list = list(archive)
        archive.close()
        nro_tweets = len(tweets_list) - 1

    if nro_tweets is None or nro_tweets == 0:
        return None, None, None

    return component_geocontextualizer_geodict(int(date['id']), 0.4, nro_tweets)


def get_screen_name(id_user):
    while True:
        try:
            matches = api.lookup_users(user_ids=[id_user])
            if len(matches) == 1:
                return matches[0].screen_name
            else:
                return ''
        except tweepy.TweepError, e:
            print "Primero: " + e.reason + " Finish in get screen name."
            if e.reason == 'Failed to send request: (\'Connection aborted.\', gaierror(-2, \'Name or service not known\'' \
                           '))':
                print 'Internet. Dormir durante 1 minuto. ' + e.message
                time.sleep(60)
                continue
            if e.reason == 'Failed to send request: HTTPSConnectionPool(host=\'api.twitter.com\', port=443): Read ' \
                           'timed out. (read timeout=60)':
                print 'Internet. Dormir durante 1 minuto. ' + e.message
                time.sleep(60)
                continue
            else:
                # hit rate limit, sleep for 15 minutes
                print 'Rate limited. Dormir durante 15 minutos. ' + e.reason
                time.sleep(15 * 60 + 15)
                continue
        except StopIteration:
            return ''


def main():
    gdb = get_conecction_neo()
    users = get_user_foreign(gdb)
    for user in users:

        id_user, user_locate, frequency = user_locate_by_tweets(user)
        if user_locate is None:
            continue
        print "User id: %d, country: %s, frequency: %s " % (id_user, user_locate, str(frequency))
        if user_locate == 'cl':
            sn = get_screen_name(id_user)
            set_chile_user(gdb, id_user, sn)


def region():
    date = {'id': 18488424}
    user_f_name = os.path.join(BD_DATA, 'tweets_per_component' + str(date['id']) + '.txt')

    if os.path.exists(user_f_name) is False:
        nro_tweets = get_all_tweets(int(date['id']))
    else:
        archive = codecs.open(user_f_name, encoding='utf-8')
        tweets_list = list(archive)
        archive.close()
        nro_tweets = len(tweets_list) - 1

    if nro_tweets is None or nro_tweets == 0:
        print "Not Tweets"
        return

    user_located = component_geocontextualizer_geodict(int(date['id']), 0.09, nro_tweets)

    print user_located


def get_tweets(connection):
    query = "SELECT Tweet.text FROM Tweet;"
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        if data is None:
            return None
        else:
            for t in data:
                print t[0]
    except MySQLdb.Error:
        print "Error: unable to fetch data"
        return -1
    pass


def prueba():
    gdb = get_conecction_neo()

    print getUserNodeById(gdb, 207468255)


if __name__ == '__main__':
    prueba()
