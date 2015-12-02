from peewee import IntegerField, CharField, FloatField, BooleanField, \
    BigIntegerField, DateTimeField, Model, MySQLDatabase, ForeignKeyField, CompositeKey
from credentials import *

db = MySQLDatabase(db_name, user=db_user, passwd=db_pass, charset='utf8')
db.connect()

def getDB():
    return db

def tryConnect():
    try:
        db.connect()
        return db
    except Exception as e:
        print 'Error! ' + str(e)
        tryConnect()

def tryDisconnect():
    try:
        db.close()
    except Exception as e:
        print 'Error!' + str(e)


Int = IntegerField
Bool = BooleanField
Char = CharField
Float = FloatField

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    user_id = BigIntegerField(primary_key=True)
    verified = BooleanField()
    geo_enabled = BooleanField()
    entities = CharField(null=True)
    followers_count = IntegerField()
    location = CharField(null=True)
    utc_offset = CharField(null=True)
    statuses_count = IntegerField()
    name = CharField()
    lang = CharField()
    screen_name = CharField()
    url = CharField(null=True)
    created_at = DateTimeField()
    time_zone = CharField(null=True)
    listed_count = IntegerField()
    friends_count = IntegerField()
    timestamp = BigIntegerField(index=True, default=1262314800)
    
class TempUser(BaseModel):
    user_id = BigIntegerField()
    location = CharField(null=True)
    
class Event(BaseModel):
    keywords = CharField()
    datetime = DateTimeField()
    featured = IntegerField(null=True)
    
    
class Headline(BaseModel):
    event = ForeignKeyField(Event)
    text = CharField() 
    

class Tweet(BaseModel):
    tweet_id = BigIntegerField(primary_key=True)
    text = CharField(max_length=140)
    in_reply_to_status_id = BigIntegerField(null=True)
    favorite_count = IntegerField()
    source = CharField()
    coordinates = CharField(null=True)
    entities = CharField(null=True)
    in_reply_to_screen_name = CharField(null=True)
    in_reply_to_user_id = BigIntegerField(null=True)
    retweet_count = IntegerField()
    is_retweet = BooleanField()
    retweet_of = ForeignKeyField('self', related_name='retweets', null=True)
    user_id = ForeignKeyField(User, related_name='tweets')
    lang = CharField()
    created_at = DateTimeField()
    event_id = ForeignKeyField(Event, related_name='tweets', null=True)
    
    
class Component(BaseModel):
    date = DateTimeField()
    component_kw = CharField(max_length=500)
    
    
class ComponentEvent(BaseModel):
    component = ForeignKeyField(Component, related_name='events', null=True)
    event = ForeignKeyField(Event, related_name='components', null=True)
    
    class Meta:
        database = db
        primary_key = CompositeKey('component','event')
        
class ComponentLocation(BaseModel):
    component_id = IntegerField()
    location_names = CharField(max_length=250)
    frequency = IntegerField()
    country_code = CharField(max_length=2)
    admin1 = CharField(max_length=20)
    admin2 = CharField(max_length=80)
    admin3 = CharField(max_length=20)
    admin4 = CharField(max_length=20)
    longitude = Float()
    latitude = Float()
    n_tweets = IntegerField()
    
    class Meta:
        database = db

class UserLocationAdminCoordinates(BaseModel): 
    user_id = BigIntegerField(primary_key=True)
    country_code = CharField(max_length=2, null=True)
    admin1 = CharField(max_length=20, null=True)
    admin2 = CharField(max_length=80, null=True)
    admin3 = CharField(max_length=20, null=True)
    admin4 = CharField(max_length=20, null=True)
    longitude = Float(null=True)
    latitude = Float(null=True)
    
class ComponentTweetUser(BaseModel):
    component = BigIntegerField()
    tweet = BigIntegerField()
    user = BigIntegerField()
    
    class Meta:
        database = db
        primary_key = CompositeKey('component','tweet','user')
    
def create_tables():
    try:
        Event.create_table()    
    except Exception, e:
        pass
    try:
        Headline.create_table()
    except Exception, e:
        pass
    try:
        User.create_table()
    except Exception, e:
        pass
    try:
        TempUser.create_table()
    except Exception, e:
        pass
    try:
        Tweet.create_table()
    except Exception, e:
        pass
    try:
        Component.create_table()
    except Exception, e:
        pass
    try:
        ComponentEvent.create_table()
    except Exception, e:
        pass
    try:
        ComponentLocation.create_table()
    except Exception, e:
        pass
    try:
        UserLocationAdminCoordinates.create_table()
    except Exception, e:
        pass

def create_ComponentTweetUser_table():
    try:
        ComponentTweetUser.create_table()
    except Exception, e:
        pass
