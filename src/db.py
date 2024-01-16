from decouple import config
import pymongo

user = str(config('DB_USER'))
password = str(config('DB_PASSWORD'))

client = pymongo.MongoClient('mongodb+srv://'+user+':'+password+'@cluster0.6n3js.mongodb.net/')
db = client.yoga
