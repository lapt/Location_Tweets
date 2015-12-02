from credentials import *

# Your MySQL user credentials
user = GEODB_USER
password = GEODB_KEY

# The address and port number of your database server
host = GEODB_HOST
port = 3306

# The name of the database to create
database = GEODB_NAME

# The maximum number of words in any name
word_max = 3

# Words that provide evidence that what follows them is a location
location_words = {
    'at': True,
    'in': True
}
