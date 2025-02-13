## Script to fetch real user data and update csv files.
## Note: this solution is considered as a temp, as it's not scalable. Current setup assumes multiple chatbot instances
## might be running behind the load balancer. Therefore, every instance will do the same job which is a bit of overhead.
## Ideally, a separate job (outside chatbot instance) should be responsible for preparing dataset, while chatbot responsibility
## should be pulling the latest dataset

from random import randrange
import datetime
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv, find_dotenv
import csv
import numpy as np
import pandas as pd
import boto3
import botocore
from copy import deepcopy

load_dotenv(find_dotenv())
MONGODB_URL = os.getenv('MONGODB_URL')
S3_BUCKET = os.getenv('S3_DATA_BUCKET')
S3_REGION = 'eu-west-2'

s3 = boto3.resource(
    service_name='s3',
    region_name=S3_REGION
)


def print_csv_shape():
	print("==========NEW BUCKET CSV SIZE===========",pd.read_csv('updated_fitbit_dataset.csv').shape)


def download_from_bucket():
    try:
	    s3.Bucket(S3_BUCKET).download_file(Key='viki_userdata/updated_fitbit_dataset.csv', Filename='updated_fitbit_dataset.csv')
	    print("==========NEW BUCKET CSV SIZE===========",pd.read_csv('updated_fitbit_dataset.csv').shape)
    except botocore.exceptions.ClientError:
        print("Error downloading dataset from S3, using default one...")
        pass


def get_mongo_database():
    client = pymongo.MongoClient(MONGODB_URL)
    return client.get_default_database()

def print_database():
	user_db = get_mongo_database()
	records = user_db.stepDailyData.find({})
	print("RECORDS: ",records.count())
	data_for_model=[]
	goal_dict = { 'LOSE_WEIGHT':'lose', 'GAIN_WEIGHT':'gain', 'MAINTAIN_WEIGHT':'maintain'}
	if records.count() > 0:
		for ind,record in enumerate(records):
			print(ind,record)
			user_id = record['userId']
			user_id = str(user_id)
			timestamp = record['date'].replace(hour=0, minute=0, second=0)
			single_record=[[np.nan]*9]
			user_main_goal = user_db.users.find_one({'_id': ObjectId(user_id), 'userInfo.goal':{'$exists': True}})
			user_health = user_db.healthRecords.find({'userId': user_id, 'timestamp':{"$gte": timestamp,"$lt":timestamp + datetime.timedelta(days=1)}})
			user_sleep = user_db.sleepDailyData.find({'userId':ObjectId(user_id), 'date':{"$gte": timestamp,"$lt":timestamp+ datetime.timedelta(days=1)}})
			user_meal = user_db.userMeals.find({'user_id':user_id, 'type' : 'CALORIES', 'date':{"$gte": timestamp,"$lt":timestamp + datetime.timedelta(days=1) }})
			single_record[0][0]=user_id
			single_record[0][1]=timestamp.strftime('%Y-%m-%d')
			target = randrange(2)
			single_record[0][6] = target
			try:
				steps=record['step']
			except:
				steps=np.nan
			single_record[0][2]=steps

				
			try:
				cals=record['calorie']
			except:
				cals=np.nan
			single_record[0][3]=cals


			try:
				goal=user_main_goal['userInfo']['goal']
				goal=goal_dict[goal]
			except:
				goal=np.nan
			single_record[0][7]=goal
			##############
			cal_sum=0.0
			for i in user_meal:
				try:
					cal=i['calories']
				except:
					cal=np.nan
				if cal!=np.nan:
					cal_sum+=float(cal)
					break
			if cal_sum!=0.0:
				single_record[0][4]=cal_sum

			total_sleep=0
			for i in user_sleep:
				try:
					sleep=i['sleepTotalTime']
				except:
					sleep=np.nan
				if sleep!=np.nan:
					h,m=sleep.split(':')
					h,m=int(h),int(m)
					if m>30:
						h+=1
					total_sleep+=h
					# single_record[0][5]=h
				if total_sleep !=0:
					single_record[0][5]=total_sleep
			

			for i in user_health:
				try:
					weight=i['payload']['weight']
				except:
					weight=np.nan
				if weight!=np.nan:
					single_record[0][8]=weight
					break


			if len(data_for_model)==0:
				data_for_model=single_record
			else:
				data_for_model=data_for_model+single_record


		print('Data for model: ',data_for_model)
		data_for_model=np.array(data_for_model)
		data_for_model_df=pd.DataFrame(data_for_model,columns=['id','date','total_steps','calories','calories_in','sleep_hours','target','Class','weight'])
		df = pd.read_csv('updated_fitbit_dataset.csv')
		df = pd.concat([df,data_for_model_df])
		df = df.drop_duplicates(subset=['id','date'], keep='last')
		df.to_csv('updated_fitbit_dataset.csv',index=False)

	else:
		print('No record in step Daily data\n')
	
	print("CURRENT DIR WORKING",os.getcwd())
	s3.Bucket(S3_BUCKET).upload_file(Filename='updated_fitbit_dataset.csv', Key='viki_userdata/updated_fitbit_dataset.csv')


if __name__=='__main__':
	print_database()


