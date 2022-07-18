import pymongo
from pymongo import MongoClient
def get_database():

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb+srv://root:Password!23@cluster0.7ua3r.mongodb.net/?retryWrites=true&w=majority"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['user_db']
    
# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":    
    
    # Get the database
    dbname = get_database()
    print(dbname)
    records = dbname["users_records"] 
    x = records.delete_many({})
    print(x.deleted_count, " documents deleted.")
    print(records.count_documents({}))
    # newUser={
    #     'name':'jack',
    # }
    # records.insert_one(newUser)
    print(list(records.find()))