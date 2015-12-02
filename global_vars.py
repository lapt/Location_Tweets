# Project path, must be configured if the project is installed in other PC
project_dir_path = '/home/luisangel/PycharmProjects/Ubicacion_Tweets/'

# Folder to save complete information about headlines
headlines_dir = project_dir_path + 'data/headlines'

# Folder to save temporary files
temp_dir = project_dir_path + 'data/tmp/'

# Folder to save collected tweets
tweets_dir = project_dir_path + 'data/news/' 

# Folder to save logs
log_dir = project_dir_path + 'data/log/'

# Path to clavin jar to execute
path_to_jar = project_dir_path + 'clavin/target/clavin-2.0.0-jar-with-dependencies.jar'

index_directory_path = project_dir_path + 'clavin/IndexDirectory'

# clavin process to localize a user 
clavin_userLocationExtractorAdmin = 'com.bericotech.clavin.extensions.ProcessUserLocationAdmin'
clavin_locationWordsExtractor = 'com.bericotech.clavin.extensions.ToponymExtractor_Method1'
clavin_locationResolver = 'com.bericotech.clavin.extensions.ToponymResolver_Method1'

# Base name to temp files used in event geocontextualizer
tweets_filename_base = 'tweets_per_component'
location_to_verify = 'locationToVerify_per_component'
locationWords_filename_base = 'locationWords_per_component'
combinatedLocationWords_filename_base = 'combinedLocationWords_per_component_'
locationsResolved_filename_base = 'locationResolved_per_component_'
finalLocations_filename_base = 'finalLocations_per_component_'
