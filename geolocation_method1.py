# -*- coding: utf-8 -*-

import global_vars as gv
import geodict.geodict_lib
import re
import unicodedata
import string

def delete_tildes(s=''):
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))


def clean_tweets_text(text):
    '''Clean all text to drop hashtag symbol and modify some words to facilitate location extract'''
    text = re.sub(r"\d*\*\*\*,\*\*\*", '', text)
    text = text.replace('#', '')
    # remove punctuation symbols
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    # remove number
    text = re.sub('\d', '', text)
    # Converted to lowercase
    text = text.lower()
    # Replace newline
    text = text.replace('\n', ' ')
    # remove accents
    text = delete_tildes(text.decode('utf-8'))
    #ISO-8859-1
    return u''.join(text).encode('utf-8').strip()

def component_geocontextualizer_geodict(component_id, tw_threshold, n_tweets):
    ''' Find chilean locations in tweets and some other country names, when found  locations
    are not frequent enough, the component location isn't saved for verify locations after
    with the classifier'''
    tweets_filename = gv.temp_dir + gv.tweets_filename_base + str(component_id) + '.txt'
    tweets_file = open(tweets_filename, 'r')
    text = tweets_file.read()
    #text = u''.join(text).encode('utf8').strip()
    text = clean_tweets_text(text)
    tweets_file.close()

    locs_dict = {}
    max_locs = 0
    all_tokens = []

    # Obtain all Chilean cities locations and country names in tweets (not international cities)
    all_tokens += geodict.geodict_lib.find_chilean_locations_in_text(text)

    # Add location data to a dictionary with its frequency and save max frequency (max_locs)   
    for token in all_tokens:
        location = token['found_tokens'][0]
        place = location['country_code']
        if place in locs_dict:
            locs_dict[place]['count'] += 1
            if locs_dict[place]['count'] > max_locs:
                max_locs = locs_dict[place]['count']
        else:
            locs_dict[place] = {}
            locs_dict[place]['count'] = 1
            locs_dict[place]['lat'] = location['lat']
            locs_dict[place]['lon'] = location['lon']
            locs_dict[place]['country_code'] = location['country_code']
            if locs_dict[place]['count'] > max_locs:
                max_locs = locs_dict[place]['count']

    # Remove those words that haven't appear enough given a fq_threshold for frequency percentage
    # and also left a mark when a word is the word with more frequency but it hasn't appear enough 
    # given a tw_threshold for tweets percentage
    # frequency_percentage = count/max_locs 
    # tweets_percentage = count/n_tweets
    key_to_remove = []
    need_verification = True
    freq_location = ''
    for (key, value) in locs_dict.items():

        locs_dict[key]['tweets_percentage'] = float(value['count']) / float(n_tweets)
        locs_dict[key]['n_tweets'] = n_tweets

        if locs_dict[key]['count'] == max_locs:
            freq_location = key
            if locs_dict[key]['tweets_percentage'] > tw_threshold:
                need_verification = False

    for (key, value) in locs_dict.items():
        location_name = re.sub("'", "", key)
        words = location_name.split()
        location_name = "'"
        for w in words:
            location_name = location_name + w[0].upper() + w[1:] + ' '
        location_name = location_name[:-1] + "'"

        # Print result in screen
        #print "component_id="+str(component_id)+ ", location_names=" +location_name + ", frequency=" + str(value['frequency_percentage']) + ", tweets_percentage=" + str(value['tweets_percentage'])

    max_country = locs_dict.get(freq_location)
    if (need_verification is False) & (max_country is not None):
        result = (component_id, freq_location, max_country['tweets_percentage'])
        return result
    return None, None, None


def geocontextualizer_prueba(component_id, tw_threshold, n_tweets):
    ''' Find chilean locations in tweets and some other country names, when found  locations
    are not frequent enough, the component location isn't saved for verify locations after
    with the classifier'''
    tweets_filename = gv.temp_dir + gv.tweets_filename_base + str(component_id) + '.txt'
    tweets_file = open(tweets_filename, 'r')
    text = tweets_file.read()
    #text = u''.join(text).encode('utf8').strip()
    text = clean_tweets_text(text)
    tweets_file.close()

    locs_dict = {}
    max_locs = 0
    all_tokens = []

    # Obtain all Chilean cities locations and country names in tweets (not international cities)
    all_tokens += geodict.geodict_lib.find_chilean_locations_in_text(text)

    # Add location data to a dictionary with its frequency and save max frequency (max_locs)
    for token in all_tokens:
        location = token['found_tokens'][0]
        place = location['country_code']
        if place in locs_dict:
            locs_dict[place]['count'] += 1
            if locs_dict[place]['count'] > max_locs:
                max_locs = locs_dict[place]['count']
        else:
            locs_dict[place] = {}
            locs_dict[place]['count'] = 1
            locs_dict[place]['lat'] = location['lat']
            locs_dict[place]['lon'] = location['lon']
            locs_dict[place]['country_code'] = location['country_code']
            if locs_dict[place]['count'] > max_locs:
                max_locs = locs_dict[place]['count']

    # Remove those words that haven't appear enough given a fq_threshold for frequency percentage
    # and also left a mark when a word is the word with more frequency but it hasn't appear enough
    # given a tw_threshold for tweets percentage
    # frequency_percentage = count/max_locs
    # tweets_percentage = count/n_tweets
    key_to_remove = []
    need_verification = True
    freq_location = ''
    for (key, value) in locs_dict.items():

        locs_dict[key]['tweets_percentage'] = float(value['count']) / float(n_tweets)
        locs_dict[key]['n_tweets'] = n_tweets

        if locs_dict[key]['count'] == max_locs:
            freq_location = key
            if locs_dict[key]['tweets_percentage'] > tw_threshold:
                need_verification = False

    for (key, value) in locs_dict.items():
        location_name = re.sub("'", "", key)
        words = location_name.split()
        location_name = "'"
        for w in words:
            location_name = location_name + w[0].upper() + w[1:] + ' '
        location_name = location_name[:-1] + "'"

        # Print result in screen
        print "component_id="+str(component_id)+ ", location_names=" +location_name + ", tweets_percentage=" + str(value['tweets_percentage'])



if __name__ == '__main__':
#    geocontextualize_component_by_id(7307)

    n_tweets = 1307
    component_id = 3413562833
    geocontextualizer_prueba(component_id, 0.09, n_tweets)