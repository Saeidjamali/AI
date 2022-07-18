from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import pymongo


# ALLOWED_PIZZA_SIZES = ["small", "medium", "large", "extra-large", "extra large", "s", "m", "l", "xl"]
# ALLOWED_PIZZA_TYPES = ["mozzarella", "fungi", "veggie", "pepperoni", "hawaii"]
#def weight_function():

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
        user_information = pymongo.MongoClient("mongodb+srv://root:Password!23@cluster0.7ua3r.mongodb.net/?retryWrites=true&w=majority")
        user_db = user_information['user_db']
        records = user_db["users_records"] 
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
        dispatcher.utter_message(text = f"your data is stored in the database.")
        mydict = { "name": tracker.get_slot('name'), "measuringUnit": tracker.get_slot('measuringUnit'), 
                   "age": tracker.get_slot('age'), "gender": tracker.get_slot('gender'), 
                   "weight": tracker.get_slot('weight'), "height": tracker.get_slot('height1'), 
                   "eating": tracker.get_slot('eating'), "stressLevel": tracker.get_slot('stressLevel'),
                   "likeFood": tracker.get_slot('likeFood'), "userGoal": tracker.get_slot('userGoal') }

        x = records.insert_one(mydict) ## Command for entrying the json document into the collection
        print(x)
        cursor = records.find()
        for record in cursor:
            print(record)
        return None