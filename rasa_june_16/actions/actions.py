from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, SlotSet, FollowupAction
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
from copy import deepcopy
from bson.objectid import ObjectId
pd.options.mode.chained_assignment = None
# get_ipython().run_line_magic('matplotlib', 'inline')

# ALLOWED_PIZZA_SIZES = ["small", "medium", "large", "extra-large", "extra large", "s", "m", "l", "xl"]
# ALLOWED_PIZZA_TYPES = ["mozzarella", "fungi", "veggie", "pepperoni", "hawaii"]
#def weight_function():

load_dotenv(find_dotenv())
MONGODB_URL = os.getenv('MONGODB_URL')


def get_mongo_database():
    client = pymongo.MongoClient(MONGODB_URL)
    return client.get_default_database()


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
            dispatcher.utter_message(text=f"I’m sorry I didn’t understand, I’m still learning please try entering your height differently.")
            return {"height1": None}
        # have height 1
        unit_temp = next(tracker.get_latest_entity_values('unit'), None)
        measuringUnit = tracker.get_slot('measuringUnit')
        print('unit_temp:', unit_temp)
        print('measuringUnit:', measuringUnit)

        if unit_temp not in ['cm', 'feet', None]:
            dispatcher.utter_message(text="Seems like you have entered incorrect unit. I’m still learning please try entering your height differently.")
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
                        text="Entered height seems incorrect to me, typically human height is between 1 to 9 feets.\n I’m still learning please try entering your height differently.")
                    return {"height1": None}
            elif measuringUnit == 'metric':
                if float(slot_value) >= 80 and float(slot_value) <= 250:
                    value = slot_value + " " + "cm"
                    dispatcher.utter_message(text=f"Your height is set to {value}")
                    print('value of height is', value)
                    return {"height1": value, "height2": 0}
                else:
                    dispatcher.utter_message(
                        text="Entered height seems incorrect to me, typically human height is between 80 to 250 cm.\n I’m still learning please try entering your height differently.")
                    return {"height1": None}

        if measuringUnit == 'metric' and unit_temp == 'cm':
            if float(slot_value) < 80:
                dispatcher.utter_message(
                    text="Entered value seems quite low to me, typically human height is between 80 to 250 cm.\n I’m still learning please try entering your height differently.")
                return {"height1": None}
            elif float(slot_value) > 250:
                dispatcher.utter_message(
                    text="Entered value seems quite high, typically human height is between 80 to 250 cm.\n I’m still learning please try entering your height differently.")
                return {"height1": None}
            else:
                slot_value = slot_value + " cm"

        elif measuringUnit == 'imperial' and unit_temp == 'feet':
            if float(slot_value) < 1:
                dispatcher.utter_message(
                    text="Entered value seems quite low, typically human height is between 1 to 9 feets.\n I’m still learning please try entering your height differently.")
                return {"height1": None}
            elif float(slot_value) > 9:
                dispatcher.utter_message(
                    text="Entered value seems quite high, typically human height is between 1 to 9 feets.\n I’m still learning please try entering your height differently.")
                return {"height1": None}
            else:
                slot_value = slot_value + " feets"
        else:
            dispatcher.utter_message(text="Seems like you have entered incorrect unit according to the entered measuring system.")
            return {"height1": None, "height2": None}

        # unit is cm or feet.
        if tracker.get_slot('height2') == None:
            # height in cm or user has entered e.g. "45 feets" only
            dispatcher.utter_message(text=f"OK! Your height is {slot_value}")
            return {"height1": slot_value, "height2": 0}
        # there is height2

        height2_temp = tracker.get_slot('height2')
        if float(height2_temp) > 12 or float(height2_temp) < 0:
            dispatcher.utter_message(text="You have entered incorrect amount of inches, kindly type between 1 and 12 inches.\n I’m still learning please try entering your height differently.")
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
            # dispatcher.utter_message(text=f"You have entered wrong height.")
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
            dispatcher.utter_message(text="You have entered wrong weight")
            return {"weight": None}

        unit_temp = next(tracker.get_latest_entity_values('unit'), None)
        measuringUnit = tracker.get_slot('measuringUnit')

        print('unit_temp:', unit_temp)
        if unit_temp not in ['kg', 'pound', None]:
            dispatcher.utter_message(text="Seems like you have entered incorrect unit.\n I’m still learning please try entering your height differently.")
            return {"weight": None}

        if unit_temp == None:
            if measuringUnit == 'imperial':
                if float(slot_value) > 20 and float(slot_value) < 640:
                    value = slot_value + " " + "pounds"
                    dispatcher.utter_message(text=f"Your weight is set to {value}")
                    return {"weight": value}
                else:
                    dispatcher.utter_message(
                        text=f"Entered weight seems incorrect to me, typically human weight is between 20 to 640 pounds.")
                    return {"weight": None}
            elif measuringUnit == 'metric':
                if float(slot_value) > 20 and float(slot_value) < 290:
                    value = slot_value + " " + "kgs"
                    dispatcher.utter_message(text=f"Your weight is set to {value}")
                    return {"weight": value}
                else:
                    dispatcher.utter_message(
                        text=f"Entered weight seems incorrect to me, typically human weight is between 20 to 290 kgs.")
                    return {"weight": None}

        if measuringUnit == 'imperial' and unit_temp == 'pound':
            if float(slot_value) < 20:
                dispatcher.utter_message(
                    text="Entered value seems quite low, typically human weight is between 20 to 640 pounds.")
                return {"weight": None}
            elif float(slot_value) > 640:
                dispatcher.utter_message(
                    text="Entered value seems quite high, typically human weight is between 20 to 640 pounds.")
                return {"weight": None}
            else:
                slot_value = slot_value + " pounds"
        elif measuringUnit == 'metric' and unit_temp == 'kg':
            if float(slot_value) < 20:
                dispatcher.utter_message(
                    text="Entered value seems quite low, typically human weight is between 20 to 290 kgs.")
                return {"weight": None}
            elif float(slot_value) > 290:
                dispatcher.utter_message(
                    text="Entered value seems quite high, typically human weight is between 20 to 290 kgs.")
                return {"weight": None}
            else:
                slot_value = slot_value + " kgs"
        else:
            dispatcher.utter_message(text="Seems like you have entered incorrect unit for the entered measuring system.")
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
            dispatcher.utter_message(text=f"Seems like you have entered incorrect age, Please type between 1 and 150 years old")
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
            dispatcher.utter_message(text=f"Seems like you have entered incorrect gender. I’m still learning please try saying it differently.")
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
            dispatcher.utter_message(text="Seems like you have entered incorrect stress Level. I’m still learning please try saying it differently.")
            return {"stressLevel": None}
        elif slot_value not in ['1','2','3','4','5']:
            dispatcher.utter_message(text="Seems like you have entered incorrect stress Level.")
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
            dispatcher.utter_message(text="Seems like you have entered incorrect Level. I’m still learning please try saying it differently.")
            return {"likeFood": None}
        elif slot_value not in ['1','2','3','4','5']:
            dispatcher.utter_message(text="Seems like you have entered incorrect level.")
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
            dispatcher.utter_message(text=f"Seems like you have entered incorrect goal. I’m still learning please try saying it differently.")
            return {"userGoal": None}

        elif Number in ['1', '2', '3', '4']:
            dispatcher.utter_message(text=f"OK! {goal[Number]}.")
            return {"userGoal": goal[Number]}

        elif slot_value in ['lose', 'maintain', 'gain', 'gther']:
            dispatcher.utter_message(text=f"OK! You are a {goal[slot_value]}.")
            return {"userGoal": goal[slot_value]}
        #else:
        dispatcher.utter_message(text=f"Seems like you have entered incorrect goal.")
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
        message_displayed = {'1': 'Its great to hear that you follows a vegan diet and lifestyle',
                             '2': 'Its great to hear that you follows a vegetarian diet and lifestyle',
                             '3': 'Great! so you are an omnivore',
                             'vegan': 'Its great to hear that you follows a vegan diet and lifestyle',
                             'vegetarian': 'Its great to hear that you follows a vegetarian diet and lifestyle',
                             'non-vegetarian': 'Great! so you are an omnivore',
                             }
        if not (slot_value or Number):
            dispatcher.utter_message(text=f"Seems like you have entered incorrect eating category. I’m still learning please try saying it differently.")
            return {"eating": None}
        elif slot_value in ['vegan', 'vegetarian', 'non-vegetarian']:
            dispatcher.utter_message(text=f"{message_displayed.get(slot_value, None)}")
            return {"eating": eating.get(slot_value, None)}
        elif Number in ['1', '2', '3']:
            dispatcher.utter_message(text=f"{message_displayed.get(Number, None)}")
            return {"eating": eating.get(Number, None)}

        dispatcher.utter_message(text=f"Seems like you have entered incorrect eating category.")
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

        MEASURE = {'1': 'Imperial', '2': 'Metric', '3': 'Default'}

        slot_value = next(tracker.get_latest_entity_values('measurement'), None)
        print(slot_value)

        if not (slot_value or Number):
            dispatcher.utter_message(text="Seems like you have entered incorrect measuring unit. I’m still learning please try saying it differently.")
            return {"measuringUnit": None}

        elif slot_value in ['imperial','metric','default']:
            dispatcher.utter_message(text=f"Noted! You have chosen {slot_value} as your measuring unit.")
            return {"measuringUnit": slot_value}

        elif Number in ['1','2','3']:
            dispatcher.utter_message(text=f"Noted! You have chosen {MEASURE[Number]} as your measuring unit.")
            return {"measuringUnit": MEASURE[Number]}

        dispatcher.utter_message(text=f"Seems like you have entered incorrect measuring unit. I’m still learning please try saying it differently.")
        return {"measuringUnit": None}

    def validate_healthcondition(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if not slot_value:
            dispatcher.utter_message(text=f"Seems like you have entered incorrect medical condidion. I’m still learning please try saying it differently.")
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
            dispatcher.utter_message(text=f"you have not entered correct response.")
            return {"diseases": 'No diseases'}
        dispatcher.utter_message(text="OK!.")
        return {"diseases": slot_value}

class action_change_weight(Action):
    def name(self) -> Text:
        return "action_change_weight"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        value = next(tracker.get_latest_entity_values(entity_type="NUMBER", entity_role="weight2"), None)
        print(value)
        if not value:
            dispatcher.utter_message(text="You have entered wrong weight")
            return[SlotSet("weight", None)]
        if((tracker.get_slot('measuringUnit') == 'imperial')):
            if float(value) < 20:
                dispatcher.utter_message(
                    text="Entered weight seems incorrect to me, typically human weight is between 20 to 640 pounds.")
                return[SlotSet("weight", None)]
            elif float(value) > 640:
                dispatcher.utter_message(
                    text="Entered weight seems incorrect to me, typically human weight is between 20 to 640 pounds.")
                return[SlotSet("weight", None)]
            else:
                value = value + " pounds"
        elif((tracker.get_slot('measuringUnit') == 'metric')):
            if float(value) < 20:
                dispatcher.utter_message(
                    text="Entered weight seems incorrect to me, typically human weight is between 20 to 290 kgs")
                return[SlotSet("weight", None)]
            elif float(value) > 290:
                dispatcher.utter_message(
                    text="Entered weight seems incorrect to me, typically human weight is between 20 to 290 kgs")
                return [SlotSet("weight", None)]
            else:
                value = value + " kgs"
        if value:
            dispatcher.utter_message(text=f"your weight is changed to {value}")
            return[SlotSet('weight', value)]

class action_change_stressLevel(Action):
    def name(self) -> Text:
        return "action_change_stressLevel"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        value = next(tracker.get_latest_entity_values(entity_type="NUMBER", entity_role="stressLevel2"), None)
        print(value)
        stressLevel = {'1':'very low', '2':'low', '3':'average', '4':'high', '5':'very high'}
        if not value:
            dispatcher.utter_message(text="Seems like you have entered incorrect stress Level. I’m still learning please try saying it differently.")
            return[SlotSet("stressLevel", None)]
        elif value not in ['1','2','3','4','5']:
            dispatcher.utter_message(text="Seems like you have entered incorrect stress Level.")
            return[SlotSet("stressLevel", None)]
        dispatcher.utter_message(text=f"OK! Seems like your stress Level is {value}({stressLevel.get(value,None)}).")
        return[SlotSet("stressLevel", stressLevel.get(value,None))]

class action_change_age(Action):
    def name(self) -> Text:
        return "action_change_age"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slot_value = next(tracker.get_latest_entity_values(entity_type="NUMBER", entity_role="age2"), None)
        print(slot_value)

        if not slot_value:
            dispatcher.utter_message(text="I’m sorry I didn’t understand, I’m still learning please try saying it differently.")
            return[SlotSet("age", None)]

        elif float(slot_value) < 1 or float(slot_value) > 150:
            dispatcher.utter_message(text=f"Seems like you have entered incorrect age, Please type between 1 and 150 years old.")
            return[SlotSet("age", None)]

        dispatcher.utter_message(text=f"hmm ok! so you are {slot_value} years old.")
        return[SlotSet("age", slot_value)]


class action_change_measuringUnit(Action):
    def name(self) -> Text:
        return "action_change_measuringUnit"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slot_value = next(tracker.get_latest_entity_values(entity_type="measurement", entity_role="measurement2"), None)
        # if slot measurment is not set, and the user is in change so set the measurmnt unit.
        print(slot_value)

        if not slot_value:
            dispatcher.utter_message(text="Seems like you have entered incorrect measuring unit. I’m still learning please try saying your name differently.")
            return [SlotSet("measuringUnit", slot_value)]

        elif slot_value in ['imperial', 'metric']:
            dispatcher.utter_message(text=f"Noted! You have changed your measuring unit to {slot_value}.")
            return [SlotSet("measuringUnit", slot_value)]

        # old_measuring_unit = tracker.get_slot('measuringUnit')

        # if not slot_value:
        #     dispatcher.utter_message(text="You have entered wrong measuring unit.")
        #     return [SlotSet("measuringUnit", slot_value)]
        # elif slot_value in ['imperial', 'metric']:
        #     if slot_value == old_measuring_unit:
        #         dispatcher.utter_message(text=f"Noted! You have changed your measuring unit to {slot_value}.")
        #         return [SlotSet("measuringUnit", slot_value)]
        #     elif slot_value == 'imperial':
        #         height1 = tracker.get_slot('height1')
        #         weight = tracker.get_slot('height')
        #         if height1:
        #             inch = int(0.3937 * height);
        #             feet = int(0.0328 * height);
        #             height_temp = feet + "feets " + inch + " inches"
        #             dispatcher.utter_message(text=f"OK! Your height is {height_temp}.")
        #     elif slot_value == 'metric':

        dispatcher.utter_message(text="Seems like you have entered incorrect measuring unit. I’m still learning please try saying it differently.")
        return [SlotSet("measuringUnit", None)]

class action_change_eating(Action):
    def name(self) -> Text:
        return "action_change_eating"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
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

        if (not slot_value) or (slot_value not in ['vegan', 'vegetarian', 'non-vegetarian']):
            dispatcher.utter_message(text="Seems like you have entered incorrect eating category. I’m still learning please try saying it differently.")
            return [SlotSet("eating", None)]

        dispatcher.utter_message(text=f"{eating.get(slot_value,None)}")
        return [SlotSet("eating", eating.get(slot_value,None))]
        

class action_change_foodieLevel(Action):
    def name(self) -> Text:
        return "action_change_foodieLevel"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
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
            dispatcher.utter_message(text="Seems like you have entered incorrect stress Level. I’m still learning please try saying it differently.")
            return [SlotSet("likeFood", None)]
        #else

        dispatcher.utter_message(text=f"Your foodlevel is set to {slot_value}, {message_displayed.get(slot_value,None)}")

        return [SlotSet("likeFood", likeFood.get(slot_value,None))]

class action_change_height(Action):
    def name(self) -> Text:
        return "action_change_height"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        height = next(tracker.get_latest_entity_values(entity_type="NUMBER", entity_role="height2"), None)
        inches = next(tracker.get_latest_entity_values(entity_type="NUMBER", entity_role="inches2"), None)
        value = height
        print(value)
        print('inches:',inches)

        if not value:
            dispatcher.utter_message(text="I’m sorry I didn’t understand, I’m still learning please try entering your height differently.")
            return[SlotSet("height1", None)]
        print(tracker.get_slot('measuringUnit'))
        if(tracker.get_slot('measuringUnit') == 'imperial'):
            if inches:
                if (float(value) > 9 or float(value) < 1):
                    dispatcher.utter_message(text="Entered height seems incorrect to me, typically human height is between 1 to 9 feets in imperial measurement system.\n I’m still learning please try entering your height differently.")
                    return[SlotSet("height1", None), SlotSet("height2", None)]
                elif (float(inches) > 12 or float(inches) < 0):
                    dispatcher.utter_message(text="Seems like you have entered wrong amount of inches. Inches are between 0 to 12 in height")
                    return[SlotSet("height1", None), SlotSet("height2", None)]
                else:
                    value=value +" feet "+ inches+" inches"
                    dispatcher.utter_message(text=f"Your height is changed to {value}")
                    return [SlotSet("height1", value)]
            #else
            if float(value) < 1:
                dispatcher.utter_message(
                    text="Entered value seems quite low, typically human height is between 1 to 9 feets in imperial measurement system.")
                return[SlotSet("height1", None)]
            elif float(value) > 9:
                dispatcher.utter_message(
                    text="Entered value seems quite high, typically human height is between 1 to 9 feets in imperial measurement system.")
                return[SlotSet("height1", None)]
            else:
                value= value +" feet "
                dispatcher.utter_message(text=f"Your height is changed to {value}")
                return [SlotSet("height1", value), SlotSet("height2", 0)]
        else:
            if float(value) < 80:
                dispatcher.utter_message(
                    text="Entered value seems quite low, typically human height is between 80 to 250 cm in metric measurement system.")
                return[SlotSet("height1", None), SlotSet("height2", None)]
            elif float(value) > 250:
                dispatcher.utter_message(
                    text="Entered value seems quite high, typically human height is between 80 to 250 cm in metric measurement system.")
                return [SlotSet("height1", None), SlotSet("height2", None)]
            else:
                value = value + " cm"
                dispatcher.utter_message(text=f"Your height is changed to {value} ")
                return [SlotSet("height1", value), SlotSet("height2", 0)]

class action_store_db(Action): ## custom action function for storing user information in the database.
    def name(self) -> Text:
        return "action_store_db"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_id = str((tracker.current_state())["sender_id"])
        user_db = get_mongo_database()
        user_record = user_db.users.find_one({"_id": ObjectId(user_id)})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'profileComplete': 'true'}})

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
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.measureType': measurement.get((str(tracker.get_slot('measuringUnit'))), None)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.age': int(tracker.get_slot('age'))}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.gender': gender.get((str(tracker.get_slot('gender'))), None)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.weight': float(weight)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.height': float(height)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.eating': eating.get((str(tracker.get_slot('eating'))), None)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.stressLevel': stressLevel.get((str(tracker.get_slot('stressLevel'))), None)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.likeFood': likeFood.get((str(tracker.get_slot('likeFood'))), None)}})
        user_db.users.update_one({"_id": ObjectId(user_id)}, {'$set': {'userInfo.goal': goal.get((str(tracker.get_slot('userGoal'))), None)}})
        user_db.healthRecords.insert_one({"userId":user_id, 'type': 'WEIGHT', 'payload': {'weight' : float(weight), 'measureType': measurement.get((str(tracker.get_slot('measuringUnit'))), None)}})
        user_db.healthRecords.insert_one({"userId":user_id, 'type': 'HEIGHT', 'payload': {'height' : float(height), 'measureType': measurement.get((str(tracker.get_slot('measuringUnit'))), None)}})
        user_db.healthRecords.insert_one({"userId":user_id, 'type': 'STRESS_LEVEL', 'payload': {'stressLevel': stressLevel.get((str(tracker.get_slot('stressLevel'))), None), 'measureType': measurement.get((str(tracker.get_slot('measuringUnit'))), None)}})
        dispatcher.utter_message(text = f"your data is stored in the database.")
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
                            response = "As per your history, you have walked less in "+str(len(peaks_valleys['valleys_steps']))+" days, your calories out are less in "+str(len(peaks_valleys['valleys_cal']))+" days, you have taken more calories in "+str(len(peaks_valleys['peaks_calin']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight lossing performance."
                        else:
                            response = "As per your history, you have walked less in "+str(len(peaks_valleys['valleys_steps']))+" days, your calories out are less in "+str(len(peaks_valleys['valleys_cal']))+" days, you have taken more calories in "+str(len(peaks_valleys['peaks_calin']))+" days that are affecting your weight lossing performance."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you have walked less in "+str(len(peaks_valleys['valleys_steps']))+" days, your calories out are less in "+str(len(peaks_valleys['valleys_cal']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight lossing performance."
                        else:
                            response = "As per your history, you have walked less in "+str(len(peaks_valleys['valleys_steps']))+" days, your calories out are less in "+str(len(peaks_valleys['valleys_cal']))+" days that are affecting your weight lossing performance."
                else:
                    if len(peaks_valleys['peaks_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you have walked less in "+str(len(peaks_valleys['valleys_steps']))+" days, you have taken more calories in "+str(len(peaks_valleys['peaks_calin']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight lossing performance."
                        else:
                            response = "As per your history, you have walked less in "+str(len(peaks_valleys['valleys_steps']))+" days, you have taken more calories in "+str(len(peaks_valleys['peaks_calin']))+" days that are affecting your weight lossing performance."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you have walked less in "+str(len(peaks_valleys['valleys_steps']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight lossing performance."
                        else:
                            response = "As per your history, you have walked less in "+str(len(peaks_valleys['valleys_steps']))+" days that is affecting your weight lossing performance."
            else:
                if len(peaks_valleys['valleys_cal'])>3:
                    if len(peaks_valleys['peaks_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, your calories out are less in "+str(len(peaks_valleys['valleys_cal']))+" days, you have taken more calories in "+str(len(peaks_valleys['peaks_calin']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight lossing performance."
                        else:
                            response = "As per your history, your calories out are less in "+str(len(peaks_valleys['valleys_cal']))+" days, you have taken more calories in "+str(len(peaks_valleys['peaks_calin']))+" days that are affecting your weight lossing performance."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, your calories out are less in "+str(len(peaks_valleys['valleys_cal']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight lossing performance."
                        else:
                            response = "As per your history, your calories out are less in "+str(len(peaks_valleys['valleys_cal']))+" days that are affecting your weight lossing performance."
                else:
                    if len(peaks_valleys['peaks_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you have taken more calories in "+str(len(peaks_valleys['peaks_calin']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight lossing performance."
                        else:
                            response = "As per your history, you have taken more calories in "+str(len(peaks_valleys['peaks_calin']))+" days that are affecting your weight lossing performance."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight lossing performance."
                        else:
                            response = "As per your history, your activities seems normal. Contact cosultant for detailed diagnosis."
            return response
        elif self.id == 2:
            if len(peaks_valleys['peaks_steps'])>3:
                if len(peaks_valleys['peaks_cal'])>3:
                    if len(peaks_valleys['valleys_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you have walked more in "+str(len(peaks_valleys['peaks_steps']))+" days, your calories out are more in "+str(len(peaks_valleys['peak_cal']))+" days, you have taken less calories in "+str(len(peaks_valleys['valleys_calin']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight gaining performance."
                        else:
                            response = "As per your history, you have walked more in "+str(len(peaks_valleys['peaks_steps']))+" days, your calories out are more in "+str(len(peaks_valleys['peak_cal']))+" days, you have taken less calories in "+str(len(peaks_valleys['valleys_calin']))+" days that are affecting your weight gaining performance."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you have walked more in "+str(len(peaks_valleys['peaks_steps']))+" days, your calories out are more in "+str(len(peaks_valleys['peak_cal']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight gaining performance."
                        else:
                            response = "As per your history, you have walked more in "+str(len(peaks_valleys['peaks_steps']))+" days, your calories out are more in "+str(len(peaks_valleys['peak_cal']))+" days that are affecting your weight gaining performance."
                else:
                    if len(peaks_valleys['valleys_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you have walked more in "+str(len(peaks_valleys['peaks_steps']))+" days, you have taken less calories in "+str(len(peaks_valleys['valleys_calin']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight gaining performance."
                        else:
                            response = "As per your history, you have walked more in "+str(len(peaks_valleys['peaks_steps']))+" days, you have taken less calories in "+str(len(peaks_valleys['valleys_calin']))+" days that are affecting your weight gaining performance."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you have walked more in "+str(len(peaks_valleys['peask_steps']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight gaining performance."
                        else:
                            response = "As per your history, you have walked more in "+str(len(peaks_valleys['peak_ssteps']))+" days that is affecting your weight gaining performance."
            else:
                if len(peaks_valleys['peaks_cal'])>3:
                    if len(peaks_valleys['valleys_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, your calories out are more in "+str(len(peaks_valleys['peaks_cal']))+" days, you have taken less calories in "+str(len(peaks_valleys['valleys_calin']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight gaining performance."
                        else:
                            response = "As per your history, your calories out are more in "+str(len(peaks_valleys['peaks_cal']))+" days, you have taken less calories in "+str(len(peaks_valleys['valleys_calin']))+" days that are affecting your weight gaining performance."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, your calories out are more in "+str(len(peaks_valleys['peaks_cal']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight gaining performance."
                        else:
                            response = "As per your history, your calories out are more in "+str(len(peaks_valleys['peaks_cal']))+" days that are affecting your weight gaining performance."
                else:
                    if len(peaks_valleys['valleys_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you have taken less calories in "+str(len(peaks_valleys['valleys_calin']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight gaining performance."
                        else:
                            response = "As per your history, you have taken less calories in "+str(len(peaks_valleys['valleys_calin']))+" days that are affecting your weight gaining performance."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight gaining performance."
                        else:
                            response = "As per your history, your activities seems normal. Contact cosultant for detailed diagnosis."
            return response

        elif self.id == 3:
            if len(peaks_valleys['peaks_steps'])>2 or len(peaks_valleys['valleys_steps'])>2:
                if len(peaks_valleys['peaks_cal'])>2 or len(peaks_valleys['valleys_cal'])>2:
                    if len(peaks_valleys['valleys_calin'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you have inconsistent walking in "+str(len(peaks_valleys['peaks_steps'])+ len(peaks_valleys['valleys_steps']))+" days, your calories out are improper in "+str(len(peaks_valleys['peaks_cal'])+len(peaks_valleys['valleys_cal']))+" days, you have taken inconsistent calories in "+str(len(peaks_valleys['valleys_calin'])+len(peaks_valleys['peaks_calin']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight maintaining performance."
                        else:
                            response = "As per your history, you have inconsistent walking in "+str(len(peaks_valleys['peaks_steps'])+ len(peaks_valleys['valleys_steps']))+" days, your calories out are improper in "+str(len(peaks_valleys['peaks_cal'])+len(peaks_valleys['valleys_cal']))+" days, you have taken inconsistent calories in "+str(len(peaks_valleys['valleys_calin'])+len(peaks_valleys['peaks_calin']))+" days that are affecting your weight maintainig performance."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you have inconsistent walking in "+str(len(peaks_valleys['peaks_steps'])+ len(peaks_valleys['valleys_steps']))+" days, your calories out are improper in "+str(len(peaks_valleys['peaks_cal'])+len(peaks_valleys['valleys_cal']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight maintainig performance."
                        else:
                            response = "As per your history, you have inconsistent walking in "+str(len(peaks_valleys['peaks_steps'])+ len(peaks_valleys['valleys_steps']))+" days, your calories out are improper in "+str(len(peaks_valleys['peaks_cal'])+len(peaks_valleys['valleys_cal']))+" days that are affecting your weight maintainig performance."
                else:
                    if len(peaks_valleys['valleys_calin'])>3 or len(peaks_valleys['peaks_calin']):
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you have inconsistent walking in "+str(len(peaks_valleys['peaks_steps'])+ len(peaks_valleys['valleys_steps']))+" days, you have taken improper calories in "+str(len(peaks_valleys['valleys_calin'])+len(peaks_valleys['valleys_cal']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight maintainig performance."
                        else:
                            response = "As per your history, you have inconsistent walking in "+str(len(peaks_valleys['peaks_steps'])+ len(peaks_valleys['valleys_steps']))+" days, you have taken improper calories in "+str(len(peaks_valleys['valleys_calin'])+len(peaks_valleys['valleys_cal']))+" days that are affecting your weight maintainig performance."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you have inconsistent walking in "+str(len(peaks_valleys['peaks_steps'])+ len(peaks_valleys['valleys_steps']))+" days, and you have improper sleep pattern in "+str(len(peaks_valleys['peaks_sleep'])+len(peaks_valleys['valleys_sleep']))+" days that are affecting your weight maintainig performance."
                        else:
                            response = "As per your history, you have inconsistent walking in "+str(len(peaks_valleys['peaks_steps'])+ len(peaks_valleys['valleys_steps']))+" days that is affecting your weight maintainig performance."
            else:
                response = "As per your history, your activities seems normal. Contact cosultant for detailed diagnosis."

            return response

        elif self.id == 4:
            if len(peaks_valleys['peaks_steps'])>3:
                if len(peaks_valleys['peaks_cal'])>3:
                    if len(peaks_valleys['valleys_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you can gain weight by walking less then normal range, by consuming less calories and increasing calories intake, also by sleeping 7-9 hours."
                        else:
                            response = "As per your history, you can gain weight by walking less then normal range, by consuming less calories and increasing calories intake."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you can gain weight by walking less then normal range, by consuming less calories, also by sleeping 7-9 hours."
                        else:
                            response = "As per your history, you can gain weight by walking less then normal range, by consuming less calories."
                else:
                    if len(peaks_valleys['valleys_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you can gain weight by walking less then normal range, by increasing calories intake, also by sleeping 7-9 hours."
                        else:
                            response = "As per your history, you can gain weight by walking less then normal range, by increasing calories intake."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you can gain weight by walking less then normal range and  by sleeping 7-9 hours."
                        else:
                            response = "As per your history, you can gain weight by walking less then normal range."
            else:
                if len(peaks_valleys['peaks_cal'])>3:
                    if len(peaks_valleys['valleys_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you can gain weight by consuming less calories and increasing calories intake, also by sleeping 7-9 hours."
                        else:
                            response = "As per your history, you can gain weight by consuming less calories and increasing calories intake."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you can gain weight by consuming less calories, also by sleeping 7-9 hours."
                        else:
                            response = "As per your history, you can gain weight by consuming less calories."
                else:
                    if len(peaks_valleys['valleys_calin'])>3:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you can gain weight by increasing calories intake, also by sleeping 7-9 hours."
                        else:
                            response = "As per your history, you can gain weight by increasing calories intake."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you can gain weight by sleeping 7-9 hours."
                        else:
                            response = "As per your history, your activities are as per weight gaining criteria. Contact cosultant for detailed diagnosis."

            return response

        elif self.id == 5:
            if len(peaks_valleys['valleys_steps'])>3:
                if len(peaks_valleys['valleys_cal'])>3:
                    if len(peaks_valleys['peaks_calin'])>3:
                        if len(peaks_valleys['peaks_sleep'])>2 or len(peaks_valleys['valleys_sleep'])>2:
                            response = "As per your history, you can lose weight by walking more then normal range, by consuming more calories and decreasing calories intake, also by sleeping 7-9 hours."
                        else:
                            response = "As per your history, you can lose weight by walking more then normal range, by consuming more calories and decreasing calories intake."
                    else:
                        if len(peaks_valleys['peaks_sleep'])>2 or len(peaks_valleys['valleys_sleep'])>2:
                            response = "As per your history, you can lose weight by walking more then normal range, by consuming more calories, also by sleeping 7-9 hours."
                        else:
                            response = "As per your history, you can lose weight by walking more then normal range, by consuming more calories."
                else:
                    if len(peaks_valleys['peaks_calin'])>3:
                        if len(peaks_valleys['peaks_sleep'])>2 or len(peaks_valleys['valleys_sleep'])>2:
                            response = "As per your history, you can lose weight by walking more then normal range, by decreasing calories intake, also by sleeping 7-9 hours."
                        else:
                            response = "As per your history, you can lose weight by walking more then normal range, by decreasing calories intake."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you can lose weight by walking more then normal range and by sleeping 7-9 hours."
                        else:
                            response = "As per your history, you can lose weight by walking more then normal range."
            else:
                if len(peaks_valleys['valleys_cal'])>3:
                    if len(peaks_valleys['peaks_calin'])>3:
                        if len(peaks_valleys['peaks_sleep'])>2 or len(peaks_valleys['valleys_sleep'])>2:
                            response = "As per your history, you can lose weight by consuming more calories and decreasing calories intake, also by sleeping 7-9 hours."
                        else:
                            response = "As per your history, you can lose weight by consuming more calories and decreasing calories intake."
                    else:
                        if len(peaks_valleys['peaks_sleep'])>2 or len(peaks_valleys['valleys_sleep'])>2:
                            response = "As per your history, you can lose weight by consuming more calories, also by sleeping 7-9 hours."
                        else:
                            response = "As per your history, you can lose weight by consuming more calories."
                else:
                    if len(peaks_valleys['peaks_calin'])>3:
                        if len(peaks_valleys['peaks_sleep'])>2 or len(peaks_valleys['valleys_sleep'])>2:
                            response = "As per your history, you can lose weight by decreasing calories intake, also by sleeping 7-9 hours."
                        else:
                            response = "As per your history, you can lose weight by decreasing calories intake."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you can lose weight by sleeping 7-9 hours."
                        else:
                            response = "As per your history, your activities are as per weight losing criteria. Contact cosultant for detailed diagnosis."
            return response

        elif self.id == 6:
            if len(peaks_valleys['peaks_steps'])>2 or len(peaks_valleys['valleys_steps'])>2:
                if len(peaks_valleys['peaks_cal'])>2 or len(peaks_valleys['valleys_cal'])>2:
                    if len(peaks_valleys['valleys_calin'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you can maintain weight by walking in normal range, by consuming calories in normal range, by taking calories in normal range, and with proper sleep pattern."
                        else:
                            response = "As per your history, you can maintain weight by walking in normal range, by consuming calories in normal range, and by taking calories in normal range."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you can maintain weight by walking in normal range, by consuming calories in normal range, and with proper sleep pattern."
                        else:
                            response = "As per your history, you can maintain weight by walking in normal range, and by consuming calories in normal range."
                else:
                    if len(peaks_valleys['valleys_calin'])>3 or len(peaks_valleys['peaks_calin']):
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you can maintain weight by walking in normal range, by taking calories in normal range, and with proper sleep pattern."
                        else:
                            response = "As per your history, you can maintain weight by walking in normal range, and by taking calories in normal range."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>2 or len(peaks_valleys['peaks_sleep'])>2:
                            response = "As per your history, you can maintain weight by walking in normal range, and with proper sleep pattern."
                        else:
                            response = "As per your history, you can maintain weight by walking in normal range."
            else:
                response = "As per your history, your activities are as per weight maintaining criteria. Contact cosultant for detailed diagnosis."

            return response

        elif self.id == 7:
            if len(peaks_valleys['peaks_steps'])>4 or len(peaks_valleys['valleys_steps'])>4:
                if len(peaks_valleys['peaks_cal'])>4 or len(peaks_valleys['valleys_cal'])>4:
                    if len(peaks_valleys['valleys_calin'])>4 or len(peaks_valleys['peaks_sleep'])>4:
                        if len(peaks_valleys['valleys_sleep'])>4 or len(peaks_valleys['peaks_sleep'])>4:
                            response = "As per your history, inconsistent walking, improper calories consumption and intake, and poor sleep pattern are bad habits in your life."
                        else:
                            response = "As per your history, inconsistent walking, improper calories consumption and intake are bad habits in your life."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>4 or len(peaks_valleys['peaks_sleep'])>4:
                            response = "As per your history, inconsistent walking, improper calories consumption, and poor sleep pattern are bad habits in your life."
                        else:
                            response = "As per your history, inconsistent walking, and improper calories consumption are bad habits in your life."
                else:
                    if len(peaks_valleys['valleys_calin'])>4 or len(peaks_valleys['peaks_calin'])>4:
                        if len(peaks_valleys['valleys_sleep'])>4 or len(peaks_valleys['peaks_sleep'])>4:
                            response = "As per your history, inconsistent walking, improper calories intake, and poor sleep pattern are bad habits in your life."
                        else:
                            response = "As per your history, inconsistent walking, and improper calories intake bad habits in your life."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>4 or len(peaks_valleys['peaks_sleep'])>4:
                            response = "As per your history, inconsistent walking, and poor sleep pattern are bad habits in your life."
                        else:
                            response = "As per your history, inconsistent walking is the bad habits in your life."
            else:
                response = "As per your history, your activities are normal. Contact cosultant for detailed analysis."

            return response


        elif self.id == 8:
            return 'System is unable to answer this question at this moment.'

        elif self.id == 9 and goal==1:
            if len(peaks_valleys['valleys_steps'])>4:
                if len(peaks_valleys['valleys_cal'])>4:
                    if len(peaks_valleys['peaks_calin'])>4:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "As per your history, less walking, less calories consumption and more calories intake, also poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "As per your history, less walking, less calories consumption and more calories intake are keeping you away from your goal."
                    else:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "As per your history, less walking, less calories consumption, also poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "As per your history, less walking, less calories consumption are keeping you away from your goal."
                else:
                    if len(peaks_valleys['peaks_calin'])>4:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "As per your history, less walking, more calories intake, also poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "As per your history, less walking, more calories intake are keeping you away from your goal."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>3 or len(peaks_valleys['peaks_sleep'])>3:
                            response = "As per your history, less walking, and poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "As per your history, less walking is keeping you away from your goal."
            else:
                if len(peaks_valleys['valleys_cal'])>4:
                    if len(peaks_valleys['peaks_calin'])>4:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "As per your history, less calories consumption and more calories intake, also poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "As per your history, less calories consumption and more calories intake are keeping you away from your goal."
                    else:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "As per your history, less calories consumption, also poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "As per your history, less calories consumption are keeping you away from your goal."
                else:
                    if len(peaks_valleys['peaks_calin'])>4:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "As per your history, more calories intake, also poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "As per your history, more calories intake is keeping you away from your goal."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>3 or len(peaks_valleys['peaks_sleep'])>3:
                            response = "As per your history, poor sleep pattern is keeping you away from your goal."
                        else:
                            response = "As per your history, you are on track to achieve your goal. Contact cosultant for detailed diagnosis."

            return response

        elif self.id == 10 and goal==0:
            if len(peaks_valleys['peaks_steps'])>4:
                if len(peaks_valleys['peaks_cal'])>4:
                    if len(peaks_valleys['valleys_calin'])>4:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "As per your history, extra walking, increased calories consumption and less calories intake, also poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "As per your history, extra walking, increased calories consumption and less calories intake are keeping you away from your goal."
                    else:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "As per your history, extra walking, increased calories consumption, also poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "As per your history, extra walking, increased calories consumption are keeping you away from your goal."
                else:
                    if len(peaks_valleys['valleys_calin'])>4:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "As per your history, extra walking, less calories intake, also poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "As per your history, extra walking, less calories intake are keeping you away from your goal."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>3 or len(peaks_valleys['peaks_sleep'])>3:
                            response = "As per your history, extra walking, and poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "As per your history, extra walking is keeping you away from your goal."
            else:
                if len(peaks_valleys['peaks_cal'])>4:
                    if len(peaks_valleys['valleys_calin'])>4:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "As per your history, increased calories consumption and less calories intake, also poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "As per your history, increased calories consumption and less calories intake are keeping you away from your goal."
                    else:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "As per your history, increased calories consumption, also poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "As per your history, increased calories consumption are keeping you away from your goal."
                else:
                    if len(peaks_valleys['valleys_calin'])>4:
                        if len(peaks_valleys['peaks_sleep'])>3 or len(peaks_valleys['valleys_sleep'])>3:
                            response = "As per your history, less calories intake, also poor sleep pattern are keeping you away from your goal."
                        else:
                            response = "As per your history, less calories intake is keeping you away from your goal."
                    else:
                        if len(peaks_valleys['valleys_sleep'])>3 or len(peaks_valleys['peaks_sleep'])>3:
                            response = "As per your history, poor sleep pattern is keeping you away from your goal."
                        else:
                            response = "As per your history, you are on track to achieve your goal. Contact cosultant for detailed diagnosis."
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
      self.return_print='Your current weight is: '+str(self.current_weight)+ ', and your predicted weight after '+str(Horizon)+ ' days is: '+ str(self.predicted_weight)
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
        import pandas as pd
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
        user_id = 1503960366
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
