# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

# Creating Zomato APi key
# You'll need to go to this link: https://developers.zomato.com/api
# you can use your email id or just write upgrad site link
# log in with your email id/ create a account
# After logging in click on Generate API key

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import zomatopy
import json

# class ActionSearchRestaurants(Action):
# 	def name(self):
# 		return 'action_search_restaurants'
		
# 	def run(self, dispatcher, tracker, domain):
# 		config={ "user_key":"af99f4cef4727047ba527df7a2427b0d"}
# 		zomato = zomatopy.initialize_app(config)
# 		loc = tracker.get_slot('location')
# 		cuisine = tracker.get_slot('cuisine')
# 		location_detail=zomato.get_location(loc, 1)
# 		d1 = json.loads(location_detail)
# 		lat=d1["location_suggestions"][0]["latitude"]
# 		lon=d1["location_suggestions"][0]["longitude"]
# 		cuisines_dict={'bakery':5,'chinese':25,'cafe':30,'italian':55,'biryani':7,'north indian':50,'south indian':85}
# 		results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 5)
# 		d = json.loads(results)
# 		response=""
# 		if d['results_found'] == 0:
# 			response= "no results"
# 		else:
# 			for restaurant in d['restaurants']:
# 				response=response+ "Found "+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+"\n"
		
# 		dispatcher.utter_message("-----"+response)
# 		return [SlotSet('location',loc)]

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class ActionSearchRestaurants(Action):
    def name(self):
        return 'action_search_restaurants'
        
    def run(self, dispatcher, tracker, domain):        
        count = 0
        config={ "user_key":"af99f4cef4727047ba527df7a2427b0d"}
        zomato = zomatopy.initialize_app(config)
        loc = tracker.get_slot('location')
        cuisine = tracker.get_slot('cuisine')
        price = tracker.get_slot('price')
        location_detail=zomato.get_location(loc, 1)
        d1 = json.loads(location_detail)
        lat=d1["location_suggestions"][0]["latitude"]
        lon=d1["location_suggestions"][0]["longitude"]
        cuisines_dict={'chinese':25,'italian':55,'north indian':50,'south indian':85,'american':1,'mexican':73}
        price_dict = {'low':1,'medium':2,'high':3}
        results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 50000)
        d = json.loads(results)
        response="Showing you top rated restaurants:"+"\n"
        if d['results_found'] == 0:
            response= "No restaurant found for your criteria"
            dispatcher.utter_message(response)
        else:           
            for restaurant in sorted(d['restaurants'], key=lambda x: x['restaurant']['user_rating']['aggregate_rating'], reverse=True): 
                #Getting Top 10 restaurants for chatbot response
                if((price_dict.get(price) == 1) and (restaurant['restaurant']['average_cost_for_two'] < 300) and (count < 10)):
                    response=response+str(count+1)+". "+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+ " has been rated "+ restaurant['restaurant']['user_rating']['aggregate_rating']+""
                    response=response+". And the average price for two people here is: "+ str(restaurant['restaurant']['average_cost_for_two'])+"Rs\n"
                    count = count + 1
                elif((price_dict.get(price) == 2) and (restaurant['restaurant']['average_cost_for_two'] >= 300) and (restaurant['restaurant']['average_cost_for_two'] <= 700) and (count < 10)):
                    response=response+str(count+1)+". "+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+ " has been rated "+ restaurant['restaurant']['user_rating']['aggregate_rating']+""
                    response=response+". And the average price for two people here is: "+ str(restaurant['restaurant']['average_cost_for_two'])+"Rs\n"
                    count = count + 1                        
                elif((price_dict.get(price) == 3) and (restaurant['restaurant']['average_cost_for_two'] > 700) and (count < 10)):
                    response=response+str(count+1)+". "+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+ " has been rated "+ restaurant['restaurant']['user_rating']['aggregate_rating']+""
                    response=response+". And the average price for two people here is: "+ str(restaurant['restaurant']['average_cost_for_two'])+"Rs\n"
                    count = count + 1         
                if(count==5):
                    dispatcher.utter_message(response)
        if(count<5 and count>0):
            dispatcher.utter_message(response)
        if(count==0):
            response = "Sorry, No results found for your criteria. Would you like to search for some other restaurants?"
            dispatcher.utter_message(response)
        return [SlotSet('emailbody',response)]

        
class ActionSendEmail(Action):

    def name(self):
        return 'action_sendemail'

    def run(self, dispatcher, tracker, domain):
        from_user = 'billiondollar.plutocrat.8@gmail.com' # foodie.chatbot10@gmail.com
        to_user = tracker.get_slot('email')
        password = 'Dev811995'
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login(from_user, password)
        subject = 'Foodie Khana - Top Restaurants for you'
        msg = MIMEMultipart()
        msg['From'] = from_user
        msg['TO'] = to_user
        msg['Subject'] = subject
        body = tracker.get_slot('emailbody')
        body_header = '''Hi User, \n \n'''
        body_footer = '''\n\n Thanks & Regards \n Team: Foodie Khana \n For more information reply on same mail. Our Team will connect with you soon.'''
        body = body_header+body+body_footer
        msg.attach(MIMEText(body,'plain'))
        text = msg.as_string()
        server.sendmail(from_user,to_user,text)
        server.close()
        
class ActionCheckLocation(Action):

    def name(self):
        return 'action_chklocation'

    def run(self, dispatcher, tracker, domain):
        loc = tracker.get_slot('location')
        
        cities=['Agra', 'Ajmer', 'Aligarh', 'Amravati', 'Amritsar', 'Asansol', 'Aurangabad', 'Bareilly', 'Belgaum', 'Bhavnagar', 'Bhiwandi', 'Bhopal', 'Bhubaneswar', 'Bikaner', 'Bilaspur', 'BokaroSteelCity', 'Chandigarh', 'Coimbatore', 'Cuttack', 'Dehradun', 'Dhanbad', 'Bhilai', 'Durgapur', 'Dindigul', 'Erode', 'Faridabad', 'Firozabad', 'Ghaziabad', 'Gorakhpur', 'Gulbarga', 'Guntur', 'Gwalior', 'Gurgaon', 'Guwahati', 'Hamirpur', 'Hubli–Dharwad', 'Indore', 'Jabalpur', 'Jaipur', 'Jalandhar', 'Jammu', 'Jamnagar', 'Jamshedpur', 'Jhansi', 'Jodhpur', 'Kakinada', 'Kannur', 'Kanpur', 'Karnal', 'Kochi', 'Kolhapur', 'Kollam', 'Kozhikode', 'Kurnool', 'Ludhiana', 'Lucknow', 'Madurai', 'Malappuram', 'Mathura', 'Mangalore', 'Meerut', 'Moradabad', 'Mysore', 'Nagpur', 'Nanded', 'Nashik', 'Nellore', 'Noida', 'Patna', 'Pondicherry', 'Purulia', 'Prayagraj', 'Raipur', 'Rajkot', 'Rajahmundry', 'Ranchi', 'Rourkela', 'Salem', 'Sangli', 'Shimla', 'Siliguri', 'Solapur', 'Srinagar', 'Surat', 'Thanjavur', 'Thiruvananthapuram', 'Thrissur', 'Tiruchirappalli', 'Tirunelveli', 'Ujjain', 'Bijapur', 'Vadodara', 'Varanasi', 'Vasai-VirarCity', 'Vijayawada', 'Visakhapatnam', 'Vellore', 'Warangal', 'Ahmedabad', 'Bengaluru', 'Chennai', 'Delhi', 'Hyderabad', 'Kolkata', 'Mumbai', 'Pune']


        
        cities_lower=[x.lower() for x in cities]
        
        if loc.lower() not in cities_lower:
            dispatcher.utter_message("Sorry, we don’t operate in this city. Can you please specify some other location")
        return     