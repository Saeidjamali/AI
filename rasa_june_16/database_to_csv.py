## Script to fetch real user data and update csv files.
from random import randrange
import datetime
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv, find_dotenv
import csv
from random import randrange

load_dotenv(find_dotenv())
MONGODB_URL = os.getenv('MONGODB_URL')

def get_mongo_database():
    client = pymongo.MongoClient(MONGODB_URL)
    return client.get_default_database()

def get_database():

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb+srv://root:Password!23@cluster0.7ua3r.mongodb.net/?retryWrites=true&w=majority"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['user_db']


def print_database():
	user_db = get_mongo_database()
	records = user_db.stepDailyData.find({})
	with open("updated_fitbit_dataset.csv", mode = "a") as f_object:
		if records.count() > 0:
			for record in records:
				print(record)
				user_id = record['userId']
				user_id = str(user_id)
				sleep = randrange(8)
				calories_burned = record['calorie']
				steps = record['step']
				timestamp = record['date']
				timestamp_string = timestamp.strftime('%Y-%m-%d')
				print(timestamp_string)
				print(user_id)
				print(sleep)
				print(calories_burned)
				calories = calories_burned + randrange(100)
				target = randrange(2)
				user_main = user_db.users.find_one({'_id': ObjectId(user_id), 'userInfo.goal':{'$exists': True}})
				if user_main:
					print(user_main)
					goal_db = user_main['userInfo']['goal']
					goal_dict = { 'LOSE_WEIGHT':'lose', 'GAIN_WEIGHT':'gain', 'MAINTAIN_WEIGHT':'maintain'}
					goal = goal_dict.get(goal_db,None)
					user_records = user_db.healthRecords.find({'userId': user_id, 'type':'WEIGHT', 'payload.weight':{'$exists': True}})
					if user_records.count()>0:
						found = False
						for user_record in user_records:
							if str(user_record['createdAt'].date()) == timestamp_string:
								weight = user_record['userInfo']['payload']['weight']
			# 			# calorie_record = user_db.healthRecords.find_one({'user_id': user_id , 'type':'CALORIES_IN'})
			# 			# if calorie_record:
								date_csv = timestamp.strftime('%d/%m/%Y')
								list_data = [user_id, date_csv, steps, calories_burned, calories,sleep, target, goal, weight]
								writer_object = csv.writer(f_object)
								writer_object.writerow(list_data)
								found = True
						if found == False:
							print('No record found for user in healthRecords for weight:', user_id)
					else:
						print('no healthRecord found for user:', user_id)
				else:
					print('no entry for user n \'users\' collection\n')
		else:
			print('No record in step Daily data\n')
		f_object.close()



# records = user_db.healthRecords.find({'type':'CALORIES_IN'})
# if records.count() > 0:
# for record in records:
# 	user_id = record['user_id']
	# calories = record['payload']['calories']
