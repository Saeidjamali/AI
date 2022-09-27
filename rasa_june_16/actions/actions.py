from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, SlotSet, FollowupAction, UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from dotenv import load_dotenv, find_dotenv
import pymongo
import numpy as np # data arrays
import pandas as pd # data analysis
import matplotlib.pyplot as plt # data visualization
import pyaf.ForecastEngine as autof
import os
import datetime
from dateutil import parser
from copy import deepcopy
from bson.objectid import ObjectId
import ast
pd.options.mode.chained_assignment = None
from time import sleep
from random import randint

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import threading
# get_ipython().run_line_magic('matplotlib', 'inline')

# ALLOWED_PIZZA_SIZES = ["small", "medium", "large", "extra-large", "extra large", "s", "m", "l", "xl"]
# ALLOWED_PIZZA_TYPES = ["mozzarella", "fungi", "veggie", "pepperoni", "hawaii"]
#def weight_function():

load_dotenv(find_dotenv())
MONGODB_URL = os.getenv('MONGODB_URL')


def get_mongo_database():
    client = pymongo.MongoClient(MONGODB_URL)
    return client.get_default_database()

get_mongo_database()

def send_email(email_recipient,
               email_subject,
               email_message,
               attachment_location=''):
    email_mime_sender = 'viki@intellithing.tech'
    email_sender = 'viki@intellithing.tech'
    email_password = 'Dev301-d=1az'

    msg = MIMEMultipart()
    msg['From'] = email_mime_sender
    msg['To'] = email_recipient
    msg['Subject'] = email_subject

    success = False

    msg.attach(MIMEText(email_message, 'plain'))

    if attachment_location != '':
      filename = os.path.basename(attachment_location)
      attachment = open(attachment_location, "rb")
      part = MIMEBase('application', 'octet-stream')
      part.set_payload(attachment.read())
      encoders.encode_base64(part)
      part.add_header('Content-Disposition',
                      "attachment; filename= %s" % filename)
      msg.attach(part)

    try:
      server = smtplib.SMTP_SSL('smtp.mail.us-west-2.awsapps.com', 465)
      server.ehlo()
      # server.starttls()
      server.login(email_sender, email_password)
      text = msg.as_string()
      server.sendmail(email_sender, email_recipient, text)
      print('Email sent to %s' % email_recipient)
      server.quit()
      success = True
    except:
      print("SMTP server connection error")
      success = False
    return success

class action_validate_user(Action): 
    def name(self) -> Text:
        return "action_validate_user"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(str((tracker.current_state())["sender_id"]))
        user_id = str((tracker.current_state())["sender_id"])
        #print(tracker.current_state())
        user_db = get_mongo_database()
        user_record = user_db.users.find_one({"_id": ObjectId(user_id)})

        print(user_record["_id"])
        if 'profileComplete' not in user_record:
            print('not in')
            return [FollowupAction("simple_user_form")]
        else:
            dispatcher.utter_message(text=f"Hi! How can I help? Ask me questions or ask me to list the questions I can answer. ")
            print('here')
            return {}

class ValidateSimpleUserForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_simple_user_form"

    def validate_height1(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `pizza_size` value."""
        if not slot_value:
            dispatcher.utter_message(text=f"I’m sorry I didn’t understand, I’m still learning please try telling me your height differently.")
            return {"height1": None}
        # have height 1
        unit_temp = next(tracker.get_latest_entity_values('unit'), None)
        measuringUnit = tracker.get_slot('measuringUnit')
        print('unit_temp:', unit_temp)
        print('measuringUnit:', measuringUnit)

        if unit_temp not in ['cm', 'feet', None]:
            dispatcher.utter_message(text="Seems like you have typed incorrect unit. I’m still learning please try telling me your height differently.")
            return {"height1": None}

        if unit_temp == None:
            if measuringUnit == 'imperial':
                if float(slot_value) >= 1 and float(slot_value) <= 9:
                    value = slot_value + " " + "feets"
                    dispatcher.utter_message(text=f"Your height is set to {value}")
                    print('value of height is:', value)
                    return {"height1": value, "height2": 0}
                else:
                    dispatcher.utter_message(
                        text="Typed height seems incorrect to me, typically human height is between 1 to 9 feets.\n I’m still learning please try telling me your height differently.")
                    return {"height1": None}
            elif measuringUnit == 'metric':
                if float(slot_value) >= 80 and float(slot_value) <= 250:
                    value = slot_value + " " + "cm"
                    dispatcher.utter_message(text=f"Your height is set to {value}")
                    print('value of height is', value)
                    return {"height1": value, "height2": 0}
                else:
                    dispatcher.utter_message(
                        text="Typed height seems incorrect to me, typically human height is between 80 to 250 cm.\n I’m still learning please try telling me your height differently.")
                    return {"height1": None}

        if measuringUnit == 'metric' and unit_temp == 'cm':
            if float(slot_value) < 80:
                dispatcher.utter_message(
                    text="Typed value seems quite low to me, typically human height is between 80 to 250 cm.\n I’m still learning please try telling me your height differently.")
                return {"height1": None}
            elif float(slot_value) > 250:
                dispatcher.utter_message(
                    text="Typed value seems quite high, typically human height is between 80 to 250 cm.\n I’m still learning please try telling me your height differently.")
                return {"height1": None}
            else:
                slot_value = slot_value + " cm"

        elif measuringUnit == 'imperial' and unit_temp == 'feet':
            if float(slot_value) < 1:
                dispatcher.utter_message(
                    text="Typed value seems quite low, typically human height is between 1 to 9 feets.\n I’m still learning please try telling me your height differently.")
                return {"height1": None}
            elif float(slot_value) > 9:
                dispatcher.utter_message(
                    text="Typed value seems quite high, typically human height is between 1 to 9 feets.\n I’m still learning please try telling me your height differently.")
                return {"height1": None}
            else:
                slot_value = slot_value + " feets"
        else:
            dispatcher.utter_message(text="Seems like you have typed incorrect unit according to the typed measuring system.")
            return {"height1": None, "height2": None}

        # unit is cm or feet.
        if tracker.get_slot('height2') == None:
            # height in cm or user has typed e.g. "45 feets" only
            dispatcher.utter_message(text=f"OK! Your height is {slot_value}")
            return {"height1": slot_value, "height2": 0}
        # there is height2

        height2_temp = tracker.get_slot('height2')
        if float(height2_temp) > 12 or float(height2_temp) < 0:
            dispatcher.utter_message(text="You have typed incorrect amount of inches, kindly type between 1 and 12 inches.\n I’m still learning please try telling me your height differently.")
            return {"height1": None}

        height_temp = slot_value + " " + height2_temp + " inches"
        dispatcher.utter_message(text=f"OK! Your height is {height_temp}.")
        return {"height1": height_temp}

    def validate_height2(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `pizza_type` value."""
        print(slot_value)
        if not slot_value:
            return {"height2": 0}
            # dispatcher.utter_message(text=f"Your height seems wrong.")
            # return {"height2": None}
        #dispatcher.utter_message(text=f"OK! You want to have a {slot_value} pizza.")
        return {"height2": slot_value}

    def validate_weight(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if not slot_value:
            dispatcher.utter_message(text="Your weight seems wrong")
            return {"weight": None}

        unit_temp = next(tracker.get_latest_entity_values('unit'), None)
        measuringUnit = tracker.get_slot('measuringUnit')

        print('unit_temp:', unit_temp)
        if unit_temp not in ['kg', 'pound', None]:
            dispatcher.utter_message(text="Seems like you have typed incorrect unit.\n I’m still learning please try telling me your height differently.")
            return {"weight": None}

        if unit_temp == None:
            if measuringUnit == 'imperial':
                if float(slot_value) > 20 and float(slot_value) < 640:
                    value = slot_value + " " + "pounds"
                    dispatcher.utter_message(text=f"Your weight is set to {value}")
                    return {"weight": value}
                else:
                    dispatcher.utter_message(
                        text=f"Typed weight seems incorrect to me, typically human weight is between 20 to 640 pounds.")
                    return {"weight": None}
            elif measuringUnit == 'metric':
                if float(slot_value) > 20 and float(slot_value) < 290:
                    value = slot_value + " " + "kgs"
                    dispatcher.utter_message(text=f"Your weight is set to {value}")
                    return {"weight": value}
                else:
                    dispatcher.utter_message(
                        text=f"Typed weight seems incorrect to me, typically human weight is between 20 to 290 kgs.")
                    return {"weight": None}

        if measuringUnit == 'imperial' and unit_temp == 'pound':
            if float(slot_value) < 20:
                dispatcher.utter_message(
                    text="Typed value seems quite low, typically human weight is between 20 to 640 pounds.")
                return {"weight": None}
            elif float(slot_value) > 640:
                dispatcher.utter_message(
                    text="Typed value seems quite high, typically human weight is between 20 to 640 pounds.")
                return {"weight": None}
            else:
                slot_value = slot_value + " pounds"
        elif measuringUnit == 'metric' and unit_temp == 'kg':
            if float(slot_value) < 20:
                dispatcher.utter_message(
                    text="Typed value seems quite low, typically human weight is between 20 to 290 kgs.")
                return {"weight": None}
            elif float(slot_value) > 290:
                dispatcher.utter_message(
                    text="Typed value seems quite high, typically human weight is between 20 to 290 kgs.")
                return {"weight": None}
            else:
                slot_value = slot_value + " kgs"
        else:
            dispatcher.utter_message(text="Seems like you have typed incorrect unit for the typed measuring system.")
            return {"weight": None}

        dispatcher.utter_message(text=f"Noted! Your weight is {slot_value}.")
        return {"weight": slot_value}

    def validate_name(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        value = next(tracker.get_latest_entity_values('name'), None)
        person_value = next(tracker.get_latest_entity_values('PERSON'), None)
        print('name', value)
        print('PERSON', person_value)
        print(str((tracker.current_state())["sender_id"]))

        if person_value:
            dispatcher.utter_message(text=f"Hello! {person_value}.")
            return {"name": person_value}
        elif value:
            dispatcher.utter_message(text=f"Hello! {value}.")
            return {"name": value}
        else:
            dispatcher.utter_message(text="I’m sorry I didn’t understand, I’m still learning please try saying your name differently.")
            return {"name": None}


    def validate_age(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `pizza_type` value."""

        if not slot_value:
            dispatcher.utter_message(text=f"I’m sorry I didn’t understand, I’m still learning please try typing your age differently.")
            return {"age": None}
        elif float(slot_value) < 1 or float(slot_value) > 150:
            dispatcher.utter_message(text=f"Seems like you have typed incorrect age, Please type between 1 and 150 years old")
            return {"age": None}
        dispatcher.utter_message(text=f"hmm ok! so you are {slot_value} years old.")
        return {"age": slot_value}

    def validate_gender(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `pizza_type` value."""
        gender = {'1':'male', '2':'female'}

        Number = next(tracker.get_latest_entity_values('NUMBER'), None)
        print('Number', Number)

        slot_value = next(tracker.get_latest_entity_values('gender'), None)
        print('gender', slot_value)

        if not (slot_value or  Number):
            dispatcher.utter_message(text=f"Seems like you have typed incorrect gender. I’m still learning please try saying it differently.")
            return {"gender": None}

        elif Number in ['1','2']:
            dispatcher.utter_message(text=f"OK! Your gender is {gender[Number]}.")
            return {"gender": gender[Number]}

        elif slot_value in ['male','female']:
            dispatcher.utter_message(text=f"OK! You are a {slot_value}.")
            return {"gender": slot_value}
        #else
        dispatcher.utter_message(text=f"I’m sorry I didn’t understand, I’m still learning please try saying it differently.")
        return {"gender": None}

    def validate_stressLevel(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        stressLevel = {'1':'very low', '2':'low', '3':'average', '4':'high', '5':'very high'}
        if not slot_value:
            dispatcher.utter_message(text="Seems like you have typed incorrect stress Level. I’m still learning please try saying it differently.")
            return {"stressLevel": None}
        elif slot_value not in ['1','2','3','4','5']:
            dispatcher.utter_message(text="Seems like you have typed incorrect stress Level.")
            return {"stressLevel": None}

        dispatcher.utter_message(text=f"OK! Seems like your stress Level is {stressLevel[slot_value]}.")
        return {"stressLevel": stressLevel[slot_value]}

    def validate_likeFood(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        likeFood = {'1':'and you are not much of a foodie at all', '2':'and your food likeness rating is below average',
                    '3':'and your food likeness rating is average', '4':'and you love food', '5':'and food is life for you'}
        if not slot_value:
            dispatcher.utter_message(text="Seems like you have typed incorrect Level. I’m still learning please try saying it differently.")
            return {"likeFood": None}
        elif slot_value not in ['1','2','3','4','5']:
            dispatcher.utter_message(text="Seems like you have typed incorrect level.")
            return {"likeFood": None}
        message_displayed={'1':'Seems like you are not much of a foodie at all...',
        '2':'So, you are not much of a foodie...', '3':'It seems like you are not much of a foodie...',
        '4':'So, you love food...', '5':'hmm great, so food is life for you... '}
        dispatcher.utter_message(text=f" {message_displayed.get(slot_value, None)}")
        return {"likeFood": likeFood.get(slot_value,None)}

    def validate_userGoal(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `pizza_type` value."""
        Number = next(tracker.get_latest_entity_values('NUMBER'), None)
        print('Usergoal_Number',Number)

        slot_value = next(tracker.get_latest_entity_values('userGoal'), None)
        print('userGoal', slot_value)

        goal = {'1':"You are trying to Lose weight",
                '2':"You are trying to Mantain Weight",
                '3':"You are trying to Gain Weight",
                '4':"you have not set any goals for the moment.",
                'lose': "You are trying to Lose weight",
                'maintain': "You are trying to Mantain Weight",
                'gain': "You are trying to Gain Weight",
                'other': "you have not set any goals for the moment.",
                }

        if not (slot_value or Number):
            dispatcher.utter_message(text=f"Seems like you have typed incorrect goal. I’m still learning please try saying it differently.")
            return {"userGoal": None}

        elif Number in ['1', '2', '3', '4']:
            dispatcher.utter_message(text=f"OK! {goal[Number]}.")
            return {"userGoal": goal[Number]}

        elif slot_value in ['lose', 'maintain', 'gain', 'other']:
            dispatcher.utter_message(text=f"OK! You are a {goal[slot_value]}.")
            return {"userGoal": goal[slot_value]}
        #else:
        dispatcher.utter_message(text=f"Seems like you have typed incorrect goal.")
        return {"userGoal": None}

    def validate_eating(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `pizza_type` value."""
        Number = next(tracker.get_latest_entity_values('NUMBER'), None)
        print('eating-Number', Number)

        slot_value = next(tracker.get_latest_entity_values('eating'), None)
        print('eating', slot_value)

        eating = {'1': 'You are a Vegan',
                  '2': 'You are a Vegetarian',
                  '3': 'You are a Non-vegetarian',
                  'vegan': 'You are a Vegan',
                  'vegetarian': 'You are a Vegetarian',
                  'non-vegetarian': 'You are a Non-vegetarian',
                  }
        message_displayed = {'1': 'It\'s great to hear that you follow a vegan diet and lifestyle',
                             '2': 'It\'s great to hear that you follow a vegetarian diet and lifestyle',
                             '3': 'Great! so you are an omnivore',
                             'vegan': 'It\'s great to hear that you follows a vegan diet and lifestyle',
                             'vegetarian': 'It\'s great to hear that you follows a vegetarian diet and lifestyle',
                             'non-vegetarian': 'Great! so you are an omnivore',
                             }
        if not (slot_value or Number):
            dispatcher.utter_message(text=f"Seems like you have typed incorrect eating category. I’m still learning please try saying it differently.")
            return {"eating": None}
        elif slot_value in ['vegan', 'vegetarian', 'non-vegetarian']:
            dispatcher.utter_message(text=f"{message_displayed.get(slot_value, None)}")
            return {"eating": eating.get(slot_value, None)}
        elif Number in ['1', '2', '3']:
            dispatcher.utter_message(text=f"{message_displayed.get(Number, None)}")
            return {"eating": eating.get(Number, None)}

        dispatcher.utter_message(text=f"Seems like you have typed incorrect eating category.")
        return {"eating": None}

    def validate_measuringUnit(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `pizza_type` value."""

        Number = next(tracker.get_latest_entity_values('NUMBER'), None)
        print('Number', Number)

        slot_value = next(tracker.get_latest_entity_values('measurement'), None)
        print('measurement', slot_value)

        MEASURE = {'1': 'imperial', '2': 'metric'}

        slot_value = next(tracker.get_latest_entity_values('measurement'), None)
        print(slot_value)

        if not (slot_value or Number):
            dispatcher.utter_message(text="Seems like you have typed incorrect measuring unit. I’m still learning please try saying it differently.")
            return {"measuringUnit": None}

        elif slot_value in ['imperial','metric']:
            dispatcher.utter_message(text=f"Noted! You have chosen {slot_value} as your measuring unit.")
            return {"measuringUnit": slot_value}

        elif Number in ['1','2']:
            dispatcher.utter_message(text=f"Noted! You have chosen {MEASURE[Number]} as your measuring unit.")
            return {"measuringUnit": MEASURE[Number]}

        dispatcher.utter_message(text=f"Seems like you have typed incorrect measuring unit. I’m still learning please try saying it differently.")
        return {"measuringUnit": None}

    def validate_healthcondition(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if not slot_value:
            dispatcher.utter_message(text=f"Seems like you have typed incorrect medical condidion. I’m still learning please try saying it differently.")
            return {"healthcondition": None}
        dispatcher.utter_message(text="OK!.")
        return {"healthcondition": slot_value}

    def validate_diseases(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if not slot_value:
            dispatcher.utter_message(text=f"you have not typed correct response.")
            return {"diseases": 'No diseases'}
        dispatcher.utter_message(text="OK!.")
        return {"diseases": slot_value}

class action_change_weight(Action):
    def name(self) -> Text:
        return "action_change_weight"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_id = str((tracker.current_state())["sender_id"])
        user_db = get_mongo_database()
        measurement = {'metric': "METRIC",'imperial': "IMPERIAL"}
        value = next(tracker.get_latest_entity_values(entity_type="NUMBER", entity_role="weight2"), None)
        print(value)
        if not value:
            dispatcher.utter_message(text="Your weight seems wrong")
            return[SlotSet("weight", None)]
        if((tracker.get_slot('measuringUnit') == 'imperial')):
            if float(value) < 20:
                dispatcher.utter_message(
                    text="Your weight seems incorrect to me, typically human weight is between 20 to 640 pounds.")
                return[SlotSet("weight", None)]
            elif float(value) > 640:
                dispatcher.utter_message(
                    text="Your weight seems incorrect to me, typically human weight is between 20 to 640 pounds.")
                return[SlotSet("weight", None)]
            else:
                value = value + " pounds"
        elif((tracker.get_slot('measuringUnit') == 'metric')):
            if float(value) < 20:
                dispatcher.utter_message(
                    text="Your weight seems incorrect to me, typically human weight is between 20 to 290 kgs")
                return[SlotSet("weight", None)]
            elif float(value) > 290:
                dispatcher.utter_message(
                    text="Your weight seems incorrect to me, typically human weight is between 20 to 290 kgs")
                return [SlotSet("weight", None)]
            else:
                value = value + " kgs"
        if value:
            dispatcher.utter_message(text=f"your weight is changed to {value}")
            ## For weight
            weight_initial = str(value)
            weight = weight_initial.split(' ')[0]
            user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.weight': float(weight)}})
            user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.updatedAt': parser.parse(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'))}})
            user_db.healthRecords.insert_one({"userId":user_id, 'type': 'WEIGHT', 'payload': {'weight' : float(weight), 'measureType': measurement.get((str(tracker.get_slot('measuringUnit'))), None)}, 'timestamp': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'), 'createdAt': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds')})
            return[SlotSet('weight', value)]

class action_change_stressLevel(Action):
    def name(self) -> Text:
        return "action_change_stressLevel"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_id = str((tracker.current_state())["sender_id"])
        user_db = get_mongo_database()
        measurement = {'metric': "METRIC",'imperial': "IMPERIAL"}
        value = next(tracker.get_latest_entity_values(entity_type="NUMBER", entity_role="stressLevel2"), None)
        print(value)
        stressLevel = {'1':'very low', '2':'low', '3':'average', '4':'high', '5':'very high'}
        if not value:
            dispatcher.utter_message(text="Your stress Level seems incorrect to me. I’m still learning please try saying it differently.")
            return[SlotSet("stressLevel", None)]
        elif value not in ['1','2','3','4','5']:
            dispatcher.utter_message(text="Your stress Level seems incorrect to me. I’m still learning please try saying it differently.")
            return[SlotSet("stressLevel", None)]
        dispatcher.utter_message(text=f"OK! Seems like your stress Level is {value}({stressLevel.get(value,None)}).")
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.stressLevel': int(value)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.updatedAt': parser.parse(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'))}})
        user_db.healthRecords.insert_one({"userId":user_id, 'type': 'STRESS_LEVEL', 'payload': {'stressLevel': int(value), 'measureType': measurement.get((str(tracker.get_slot('measuringUnit'))), None)}, 'timestamp': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'),  'createdAt': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds')})
        return[SlotSet("stressLevel", stressLevel.get(value,None))]

class action_change_age(Action):
    def name(self) -> Text:
        return "action_change_age"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_id = str((tracker.current_state())["sender_id"])
        user_db = get_mongo_database()
        slot_value = next(tracker.get_latest_entity_values(entity_type="NUMBER", entity_role="age2"), None)
        print(slot_value)

        if not slot_value:
            dispatcher.utter_message(text="I’m sorry I didn’t understand, I’m still learning please try saying it differently.")
            return[SlotSet("age", None)]

        elif float(slot_value) < 1 or float(slot_value) > 150:
            dispatcher.utter_message(text=f"Your age seems incorrect to me, Please type between 1 and 150 years old.")
            return[SlotSet("age", None)]

        dispatcher.utter_message(text=f"hmm ok! so you are {slot_value} years old.")
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.age': int(slot_value)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.updatedAt': parser.parse(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'))}})
        return[SlotSet("age", slot_value)]


class action_change_measuringUnit(Action):
    def name(self) -> Text:
        return "action_change_measuringUnit"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slot_value = next(tracker.get_latest_entity_values(entity_type="measurement", entity_role="measurement2"), None)
        # if slot measurment is not set, and the user is in change so set the measurmnt unit.
        print(slot_value)

        if not slot_value:
            dispatcher.utter_message(text="Your measuring unit seems incorrect to me. I’m still learning please try saying your name differently.")
            return [SlotSet("measuringUnit", slot_value)]

        elif slot_value in ['imperial', 'metric']:
            dispatcher.utter_message(text=f"Noted! You have changed your measuring unit to {slot_value}.")
            return [SlotSet("measuringUnit", slot_value)]

        # old_measuring_unit = tracker.get_slot('measuringUnit')

        # if not slot_value:
        #     dispatcher.utter_message(text="You have typed wrong measuring unit.")
        #     return [SlotSet("measuringUnit", slot_value)]
        # elif slot_value in ['imperial', 'metric']:
        #     if slot_value == old_measuring_unit:
        #         dispatcher.utter_message(text=f"Noted! You have changed your measuring unit to {slot_value}.")
        #         return [SlotSet("measuringUnit", slot_value)]
        #     elif slot_value == 'imperial':
        #         height = tracker.get_slot('height1')
        #         weight = tracker.get_slot('height')
        #         if height1:
        #             inches = int(0.3937 * height)
        #             #feet = int(0.0328 * height)
        #             feet = int(inches / 12)
        #             inches = inches - float(feet * 12)
        #             final_height = feet  "feets " + inches + " inches"
        #             dispatcher.utter_message(text=f"OK! Your height is {final_height}.")
        #     elif slot_value == 'metric':

        dispatcher.utter_message(text="Your measuring unit seems incorrect to me. I’m still learning please try saying it differently.")
        return [SlotSet("measuringUnit", None)]

class action_change_eating(Action):
    def name(self) -> Text:
        return "action_change_eating"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_id = str((tracker.current_state())["sender_id"])
        user_db = get_mongo_database()
        slot_value = next(tracker.get_latest_entity_values(entity_type="eating", entity_role="eating2"), None)
        # if slot measurment is not set, and the user is in change so set the measurmnt unit.
        print(slot_value)

        eating = {'1': 'You are a Vegan',
                  '2': 'You are a Vegetarian',
                  '3': 'You are a Non-vegetarian',
                  'vegan': 'You are a Vegan',
                  'vegetarian': 'You are a Vegetarian',
                  'non-vegetarian': 'You are a Non-vegetarian',
                  }

        eating_db = {'1' : 'VEGAN', '2': 'VEGETARIAN', '3': 'NON_VEGETARIAN', 'vegan': 'VEGAN',
                  'vegetarian': 'VEGETARIAN',
                  'non-vegetarian': 'NON_VEGETARIAN',}

        if (not slot_value) or (slot_value not in ['vegan', 'vegetarian', 'non-vegetarian']):
            dispatcher.utter_message(text="Your eating category seems incorrect to me. I’m still learning please try saying it differently.")
            return [SlotSet("eating", None)]

        dispatcher.utter_message(text=f"{eating.get(slot_value,None)}")
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.eating': eating_db.get((str(slot_value)), None)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.updatedAt': parser.parse(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'))}})
        return [SlotSet("eating", eating.get(slot_value,None))]
        

class action_change_foodieLevel(Action):
    def name(self) -> Text:
        return "action_change_foodieLevel"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_id = str((tracker.current_state())["sender_id"])
        user_db = get_mongo_database()
        slot_value = next(tracker.get_latest_entity_values(entity_type="Number", entity_role="likeFood"), None)
        print(slot_value)
        likeFood = {'1': 'and you are not much of a foodie at all',
                    '2': 'and your food likeness rating is below average',
                    '3': 'and your food likeness rating is average', '4': 'and you love food',
                    '5': 'and food is life for you'}
        message_displayed = {'1': 'Seems like you are not much of a foodie at all...',
                             '2': 'So, you are not much of a foodie...',
                             '3': 'It seems like you are not much of a foodie...',
                             '4': 'So, you love food...', '5': 'hmm great, so food is life for you... '}
        if (not slot_value) or (slot_value not in ['1', '2', '3', '4', '5']):
            dispatcher.utter_message(text="Seems like you have typed incorrect stress Level. I’m still learning please try saying it differently.")
            return [SlotSet("likeFood", None)]
        #else

        dispatcher.utter_message(text=f"Your foodlevel is set to {slot_value}, {message_displayed.get(slot_value,None)}")
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.likeFood': int(slot_value)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.updatedAt': parser.parse(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'))}})
        return [SlotSet("likeFood", likeFood.get(slot_value,None))]

class action_change_height(Action):
    def name(self) -> Text:
        return "action_change_height"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_id = str((tracker.current_state())["sender_id"])
        user_db = get_mongo_database()
        measurement = {'metric': "METRIC",'imperial': "IMPERIAL"}

        height = next(tracker.get_latest_entity_values(entity_type="NUMBER", entity_role="height2"), None)
        inches = next(tracker.get_latest_entity_values(entity_type="NUMBER", entity_role="inches2"), None)
        value = height
        print(value)
        print('inches:',inches)

        if not value:
            dispatcher.utter_message(text="I’m sorry I didn’t understand, I’m still learning please try telling me your height differently.")
            return[SlotSet("height1", None)]
        print(tracker.get_slot('measuringUnit'))
        if(tracker.get_slot('measuringUnit') == 'imperial'):
            if inches:
                if (float(value) > 9 or float(value) < 1):
                    dispatcher.utter_message(text="Your height seems incorrect to me, typically human height is between 1 to 9 feets in imperial measurement system.\n I’m still learning please try telling me your height differently.")
                    return[SlotSet("height1", None), SlotSet("height2", None)]
                elif (float(inches) > 12 or float(inches) < 0):
                    dispatcher.utter_message(text="Seems like you have typed wrong amount of inches. Inches are between 0 to 12 in height")
                    return[SlotSet("height1", None), SlotSet("height2", None)]
                else:
                    value=value +" feet "+ inches+" inches"
                    dispatcher.utter_message(text=f"Your height is changed to {value}")

                    ## For Height update in DB
                    height_initial = value
                    if len(height_initial.split(' ')) > 2:
                        height  = height_initial.split(' ')[0] + '.' + height_initial.split(' ')[2]
                    else:
                        height = height_initial.split(' ')[0]
                    user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.height': float(height)}})
                    user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.updatedAt': parser.parse(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'))}})
                    user_db.healthRecords.insert_one({"userId":user_id, 'type': 'HEIGHT', 'payload': {'height' : float(height), 'measureType': measurement.get((str(tracker.get_slot('measuringUnit'))), None)}, 'timestamp': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'), 'createdAt': parser.parse(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds')), '_class' : 'com.intellithing.common.entity.HealthRecord'})
                    return [SlotSet("height1", value), SlotSet("height2", 0)]
            else:
                if float(value) < 1:
                    dispatcher.utter_message(
                        text="Typed value seems quite low, typically human height is between 1 to 9 feets in imperial measurement system.")
                    return[SlotSet("height1", None)]
                elif float(value) > 9:
                    dispatcher.utter_message(
                        text="Typed value seems quite high, typically human height is between 1 to 9 feets in imperial measurement system.")
                    return[SlotSet("height1", None)]
                else:
                    value= value +" feet "
                    dispatcher.utter_message(text=f"Your height is changed to {value}")

                    ## For Height update in DB
                    height_initial = value
                    if len(height_initial.split(' ')) > 2:
                        height  = height_initial.split(' ')[0] + '.' + height_initial.split(' ')[2]
                    else:
                        height = height_initial.split(' ')[0]
                    user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.height': float(height)}})
                    user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.updatedAt': parser.parse(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'))}})
                    user_db.healthRecords.insert_one({"userId":user_id, 'type': 'HEIGHT', 'payload': {'height' : float(height), 'measureType': measurement.get((str(tracker.get_slot('measuringUnit'))), None)}, 'timestamp': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'), 'createdAt': parser.parse(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds')), '_class' : 'com.intellithing.common.entity.HealthRecord'})
                    return [SlotSet("height1", value), SlotSet("height2", 0)]
        else:
            if float(value) < 80:
                dispatcher.utter_message(
                    text="Typed value seems quite low, typically human height is between 80 to 250 cm in metric measurement system.")
                return[SlotSet("height1", None), SlotSet("height2", None)]
            elif float(value) > 250:
                dispatcher.utter_message(
                    text="Typed value seems quite high, typically human height is between 80 to 250 cm in metric measurement system.")
                return [SlotSet("height1", None), SlotSet("height2", None)]
            else:
                value = value + " cm"
                dispatcher.utter_message(text=f"Your height is changed to {value} ")

                ## For Height update in DB
                height_initial = value
                height = height_initial.split(' ')[0]
                user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.height': float(height)}})
                user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.updatedAt': parser.parse(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'))}})
                user_db.healthRecords.insert_one({"userId":user_id, 'type': 'HEIGHT', 'payload': {'height' : float(height), 'measureType': measurement.get((str(tracker.get_slot('measuringUnit'))), None)}, 'timestamp': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'), 'createdAt': parser.parse(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds')), '_class' : 'com.intellithing.common.entity.HealthRecord'})

                return [SlotSet("height1", value), SlotSet("height2", 0)]

class action_store_db(Action): ## custom action function for storing user information in the database.
    def name(self) -> Text:
        return "action_store_db"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_id = str((tracker.current_state())["sender_id"])
        user_db = get_mongo_database()
        user_record = user_db.users.find_one({"_id": ObjectId(user_id)})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'profileComplete': True}})

        goal = {'You are trying to Lose weight': "LOSE_WEIGHT",
                'You are trying to Mantain Weight':"MAINTAIN_WEIGHT",
                'You are trying to Gain Weight': "GAIN_WEIGHT",
                }
        gender = {'male': "MALE",'female': "FEMALE"}
        measurement = {'metric': "METRIC",'imperial': "IMPERIAL"}
        eating = {'You are a Vegan': 'VEGAN', 'You are a Vegetarian': 'VEGETARIAN', 'You are a Non-vegetarian': 'NON_VEGETARIAN'}
        stressLevel = {'very low': 1, 'low' : 2, 'average': 3, 'high': 4, 'very high': 5}
        likeFood = {'and you are not much of a foodie at all' : 1,
                    'and your food likeness rating is below average': 2,
                    'and your food likeness rating is average': 3, 'and you love food': 4,
                    'and food is life for you': 5}

        ## For weight
        weight_initial = str(tracker.get_slot('weight'))
        weight = weight_initial.split(' ')[0]
        
        ## For Height
        height_initial = str(tracker.get_slot('height1'))
        if str(tracker.get_slot('measuringUnit')) == 'imperial':
            if len(height_initial.split(' ')) > 2:
                height  = height_initial.split(' ')[0] + '.' + height_initial.split(' ')[2]
            else:
                height = height_initial.split(' ')[0]
        else:
            height = height_initial.split(' ')[0]

        print("inside storage of DB")
        print(str((tracker.current_state())["sender_id"]))
        print(tracker.get_slot('name'))
        print(tracker.get_slot('measuringUnit'))
        print(tracker.get_slot('age'))
        print(tracker.get_slot('gender'))
        print(tracker.get_slot('weight'))
        print(tracker.get_slot('height1'))
        print(tracker.get_slot('eating'))
        print(tracker.get_slot('stressLevel'))
        print(tracker.get_slot('likeFood'))
        print(tracker.get_slot('userGoal'))
        # print(records.distinct('_id'))
        #utctime = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds')
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.measureType': measurement.get((str(tracker.get_slot('measuringUnit'))), None)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.age': int(tracker.get_slot('age'))}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.gender': gender.get((str(tracker.get_slot('gender'))), None)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.weight': float(weight)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.height': float(height)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.eating': eating.get((str(tracker.get_slot('eating'))), None)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.stressLevel': stressLevel.get((str(tracker.get_slot('stressLevel'))), None)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.likeFood': likeFood.get((str(tracker.get_slot('likeFood'))), None)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.goal': goal.get((str(tracker.get_slot('userGoal'))), None)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.updatedAt': parser.parse(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'))}})
        user_db.healthRecords.insert_one({"userId":user_id, 'type': 'WEIGHT', 'payload': {'weight' : float(weight), 'measureType': measurement.get((str(tracker.get_slot('measuringUnit'))), None)}, 'timestamp': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'), 'createdAt': parser.parse(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds')), '_class' : 'com.intellithing.common.entity.HealthRecord'})
        user_db.healthRecords.insert_one({"userId":user_id, 'type': 'HEIGHT', 'payload': {'height' : float(height), 'measureType': measurement.get((str(tracker.get_slot('measuringUnit'))), None)}, 'timestamp': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'), 'createdAt': parser.parse(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds')), '_class' : 'com.intellithing.common.entity.HealthRecord'})
        user_db.healthRecords.insert_one({"userId":user_id, 'type': 'STRESS_LEVEL', 'payload': {'stressLevel': stressLevel.get((str(tracker.get_slot('stressLevel'))), None), 'measureType': measurement.get((str(tracker.get_slot('measuringUnit'))), None)}, 'timestamp': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'), 'createdAt': parser.parse(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds')), '_class' : 'com.intellithing.common.entity.HealthRecord'})
        #dispatcher.utter_message(text = f"your data is stored in the database.")
        print((user_db.users.find_one({"_id": ObjectId(user_id)})))
        # mydict = { "user_id": str(tracker.current_state()["sender_id"]), "name": tracker.get_slot('name'), "measuringUnit": tracker.get_slot('measuringUnit'), 
        #            "age": tracker.get_slot('age'), "gender": tracker.get_slot('gender'), 
        #            "weight": tracker.get_slot('weight'), "height": tracker.get_slot('height1'), 
        #            "eating": tracker.get_slot('eating'), "stressLevel": tracker.get_slot('stressLevel'),
        #            "likeFood": tracker.get_slot('likeFood'), "userGoal": tracker.get_slot('userGoal') }

        # x = records.insert_one(mydict) ## Command for entrying the json document into the collection
        # print(x)
        # cursor = records.find()
        # for record in cursor:
        #     print(record)
        return None

class Questions:
    def __init__(self, id):
        self.id = id
        
        
    def Response(self,peaks_valleys):
        if self.id == 1:
            if len(peaks_valleys['valleys_steps'])>3:
                if len(peaks_valleys['valleys_cal'])>3:
                    if len(peaks_valleys['peaks_calin'])>3:
                        if len(peaks_valleys['peaks_sleep'])>2 or len(peaks_valleys['valleys_sleep'])>2:
                            response = "You have reduced activity level in the last "+str(len(peaks_valleys['valleys_steps']))+" days, you have burnt fewer calories in the last "+str(len(peaks_valleys['valleys_cal']))+" days, you have high calorie intake levels in the "+str(len(peaks_valleys['peaks_calin']))+" days, and you have had a poor sleep pattern in the "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight loss journey."
                        else:
                            response = "You have reduced activity level in the last"+str(len(peaks_valleys['valleys_steps']))+" days, you have burnt fewer calories in the last "+str(len(peaks_valleys['valleys_cal']))+" days, you have high calorie intake levels in the "+str(len(peaks_valleys['peaks_calin']))+" days. These are affecting your weight loss journey."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You have reduced activity level in the last "+str(len(peaks_valleys['valleys_steps']))+" days, you have burnt fewer calories in the last "+str(len(peaks_valleys['valleys_cal']))+" days, and you have had a poor sleep pattern in the "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight loss journey."
                        else:
                            response = "You have reduced activity level in the  last "+str(len(peaks_valleys['valleys_steps']))+" days, you have burnt fewer calories in the last "+str(len(peaks_valleys['valleys_cal']))+" days. These are affecting your weight loss journey."
                else:
                    if len(peaks_valleys['peaks_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You have reduced activity level in "+str(len(peaks_valleys['valleys_steps']))+" days, you have high calorie intake levels in the last "+str(len(peaks_valleys['peaks_calin']))+" days, and you have had a poor sleep pattern in the "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight loss journey."
                        else:
                            response = "You have reduced activity level in "+str(len(peaks_valleys['valleys_steps']))+" days, you have high calorie intake levels in the last "+str(len(peaks_valleys['peaks_calin']))+" days. These are affecting your weight loss journey."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You have reduced activity level in the last"+str(len(peaks_valleys['valleys_steps']))+" days, and you have had a poor sleep pattern in the last "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight loss journey."
                        else:
                            response = "You have reduced activity level in the last "+str(len(peaks_valleys['valleys_steps']))+" days that is affecting your weight lossing performance."
            else:
                if len(peaks_valleys['valleys_cal'])>3:
                    if len(peaks_valleys['peaks_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You have burnt fewer calories in the last "+str(len(peaks_valleys['valleys_cal']))+" days, you have high calorie intake levels in the "+str(len(peaks_valleys['peaks_calin']))+" days, and you have had a poor sleep pattern in the "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight loss journey."
                        else:
                            response = "You have burnt fewer calories in the last "+str(len(peaks_valleys['valleys_cal']))+" days, you have high calorie intake levels in the "+str(len(peaks_valleys['peaks_calin']))+" days. These are affecting your weight loss journey."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You have burnt fewer calories in the last "+str(len(peaks_valleys['valleys_cal']))+" days, and you have had a poor sleep pattern in the "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight loss journey."
                        else:
                            response = "You have burnt fewer calories in the last "+str(len(peaks_valleys['valleys_cal']))+" days. These are affecting your weight loss journey."
                else:
                    if len(peaks_valleys['peaks_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You have high calorie intake levels in the last "+str(len(peaks_valleys['peaks_calin']))+" days, and you have had a poor sleep pattern in the "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight loss journey ."
                        else:
                            response = "You have high calorie intake levels in the last "+str(len(peaks_valleys['peaks_calin']))+" days. These are affecting your weight loss journey."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "you have had a poor sleep pattern in the last "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight loss journey."
                        else:
                            response = "Your body performance and habits seem to be great. I didn’t spot any issue."
            return response

        elif self.id == 2:
            if len(peaks_valleys['peaks_steps'])>3:
                if len(peaks_valleys['peaks_cal'])>3:
                    if len(peaks_valleys['valleys_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You have high activity level in the last "+str(len(peaks_valleys['peaks_steps']))+" days, high calories burn rate in the "+str(len(peaks_valleys['peak_cal']))+" days, you have taken fewer calories in "+str(len(peaks_valleys['valleys_calin']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight gain journey."
                        else:
                            response = "You have high activity level in the last "+str(len(peaks_valleys['peaks_steps']))+" days, high calories burn rate in the "+str(len(peaks_valleys['peak_cal']))+" days, you have taken fewer calories in "+str(len(peaks_valleys['valleys_calin']))+" days. These are affecting your weight gain journey."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You have high activity level in the last "+str(len(peaks_valleys['peaks_steps']))+" days, high calories burn rate in the "+str(len(peaks_valleys['peak_cal']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight gain journey."
                        else:
                            response = "You have high activity level in the last "+str(len(peaks_valleys['peaks_steps']))+" days, high calories burn rate in the "+str(len(peaks_valleys['peak_cal']))+" days. These are affecting your weight gain journey."
                else:
                    if len(peaks_valleys['valleys_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You have high activity level in the last "+str(len(peaks_valleys['peaks_steps']))+" days, you have taken fewer calories in "+str(len(peaks_valleys['valleys_calin']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight gain journey."
                        else:
                            response = "You have high activity level in the last "+str(len(peaks_valleys['peaks_steps']))+" days, you have taken fewer calories in "+str(len(peaks_valleys['valleys_calin']))+" days. These are affecting your weight gain journey."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You have high activity level in the last "+str(len(peaks_valleys['peask_steps']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight gain journey."
                        else:
                            response = "You have high activity level in the last "+str(len(peaks_valleys['peak_ssteps']))+" days that is affecting your weight gaining performance."
            else:
                if len(peaks_valleys['peaks_cal'])>3:
                    if len(peaks_valleys['valleys_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = " You have high calories burn rate in the last "+str(len(peaks_valleys['peaks_cal']))+" days, you have taken fewer calories in "+str(len(peaks_valleys['valleys_calin']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight gain journey."
                        else:
                            response = "You have high calories burn rate in the last "+str(len(peaks_valleys['peaks_cal']))+" days, you have taken fewer calories in "+str(len(peaks_valleys['valleys_calin']))+" days. These are affecting your weight gain journey."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You have high calories burn rate in the last "+str(len(peaks_valleys['peaks_cal']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight gain journey."
                        else:
                            response = "You have high calories burn rate in the last "+str(len(peaks_valleys['peaks_cal']))+" days. These are affecting your weight gain journey."
                else:
                    if len(peaks_valleys['valleys_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You have taken fewer calories in the last"+str(len(peaks_valleys['valleys_calin']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight gain journey."
                        else:
                            response = "You have taken fewer calories in the last "+str(len(peaks_valleys['valleys_calin']))+" days. These are affecting your weight gain journey."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You have improper sleep pattern in the last"+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight gain journey."
                        else:
                            response = "Your body performance and habits seem to be great. I didn’t spot any issue."
            return response

        elif self.id == 3:
            if len(peaks_valleys['peaks_steps'])>2 or len(peaks_valleys['valleys_steps'])>2:
                if len(peaks_valleys['peaks_cal'])>2 or len(peaks_valleys['valleys_cal'])>2:
                    if len(peaks_valleys['valleys_calin'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You have had an inconsistent activity level in the last "+str(len(peaks_valleys['peaks_steps'])+ len(peaks_valleys['valleys_steps']))+" days, poor calories burn rate in the  "+str(len(peaks_valleys['peaks_cal'])+len(peaks_valleys['valleys_cal']))+" days, inconsistent calories intake in the "+str(len(peaks_valleys['valleys_calin'])+len(peaks_valleys['peaks_calin']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight maintaining performance."
                        else:
                            response = "You have had an inconsistent activity level in the last "+str(len(peaks_valleys['peaks_steps'])+ len(peaks_valleys['valleys_steps']))+" days, poor calories burn rate in the  "+str(len(peaks_valleys['peaks_cal'])+len(peaks_valleys['valleys_cal']))+" days, and inconsistent calories intake in the "+str(len(peaks_valleys['valleys_calin'])+len(peaks_valleys['peaks_calin']))+" days. These are affecting your weight maintainig performance."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You have had an inconsistent activity level in the last "+str(len(peaks_valleys['peaks_steps'])+ len(peaks_valleys['valleys_steps']))+" days, poor calories burn rate in the  "+str(len(peaks_valleys['peaks_cal'])+len(peaks_valleys['valleys_cal']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight maintainig performance."
                        else:
                            response = "You have had an inconsistent activity level in the last "+str(len(peaks_valleys['peaks_steps'])+ len(peaks_valleys['valleys_steps']))+" days, and poor calories burn rate in the  "+str(len(peaks_valleys['peaks_cal'])+len(peaks_valleys['valleys_cal']))+" days that are affecting your weight maintainig performance."
                else:
                    if len(peaks_valleys['valleys_calin'])>3 or len(peaks_valleys['peaks_calin']):
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You have had an inconsistent activity level in the last "+str(len(peaks_valleys['peaks_steps'])+ len(peaks_valleys['valleys_steps']))+" days, you have improper calories intake in the "+str(len(peaks_valleys['valleys_calin'])+len(peaks_valleys['valleys_cal']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight maintainig performance."
                        else:
                            response = "You have had an inconsistent activity level in the last "+str(len(peaks_valleys['peaks_steps'])+ len(peaks_valleys['valleys_steps']))+" days, and you have improper calories intake in the "+str(len(peaks_valleys['valleys_calin'])+len(peaks_valleys['valleys_cal']))+" days. These are affecting your weight maintainig performance."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You have had an inconsistent activity level in the last "+str(len(peaks_valleys['peaks_steps'])+ len(peaks_valleys['valleys_steps']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days. These are affecting your weight maintainig performance."
                        else:
                            response = "You have had an inconsistent activity level in the last "+str(len(peaks_valleys['peaks_steps'])+ len(peaks_valleys['valleys_steps']))+" days that is affecting your weight maintainig performance."
            else:
                response = "Your body performance and habits seem to be great. I didn’t spot any issue."

            return response

        elif self.id == 4:
            if len(peaks_valleys['peaks_steps'])>3:
                if len(peaks_valleys['peaks_cal'])>3:
                    if len(peaks_valleys['valleys_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You can gain weight by reducing your activity level, burning fewer calories and high calories intake. Also, by sleeping 7-9 hours."
                        else:
                            response = "You can gain weight by reducing your activity level, burning fewer calories and high calories intake."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You can gain weight by reducing your activity level, burning fewer calories. Also, by sleeping 7-9 hours."
                        else:
                            response = "You can gain weight by reducing your activity level, burning fewer calories."
                else:
                    if len(peaks_valleys['valleys_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You can gain weight by reducing your activity level, by increasing calories intake. Also, by sleeping 7-9 hours."
                        else:
                            response = "You can gain weight by reducing your activity level, by increasing calories intake."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You can gain weight by reducing your activity level and  by sleeping 7-9 hours."
                        else:
                            response = "You can gain weight by reducing your activity level."
            else:
                if len(peaks_valleys['peaks_cal'])>3:
                    if len(peaks_valleys['valleys_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You can gain weight by burning fewer calories and high calories intake. Also, by sleeping 7-9 hours."
                        else:
                            response = "You can gain weight by burning fewer calories and high calories intake."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You can gain weight by burning fewer calories. Also, by sleeping 7-9 hours."
                        else:
                            response = "You can gain weight by burning fewer calories."
                else:
                    if len(peaks_valleys['valleys_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You can gain weight by high calories intake. Also, by sleeping 7-9 hours."
                        else:
                            response = "You can gain weight by high calories intake."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You can gain weight by sleeping 7-9 hours."
                        else:
                            response = "Your body performance seems fine for gaining weight. I didn’t spot any issue at this time."

            return response

        elif self.id == 5:
            if len(peaks_valleys['valleys_steps'])>3:
                if len(peaks_valleys['valleys_cal'])>3:
                    if len(peaks_valleys['peaks_calin'])>3:
                        if len(peaks_valleys['peaks_sleep'])>2 or len(peaks_valleys['valleys_sleep'])>2:
                            response = "You can lose weight by increasing your activity level, by burning more calories and fewer calories intake. Also, by sleeping 7-9 hours."
                        else:
                            response = "You can lose weight by increasing your activity level, by burning more calories and fewer calories intake."
                    else:
                        if len(peaks_valleys['peaks_sleep'])>2 or len(peaks_valleys['valleys_sleep'])>2:
                            response = "You can lose weight by increasing your activity level, by burning more calories. Also, by sleeping 7-9 hours."
                        else:
                            response = "You can lose weight by increasing your activity level, by burning more calories."
                else:
                    if len(peaks_valleys['peaks_calin'])>3:
                        if len(peaks_valleys['peaks_sleep'])>2 or len(peaks_valleys['valleys_sleep'])>2:
                            response = "You can lose weight by increasing your activity level, by fewer calories intake. Also, by sleeping 7-9 hours."
                        else:
                            response = "You can lose weight by increasing your activity level, by fewer calories intake."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = " you can lose weight by increasing your activity level and by sleeping 7-9 hours."
                        else:
                            response = "You can lose weight by increasing your activity level."
            else:
                if len(peaks_valleys['valleys_cal'])>3:
                    if len(peaks_valleys['peaks_calin'])>3:
                        if len(peaks_valleys['peaks_sleep'])>2 or len(peaks_valleys['valleys_sleep'])>2:
                            response = "You can lose weight by burning more calories and fewer calories intake. Also, by sleeping 7-9 hours."
                        else:
                            response = "You can lose weight by burning more calories and fewer calories intake."
                    else:
                        if len(peaks_valleys['peaks_sleep'])>2 or len(peaks_valleys['valleys_sleep'])>2:
                            response = "You can lose weight by burning more calories. Also, by sleeping 7-9 hours."
                        else:
                            response = "You can lose weight by burning more calories."
                else:
                    if len(peaks_valleys['peaks_calin'])>3:
                        if len(peaks_valleys['peaks_sleep'])>2 or len(peaks_valleys['valleys_sleep'])>2:
                            response = "You can lose weight by fewer calories intake. Also, by sleeping 7-9 hours."
                        else:
                            response = "You can lose weight by fewer calories intake."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "You can lose weight by sleeping 7-9 hours."
                        else:
                            response = "Your body performance seems fine for losing weight. I didn’t spot any issue."
            return response

        elif self.id == 6:
            if len(peaks_valleys['peaks_cal'])>2 or len(peaks_valleys['valleys_cal'])>2:
                if len(peaks_valleys['valleys_calin'])>2 or len(peaks_valleys['peaks_calin'])>2:
                    if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                        response = "You can maintain weight by balancing calories in/out ratio and with proper sleep pattern."
                    else:
                        response = "You can maintain weight by balancing calories in/out ratio."
                else:
                    if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                        response = "You can maintain weight by burning calories as per calories intake, and with proper sleep pattern."
                    else:
                        response = "You can maintain weight by burning calories as per calories intake."
            else:
                if len(peaks_valleys['valleys_calin'])>3 or len(peaks_valleys['peaks_calin']):
                    if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                        response = "You can maintain weight by taking calories as per calories burnt, and with proper sleep pattern."
                    else:
                        response = "You can maintain weight by taking calories as per calorie burnt."
                else:
                    if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                        response = "You can maintain weight with proper sleep pattern."
                    else:
                        response = "Your activity level seems fine maintaining weight. I didn’t spot any issue."

            return response

        elif self.id == 7:
            if len(peaks_valleys['peaks_steps'])>4 or len(peaks_valleys['valleys_steps'])>4:
                if len(peaks_valleys['peaks_cal'])>4 or len(peaks_valleys['valleys_cal'])>4:
                    if len(peaks_valleys['valleys_calin'])>4 or len(peaks_valleys['peaks_sleep'])>4:
                        if len(peaks_valleys['valleys_sleep'])>4 or len(peaks_valleys['peaks_sleep'])>4:
                            response = "Inconsistent activity level, poor calories in/out patterns, and poor sleep pattern are bad habits in your life."
                        else:
                            response = "Inconsistent activity level, poor calories in/out patterns are bad habits in your life."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>4 or len(peaks_valleys['peaks_sleep'])>4:
                            response = "Inconsistent activity level, poor calories burning rate, and poor sleep pattern are bad habits in your life."
                        else:
                            response = "Inconsistent activity level, and poor calories burning rate are bad habits in your life."
                else:
                    if len(peaks_valleys['valleys_calin'])>4 or len(peaks_valleys['peaks_calin'])>4:
                        if len(peaks_valleys['valleys_sleep'])>4 or len(peaks_valleys['peaks_sleep'])>4:
                            response = "Inconsistent activity level, improper calories intake, and poor sleep pattern are bad habits in your life."
                        else:
                            response = "Inconsistent activity level, and improper calories intake bad habits in your life."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>4 or len(peaks_valleys['peaks_sleep'])>4:
                            response = "Inconsistent activity level, and poor sleep pattern are bad habits in your life."
                        else:
                            response = "Inconsistent activity level is the bad habit in your life."
            else:
                response = "Your body performance and habits seem to be great. I didn’t spot any issue."

            return response


        elif self.id == 8:
            return 'System is unable to answer this question at this moment.'

        elif self.id == 9 and goal==1:
            if len(peaks_valleys['valleys_steps'])>4:
                if len(peaks_valleys['valleys_cal'])>4:
                    if len(peaks_valleys['peaks_calin'])>4:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "Low level activity, fewer calories consumption and high calories intake, and poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "Low level activity, fewer calories consumption and high calories intake are keeping you away from your goal."
                    else:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "Low level activity, fewer calories consumption, and poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "Low level activity, fewer calories consumption are keeping you away from your goal."
                else:
                    if len(peaks_valleys['peaks_calin'])>4:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "Low level activity, high calories intake, and poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "Low level activity and high calories intake are keeping you away from your goal."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>3 or len(peaks_valleys['peaks_sleep'])>3:
                            response = "Low level activity, and poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "Low level activity is keeping you away from your goal."
            else:
                if len(peaks_valleys['valleys_cal'])>4:
                    if len(peaks_valleys['peaks_calin'])>4:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "Fewer calories consumption and more calories intake. Also, poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "Fewer calories consumption and more calories intake are keeping you away from your goal."
                    else:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "Fewer calories consumption. Also, poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "Fewer calories consumption is keeping you away from your goal."
                else:
                    if len(peaks_valleys['peaks_calin'])>4:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "High calories intake. Also, poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "High calories intake is keeping you away from your goal."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>3 or len(peaks_valleys['peaks_sleep'])>3:
                            response = "Poor sleep pattern is keeping you away from your goal."
                        else:
                            response = "You are on track to achieving your goal. Keep up the great work!"

            return response

        elif self.id == 10 and goal==0:
            if len(peaks_valleys['peaks_steps'])>4:
                if len(peaks_valleys['peaks_cal'])>4:
                    if len(peaks_valleys['valleys_calin'])>4:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "High level activity, high calories burn rate and fewer calories intake, and poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "High level activity, high calories burn rate and fewer calories intake are keeping you away from your goal."
                    else:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "High level activity, high calories burn rate, and poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "High level activity, high calories burn rate are keeping you away from your goal."
                else:
                    if len(peaks_valleys['valleys_calin'])>4:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "High level activity, fewer calories intake, and poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "High level activity, fewer calories intake are keeping you away from your goal."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>3 or len(peaks_valleys['peaks_sleep'])>3:
                            response = "High level activity and poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "High level activity is keeping you away from your goal."
            else:
                if len(peaks_valleys['peaks_cal'])>4:
                    if len(peaks_valleys['valleys_calin'])>4:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "High calories burn rate and fewer calories intake and poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "High calories burn rate and fewer calories intake are keeping you away from your goal."
                    else:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "High calories burn rate and poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "High calories burn rate are keeping you away from your goal."
                else:
                    if len(peaks_valleys['valleys_calin'])>4:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "Fewer calories intake and poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "Fewer calories intake is keeping you away from your goal."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>3 or len(peaks_valleys['peaks_sleep'])>3:
                            response = "Poor sleep pattern is keeping you away from your goal."
                        else:
                            response = "You are on track to achieving your goal. Keep up the great work!"
            return response

        elif self.id==11:    
            return 'Predicted Weight: '

        else:
            return "nothing"


class forcasting:
  
  def __init__(self):
    self.lEnginefinal=None
    self.mean=None
    self.std=None
    self.predicted_weight=None
    self.current_weight=None
    self.return_print=None
   
  def data_preprocessing(self,range=None,unique_id=None,
                         filename = "updated_fitbit_dataset.csv",sort=True):
  # given the list if unique id and range i.e unique_id=['645724], range =1
  # else it will get all unique id's and store its dates and weights as weight_id, date_id
    fitbit_df = pd.read_csv(filename);

    df_data={}
    if not unique_id:
      unique_id=(fitbit_df['id'].unique())

    if (not range) or range>len(unique_id):
      range=len(unique_id)

    #unique_id=unique_id[:10]
    for i in unique_id[:range]:
      #print(i)
      id_list=np.where(fitbit_df['id']==i)
      #print(id_list[0])
      if sort:
        df_data['WEIGHT'+str(i)]=sorted((self.standard(fitbit_df.loc[id_list[0],'weight'].values)),key = lambda x:float(x))
      else:
        df_data['WEIGHT'+str(i)]=(self.standard(fitbit_df.loc[id_list[0],'weight'].values))
      df_data['DATE'+str(i)]=fitbit_df.loc[id_list[0],'date'].values

    #print('df_data:',df_data)
    df_data=pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in df_data.items() ]))
    return df_data


  def standard(self,arr1):
    std=np.std(arr1)
    mean=np.mean(arr1)
    self.std=std
    self.mean=mean
    for i in range(0,len(arr1)):
      arr1[i]=(arr1[i]-mean)/std
    return arr1
  
  def inverse_standard(self,arr1):
    if self.std and self.mean:
      std=self.std
      mean=self.mean
      for i in range(0,len(arr1)):
        arr1[i]=(arr1[i]*std)+mean
      return arr1
    print('calculate standardization first')

  def single_user(self,df_train,i_weight,i_date):
    columns=df_train.columns
    length=len(columns)

    if i_date%2!=0 and i_weight%2==0 and i_weight<length and i_date<length:
      df_train_temp = pd.DataFrame({"Date" :df_train.loc[:,columns[i_date]] ,
                         "Signal" :df_train.loc[:,columns[i_weight]]})
      df_train_temp=df_train_temp.dropna()
      df_train_temp['Date']= df_train_temp['Date'].apply(lambda x : datetime.datetime.strptime(str(x), "%Y-%m-%d"))
      return df_train_temp
    else:
      print('wrong i_weight or i_date')
      return None

  def train(self,df_train_1,Horizon=9,printing=False):
    # create a forecast engine. This is the main object handling all the operations
    #print(df_train_1)

    lEngine = autof.cForecastEngine()
    print('lEngine:',lEngine)
    # get the best time series model for predicting one week
    lEngine.train(iInputDS = df_train_1, iTime = 'Date', iSignal = 'Signal', iHorizon = Horizon)
    print('here 1')

    lEngine.getModelInfo() # => relative error 7% (MAPE)
    print('here 2 ')
    # df_forecast = lEngine.forecast(iInputDS = df_train_1, iHorizon = Horizon)
    # print(df_forecast)
    # print(df_forecast['Date'].tail(Horizon).values)
    # print(df_forecast['Signal'].tail(Horizon).values)

    # df_forecast['Signal']=self.inverse_standard(df_forecast['Signal'].values)

    # print(df_forecast['Signal'].tail(Horizon).values)

    if printing:
      lEngine.standardPlots()
    self.lEnginefinal=lEngine
    return lEngine

  def forcast(self,df_train_2,lEnginefinal1=None,Horizon=9):

    # if lEnginefinal1:

    #   engine=lEnginefinal1

    # elif self.lEnginefinal:

    #   engine=self.lEnginefinal
    # else:
    #   print('Error: In order to predict, train the model first, or provide the trained model as argument.')
    #   return 
    
    try:
      df_forecast = self.lEnginefinal.forecast(iInputDS = df_train_2, iHorizon = Horizon)

      print(df_forecast['Date'].tail(Horizon).values)
      df_forecast.plot('Date' , ['Signal','Signal_Forecast'])
      df_forecast['Signal_Forecast']=self.inverse_standard(df_forecast['Signal_Forecast'].values)
      print(df_forecast['Signal_Forecast'].tail(Horizon).values)
      self.predicted_weight=(df_forecast['Signal_Forecast']).iloc[-1]
      self.current_weight=(df_forecast['Signal_Forecast']).iloc[-16]
      self.return_print = 'Your current weight is: ' + str(round(self.current_weight, 2)) + ', and your predicted weight after ' + str(Horizon) + ' days is: ' + str(round(self.predicted_weight, 2))
      return None 
  
      #return deepcopy((df_forecast['Signal_Forecast'].tail(Horizon).values))

      #df_forecast.plot('Date' , ['Signal','Signal_Forecast'])
      #return (df_forecast['Signal_Forecast'][len(df_forecast['Signal_Forecast'])-Horizon+1]),((df_forecast['Signal_Forecast']).iloc[-1]),df_forecast
    except Exception as e:
      print ("error in forcasting : ",e)
      return None

  def forcast_weight(self,id,time,sort=True):
    try:
      df_train=self.data_preprocessing(range=1,unique_id=[id],sort=sort)
      print('df_train:', df_train)
      #getting the user data 
      print(df_train.columns)
      df_train_temp=self.single_user(df_train,0,1)
      print('df_train_temp:', df_train_temp)
      #print(df_train_temp)
      # training on user 
      self.train(df_train_temp,Horizon=time-3)
      # forcasting the data 
      print('model has trained')
      return self.forcast(df_train_temp,Horizon=time)
    except Exception as e:
      print ("error in forcast_weight : ",e)


class Pipeline:
    def __init__(self, id, goal, days=30):
        self.id = id
        self.days = days
        self.goal = goal
        df_updated= pd.read_csv("UpdatedDatasetFitBit.csv")
        domain = df_updated.groupby('id')
        self.user=domain.get_group(id)
        self.user= self.user[-days:]
    
    def FindPeaksValleys(self):
        t = np.arange(1,len(self.user.total_steps)+1)
    #     user['SMA_steps']=user['total_steps'].rolling(2, min_periods=1).mean().tolist()
    #     series1 = user.SMA_steps
        max_thresh = 11000
        min_thresh = 9000
        peak_idx1 = self.user.total_steps > max_thresh
        peak_idx1 = [i for i, x in enumerate(peak_idx1) if x]
        valley_idx1 = self.user.total_steps < min_thresh
        valley_idx1 = [i for i, x in enumerate(valley_idx1) if x]

        max_thresh = 2600
        min_thresh = 1800
        peak_idx2 = self.user.calories > max_thresh
        peak_idx2 = [i for i, x in enumerate(peak_idx2) if x]
        valley_idx2 = self.user.calories < min_thresh
        valley_idx2 = [i for i, x in enumerate(valley_idx2) if x]  

        max_thresh = 2800
        min_thresh = 2300

        peak_idx3 = self.user.calories_in > max_thresh
        peak_idx3 = [i for i, x in enumerate(peak_idx3) if x]
        valley_idx3 = self.user.calories_in < min_thresh
        valley_idx3 = [i for i, x in enumerate(valley_idx3) if x]

        max_thresh = 9
        min_thresh = 7

        peak_idx4 = self.user.sleep_hours > max_thresh
        peak_idx4 = [i for i, x in enumerate(peak_idx4) if x]
        valley_idx4 = self.user.sleep_hours < min_thresh
        valley_idx4 = [i for i, x in enumerate(valley_idx4) if x]
        
        new_ke_lis = ['peaks_steps', 'peaks_cal', 'peaks_calin','peaks_sleep','valleys_steps', 'valleys_cal', 'valleys_calin','valleys_sleep']

        new_val_lis = [peak_idx1,peak_idx2,peak_idx3, peak_idx4,valley_idx1,valley_idx2,valley_idx3, valley_idx4]
        peaks_valleys = dict(zip(new_ke_lis, new_val_lis))
        
        
        return peaks_valleys

    def Run(self,id):
        peaks_valleys = self.FindPeaksValleys()
        intent=Questions(id)
        response=intent.Response(peaks_valleys)
        #self.ShowGraph(peaks_valleys)
        return peaks_valleys,response

class action_QN_response(Action): 
    def name(self) -> Text:
        return "action_QN_response"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        filename = "UpdatedDatasetFitBit.csv"
        fitbit_df = pd.read_csv(filename);
        user_ids = fitbit_df.iloc[:, 1]

        print(str((tracker.current_state())["sender_id"]))
        user_id = str((tracker.current_state())["sender_id"])


        if user_id not in user_ids.values:
            dispatcher.utter_message(text = "There is no historical data available about you at the moment.")
            return []
        days=30
        goal=0
        pipeline= Pipeline(user_id,days,goal)


        if str(tracker.latest_message['intent'].get('name')) == "QN1":
            ques_id=1
        if str(tracker.latest_message['intent'].get('name')) == "QN2":
            ques_id=2
        if str(tracker.latest_message['intent'].get('name')) == "QN3":
            ques_id=3
        if str(tracker.latest_message['intent'].get('name')) == "QN4":
            ques_id=4
        if str(tracker.latest_message['intent'].get('name')) == "QN5":
            ques_id=5
        if str(tracker.latest_message['intent'].get('name')) == "QN6":
            ques_id=6
        if str(tracker.latest_message['intent'].get('name')) == "QN7":
            ques_id=7
        if str(tracker.latest_message['intent'].get('name')) == "QN8":
            ques_id=8
        if str(tracker.latest_message['intent'].get('name')) == "QN9_10":
            if goal == 1:
                ques_id=9
        if str(tracker.latest_message['intent'].get('name')) == "QN9_10":
            if goal == 0:
                ques_id=10
        if str(tracker.latest_message['intent'].get('name')) == "QN11":
            days = next(tracker.get_latest_entity_values(entity_type="NUMBER", entity_role="predict"),None)
            if days:
                days = int(days)
            else:
                days = 30
            print(days)
            obj=forcasting()
            data=obj.forcast_weight(user_id,days)
            dispatcher.utter_message(text = obj.return_print)
            ques_id = 0
        if ques_id != 0:
            peaks_valleys,response = pipeline.Run(ques_id)
            print(response)
            dispatcher.utter_message(text = response)


class MealPlanner:
    def __init__(self, data, dietPlan, specific, budget, days=7):
        self.data = data
        self.dietPlan = dietPlan
        self.specific = specific
        self.budget = budget
        
        
        self.specific = self.specific.replace(',','|')
        user_data =  self.data[self.data.Type.str.lower().str.contains(self.dietPlan)]
        user_data = user_data[user_data.specific.str.lower().str.contains(self.specific)]
        
        user_data.rename(columns = {'meal-type':'meal_type'}, inplace = True)
        user_data['calories'] = user_data['calories'].astype('str').str.extractall('(\d+)').unstack().fillna('').sum(axis=1).astype(int)
        
        if user_data.empty:
            print('Issue in diet plan name, food preference, or budget. Unable to get data with given conditions.')
            return
        
        self.types=user_data.groupby('meal_type')
        
        two = 0.2 * int(self.budget)
        three = 0.3 * int(self.budget)
        four = 0.4 * int(self.budget)
        five = 0.05 * int(self.budget)
        cal = 0
        plan=[]
        self.N=int(days)+1
        try:
            for i in range(1,self.N):
                cal=0
                for meal,detail in self.types:
                    if meal == 'Breakfast':
                        df = detail.query('calories >= @two and calories <= @three').sample()
                    elif meal == 'Lunch' or meal == 'Dinner':
                        df = detail.query('calories >= @three and calories <= @four').sample()
                    else:
                        df = detail.query('calories >= @five and calories <= (@five+@five)').sample()

                    if (int(df['calories']) + cal) <= (1.2*int(budget)):
                        cal += int(df['calories'])
                        df['Day'] = i
                        plan.append(df)
                    else:
                        j=0
                        while (int(df['calories']) + cal) > (1.2*int(budget)):
                            if meal == 'Breakfast':
                                df = detail.query('calories >= @two and calories <= @three').sample()
                            elif meal == 'Lunch' or meal == 'Dinner':
                                df = detail.query('calories >= @three and calories <= @four').sample()
                            else:
                                df = detail.query('calories >= @five and calories <= (@five+@five)').sample()
                            j +=1
                            if (int(df['calories']) + cal) <= (1.2*int(budget)):
                                cal += int(df['calories'])
                                df['Day'] = i
                                plan.append(df)
                                break
                            if j>=len(detail):
                                break

            self.meal_plan = pd.concat(plan)
        except Exception as exp:
            self.meal_plan = None
            print('Not enough meals are available for given specifications.')
            
    
    def getMealPlanner(self):
        return self.meal_plan
    
    def getShoppingList(self):
        ingred = []
        for ing in self.meal_plan['Ingredients']:
            ingred.append(list(ast.literal_eval(ing)))
        
        ingredient = []
        for ing in ingred:
            method=''
            for i in range(len(ing)):

                s=''
                if len(ing[i]) > 1:
                    for j in range(1,len(ing[i])):
                        if ing[i][j]!=' ':
                            s += ' '+''.join(ing[i][j])

        #         print(s)
                method += s+'\n'
            #print(method)
            ingredient.append(method)
            
        shoping_list = set()
        for i in range(len(self.meal_plan)):
            shoping=set(ingredient[i].split('\n'))
            for val in shoping:
                shoping_list.add(val)
        
        shoping_list = list(shoping_list)
        shoping_list = [val.lstrip() for val in shoping_list]
        shoping_list = [val.lstrip(',') for val in shoping_list]
        shoping_list = [val.lstrip() for val in shoping_list]
        shop_list='\n'.join(shoping_list)
        
        return shop_list
    
    def getMealDetails(self,day,dietType, meal_df):
        dietType = dietType.capitalize()
        mealDetail = meal_df.query('Day == @day and meal_type == @dietType')
        
        return mealDetail
    
    def getAlternateMeal(self, day, dietType):
        dietType = dietType.capitalize()
        two = 0.2 * int(self.budget)
        three = 0.3 * int(self.budget)
        four = 0.4 * int(self.budget)
        five = 0.05 * int(self.budget)
        
        group = self.types.get_group(dietType)
        
        if dietType == 'Breakfast':
            meal = group.query('calories >= @two and calories <= @three').sample()
            
        elif dietType == 'Lunch' :
            meal = group.query('calories >= @three and calories <= @four').sample()
            
        elif dietType == 'Dinner':
            meal = group.query('calories >= @three and calories <= @four').sample()
            
        else:
            meal = group.query('calories >= @five and calories <= (@five+@five)').sample()
        
        meal['Day']=day
        
        self.meal_plan.drop(self.meal_plan.query('Day == @day and meal_type== @dietType').index,inplace = True)
        self.meal_plan = pd.concat([self.meal_plan, meal], ignore_index = True, axis = 0)
        
        return meal

class ValidateDietForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_diet_form"

    def validate_diet_type(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if not slot_value:
            dispatcher.utter_message(text=f"I’m sorry I didn’t understand, I’m still learning please try telling me your diet type differently.")
            return {"diet_type": None}
        elif slot_value in ['keto', 'low-carb', 'high-protein']:
            dispatcher.utter_message(text=f"Noted! You have chosen {slot_value} as your diet type.")
            return {"diet_type": slot_value}
        else:
            dispatcher.utter_message(text=f"Seems like you have typed incorrect diet type. I’m still learning please try saying it differently.")
            return {"diet_type": None}

    # def validate_calories_budget(
    #         self,
    #         slot_value: Any,
    #         dispatcher: CollectingDispatcher,
    #         tracker: Tracker,
    #         domain: DomainDict,
    # ) -> Dict[Text, Any]:
    # if not slot_value:
    #     dispatcher.utter_message(text=f"I’m sorry I didn’t understand, I’m still learning please try telling me your diet type differently.")
    #     return {"diet_type": None}
    # else:
    #     dispatcher.utter_message(text=f"Noted! Your calories budget is {slot_value}.")
    #     return {"calories_budget": slot_value}


class ActionChangeDietPlan(Action):
    def name(self) -> Text:
        return "action_change_diet_plan"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(str((tracker.current_state())["sender_id"]))
        user_id = str((tracker.current_state())["sender_id"])
        # mealplan_file = user_id + '_mealPlan.csv'

        user_db = get_mongo_database()

        data = pd.read_csv('FinalFoodDatabase_V1.csv')

        slot_value = next(tracker.get_latest_entity_values(entity_type="diet", entity_role="diet2"), None)
        if not slot_value:
            dispatcher.utter_message(text=f"I’m sorry I didn’t understand, I’m still learning please try telling me your diet type differently.")
            return {"diet_type": None}
        elif slot_value in ['keto', 'low-carb', 'high-protein']:
            user_record = user_db.users.find_one({"_id": ObjectId(user_id)})
            if dietType in user_record["userInfo"]:
                if user_db['users']['userInfo']['dietType'] == slot_value:
                    dispatcher.utter_message(text = f'You already have a {dietType} plan, if you want to create one for another diet type then try typing something like:\n\
                Change my diet plan from keto to low-carb.\n And I will create one for you as per your new diet type.')

            user_db.userMeals.delete_many({"user_id": user_id})
            dispatcher.utter_message(text=f"Noted! You have chosen {slot_value} as your diet type.")
            diet_type = slot_value
            user_record = user_db.users.find_one({"_id": ObjectId(user_id)})
            email = user_record['email']
            eating_db = user_record['userInfo']['eating'] ## Will give values: 'VEGAN', 'VEGETARIAN', 'NON_VEGETARIAN'
            eating_dict = {'VEGAN': 'vegan', 'VEGETARIAN': 'vegetarian', 'NON_VEGETARIAN': 'high-protien,dairy-free'}
            eating = eating_dict.get(eating_db, None)
            # eating = tracker.get_slot('eating') ## Need to get this value from database so that it is updated always.
            # eating = 'vegetarian'
            #calories_budget = int(tracker.get_slot('calories_budget'))
            calories_budget = 2000
            print(diet_type, eating)
            planner = MealPlanner(data, diet_type, eating, calories_budget, 7)
            print(planner)
            day_created = datetime.datetime.today()
            if planner.meal_plan is not None:
                for i in range(len(planner.meal_plan)):
                    user_db.userMeals.insert_one({"user_id":user_id, 'day_created': day_created,'name':planner.meal_plan['name'].iat[i], 'meal_type':planner.meal_plan['meal_type'].iat[i], 
                        'specific' : planner.meal_plan['specific'].iat[i], 'net_carbs' : int(planner.meal_plan['net-carbs'].iat[i]), 'type' : planner.meal_plan['Type'].iat[i],
                         'calories' : int(planner.meal_plan['calories'].iat[i]), 'unit' : planner.meal_plan['Unit'].iat[i], 'serving' : int(planner.meal_plan['serving'].iat[i]), 
                         'ingredients' : planner.meal_plan['Ingredients'].iat[i], 'nutrients' : planner.meal_plan['Nutrients'].iat[i], 
                         'method': planner.meal_plan['Method'].iat[i], 'time': planner.meal_plan['Time'].iat[i], 'difficulty': planner.meal_plan['Difficulty'].iat[i],
                         'link': planner.meal_plan['link'].iat[i], 'day': int(planner.meal_plan['Day'].iat[i])})
                shop_list = planner.getShoppingList()
                user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.dietType': diet_type}})
                print(shop_list)
                email_subject = 'Diet Plan Shopping List'
                raw_email_message = shop_list
                email_message = raw_email_message ## We can use the raw email message here as it is in string datatype
                threading.Thread(target = send_email, args = (email, email_subject, email_message, '')).start()
                # status = send_email('sdin.bscs15seecs@seecs.edu.pk', email_subject, email_message, '')
                #sleep(randint(1, 3))
                # planner.meal_plan.to_csv(mealplan_file)
                # if status:
                dispatcher.utter_message(text = "Sure, I emailed you a shopping list that will last for 7 days.Once you have the ingredients ask me for meal plans. Say things like “give me a breakfast plan”.")
                return [SlotSet("diet_type", None)]
                # else:
                #     dispatcher.utter_message(text = "Sure, Meal plan has been created for you that will last for 7 days.Once you have the ingredients ask me for meal plans. Say things like “give me a breakfast plan”.\nThe shopping list could not be emailed to you for the time being.")
            else:
                dispatcher.utter_message(text = "Meal plan can not be created for the time being as per your requirements.\n\
                 I am really sorry for the inconvinience, keep using the app and in future we will have more data and will be able to accomodate your requirements.")
                return [SlotSet("diet_type", None)]
        else:
            dispatcher.utter_message(text=f"Seems like you have typed incorrect diet type. I’m still learning please try saying it differently.")
            return {"diet_type": None}


class ActionGetShoppingList(Action):
    def name(self) -> Text:
        return "action_get_shopping_list"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(str((tracker.current_state())["sender_id"]))
        user_id = str((tracker.current_state())["sender_id"])
        # mealplan_file = user_id + '_mealPlan.csv'

        user_db = get_mongo_database()

        data = pd.read_csv('FinalFoodDatabase_V1.csv')
        diet_type = tracker.get_slot('diet_type')
        if user_db.userMeals.find({'user_id':user_id}).count()>0:
            user_meals = user_db.userMeals.find({"user_id": user_id})
            day = ((datetime.datetime.today() - user_meals[0]['day_created']).days + 1)
            day_number = 7 - day
            if day <= 7:
                dispatcher.utter_message(text = f"You already are on a {diet_type} diet plan and currently on day number{day_number}\n\
                    Say things like “give me a breakfast plan”. And I will be able to give you your meal plan.\n\
                    If you want to change the diet type then try typing something like \'change my diet type from keto to low-carb\' and I'll give you a new diet plan.")
                return [SlotSet("diet_type", None)]
            else:
                user_db.userMeals.delete_many({"user_id": user_id})
        user_record = user_db.users.find_one({"_id": ObjectId(user_id)})
        email = user_record['email']
        eating_db = user_record['userInfo']['eating'] ## Will give values: 'VEGAN', 'VEGETARIAN', 'NON_VEGETARIAN'
        eating_dict = {'VEGAN': 'vegan', 'VEGETARIAN': 'vegetarian', 'NON_VEGETARIAN': 'high-protien,dairy-free'}
        eating = eating_dict.get(eating_db, None)
        # eating = tracker.get_slot('eating') ## Need to get this value from database so that it is updated always.
        # eating = 'vegetarian'
        #calories_budget = int(tracker.get_slot('calories_budget'))
        calories_budget = 2000
        print(diet_type, eating)
        planner = MealPlanner(data, diet_type, eating, calories_budget, 7)
        print(planner)
        day_created = datetime.datetime.today()
        if planner.meal_plan is not None:
            for i in range(len(planner.meal_plan)):
                user_db.userMeals.insert_one({"user_id":user_id, 'day_created': day_created,'name':planner.meal_plan['name'].iat[i], 'meal_type':planner.meal_plan['meal_type'].iat[i], 
                    'specific' : planner.meal_plan['specific'].iat[i], 'net_carbs' : int(planner.meal_plan['net-carbs'].iat[i]), 'type' : planner.meal_plan['Type'].iat[i],
                     'calories' : int(planner.meal_plan['calories'].iat[i]), 'unit' : planner.meal_plan['Unit'].iat[i], 'serving' : int(planner.meal_plan['serving'].iat[i]), 
                     'ingredients' : planner.meal_plan['Ingredients'].iat[i], 'nutrients' : planner.meal_plan['Nutrients'].iat[i], 
                     'method': planner.meal_plan['Method'].iat[i], 'time': planner.meal_plan['Time'].iat[i], 'difficulty': planner.meal_plan['Difficulty'].iat[i],
                     'link': planner.meal_plan['link'].iat[i], 'day': int(planner.meal_plan['Day'].iat[i])})
            user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.dietType': diet_type}})
            shop_list = planner.getShoppingList()
            print(shop_list)
            email_subject = 'Diet Plan Shopping List'
            raw_email_message = shop_list
            email_message = raw_email_message ## We can use the raw email message here as it is in string datatype
            threading.Thread(target = send_email, args = (email, email_subject, email_message, '')).start()
            # status = send_email('sdin.bscs15seecs@seecs.edu.pk', email_subject, email_message, '')
            #sleep(randint(1, 3))
            # planner.meal_plan.to_csv(mealplan_file)
            # if status:
            dispatcher.utter_message(text = "Sure, I emailed you a shopping list that will last for 7 days.Once you have the ingredients ask me for meal plans. Say things like “give me a breakfast plan”.")
            return [SlotSet("diet_type", None)]
            # else:
            #     dispatcher.utter_message(text = "Sure, Meal plan has been created for you that will last for 7 days.Once you have the ingredients ask me for meal plans. Say things like “give me a breakfast plan”.\nThe shopping list could not be emailed to you for the time being.")
        else:
            dispatcher.utter_message(text = "Meal plan can not be created for the time being as per your requirements.\n\
             I am really sorry for the inconvinience, keep using the app and in future we will have more data and will be able to accomodate your requirements.")
            return [SlotSet("diet_type", None)]

class ActionGivePlan(Action):
    def name(self) -> Text:
        return "action_give_plan"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(str((tracker.current_state())["sender_id"]))
        user_id = str((tracker.current_state())["sender_id"])

        user_db = get_mongo_database()

        plan = next(tracker.get_latest_entity_values(entity_type="plan"),None)

        # mealplan_file = user_id + '_mealPlan.csv'
        # if os.path.exists(mealplan_file):
        #     meal_df = pd.read_csv(mealplan_file)
        user_meals = user_db.userMeals.find({"user_id": user_id})
        if user_meals.count() > 0:
            print('list of user meals\n')
            for meal in user_meals:
                print(meal)
                print('\n')
        else:
            dispatcher.utter_message(text = 'You do not have a meal/diet plan yet, if you want to create one then try typing something like:\n\
                I\'m thiking of going on a diet.\n And I will create one for you as per your diet type.')
            return []
        if plan in ['breakfast', 'lunch', 'snacks', 'dinner']:
            dietType = plan.capitalize()
            user_db.userMeals.update_many({'user_id' : user_id}, {'$set': {'last_meal':dietType}})
            day = ((datetime.datetime.today() - user_meals[0]['day_created']).days + 1)    ## Getting the meal day from current day minus day meal plan was created.
            #mealDetail = meal_df.query('Day == @day and meal_type == @dietType')
            for meal in user_meals:
                if (meal['day'] == day and meal['meal_type'] == dietType):
                    print('Meal given to user: ', meal)
                    break
            #lunch = planner.getMealDetails(day, plan, meal_df)
            lunch_name = meal['name'] + '(' + str(meal['calories']) + 'kcal)'   ## Lunch Name and Calories from the userMeals database
            lunch_ingridients = meal['ingredients']     ## Lunch Ingredients from the userMeals database
            lunch_method = meal['method']   ## Lunch method from the userMeals database
            dispatcher.utter_message(text = f"Your {meal['meal_type']} today is below. If you don’t like the meal ask me for another one instead.")
            dispatcher.utter_message(text = lunch_name)
            dispatcher.utter_message(text = 'The ingredients you need are:\n')
            dispatcher.utter_message(text = lunch_ingridients)
            dispatcher.utter_message(text = "Here is how to prepare it. Once you finish eating let me know and I count your calories and nutrition.")
            dispatcher.utter_message(text = lunch_method)

        else:
            dispatcher.utter_message(text = "I’m sorry I didn’t understand, I’m still learning please try asking about your meal type differently.")

class ActionFinishMeal(Action):
    def name(self) -> Text:
        return "action_finish_meal"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(str((tracker.current_state())["sender_id"]))
        user_id = str((tracker.current_state())["sender_id"])

        user_db = get_mongo_database()

        ## Need the last meal taken here along with the day.
        user_meals = user_db.userMeals.find({"user_id": user_id})
        if user_meals.count() > 0:
            last_plan_check = user_db.userMeals.find({"user_id":user_id, "last_meal":{"$exists":True}})
            if last_plan_check.count() > 0:
                last_plan = userMeals[0]['last_meal'];
            else:
                dispatcher.utter_message(text = 'You have not asked for a meal plan yet, so I am not sure what your last meal was, if you want to create one then try typing something like:\n\
                \'I bought the ingredients. Give me a lunch plan.\'\n And I will give a meal plan for you as per your diet type and requested meal. Then I\'ll be able to calculate your nutritonal intake.')
                return []
        else:
            dispatcher.utter_message(text = 'You do not have a meal/diet plan yet, if you want to create one then try typing something like:\n\
                I\'m thiking of going on a diet.\n And I will create one for you as per your diet type.')
            return []
        day = ((datetime.datetime.today() - user_meals[0]['day_created']).days + 1)    ## Getting the meal day from current day minus day meal plan was created.
        # mealDetail = meal_df.query('Day == @day and meal_type == @dietType')
        for meal in user_meals:
                if (meals['day'] == day and meals['meal_type'] == last_plan):
                    print('Meal given to user: ', meal)
                    break
        dispatcher.utter_message(text = "Great! Your nutrition intake for this meal is:\n")
        lunch_nutrients = meal['nutrients'] + '–' + str(meal['calories']) + 'kcal'   ## Lunch Nutrients and Calories from the mealplan dataframe
        dispatcher.utter_message(text = lunch_nutrients)

class ActionNutritionYesterday(Action): ## Under Process.
    def name(self) -> Text:
        return "action_nutrition_yesterday"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(str((tracker.current_state())["sender_id"]))
        user_id = str((tracker.current_state())["sender_id"])

        user_db = get_mongo_database()

        ## Need the last meal taken here along with the day.
        user_meals = user_db.userMeals.find({"user_id": user_id})
        if user_meals.count() > 0:
            print('list of user meals\n')
            for meal in user_meals:
                print(meal)
                print('\n')
        else:
            dispatcher.utter_message(text = 'You do not have a meal/diet plan yet, if you want to create one then try typing something like:\n\
                I\'m thiking of going on a diet.\n And I will create one for you as per your diet type.')
            return []
        day = ((datetime.datetime.today() - user_meals[0]['day_created']).days) ## Getting the previous day here.
        if day == 0:
            dispatcher.utter_message(text = 'Your diet plan started today, I am sorry I unable to give you your nutrition intake about yesterday.\n\
                You can come tomorrow after eating the meals according to your plan today and then I\'ll be able to tell you your nutrition intake for today.')
            return []
        net_carbs = 0
        proteins = 0
        fats = 0
        fiber = 0
        total_carbs = 0
        calories = 0
        plans = ['breakfast', 'dinner', 'lunch', 'snacks']
        for plan in plans:
            dietType = plan.capitalize()
            # mealDetail = meal_df.query('Day == @day and meal_type == @dietType')
            
            for meal in user_meals:
                if (meals['day'] == day and meals['meal_type'] == dietType):
                    print('Meal given to user: ', meal)
                    net_carbs = net_carbs + int(meal['nutrients'].split('\'')[3].strip().split('g')[0])
                    proteins = proteins + int(meal['nutrients'].split('\'')[9].strip().split('g')[0])
                    fats = fats + int(meal['nutrients'].split('\'')[15].strip().split('g')[0])
                    fiber = fiber + int(meal['nutrients'].split('\'')[21].strip().split('g')[0])
                    total_carbs = total_carbs + int(meal['nutrients'].split('\'')[25].strip().split('g')[0])
                    calories = calories + int(meal['calories'])
                    break
        net_carbs_percentage = int(float(net_carbs/(net_carbs + proteins + fats)) * 100.0)
        proteins_percentage = int(float(proteins/(net_carbs + proteins + fats)) * 100.0)
        fats_percentage = int(float(fats/(net_carbs + proteins + fats)) * 100.0)
        dispatcher.utter_message(text = "Your nutrition intake for yesterday is:\n")
        message = '{\'Net-carbs\': (\' ' + str(net_carbs) + 'g \', \'' + str(net_carbs_percentage) + '%\'), \'Protien\': (\' ' + \
        str(proteins) + 'g \', \'' + str(proteins_percentage) + '%\'), \'Fat\': (\' ' + str(fats) + 'g \', \'' + str(fats_percentage) + '%\'), \'Fiber\': \''+ str(fiber) + 'g\', \'Total-Carb\': \'' + \
        str(total_carbs) + 'g\'} – ' + str(calories) + 'kcal'
        dispatcher.utter_message(text = message)

class ActionMealNutritionYesterday(Action): ## Under Process.
    def name(self) -> Text:
        return "action_meal_nutrition_yesterday"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(str((tracker.current_state())["sender_id"]))
        user_id = str((tracker.current_state())["sender_id"])

        user_db = get_mongo_database()

        ## Need the last meal taken here along with the day.
        user_meals = user_db.userMeals.find({"user_id": user_id})
        plan = next(tracker.get_latest_entity_values(entity_type="plan"),None)

        plans = ['breakfast', 'dinner', 'lunch', 'snacks']
        if plan not in plans:
            dispatcher.utter_message(text = "I’m sorry I didn’t understand, I’m still learning please try asking about your meal type differently.")
            return []

        dietType = plan.capitalize()
        if user_meals.count() > 0:
            print('list of user meals\n')
            for meal in user_meals:
                print(meal)
                print('\n')
        else:
            dispatcher.utter_message(text = 'You do not have a meal/diet plan yet, if you want to create one then try typing something like:\n\
                I\'m thiking of going on a diet.\n And I will create one for you as per your diet type.')
            return []
        day = ((datetime.datetime.today() - user_meals[0]['day_created']).days) ## Getting the previous day here.
        if day == 0:
            dispatcher.utter_message(text = 'Your diet plan started today, I am sorry I unable to give you your nutrition intake about yesterday.\n\
                You can come tomorrow after eating the meals according to your plan today and then I\'ll be able to tell you your nutrition intake for today.')
            return []
        for meal in user_meals:
                if (meals['day'] == day and meals['meal_type'] == dietType):
                    print('Meal given to user: ', meal)
                    break
        dispatcher.utter_message(text = f"Your nutrition intake for yesterday {dietType} meal was:\n")
        lunch_nutrients = meal['nutrients'] + '–' + str(meal['calories']) + 'kcal'   ## Lunch Nutrients and Calories from the mealplan dataframe
        dispatcher.utter_message(text = lunch_nutrients)

class ActionNutritionWeek(Action): ## Under Process.
    def name(self) -> Text:
        return "action_nutrition_week"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(str((tracker.current_state())["sender_id"]))
        user_id = str((tracker.current_state())["sender_id"])

        user_db = get_mongo_database()

        ## Need the last meal taken here along with the day.
        user_meals = user_db.userMeals.find({"user_id": user_id})
        if user_meals.count() > 0:
            print('list of user meals\n')
            for meal in user_meals:
                print(meal)
                print('\n')
        else:
            dispatcher.utter_message(text = 'You do not have a meal/diet plan yet, if you want to create one then try typing something like:\n\
                I\'m thiking of going on a diet.\n And I will create one for you as per your diet type.')
            return []
        current_day = ((datetime.datetime.today() - user_meals[0]['day_created']).days + 1) ## Getting the previous day here.
        if current_day <=7:
            dispatcher.utter_message(text = 'Your diet plan is not yet completed, I am sorry I unable to give you your nutrition intake for the whole week/diet plan.\n\
                You can come after eating the meals according to your plan and completing the whole week plan and then I\'ll be able to tell you your nutritional intake for the whole week/diet plan.')
            return []
        net_carbs = 0
        proteins = 0
        fats = 0
        fiber = 0
        total_carbs = 0
        calories = 0
        plans = ['breakfast', 'dinner', 'lunch', 'snacks']
        for day in range(1, 8):
            for plan in plans:
                dietType = plan.capitalize()
                # mealDetail = meal_df.query('Day == @day and meal_type == @dietType')
            
                for meal in user_meals:
                    if (meals['day'] == day and meals['meal_type'] == dietType):
                        print('Meal given to user: ', meal)
                        net_carbs = net_carbs + int(meal['nutrients'].split('\'')[3].strip().split('g')[0])
                        proteins = proteins + int(meal['nutrients'].split('\'')[9].strip().split('g')[0])
                        fats = fats + int(meal['nutrients'].split('\'')[15].strip().split('g')[0])
                        fiber = fiber + int(meal['nutrients'].split('\'')[21].strip().split('g')[0])
                        total_carbs = total_carbs + int(meal['nutrients'].split('\'')[25].strip().split('g')[0])
                        calories = calories + int(meal['calories'])
                        break
        net_carbs_percentage = int(float(net_carbs/(net_carbs + proteins + fats)) * 100.0)
        proteins_percentage = int(float(proteins/(net_carbs + proteins + fats)) * 100.0)
        fats_percentage = int(float(fats/(net_carbs + proteins + fats)) * 100.0)
        dispatcher.utter_message(text = "Your nutrition intake for yesterday is:\n")
        message = '{\'Net-carbs\': (\' ' + str(net_carbs) + 'g \', \'' + str(net_carbs_percentage) + '%\'), \'Protien\': (\' ' + \
        str(proteins) + 'g \', \'' + str(proteins_percentage) + '%\'), \'Fat\': (\' ' + str(fats) + 'g \', \'' + str(fats_percentage) + '%\'), \'Fiber\': \''+ str(fiber) + 'g\', \'Total-Carb\': \'' + \
        str(total_carbs) + 'g\'} – ' + str(calories) + 'kcal'
        dispatcher.utter_message(text = message)

# class ActionAddCalories(Action):
#     def name(self) -> Text:
#         return "action_add_calories"
#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         print(str((tracker.current_state())["sender_id"]))
#         user_id = str((tracker.current_state())["sender_id"])

#         user_db = get_mongo_database()

#         plan = next(tracker.get_latest_entity_values(entity_type="plan"),None)
#         if plan in ['breakfast', 'lunch', 'snacks', 'dinner']:
#             calories = next(tracker.get_latest_entity_values(entity_type="NUMBER", entity_role="calories"),None)
#             if calories:
#                 calories = int(calories)
#                 print(calories)
#                 print(plan.capitalize())
#                 meal_type = plan.capitalize()
#                 day_created = datetime.datetime.today()
#                 user_db.userMeals.insert_one({"user_id":user_id, 'day_created': day_created, 'type': 'CALORIES', 'meal_type': meal_type, 'calories':int(calories)})
#                 user_meals_calories = userdb.healthRecords.find_one({"user_id":user_id, 'type':'CALORIES_IN'})
#                 if user_meals_calories:
#                     calories = calories + user_meals_calories['payload']['calories']
#                     user_db.healthRecords.update_one({"user_id": user_id, 'type': 'CALORIES_IN'}, {'$set': {'payload.calories': int(calories), 'updated_at': parser.parse(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'))}})
#                 user_db.healthRecords.insert_one({"userId":user_id, 'type': 'CALORIES', 'payload': {'calories' : int(calories)}, 'timestamp': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'), 'createdAt': parser.parse(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds')), '_class' : 'com.intellithing.common.entity.HealthRecord'})





class ActionWaterIntake(Action):
    def name(self) -> Text:
        return "action_water_intake"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_db = get_mongo_database()
        print(str((tracker.current_state())["sender_id"]))
        user_id = str((tracker.current_state())["sender_id"])
        print(next(tracker.get_latest_entity_values(entity_type="NUMBER", entity_role="glasses"), None))
        measurement = {'metric': "METRIC",'imperial': "IMPERIAL"}
        water_intake = next(tracker.get_latest_entity_values(entity_type="NUMBER", entity_role="glasses"), None)
        if water_intake:
            user_db.healthRecords.insert_one({"userId":user_id, 'type': 'DRINK', 'payload': {'glasses' : float(water_intake), 'measureType': measurement.get((str(tracker.get_slot('measuringUnit'))), None)}, 'timestamp': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds'),
                'createdAt': parser.parse(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(timespec='milliseconds')), '_class' : 'com.intellithing.common.entity.HealthRecord'})
            dispatcher.utter_message(text = "Water glasses count updated.")
            return []
        else:
            dispatcher.utter_message(text = "I’m sorry I didn’t understand, I’m still learning please try telling me your water intake level in number of glasses drank.")
            return []

class action_list_questions(Action):
    def name(self) -> Text:
        return "action_list_questions"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        filename = "UpdatedDatasetFitBit.csv"
        fitbit_df = pd.read_csv(filename);
        user_ids = fitbit_df.iloc[:, 1]

        print(str((tracker.current_state())["sender_id"]))
        user_id = str((tracker.current_state())["sender_id"])


        if user_id not in user_ids.values:
            dispatcher.utter_message(text = "Currently there is no historical data available about you at the moment. \n\
                Keep updating your data on daily basis to get answers to questions like:\n\
                Ask me to predict your weight.\n\
                If you are not achieving your goal ask me questions such as:\n\
                Why am I not losing weight?\n\
                Why am I not gaining weight?\n\
                I will then be able to troubleshoot it for you.")
        else:
            dispatcher.utter_message(text = "You can ask me questions about the quality of your body functions for example:\n\
                Ask me to predict your weight.\n\
                If you are not achieving your goal ask me questions such as:\n\
                Why am I not losing weight?\n\
                Why am I not gaining weight?\n\
                I will then troubleshoot it for you.")



# Fallback, what to respond when the bot does not understand what user is saying

class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"
    def run(self, dispatcher, tracker, domain):

        ## Telling the user that the last message intent was not clear.
 
        message = "I’m sorry I didn’t understand, I’m still learning please try rephrasing your sentence."
        dispatcher.utter_message(text=message)
        # undo last user interaction
        return [UserUtteranceReverted()]
