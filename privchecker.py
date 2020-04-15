#!/usr/bin/python
import glob
import sys
import csv
from math import ceil
from lxml import html


from selenium.common.exceptions import NoSuchElementException
import requests
from bs4 import BeautifulSoup
import urllib.parse
import json
import operator
import collections 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth

import time
import re
import yaml

class LoginError(Exception):
    """Raised when failed login into Social network """
    pass

class MissingDataError(Exception):
    pass

class Constants:
    ENGLISH = "English (UK)"
    CZECH = "Čeština"

    CzEnDict = {
        "Veřejný": "Public",
        "Všichni": "Everyone",
        "Ano": "Yes",
        "Ne": "No",
        "Přátelé": "Friends",
        "Přátelé přátel": "Friends of friends",
        "Zapnuto": "On",
        "Vypnuto": "Off",
        "Povolit": "Allow",
        "Nepovolit": "Don't allow",
        "Historie vaší polohy je vypnutá": "Your location history is off",
        "Historie vaší polohy je zapnutá": "Your location history is on",
        "Kdo uvidí vaše budoucí příspěvky?":"Who can see your future posts?",
        "Kdo vám může poslat žádost o přátelství?":"Who can send you friend requests?",
        "Kdo vidí seznam vašich přátel?":"Who can see your friends list?",
        "Kdo vás může vyhledat pomocí e-mailové adresy, kterou jste zadali?":"Who can look you up using the email address you provided?",
        "Kdo vás může vyhledat pomocí telefonního čísla, které jste zadali?":"Who can look you up using the phone number you provided?",
        "Chcete, aby se vyhledávače mimo Facebook propojily s vaším profilem?":"Do you want search engines outside of Facebook to link to your Profile?",
        "Kdo může na vaši timeline přidávat příspěvky?":"Who can post on your timeline?",
        "Kdo může vidět příspěvky, které na vaši timeline přidají ostatní uživatelé?":"Who can see what others post on your timeline?",
        "Povolit ostatním sdílet vaše příspěvky ve vlastním příběhu?":"Allow others to share your posts to their story?",
        "Skrývejte na své timeline komentáře obsahující určitá slova":"Hide comments containing certain words from your timeline",
        "Kdo může na vaší timeline vidět příspěvky, ve kterých vás někdo označil?":"Who can see posts that you're tagged in on your timeline?",
        "Někdo vás označí v příspěvku. Koho chcete přidat do okruhu uživatelů příspěvku, pokud ho už nevidí?":"When you're tagged in a post, who do you want to add to the audience of the post if they can't already see it?",
        "Chcete kontrolovat příspěvky, ve kterých vás někdo označil, než se budou moct zobrazit na vaší timeline?":"Review posts that you're tagged in before the posts appear on your timeline?",
        "Chcete kontrolovat označení, která lidé přidají do vašich příspěvků, než se tato označení objeví na Facebooku?":"Review tags that people add to your posts before the tags appear on Facebook?",
        "Povolit ostatním sdílet veřejné příběhy ve vlastním příběhu?":"Allow others to share your public stories to their own story?",
        "Umožnit sdílení vašich příběhů lidem, které zmíníte?":"Allow people to share your stories if you mention them?",
        "Zapnout historii polohy v mobilním zařízení?":"Turn on Location History for your mobile devices?",
        "Jenom já":"Only me",
        "Aktivita na webu a v aplikacích":"Web & App Activity",
        "Historie polohy":"Location History",
        "Historie YouTube":"YouTube History",
        "Kontaktní údaje uložené z komunikace":"Contact info saved from interactions",
        "Kontakty z vašich zařízení":"Contact info from your devices",
        "Sdílená doporučení v reklamách":"Shared endorsements in ads",
        "Pozastaveno":"Paused",
        "Chcete, aby vás Facebook mohl rozpoznávat na fotkách a ve videích?":"Do you want Facebook to be able to recognise you in photos and videos?",
        "On":"On",
        "Off":"Off",
        "phone":"phone",
        "Paused":"Paused",
        "name":"name"

    }
    Evaluation = {
            "Public":1.3,
            "Everyone":1.3,
            "Friends":1,
            "Friends of friends":1.15,
            "On":1,
            "Off":0,
            "Allow":1,
            "Don't allow":0,
            "Yes":1,
            "No":0,
            "Only me":0

            }
    FacebookWeights = {
            "Who can see your future posts?":0.25,
            "Who can send you friend requests?":0.15,
            "Who can see your friends list?":0.60,
            "Who can look you up using the email address you provided?":0.65,
            "Who can look you up using the phone number you provided?":0.70,
            "Do you want search engines outside of Facebook to link to your Profile?":0.50, #??
            "Who can post on your timeline?":0.5, #ma dopad na soukromí?
            "Who can see what others post on your timeline?":0.5, #ma dopad na soukromí?
            "Allow others to share your posts to their story?":0.25,
            "Hide comments containing certain words from your timeline":-0.15, # improve security
            "Who can see posts that you're tagged in on your timeline?":0.45,
            "When you're tagged in a post, who do you want to add to the audience of the post if they can't already see it?":0.4, #co to znamená????
            "Review posts that you're tagged in before the posts appear on your timeline?":-0.2, #improve security
            "Review tags that people add to your posts before the tags appear on Facebook?":-0.2,
            "Allow others to share your public stories to their own story?":0.6,
            "Allow people to share your stories if you mention them?":0.5,
            "Turn on Location History for your mobile devices?":0.8
            }
    TwitterWeights = {
            "protected": 0.25, # 1FB
            "geo_enabled": 0.8, #17FB
            "discoverable_by_email": 0.60, #4FB
            "discoverable_by_mobile_phone": 0.70, #5FB
            "allow_media_tagging": 0.45 #11FB
    }

    TwitterEvaluation = {
        "false":0,
        "true":1,
        "all":1.3,
        "none":0,
        "following":1
    }

    LinkedInEvaluation = {
        "EVERYONE":1.3,
        "True":1,
        "False":0,
        "FIRST_DEGREE_CONNECTIONS":1.15,
        "HIDE":0,# need to check 
        "DISCLOSE_FULL":1.15, # need to check
        "DISCLOSE_ANONYMOUS":1, # need to check
        "JUST_ME":0,
        "FIRST_DEGREE_CONNECTIONS":1,
        "SECOND_DEGREE_CONNECTIONS":1.15,
        "EVERYONE":1.3,
        "CONNECTIONS":1,
        "LINKEDIN_USER":1.3,
        "HIDDEN":0,
        "true":1,
        "false":0,
        True:1,
        False:0
        }

    LinkedInWeights = {
        "privacy/email":0.65,
        "connections-visibility":0.60,
        "show-full-last-name":0.50, # prijmeni ?? ve spojeni s praci ....
        "meet-the-team":0.4, # zobrazeni profilu u zamestnavatelu
        "data-sharing":0.5,
        "profile-visibility":0.5, # jak jsem videt mezi lidmi co si zobrazili profil
        "presence":0.05, # jsem online??
        "activity-broadcast":0.4,# oznamovat me zmeny v síti kontaktu
        "mentions":0.45, # oznacovani
        "visibility/email":0.65,
        "visibility/phone":0.70,
        }

    GoogleEvaluation = {
            "On":1,
            "Off":0,
            "Paused":0
            }

    GoogleWeights = {
            "Web & App Activity":0.7,
            "Location History":0.8,
            "YouTube History":0.6,
            "Contact info saved from interactions":0.8,
            "Contact info from your devices":0.7,
            "Shared endorsements in ads":0.4
            }

    @staticmethod
    def dump_twitter():
        return {"weights" : Constants.TwitterWeights,"evaluation" : Constants.TwitterEvaluation}

    @staticmethod 
    def dump_facebook():
        return {"weights" : Constants.FacebookWeights,"evaluation" : Constants.Evaluation}
    
    @staticmethod
    def dump_linkedin():     
        return {"weights" : Constants.LinkedInWeights,"evaluation" : Constants.LinkedInEvaluation}

    @staticmethod
    def dump_google():
        return {"weights" : Constants.GoogleWeights,"evaluation" : Constants.GoogleEvaluation}

    @staticmethod
    def export_settings_yaml(network,path):
        if network == "facebook":
            data = Constants.dump_facebook()
        elif network == "twitter":
            data = Constants.dump_twitter()
        elif network == "linkedin":
            data = Constants.dump_linkedin()
        elif network == "google":
            data = Constants.dump_google()

        with open(path,'w') as output:
            yaml.dump(data,output,default_flow_style=False)
    
    @staticmethod
    def import_settings_yaml(network,path):
        with open(path,'r') as input:
           data = yaml.safe_load(input)

        if network == "facebook":
            Constants.FacebookWeights = data["weights"]
            Constants.Evaluation = data["evaluation"]
        elif network == "twitter":
            Constants.TwitterWeights = data["weights"]
            Constants.TwitterEvaluation = data["evaluation"]
        elif network == "google":
            Constants.GoogleWeights = data["weights"]
            Constants.GoogleEvaluation = data["evaluation"]
        elif network == "linkedin":
            Constants.LinkedInWeights = data["weights"]
            Constants.LinkedInEvaluation = data["evaluation"]

    @staticmethod
    def cz_to_en_translate(word):
        return Constants.CzEnDict[word]

    @staticmethod
    def en_to_cz_translate(world):
        pass

    @staticmethod
    def is_english(word):
        return word == Constants.ENGLISH
    
    @staticmethod
    def get_facebook_profil():
        return Constants.FacebookWeights
               

    @staticmethod
    def get_facebook_evaluation():
        return Constants.Evaluation

    @staticmethod
    def cz_to_en_dict_translate(input_dict):
        result = {}
        for key, value in input_dict.items():
            result[Constants.cz_to_en_translate(key)] = Constants.cz_to_en_translate(value)
        return result

class OSN:
    def __init__(self,settings = None):
        self._name = None
        self._weights = None
        self._evaluation = None

    def get_weights(self):
        """
        return privacy impact weights for each option
        """
        return self._weights

    def get_evaluation(self):
        """
        return mapping dict between words and values - on ->1 ....
        """
        return self._evaluation

    def export_settings_yaml(self,path):
        with open(path,'w') as output:
            yaml.dump({"name":self._name,"weights":self._weights,"evaluation":self._evaluation},output,default_flow_style=False)
    
    def import_settings_yaml(self,path):
         with open(path,'r') as input_data:
            data = yaml.safe_load(input_data)
            # TODO only for testing !!!!!!
            if self._name is None:
                self._name = data["name"]

            if data["name"] != self._name:
               print("bad OSN loaded")
               exit(1)
            
            self._weights = data["weights"]
            self._evaluation = data["evaluation"]

    def get_advice(self,data):
        """
        user settings from social network 
        """
        pass

class Facebook(OSN):
    def __init__(self, settings = None):
        super().__init__(settings)
        self._name = "Facebook"
        self._min = 1.805
        self._max = 3.393
        self._default = 3.078
        self._evaluation = {
            "Public":3,
            "Everyone":3,
            "Friends":1,
            "Friends of friends":2,
            "On":1,
            "Off":0,
            "Allow":1,
            "Don't allow":0,
            "Yes":1,
            "No":0,
            "Only me":0

            }
        self._weights = {
            "Who can see your future posts?":0.25,
            "Who can send you friend requests?":0.15,
            "Who can see your friends list?":0.60,
            "Who can look you up using the email address you provided?":0.65,
            "Who can look you up using the phone number you provided?":0.70,
            "Do you want search engines outside of Facebook to link to your Profile?":0.50, #??
            "Who can post on your timeline?":0.5, #ma dopad na soukromí?
            "Who can see what others post on your timeline?":0.5, #ma dopad na soukromí?
            "Allow others to share your posts to their story?":0.25,
            "Hide comments containing certain words from your timeline":-0.15, # improve security
            "Who can see posts that you're tagged in on your timeline?":0.45,
            "When you're tagged in a post, who do you want to add to the audience of the post if they can't already see it?":0.4, #co to znamená????
            "Review posts that you're tagged in before the posts appear on your timeline?":-0.2, #improve security
            "Review tags that people add to your posts before the tags appear on Facebook?":-0.2,
            "Allow others to share your public stories to their own story?":0.6,
            "Allow people to share your stories if you mention them?":0.5,
            "Turn on Location History for your mobile devices?":0.8,
            "Do you want Facebook to be able to recognise you in photos and videos?":0.8,
            "name":0.05,
            "photo":0.55
            }


    def get_advice(self,data):
         for key,value in collections.OrderedDict(sorted(self._weights.items(), key=lambda x: x[1], reverse=True)).items():
            if self._evaluation[data[key]] >= 1:
                if key == "phone" or key == "photo" or key == "name":
                    continue
                yield key


class LinkedIn(OSN):
    def __init__(self):
        super().__init__()
        self._name = "Linkedin"
        self._min = 1.78
        self._max = 2.84
        self._default = 2.73 
        self._weights = {
            "privacy/email":0.65,
            "connections-visibility":0.60,
            "show-full-last-name":0.50, # prijmeni ?? ve spojeni s praci ....
            "meet-the-team":0.4, # zobrazeni profilu u zamestnavatelu
            "data-sharing":0.5,
            "profile-visibility":0.5, # jak jsem videt mezi lidmi co si zobrazili profil
            "presence":0.05, # jsem online??
            "activity-broadcast":0.4,# oznamovat me zmeny v síti kontaktu
            "mentions":0.45, # oznacovani
            "visibility/email":0.65,
            "visibility/phone":0.70,
            "education":0.15,
            "name":0.05,
            "photo":0.55
        }
        
        self._advice = {
        "privacy/email":"Who can see your email address",
        "connections-visibility":"Who can see your connections",
        "show-full-last-name":"Who can see your last name", # prijmeni ?? ve spojeni s praci ....
        "meet-the-team":"Show my name and/or picture with content about my employers, such as in job posting details and on company pages and insights, and with content related to my publicly expressed interests (e.g. when I like a service or follow a company, or comment or share its posts, LinkedIn may include my name and photo with their sponsored content when shown to my connections)?", # zobrazeni profilu u zamestnavatelu
        "data-sharing":"Profile visibility off LinkedIn",
        "profile-visibility":"Choose whether you’re visible or viewing in private mode", # jak jsem videt emezi lidmi co si zobrazili profil
        "presence":"Choose who can see when you are on LinkedIn", # jsem online??
        "activity-broadcast":"Share job changes, education changes, and work anniversaries from profile",# oznamovat me zmeny v síti kontaktu
        "mentions":"Choose whether other members can mention or tag you", # oznacovani
        "visibility/email":"Manage who can discover your profile from your email address",
        "visibility/phone":"Manage who can discover your profile from your phone number",
        "education":"next",
        "name":"next",
        "photo":"next"
        }




        self._evaluation = {
            "EVERYONE":3,
            "True":1,
            "False":0,
            "FIRST_DEGREE_CONNECTIONS":1,
            "HIDE":0,# need to check 
            "DISCLOSE_FULL":2, # need to check
            "DISCLOSE_ANONYMOUS":1, # need to check
            "JUST_ME":0,
            "FIRST_DEGREE_CONNECTIONS":1,
            "SECOND_DEGREE_CONNECTIONS":2,
            "EVERYONE":3,
            "CONNECTIONS":1,
            "LINKEDIN_USER":3,
            "HIDDEN":0,
            "true":1,
            "false":0,
            True:1,
            False:0
        }

    def get_advice(self,data):
        for key,value in collections.OrderedDict(sorted(self._weights.items(), key=lambda x: x[1], reverse=True)).items():
            if self._evaluation[data[key]] >= 1:
                yield self._advice[key]

    def export_settings_yaml(self,path):
        with open(path,'w') as output:
            yaml.dump({"name":self._name,"weights":self._weights,"evaluation":self._evaluation,"advice":self._advice},output,default_flow_style=False)
    
    def import_settings_yaml(self,path):
         with open(path,'r') as input_data:
            data = yaml.safe_load(input_data)
            if data["name"] != self._name:
               print("bad ONS loaded")
               exit(1)
            
            self._weights.update(data["weights"])
            self._evaluation.update(data["evaluation"])
            self._advice.update(data["advice"])



class Twitter(LinkedIn):
    def __init__(self):
        super().__init__()
        self._name = "Twiitter"
        self._min = 1.88
        self._max = 2.38
        self._default = 2.09
        self._weights = {
            "protected": 0.25, # 1FB
            "geo_enabled": 0.8, #17FB
            "discoverable_by_email": 0.60, #4FB
            "discoverable_by_mobile_phone": 0.70, #5FB
            "allow_media_tagging": 0.45, #11FB
            "name":0.05,
            "photo":0.55
            }
 
        self._advice = {
            "protected": "Only show your Tweets to people who follow you. If selected, you will need to approve each new follower.", # 1FB
            "geo_enabled": "Add location information to my Tweets", #17FB
            "discoverable_by_email": "Let people who have your email address find you on Twitter", #4FB
            "discoverable_by_mobile_phone": "Let people who have your phone number find you on Twitter.", #5FB
            "allow_media_tagging": "Allow people to tag you in photos and receive notifications when they do", #11FB
            "photo":"next",
            "name":"next"
            }


        self._evaluation = {
        "False":0,
        "True":1,
        False:0,
        True:1,
        "false":0,
        "true":1,
        "all":3,
        "none":0,
        "following":1
        }

class Google(Facebook):
    def __init__(self):
        super().__init__()
        self._name = "Google"
        self._min = 1.44
        self._max = 5.51
        self._default = 3.62
        self._evaluation = {
            "On":1,
            "Off":0,
            "Paused":0
            }
        
        self._weights = {
            "Web & App Activity":0.7,
            "Location History":0.8,
            "YouTube History":0.6,
            "Contact info saved from interactions":0.8,
            "Contact info from your devices":0.7,
            "Shared endorsements in ads":0.4,
            "name":0.05,
            "phone":0.70
            }

class Instagram(LinkedIn):
    def __init__(self):
        super().__init__()
        # TODO set correct values
        self._min = 0.066
        self._max = 1.296
        self._default = 1.296
        self._name = "Instagram"
        self._weights = {
                "disallow_story_reshare":0.6,
                "presence_disabled":0.05,
                "private_account":0.8,
                "name":0.05
                }
        self._advice = {
                "disallow_story_reshare":"Let people share your story as messages",
                "presence_disabled":"Allow accounts you follow and anyone you message to see when you were last active on Instagram apps. When this is turned off, you won't be able to see the activity status of other accounts",
                "private_account":"When your account is private, only people you approve can see your photos and videos on Instagram. Your existing followers won't be affected.",
                "name":"next"
                }
        self._evaluation = {
                # reverted in osn settings
                "True":0,
                "False":1,
                True:0,
                False:1,
                "false":1,
                "true":0
                }

class Tumblr(Facebook):
    def __init__(self):
        super().__init__()
        # TODO set correct values
        self._min = 0
        self._max = 0.075
        self._default = 0.075
        self._name = "Tumblr"
        self._weights = {"Let others see that you're active": 0.05}
        self._evaluation = {
                # reverted in osn settings
                True:1,
                False:0,
                "True":1,
                "False":0
                }



class Model:
    def __init__(self, data=None,weights=None,evaluation=None):
        self.__data = data
        self._weights = weights
        self._evaluation = evaluation
    
    def update_data(self,data):
        self._data = data

    def update_evaluation(self,e):
        self._evaluation = e

    def evaluate(self):
        pass

    def update_profil(self,profil):
        """ profil holds weights"""
        self._weights = profil

class Weight_visibility_model(Model):
    def __init__(self,data = None , profil = None , evaluation_array = None):
        super().__init__(data,profil,evaluation_array)

    def evaluate(self,operator):
        if self._data is None or self._weights is None or self._evaluation is None:
            return -1
        
        result = 0
        for key, value in self._data.items():
            if key in self._weights:
                result = result + operator(self._weights[key], self._evaluation[value])
        return result
            
class PIDX(Model):
    def __init__(self, data = None, weights = None, evaluation = None):
        super().__init__(data = data, weights = weights, evaluation = evaluation)

    def configuration_impact(self):
        #TODO st*pjt for each 
        pass

    def visibility(self):
        """ TODO need to define visibility function g <0,1>"""
        pass

    def privacy_function(self):
        #TODO privacy function f = w(i,j)
        pass

    def evaluate(self):
        # TODO PIDX = w(i,j)/w(i,i)*100 
        pass

class W_PIDX(PIDX):
    def __init__(self, data = None, weights = None, evaluation = None):
        super().__init__(data = data, weights = weights, evaluation = evaluation)
        
    def privacy_function(self):
        pass

    def evaluate(self,operator):
        result = 0
        for key, value in self._data.items():
            if key in self._weights:
                result = result + self._weights[key]*self._evaluation[value]
     
        return result/sum(self._evaluation.values())

class M_PIDX(PIDX):
    def __init__(self, data = None, weights = None, evaluation = None):
        super().__init__(data = data, weights = weights, evaluation = evaluation)

    def evaluate(self,operator):
        result = {}
        for key, value in self._data.items():
            if key in self._weights:
                result[key] = self._weights[key]*self._evaluation[value]
        
        return max(result.values())


class C_PIDX(W_PIDX,M_PIDX):
    def __init__(self, data = None, weights = None, evaluation = None):
        super(W_PIDX, self).__init__(data = data, weights = weights, evaluation = evaluation)

    def evaluate(self,operator):
        return M_PIDX.evaluate(self,None)+(100-M_PIDX.evaluate(self,None))*W_PIDX.evaluate(self,None)/100



class Evaluator:
    def __init__(self,osn,data,model = None):
        self._model = model
        self._osn = osn
        self._data = data
        
        if model is not None:
            model.update_data(data)
            model.update_evaluation(osn.get_evaluation())
            model.update_profil(osn.get_weights())

    def apply_model(self):
        if self._model == None:
            print("set model !!")
            exit(1)
        return self._model.evaluate(operator.mul) #operator only for easy model

    def change_model(self,new_model):
        self._model = new_model
        self._model.update_data(self._data)
        self._model.update_evaluation(self._osn.get_evaluation()) 
        self._model.update_profil(self._osn.get_weights())

    def advice(self):
        return self._osn.get_advice(self._data)


    """
    def advise_settings(self):
        for key,value in collections.OrderedDict(sorted(Constants.FacebookWeights.items(), key=lambda x: x[1], reverse=True)).items():
            if Constants.get_facebook_evaluation()[self._data[key]] >= 1:
                yield key
    """

class Extractor:
    def __init__(self):
        """acc dict contains all set up accounts for test"""
        self._acc = {}

    def add_social_network(self,name = None ,username = None,password = None,file_name = None):
        if file_name is None:
            if name ==  "facebook":
                self._acc[name] = FacebookLogin()
            elif name == "twitter":
                self._acc[name] = TwitterLogin()
            elif name == "google":
                self._acc[name] = GoogleLogin()
            elif name == "linkedin":
                self._acc[name] = LinkedInLogin()

            self._acc[name].login(username,password)
            self._acc[name].parse()
        
        elif file_name is not None:
                self._acc[name] = LoginHandle()
                self._acc[name].load_data(file_name)

            

    
    def run(self):
        """ need to be translate to english - models work with english, every call return one social network"""
        for key, item in self._acc.items():
            if not Constants.is_english(item.get_language()):
                yield self.translate(item.get_data()),key
            else:
                yield item.get_data(),key
                
    def translate(self,data):
        result = {}
        for key, value in data.items():
            result[Constants.cz_to_en_translate(key)] = Constants.cz_to_en_translate(value)

        return result

class LoginHandle:
    def __init__(self):
        self._data = dict()
        self._language = Constants.ENGLISH
        self._extern_data = dict()
        self._user_id = None

    def get_language(self):
        return self._language
    
    def extern_login(self):
        pass

    def download_extern_data(self):
        if self._user_id is not None:
            self._extern_data = requests.get(self._url+"/"+self._user_id)
        else:
            print("first log in")
            return 0

    def login(self,name,passwd):
        self.name = name
        self.passwd = passwd
        pass

    def parse(self):
        pass

    def store_data(self,path):
        json.dump(self._data, open(path,"w"))

    def load_data(self,path):
        self._data.update(json.load(open(path)))

    def get_data(self):
        return self._data

    def get_user_id(self):
        return self._user_id

    def check_successful_login(self,elements):
        time.sleep(5)
        flag = 0
        for item in elements:
            try:
                self._driver.find_element_by_xpath(item)
            except (ElementNotInteractableException, ElementClickInterceptedException, NoSuchElementException):
                flag = flag+1  
            if flag < len(elements):
                self._driver.close()
                raise LoginError
            else:
                return ""

    def parse_extern(self, endpoint, paths, driver = None):
        flag = False
        if driver is None:
            driver = webdriver.Firefox()
            flag = True

        driver.get(endpoint+"/"+self._user_id)
       # time.sleep(2)
       # driver.refresh() only for facebook
        time.sleep(4)
        for key,value in paths.items():
            try:
                driver.find_element_by_xpath(value)
                self._extern_data[key] = True
            except NoSuchElementException:
                self._extern_data[key] = False
        
        if flag:
            driver.close()

        print (self._extern_data)
    


class FacebookLogin(LoginHandle):


    def __init__(self):
        super().__init__()
        self._url = "https://www.facebook.com/"
        self.__language = "https://www.facebook.com/settings?tab=language"
        self.__endpoints = [
            "https://www.facebook.com/settings?tab=privacy",
            "https://www.facebook.com/settings?tab=timeline",
            "https://www.facebook.com/settings?tab=stories",
            "https://www.facebook.com/settings?tab=location",
            "https://www.facebook.com/settings?tab=facerec"
        ]
        # different html structure
        self._location_endpoint = "https://www.facebook.com/settings?tab=location"

        self.__session = requests.Session()
        self.__session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:39.0) Gecko/20100101 Firefox/39.0'
        })
        self._language = None

        self._data["name"] = "Everyone"
        self._data["photo"] = "Everyone"
        
        self._extern_data = dict()

    def get_language(self):
        return self._language

    def login(self,name,passwd):
        super().login(name,passwd)
        self.__session.get('https://m.facebook.com')
        response = self.__session.post('https://m.facebook.com/login.php', data={
            'email': name,
            'pass': passwd
        }, allow_redirects=False)

        if 'c_user' not in response.cookies:
            raise LoginError

        return True

    def parse(self):
        data = self.__session.get("https://www.facebook.com")
        soup  = BeautifulSoup(data.text,'html.parser')
        # TODO user id cant find
        #print(data)
        data = soup.findAll("a",class_="_2s25 _606w")
        self._user_id = data[0]["href"][25:]

        # download page with language
        data = self.__session.get('https://www.facebook.com/settings?tab=language').text

        soup = BeautifulSoup(data, 'html.parser')
        settings = soup.findAll("a", class_="fbSettingsListLink clearfix pvm phs")

        #print(item.find("span", class_="fbSettingsListItemContent fcg").find("div", class_="_nll").string, end=" : ")

        # language is first item
        self._language = settings[0].find("span", class_="fbSettingsListItemContent fcg").find("div", class_="_nlm fwb").string
        result = {}

        for item in self.__endpoints:
            data = self.__session.get(item).text
            soup = BeautifulSoup(data, 'html.parser')
      #      result[soup.find("span", class_="_c24")] = None
            settings = soup.findAll("a", class_="fbSettingsListLink clearfix pvm phs")
            for x in settings:
                #sometimes is shown help and change structure
                if x.find("span", class_="fbSettingsListItemContent fcg").find("div", class_="_nll").string is None:
                    index = list(x.find("span", class_="fbSettingsListItemContent fcg").find("div", class_="_nll").stripped_strings)[0]
                else:
                    index = x.find("span", class_="fbSettingsListItemContent fcg").find("div", class_="_nll").string

                result[index] = x.find("span", class_="fbSettingsListItemContent fcg").find("div", class_="_nlm fwb").string

        # page with location has different structure then others
        #data = self.__session.get(self._location_endpoint).text
        #soup = BeautifulSoup(data,'html.parser')
        #setting = soup.find("div", class_="_4-u3 _2ph-").find("span", class_="_c24").string
        #result[setting] = True


        # remove unusable settings with None value
        result = dict(filter(lambda a:a[1] is not None , result.items()))
        self._data.update(result)
        self.parse_extern(self._url,{"hometown":'//*[@id="pagelet_hometown"]/div/div/div/span', 
            "favorites":'//*[@id="favorites"]/div[2]/table',
            "education":'//*[@id="pagelet_eduwork"]/div/div/div/span'})

class TwitterLogin(LoginHandle):

    def __init__(self):
        super().__init__()
        self._url = "http://www.twitter.com"
        self._redirect_delay = 5
        self._endpoint = "https://twitter.com/settings/account"
        self._data["name"] = "all"
        self._data["photo"] = "all"
        self._extern_data = None
    


    def login(self,name,passwd):
        self._driver = webdriver.Firefox() #TODO need to be setup gecko
        self._driver.get(self._url)
        try:
            myElem = WebDriverWait(self._driver, self._redirect_delay).until(EC.presence_of_element_located((By.NAME, 'session[username_or_email]')))
        except TimeoutException:
            print ("Loading took too much time!")
            #TODO try load again? or exit? increase delay value? 
        try:
            name_input = self._driver.find_element_by_name("session[username_or_email]")
            name_input.clear()
            name_input.send_keys(name)

            passwd_input = self._driver.find_element_by_name("session[password]")
            passwd_input.clear()
            passwd_input.send_keys(passwd)
            
            login_form = self._driver.find_element_by_xpath("//form[@class='r-13qz1uu']")
            login_form.submit()
            
            self.check_successful_login(['//*[@id="react-root"]/div/div/div[2]/main/div/div/h1/span'])
       
        except NoSuchElementException:
            print("cant find input") #Load error or page was changed
            exit(0)
        
      

        
    def get_page(self,url):
       time.sleep(self._redirect_delay) #TODO test if it enough.... and try again? 
       return self._driver.get(url)

    def parse(self):

        self.get_page(self._endpoint)
        data = self._driver.page_source
        regex = r"\"remote\":{\"settings\":.*\"fetchStatus\":\"loaded\"}"
        c_regex = re.compile(regex)
        data = c_regex.findall( data)
        self._data.update( json.loads(data[0][9:])["settings"])
        self._user_id = self._data["screen_name"]
        self._driver.close() 
        self.parse_extern(self._url,{"hometown":'//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div/div/div/div[1]/div[2]/div[4]/div/span[1]/span/span', 
            "favorites":'//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div/div/div/div[1]/div[2]/div[3]/div/div/span',
            "education":'//*[@id="pagelet_eduwork"]/div/div/div/span'})



class LinkedInLogin(LoginHandle):
    
    def __init__(self):
        super().__init__()
        self._url = "https://www.linkedin.com"
        self._login = "https://www.linkedin.com/uas/login-submit"
        self.__session = requests.Session()
        self.__session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:39.0) Gecko/20100101 Firefox/39.0'
        })
        self._endpoints = [
            "https://www.linkedin.com/psettings/privacy/email",
            "https://www.linkedin.com/psettings/connections-visibility",
            "https://www.linkedin.com/psettings/show-full-last-name",
            "https://www.linkedin.com/psettings/meet-the-team",
            "https://www.linkedin.com/psettings/data-sharing",
            "https://www.linkedin.com/psettings/profile-visibility",
            "https://www.linkedin.com/psettings/presence",
            "https://www.linkedin.com/psettings/activity-broadcast",
            "https://www.linkedin.com/psettings/mentions",
            "https://www.linkedin.com/psettings/visibility/email",
            "https://www.linkedin.com/psettings/visibility/phone",
           # "https://www.linkedin.com/psettings/ingested-data-profile-match" impact??
        ]
         # this attributes cant be modified, need to be add manualy    
        self._data["name"] = "EVERYONE"
        self._data["photo"] = "EVERYONE"
        self._data["education"] = "EVERYONE"
        self._extern_data = dict()

        
    def extern_login(self):
       pass 
        
    def login(self,name,passwd):
        HOMEPAGE_URL = 'https://www.linkedin.com'
        LOGIN_URL = 'https://www.linkedin.com/uas/login-submit'

        data = self.__session.get("https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin")
        html = data.content
        soup = BeautifulSoup(html, "html.parser")
        csrf = soup.find('input', {'name': 'loginCsrfParam'}).get('value')
        login_information = {
            'session_key': name,
            'session_password': passwd,
            'loginCsrfParam': csrf,
            'trk': 'guest_homepage-basic_sign-in-submit'
        }

        response = self.__session.post(self._login, data=login_information)
        self.check_successful_login(response)

    def check_successful_login(self, response): 
        title = BeautifulSoup(response.content,features="lxml")
        if title.title.text == "Security Verification | LinkedIn":
            raise LoginError

    def use_selenium(self,url,cookies):
        #self._driver = webdriver.Firefox()
        for c in cookies :
            self._driver.add_cookie({'name': c.name, 'value': c.value, 'path': c.path, 'expiry': c.expires})
        time.sleep(2)
        self._driver.get(url)
        time.sleep(1)
        return self._driver.page_source

    def parse_extern(self,endpoint):
        self._driver.get(endpoint+"/"+self._user_id)
        data = self._driver.page_source

        #print(data)

        hometown_r  = r"\"defaultLocalizedName\":\"[\w - | .',]*\""
        work_r  = r"\"companyName\":\"[\w - | .',]*\""
        school_r = r"\"schoolName\":\"[\w - | .',]*\""


        h_r = re.compile(hometown_r)
        w_r = re.compile(work_r)
        s_r = re.compile(school_r)

        hometown = h_r.findall(data)
        work = w_r.findall(data)
        school = s_r.findall(data)
        hometown = hometown[-1][24:][:-1]
        work = work[-1][15:][:-1]
        school = school[-1][14:][:-1]
        
        self._extern_data["hometown"] = hometown != "string"
        self._extern_data["work"] = work != "string"
        self._extern_data["education"] = school != "string"
        self._extern_data["name"] = True


    def parse(self):
        self._driver = webdriver.Firefox()
        self._driver.get(self._url)
        data = self.use_selenium("https://www.linkedin.com/feed/",self.__session.cookies)
        soup =  BeautifulSoup(data,"html.parser")
        self._user_id = soup.find("a",{"data-control-name":"nav.settings_view_profile"})
        #self._driver.close()
        self._user_id = self._user_id["href"]
    #    print (self._user_id)
        self.parse_extern(self._url)
        


        for item in self._endpoints:
            html_data = self.use_selenium(item, self.__session.cookies)
            soup = BeautifulSoup(html_data,"html.parser")
            value = soup.find("option", selected = True)

            if value is not None:
                value = value.get("value")
            else:
                value = soup.find("input",{"name":"meet-the-team"})
                if value is not None:
                    if soup.find("input",{"name":"meet-the-team","checked":True}) is not None:
                        value = True    # checkbox checked
                    else:
                        value = False

                else:  #  soup = BeautifulSoup(html_data, "html.parser")
                    value = soup.find("input",{"class":"show-full-last-name-radio","checked":True})
                    if value is not None:
                        value = value.get("value")
                    else:
                        value = soup.find("input",{"name":"data-sharing"})
                        if value is not None:
                            value = soup.find("input",{"name":"data-sharing","checked":True})
                            if value is not None:
                                value = True
                            else:
                                value = False
                        else:
                            value = soup.find("input",{"name":"discloseAsProfileViewer","checked":True})
                            if value is not None:
                                value = value.get("value")
                            else:
                                value = soup.find("input",{"name":"presenceVisibility","checked":True})
                                if value is not None:
                                    value = value.get("value")
                                else:
                                    value = soup.find("input",{"name":"activity-broadcast"})
                                    if value is not None:
                                        value = soup.find("input",{"name":"activity-broadcast","checked":True})
                                        if value is not None:
                                            value = True
                                        else:
                                            value = False
                                    else:
                                        value = soup.find("input",{"name":"mentions"})
                                        if value is not None:
                                            value = soup.find("input",{"name":"mentions","checked":True})
                                            if value is not None:
                                                value = True
                                            else:
                                                value = False
            
            self._data[item[35:]] = value 
        self._driver.close()



class GoogleLogin(LoginHandle):
    
    def __init__(self):
        super().__init__()
        self._url = "https://stackoverflow.com/"
        self._login = "https://stackoverflow.com/users/login?ssrc=head&returnurl=https%3a%2f%2fstackoverflow.com%2f"
        self._google = "https://www.youtube.com/"
        self._google_account = ""
        self._wait = 5
        self._data["phone"] = "On"
        self._data["name"] = "On"
        self._extern_data = None

    def login(self,name,passwd):
        self._driver = webdriver.Firefox()
        #login via Stack overflow

        self._driver.get(self._url)
        self._driver.get(self._login)

        google_login_redirect = self._driver.find_element_by_xpath('//*[@id="openid-buttons"]/button[1]')
        google_login_redirect.click()

        try:
            WebDriverWait(self._driver,self._wait).until(EC.presence_of_element_located((By.XPATH,'//*[@id="identifierId"]')))
        except TimeoutException:
            time.sleep(3)
        # set up credentials into google form
        try:
            time.sleep(2)
            name_input = self._driver.find_element_by_xpath('//*[@id="identifierId"]')
        except (ElementNotInteractableException, ElementClickInterceptedException, NoSuchElementException):
            time.sleep(3)

        name_input.clear()
        name_input.send_keys(name)

        next_page = self._driver.find_element_by_xpath('//*[@id="identifierNext"]')
        next_page.click()
       
        try: 
            WebDriverWait(self._driver,self._wait).until(EC.presence_of_element_located((By.XPATH,'//*[@id="passwordNext"]')))
        except TimeoutException:
            time.sleep(3)

        try:
            time.sleep(2)
            passwd_input = self._driver.find_element_by_xpath('//*[@id="password"]/div[1]/div/div[1]/input')
        except (ElementNotInteractableException, ElementClickInterceptedException, NoSuchElementException):
            time.sleep(3)

        try:
            passwd_input.clear()
        except UnboundLocalError:
            self._driver.close()
            raise LoginError
        passwd_input.send_keys(passwd)

        next_page = self._driver.find_element_by_xpath('//*[@id="passwordNext"]')
        next_page.click()
        time.sleep(1)
        
        self.check_successful_login(['//*[@id="view_container"]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div[2]/div[2]/span'])


    def parse(self):
        # logged state
        # goto google page(youtube)
        self._driver.get(self._google)

        try:
            WebDriverWait(self._driver,self._wait).until(EC.presence_of_element_located((By.XPATH,'//*[@id="avatar-btn"]')))
        except TimeoutException:
                print("timeout")
        # navigate to settings
        self._driver.get("https://myaccount.google.com/u/0/data-and-personalization")

        # extract settings
        settings = {'//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/c-wiz/div/div[3]/div/div/c-wiz/section/article[2]/div/div/div[2]/div/a/div/div[2]/div/div[1]/div/h3':'//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/c-wiz/div/div[3]/div/div/c-wiz/section/article[2]/div/div/div[2]/div/a/div/div[2]/div/div[2]/div/div[2]', #activity on web and applications
                '//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/c-wiz/div/div[3]/div/div/c-wiz/section/article[2]/div/div/div[3]/div[2]/a/div/div[2]/div/div[1]/div/h3':'//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/c-wiz/div/div[3]/div/div/c-wiz/section/article[2]/div/div/div[3]/div[2]/a/div/div[2]/div/div[2]/div/div[2]', #location history
                '//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/c-wiz/div/div[3]/div/div/c-wiz/section/article[2]/div/div/div[4]/div[2]/a/div/div[2]/div/div[1]/div/h3':'//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/c-wiz/div/div[3]/div/div/c-wiz/section/article[2]/div/div/div[4]/div[2]/a/div/div[2]/div/div[2]/div/div[2]'
                }
        self._language = self._driver.find_element_by_xpath('//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/c-wiz/div/div[3]/div/div/c-wiz/section/article[8]/div/div/div[2]/div/a/div/div[2]/div/div[2]/div/div').text
        self._language = self._language.split()[0]
        for key, value in settings.items():
            self._data[self._driver.find_element_by_xpath(key).text] =self._driver.find_element_by_xpath(value).text 
            #print(self._driver.find_element_by_xpath(key).text+":"+self._driver.find_element_by_xpath(value).text)
        
        settings = {'//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/c-wiz/div/div[3]/div/div/c-wiz/section/article[1]/div/div/div[3]/div[2]/a/div/div[2]/div/div[1]/div/h3':'//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/c-wiz/div/div[3]/div/div/c-wiz/section/article[1]/div/div/div[3]/div[2]/a/div/div[2]/div/div[2]/div/div[2]',#contacts saved from communication
                    '//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/c-wiz/div/div[3]/div/div/c-wiz/section/article[1]/div/div/div[4]/div[2]/a/div/div[2]/div/div[1]/div/h3':'//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/c-wiz/div/div[3]/div/div/c-wiz/section/article[1]/div/div/div[4]/div[2]/a/div/div[2]/div/div[2]/div/div[2]',#contacts from your device
                    '//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/c-wiz/div/div[3]/div/div/c-wiz/section/article[4]/div/div/div[2]/div/div/div/div[2]/div/div[1]/div/h3':'//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/c-wiz/div/div[3]/div/div/c-wiz/section/article[4]/div/div/div[2]/div/div/div/div[2]/div/div[2]/div/div[2]' #connect your profile with ads
                    }

           

        self._driver.get("https://myaccount.google.com/u/0/people-and-sharing")

        for key, value in settings.items():
            self._data[self._driver.find_element_by_xpath(key).text] =self._driver.find_element_by_xpath(value).text 
            #print(self._driver.find_element_by_xpath(key).text+":"+self._driver.find_element_by_xpath(value).text)
        if not Constants.is_english(self._language):
            # TODO check if update is ok !!!!!
            self._data.update(Constants.cz_to_en_dict_translate(self._data))

        self._driver.close()

class InstagramLogin(LoginHandle):

    def __init__(self):
        super().__init__()
        self._url = "https://www.instagram.com/"
        self._redirect_delay = 5
        self._endpoint = "https://www.instagram.com/accounts/privacy_and_security/"
        self._data["name"] = "false"
        self._extern_data = dict()

    def login(self,name,passwd):
        if len(passwd) < 6:
            raise LoginError

        self._driver = webdriver.Firefox()
        self._driver.get(self._url)
        
        myElem = WebDriverWait(self._driver, self._redirect_delay).until(EC.presence_of_element_located((By.XPATH,'//*[@id="react-root"]/section/main/article/div[2]/div[1]/div/form')))
        
        name_input = self._driver.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div[2]/div[1]/div/form/div[2]/div/label/input')
        name_input.clear()
        name_input.send_keys(name)
        
        passwd_input = self._driver.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div[2]/div[1]/div/form/div[3]/div/label/input')
        passwd_input.clear()
        passwd_input.send_keys(passwd)

        login_form = self._driver.find_element_by_xpath('/html/body/div[1]/section/main/article/div[2]/div[1]/div/form')
        login_form.submit()
        time.sleep(3)

        self.check_successful_login(['//*[@id="slfErrorAlert"]'])
        self._driver.get("https://www.instagram.com/accounts/edit/")
        time.sleep(3)

        self._user_id = self._driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/article/div/div[2]/h1').text

    def parse_extern(self, endpoint):
        self._driver.get(self._url+self._user_id)
        time.sleep(3)
        data = self._driver.page_source
        self._extern_data["hometown"] = data.find('"description":') > 0
        self._extern_data["name"] = True
        print(self._extern_data)

    def parse(self):
        self._driver.get(self._endpoint)
        
        data = self._driver.find_element_by_xpath('/html/body/script[1]')
        self._data.update(json.loads(data.get_attribute('innerHTML')[21:][:-1])["entry_data"]["SettingsPages"][0]["form_data"])
        
        self.parse_extern(self._url)
        self._driver.close()
        

class TumblrLogin(LoginHandle):
    def __init__(self):
        super().__init__()
        self._url = "https://www.tumblr.com/login"
        self._endpoint = "https://www.tumblr.com/settings/privacy"
        self._redirect_delay = 5
        self._extern_data = None

    def login(self,name,passwd):
        self._driver = webdriver.Firefox()
        self._driver.get(self._url)

        WebDriverWait(self._driver,self._redirect_delay).until(EC.presence_of_element_located((By.XPATH,'//*[@id="signup_determine_email"]')))
        
        name_input = self._driver.find_element_by_xpath('//*[@id="signup_determine_email"]')
        name_input.clear()
        name_input.send_keys(name)

        self._driver.find_element_by_xpath('//*[@id="signup_forms_submit"]').click()
        self.check_successful_login(['//*[@id="signup_form_errors"]/li'])
        WebDriverWait(self._driver,self._redirect_delay).until(EC.presence_of_element_located((By.XPATH,'//*[@id="signup_magiclink"]/div[2]/a')))
        time.sleep(5)
        self._driver.find_element_by_xpath('//*[@id="signup_magiclink"]/div[2]/a').click()
        
        time.sleep(2)
        passwd_input = self._driver.find_element_by_xpath('//*[@id="signup_password"]')
        passwd_input.clear()
        passwd_input.send_keys(passwd)

        self._driver.find_element_by_xpath('//*[@id="signup_form"]').submit()
        time.sleep(2)
        self.check_successful_login(['//*[@id="signup_form_errors"]/li'])
        

    def parse(self):
        self._driver.get(self._endpoint)
        time.sleep(2)
        data = self._driver.page_source

        soup = BeautifulSoup(data,"html.parser")
        value = soup.find("input",{"id":"tumblelog_setting_status_indicator","checked":True})
        if value is not None:
            value = True
        else:
            value = False

        self._data["Let others see that you're active"] = value
        self._driver.close()

class Presenter:
    def __init__(self):
        self._networks = []

    def add_network(self, network, result, advice):
        self._networks.append({"network":network,"result":result,"advice":advice})

    def calculate_result(self,value):
        """
        first move min to 0
        then calculate percentual result
        """
        result = value - network._min
        result = result/network._max*100
        
    def present_result(self,value):
       # print("")
       # print("Minimal reachable privacy score for "+self._network._name+" is: "+self._network._min)
       # print("Maximal privacy score for "+self._network._name+" is: "+self._network._max)
       # print("Your privacy score for "+self._network._name+" is: "+value+" | "+self.calculate_result(value)+"% of maximum")
        
    def present_in_browser(self,value,advice):
        page = webdriver.Firefox()
        page.get("http://www.stud.fit.vutbr.cz/~xjanus08/privchecker/dist/index.html?min="+str(self._network._min)+"&max="
                +str(self._network._max)+"&default="+str(self._network._default)+"&value="+str(value)+"&name="+self._network._name.capitalize()+"&help="+advice)


def main1(f):
    login = GoogleLogin()
    login.load_data(f)

    nt = OSN()
    nt.import_settings_yaml("google.yaml")
    evaluator = Evaluator(osn=nt,data=login.get_data())
    #evaluator.change_model(Weight_visibility_model())
    # result = {}
    result["W&V"]=evaluator.apply_model()
    #evaluator.change_model(M_PIDX())
    #result["M_PIDX"]=evaluator.apply_model()
    #evaluator.change_model(W_PIDX())
    #result["W_PIDX"]=evaluator.apply_model()
    evaluator.change_model(C_PIDX())
    result=evaluator.apply_model()

    print(result)
    #writer.writerow(result)




if __name__ == '__main__':


    name = None
    networks = {"Facebook":None,"Twitter":None,"Google":None,"Linkedin":None,"Instagram":None,"Tumblr":None,"Pinterest":None}
    firts = True

    while 1:
        ready_to_add = ""
        for key, item in networks.items():
            if item is None:
                ready_to_add = ready_to_add+" | "+key
        if First:
            print("Add network for evaluation"+ready_to_add)
        else:
            print("Type EVALUATE for skip adding new network or Add network for evaluation"+ready_to_add)
        
        ready_to_add = ""
        First = False
        
        network = input(">")
        if network == "Facebook" or network == "F" or network == "facebook":
            nt = Facebook()
            login = FacebookLogin()
            
        elif network == "Twitter" or network == "T" or network == "twitter":
            nt = Twitter()
            login = TwitterLogin()

        elif network == "Google" or network == "G" or network == "google":
            nt = Google()
            login = GoogleLogin()
        
        elif network == "LinkedIn" or network == "L" or network == "linkedin":
            nt = LinkedIn()
            login = LinkedInLogin()
        
        elif network == "Instagram" or network == "I" or network == "instagram":
            nt = Instagram()
            login = InstagramLogin()

        elif network == "Tumblr" or network == "M" or network == "tumblr":
            nt = Tumblr()
            login = TumblrLogin()
        
        elif network == "EVALUATE":
            pass
        
        else:
            print ("unsupported option")
            continue

        name = input("Username:")
        passwd = input("Password:")
            
        print ("Logging in "+nt._name)
        try:
            login.login(name,passwd)
        #    login.login("fitvut@seznam.cz","diplomka2019")
#            login.login("diplomka2020@tiscali.cz","fitvut2020")
        except (LoginError) as e:
            print("invalid credentials")
            continue

        except (ElementNotInteractableException, ElementClickInterceptedException) as e:
            if login._driver is not None:
                login._driver.close()
            login.login(name,passwd)
            #login.login("fitvut@seznam.cz","diplomka2019")
        try:
            print("Downloading data from "+nt._name)

            login.parse()
#        except (AttributeError):
 #           print("error: please try to login in browser")
  #          exit(1)

        except (ElementNotInteractableException, ElementClickInterceptedException) as e:
            login.parse()

        networks[nt._name] = (nt,login)
        cnt = input("For adding next network type NEXT and press enter, for evaluation press only enter")
        if cnt == "NEXT":
            continue

        for key,item in networks.items():
            evaluator = Evaluator(osn=item[0],data=item[1].get_data())
            evaluator.change_model(C_PIDX())
            advice = evaluator.advice()
        try:
            adv = next(advice)
        except StopIteration:
            adv = "No help"
        flag = True

        value = evaluator.apply_model()

        presenter = Presenter(nt)
        presenter.present_in_browser(ceil(value*1000)/1000,adv)
        print("Your privacy score: "+str(evaluator.apply_model()))
        
        while 1:
                print("Evaluate - E | Get advice - A | Back - B | Quit - Q")

                action = input(">")
                if action == "Evaluate" or action == "E":
                    print("Your privacy score: "+str(value))
                elif action == "Advise" or action == "A":
                    try:
                        if not flag:
                            adv = next(advice)
                    
                        if adv == "next":
                            adv = next(advice)
                        flag = False
                        print("Try to change: " +adv)
                    except StopIteration as e:
                        print("No more help")
                elif action == "Back" or action == "B":
                    break
                elif action == "Quit" or action == "Q":
                    exit(0)

    exit(0)
    
# fitvut@tiscali.cz diplomka2019
