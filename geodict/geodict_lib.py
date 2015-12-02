import MySQLdb, string
import geodict_config


def text_format(text=''):
    text_list = text.split()
    for city in chilean_cities_cache.keys():
        text_list = [(city if t.find(city) >= 0 else t) for t in text_list]
    text_list = [('chile' if t.find('chile') >= 0 else t) for t in text_list]
    return ' '.join(text_list)


def find_chilean_locations_in_text(text):
    ''' This function takes an unstructured text string and returns a list of all the
    fragments it could identify as chilean regions or chilean cities and other 
    country names too, together with lat/lon positions'''
    try:
        cursor = get_database_connection()
    except:
        print "Database connection failed. Have you set up geodict_config.py with your credentials?"
        return None

    setup_countries_cache(cursor)
    setup_chilean_cities_cache(cursor)

    text = text_format(text)

    current_index = len(text)-1
    result = []
    # This loop goes through the text string in *reverse* order. Since locations in English are typically
    # described with the broadest category last, preceded by more and more specific designations towards
    # the beginning, it simplifies things to walk the string in that direction too
    while current_index>=0:
        current_word, pulled_index, ignored_skipped = pull_word_from_end(text, current_index)
        lower_word = current_word.lower()
        could_be_country = lower_word in countries_cache
        could_be_chilean_city = lower_word in chilean_cities_cache
        
        if not could_be_country and not could_be_chilean_city:
            current_index = pulled_index
            continue

        # This holds the results of the match function for the final element of the sequence. This lets us
        # optimize out repeated calls to see if the end of the current string is a country for example
        match_cache = {}
    
        # These 'token sequences' describe patterns of discrete location elements that we'll look for.
        for token_sequence in token_sequences:
            
            # The sequences are specified in the order they'll occur in the text, but since we're walking
            # backwards we need to reverse them and go through the sequence in that order too
            token_sequence = token_sequence[::-1]
    
            # Now go through the sequence and see if we can match up all the tokens in it with parts of
            # the string
            token_result = None
            token_index = current_index
            for token_position, token_name in enumerate(token_sequence):
            
                # The token definition describes how to recognize part of a string as a match. Typical
                # tokens include country, city and region names
                token_definition = token_definitions[token_name]  
                match_function = token_definition['match_function']
                
                # This logic optimizes out repeated calls to the same match function
                if token_position == 0 and token_name in match_cache:
                    token_result = match_cache[token_name]
                else:
                    # The meat of the algorithm, checks the ending of the current string against the
                    # token testing function, eg seeing if it matches a country name
                    token_result = match_function(cursor, text, token_index, token_result)
                    if token_position == 0:
                        match_cache[token_name] = token_result
                
                if token_result is None:
                    # The string doesn't match this token, so the sequence as a whole isn't a match
                    break
                else:
                    # The current token did match, so move backwards through the string to the start of
                    # the matched portion, and see if the preceding words match the next required token
                    token_index = token_result['found_tokens'][0]['start_index']-1
            
            # We got through the whole sequence and all the tokens match, so we have a winner!
            if token_result is not None:
                break
            
        if token_result is None:
            # None of the sequences matched, so back up a word and start over again
            ignored_word, current_index, end_skipped = pull_word_from_end(text, current_index)
        else:
            # We found a matching sequence, so add the information to the result
            result.append(token_result)
            found_tokens = token_result['found_tokens']
            current_index = found_tokens[0]['start_index']-1
    
    # Reverse the result so it's in the order that the locations occured in the text
    result = result[::-1]
    
    return result

countries_cache = {}

def setup_countries_cache(cursor):
    
    select = 'SELECT * FROM countries;'
    cursor.execute(select)
    candidate_rows = cursor.fetchall()
    
    for candidate_row in candidate_rows:
        candidate_dict = get_dict_from_row(cursor, candidate_row)
        last_word = candidate_dict['last_word'].lower()
        if last_word not in countries_cache:
            countries_cache[last_word] = []
        countries_cache[last_word].append(candidate_dict)
        
chilean_cities_cache = {}

def setup_chilean_cities_cache(cursor):
    
    select = 'SELECT * FROM cities where country_code="cl" and selected=1;'
    cursor.execute(select)
    candidate_rows = cursor.fetchall()
    
    for candidate_row in candidate_rows:
        candidate_dict = get_dict_from_row(cursor, candidate_row)
        last_word = candidate_dict['last_word'].lower()
        if last_word not in chilean_cities_cache:
            chilean_cities_cache[last_word] = []
        chilean_cities_cache[last_word].append(candidate_dict)

# Matches the current fragment against our database of countries
def is_country(cursor, text, text_starting_index, previous_result):
        
    current_word = ''
    current_index = text_starting_index
    pulled_word_count = 0
    found_row = None

    # Walk backwards through the current fragment, pulling out words and seeing if they match
    # the country names we know about
    while pulled_word_count < geodict_config.word_max:
        pulled_word, current_index, end_skipped = pull_word_from_end(text, current_index)
        pulled_word_count += 1
        if current_word == '':
            # This is the first time through, so the full word is just the one we pulled
            current_word = pulled_word
            # Make a note of the real end of the word, ignoring any trailing whitespace
            word_end_index = (text_starting_index-end_skipped)
            
            # We've indexed the locations by the word they end with, so find all of them
            # that have the current word as a suffix
            last_word = pulled_word.lower()
            if last_word not in countries_cache:
                break
            candidate_dicts = countries_cache[last_word]
            
            name_map = {}
            for candidate_dict in candidate_dicts:
                name = candidate_dict['country_name'].lower()
                name_map[name] = candidate_dict
        else:
            current_word = pulled_word+' '+current_word

        # This happens if we've walked backwards all the way to the start of the string
        if current_word == '':
            return None

        # If the first letter of the name is lower case, then it can't be the start of a country
        # Somewhat arbitrary, but for my purposes it's better to miss some ambiguous ones like this
        # than to pull in erroneous words as countries (eg thinking the 'uk' in .co.uk is a country)
        # if current_word[0:1].islower():
        #   continue

        name_key = current_word.lower()
        if name_key in name_map:
            found_row = name_map[name_key]

        if found_row is not None:
            # We've found a valid country name
            break
        if current_index < 0:
            # We've walked back to the start of the string
            break
    
    if found_row is None:
        # We've walked backwards through the current words, and haven't found a good country match
        return None
    
    # Were there any tokens found already in the sequence? Unlikely with countries, but for
    # consistency's sake I'm leaving the logic in
    if previous_result is None:
        current_result = {
            'found_tokens': [],
        }
    else:
        current_result = previous_result
                                        
    country_code = found_row['country_code']
    lat = found_row['latitude']
    lon = found_row['longitude']

    # Prepend all the information we've found out about this location to the start of the 'found_tokens'
    # array in the result
    current_result['found_tokens'].insert(0, {
        'type': 'COUNTRY',
        'country_code': country_code.lower(),
        'lat': lat,
        'lon': lon,
        'matched_string': "'" + current_word.lower() + "'",
        'start_index': (current_index+1),
        'end_index': word_end_index 
    })
    
    return current_result

# Looks through our database of 2 million towns and cities around the world to locate any that match the
# words at the end of the current text fragment
def is_city(cursor, text, text_starting_index, previous_result):
    
    current_word = ''
    current_index = text_starting_index
    pulled_word_count = 0
    found_row = None
    while pulled_word_count < geodict_config.word_max:
        pulled_word, current_index, end_skipped = pull_word_from_end(text, current_index)
        pulled_word_count += 1
        
        if current_word == '':
            current_word = pulled_word
            word_end_index = (text_starting_index-end_skipped)

            select = 'SELECT * FROM cities WHERE last_word=%s AND country_code="cl" AND selected=1'
            values = (pulled_word, )
            
            # There may be multiple cities with the same name, so pick the one with the largest population
            select += ' ORDER BY population;'

            cursor.execute(select, values)
            candidate_rows = cursor.fetchall()
            if len(candidate_rows) < 1:
                break
            
            name_map = {}
            for candidate_row in candidate_rows:
                candidate_dict = get_dict_from_row(cursor, candidate_row)
                name = candidate_dict['city_name'].lower()
                name_map[name] = candidate_dict
        else:
            current_word = pulled_word+' '+current_word
        
        if current_word == '':
            return None
        
        #If first letter is lowercase probably is not referred to a location name.
        #if current_word[0:1].islower():
        #    continue
        
        name_key = current_word.lower()
        if name_key in name_map:
            found_row = name_map[name_key]

        if found_row is not None:
            break
        if current_index < 0:
            break
    
    if found_row is None:
        return None
    
    if previous_result is None:
        current_result = {
            'found_tokens': [],
        }
    else:
        current_result = previous_result
                                        
    lat = found_row['latitude']
    lon = found_row['longitude']
    country_code = found_row['country_code']
    region_code = found_row['region_code']
                
    current_result['found_tokens'].insert(0, {
        'type': 'CITY',
        'country_code': country_code.lower(),
        'region_code': region_code,
        'lat': lat,
        'lon': lon,
        'matched_string': "'" + current_word.lower() + "'",
        'start_index': (current_index+1),
        'end_index': word_end_index 
    })
    
    return current_result


# A special case - used to look for 'at' or 'in' before a possible location word. This helps me be more certain
# that it really is a location in this context. Think 'the New York Times' vs 'in New York' - with the latter
# fragment we can be pretty sure it's talking about a location
def is_location_word(cursor, text, text_starting_index, previous_result):

    current_index = text_starting_index
    current_word, current_index, end_skipped = pull_word_from_end(text, current_index)
    word_end_index = (text_starting_index-end_skipped)
    if current_word == '':
        return None

    current_word = current_word.lower()
    
    if current_word not in geodict_config.location_words:
        return None

    return previous_result

# Utility functions

def get_database_connection():

    db=MySQLdb.connect(host=geodict_config.host,user=geodict_config.user,passwd=geodict_config.password,port=geodict_config.port)
    cursor=db.cursor()
    cursor.execute('USE '+geodict_config.database+';')

    return cursor


# Characters to ignore when pulling out words
whitespace = set(string.whitespace+"'\",.:-/\n\r<>!?")

tokenized_words = {}

# Walks backwards through the text from the end, pulling out a single unbroken sequence of non-whitespace
# characters, trimming any whitespace off the end
def pull_word_from_end(text, index, use_cache=False):

    if use_cache and index in tokenized_words:
        return tokenized_words[index]

    found_word = ''
    current_index = index
    end_skipped = 0
    while current_index>=0:
        current_char = text[current_index]
        current_index -= 1
        
        char_as_set = set(current_char)
        
        if char_as_set.issubset(whitespace):
            if found_word is '':
                end_skipped += 1
                continue
            else:
                current_index += 1
                break
        
        found_word += current_char
    
    # reverse the result (since we're appending for efficiency's sake)
    found_word = found_word[::-1]
    
    result = (found_word, current_index, end_skipped)
    tokenized_words[index] = result

    return result

# Converts the result of a MySQL fetch into an associative dictionary, rather than a numerically indexed list
def get_dict_from_row(cursor, row):
    
    d = {}
    for idx,col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# Types of locations we'll be looking for
token_definitions = {
    'COUNTRY': {
        'match_function': is_country
    },
    'CITY': {
        'match_function': is_city
    },
    'LOCATION_WORD': {
        'match_function': is_location_word
    }
}

# Particular sequences of those location words that give us more confidence they're actually describing
# a place in the text, and aren't coincidental names (eg 'New York Times')
token_sequences = [
    [ 'CITY' ],
    [ 'COUNTRY' ]  
];