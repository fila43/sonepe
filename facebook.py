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
        "Pozastaveno":"Paused"

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
            if data["name"] != self._name:
               print("bad ONS loaded")
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
        self._name = "facebook"
        self._evaluation = {
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
            "Turn on Location History for your mobile devices?":0.8
            }


    def get_advice(self,data):
         for key,value in collections.OrderedDict(sorted(self._weights.items(), key=lambda x: x[1], reverse=True)).items():
            if self._evaluation[data[key]] >= 1:
                yield key


class LinkedIn(OSN):
    def __init__(self):
        super().__init__()
        self._name = "linkedin"
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
            "visibility/phone":0.70
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
        "visibility/phone":"Manage who can discover your profile from your phone number"
        }




        self._evaluation = {
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
            
            self._weights = data["weights"]
            self._evaluation = data["evaluation"]
            self._advice = data["advice"]



class Twitter(LinkedIn):
    def __init__(self):
        super().__init__()
        self._name = "twiitter"
        self._weights = {
            "protected": 0.25, # 1FB
            "geo_enabled": 0.8, #17FB
            "discoverable_by_email": 0.60, #4FB
            "discoverable_by_mobile_phone": 0.70, #5FB
            "allow_media_tagging": 0.45 #11FB
            }
 
        self._advice = {
            "protected": "Only show your Tweets to people who follow you. If selected, you will need to approve each new follower.", # 1FB
            "geo_enabled": "Add location information to my Tweets", #17FB
            "discoverable_by_email": "Let people who have your email address find you on Twitter", #4FB
            "discoverable_by_mobile_phone": "Let people who have your phone number find you on Twitter.", #5FB
            "allow_media_tagging": "Allow people to tag you in photos and receive notifications when they do" #11FB
            }


        self._evaluation = {
        "False":0,
        "True":1,
        False:0,
        True:1,
        "false":0,
        "true":1,
        "all":1.3,
        "none":0,
        "following":1
        }

class Google(Facebook):
    def __init__(self):
        super().__init__()
        self._name = "google"
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
            "Shared endorsements in ads":0.4
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

    def get_language(self):
        return self._language

    def login(self,name,passwd):
        self.name = name
        self.passwd = passwd
        pass

    def parse(self):
        pass

    def store_data(self,path):
        json.dump(self._data, open(path,"w"))

    def load_data(self,path):
        self._data = json.load(open(path))

    def get_data(self):
        return self._data

class FacebookLogin(LoginHandle):


    def __init__(self):
        super().__init__()
        self.__language = "https://www.facebook.com/settings?tab=language"
        self.__endpoints = [
            "https://www.facebook.com/settings?tab=privacy",
            "https://www.facebook.com/settings?tab=timeline",
            "https://www.facebook.com/settings?tab=stories",
            "https://www.facebook.com/settings?tab=location"
        ]
        # different html structure
        self._location_endpoint = "https://www.facebook.com/settings?tab=location"

        self.__session = requests.Session()
        self.__session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:39.0) Gecko/20100101 Firefox/39.0'
        })
        self._language = None

    def get_language(self):
        return self._language

    def login(self,name,passwd):
        super().login(name,passwd)
        self.__session.get('https://m.facebook.com')
        response = self.__session.post('https://m.facebook.com/login.php', data={
            'email': "fitvut@seznam.cz",
            'pass': "diplomka2019"
        }, allow_redirects=False)

        if 'c_user' not in response.cookies:
            raise LoginError

        return True

    def parse(self):
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
        self._data = result

class TwitterLogin(LoginHandle):

    def __init__(self):
        super().__init__()
        self._url = "http://www.twitter.com"
        self._redirect_delay = 5
        self._endpoint = "https://twitter.com/settings/account"

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
            name_input.send_keys("ikariamforest@gmail.com")

            passwd_input = self._driver.find_element_by_name("session[password]")
            passwd_input.clear()
            passwd_input.send_keys("diplomka2019")
            
            login_form = self._driver.find_element_by_xpath("//form[@class='r-13qz1uu']")
            login_form.submit()
            
       
        except NoSuchElementException:
            print("cant find input") #Load error or page was changed
            exit(0)
        
    def get_page(self,url):
       time.sleep(self._redirect_delay) #TODO test if it enough.... and try again? 
       return self._driver.get(url)

    def parse(self):
        self.get_page(self._endpoint)
        #time.sleep(5)
        data = self._driver.page_source
        regex = r"\"remote\":{\"settings\":.*\"fetchStatus\":\"loaded\"}"
        c_regex = re.compile(regex)
        data = c_regex.findall( data)
        self._data = json.loads(data[0][9:])["settings"]
        self._driver.close() 

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
 
    def login(self,name,passwd):
        HOMEPAGE_URL = 'https://www.linkedin.com'
        LOGIN_URL = 'https://www.linkedin.com/uas/login-submit'

        html = self.__session.get(self._url).content
        soup = BeautifulSoup(html, "html.parser")
        csrf = soup.find('input', {'name': 'loginCsrfParam'}).get('value')

        login_information = {
            'session_key': "fitvut@seznam.cz",
            'session_password': "diplomka2019",
            'loginCsrfParam': csrf,
            'trk': 'guest_homepage-basic_sign-in-submit'
        }

        self.__session.post(self._login, data=login_information)
   
    def use_selenium(self,url,cookies):
        self._driver = webdriver.Firefox()
        self._driver.get(self._url)
        for c in cookies :
            self._driver.add_cookie({'name': c.name, 'value': c.value, 'path': c.path, 'expiry': c.expires})
        time.sleep(2)
        self._driver.get(url)
        time.sleep(1)
        return self._driver.page_source


    def parse(self):
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
            print("timeout")
        # set up credentials into google form
        name_input = self._driver.find_element_by_xpath('//*[@id="identifierId"]')
        name_input.clear()
        name_input.send_keys("fitvut2019")

        next_page = self._driver.find_element_by_xpath('//*[@id="identifierNext"]')
        next_page.click()
       
        try: 
            WebDriverWait(self._driver,self._wait).until(EC.presence_of_element_located((By.XPATH,'//*[@id="passwordNext"]')))
        except TimeoutException:
            print("timeout")

        passwd_input = self._driver.find_element_by_xpath('//*[@id="password"]/div[1]/div/div[1]/input')
        passwd_input.clear()
        passwd_input.send_keys("diplomka2019")

        next_page = self._driver.find_element_by_xpath('//*[@id="passwordNext"]')
        next_page.click()

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
            self._data = Constants.cz_to_en_dict_translate(self._data)

        self._driver.close()


if __name__ == '__main__':
    name = None
    while 1:
        print("Interni - I | Externi - E | Quit - Q")
        mode = input(">")
        if mode == "Interni" or mode == "I" or mode == "interni":
            print("Podporovane site: Facebook - F | Twitter - T | LinkedIn - L | Google - G ")
            network = input(">")
            if network == "Facebook" or network == "F" or network == "facebook":
                nt = Facebook()
#                nt.import_settings_yaml("facebook.yaml")

                login = FacebookLogin()
            elif network == "Twitter" or network == "T" or network == "twitter":
                nt = Twitter()
 #               nt.import_settings_yaml("twitter.yaml")

                login = TwitterLogin()
            elif network == "Google" or network == "G" or network == "google":
                nt = Google()
  #              nt.import_settings_yaml("google.yaml")

                login = GoogleLogin()
            elif network == "LinkedIn" or network == "L" or network == "linkedin":
                nt = LinkedIn()
   #             nt.import_settings_yaml("linkedin.yaml")

                login = LinkedInLogin()

            print("Download data from web - D | Load from local - L")
            local = input(">")
            if local == "D":
                print ("downloading data from "+nt._name)
                try:
                    login.login("","")
                except (ElementNotInteractableException, ElementClickInterceptedException) as e:
                    login._driver.close()
                    login.login("","")
                try:
                    login.parse()
                except (ElementNotInteractableException, ElementClickInterceptedException) as e:
                    login.parse()
            else:
                path = input("data path: ")
                login.load_data(path)
            
            while 1:
                print("Model: Weight&visibility - WV | M-PIDX - MP  | W-PIDX - WP  | C-PIDX - CP || Store_data - S")

                evaluator = Evaluator(osn=nt,data=login.get_data())
                model = input(">")
                if model == "Weight&visibility" or model == "WV":
                    evaluator.change_model(Weight_visibility_model())
                    break
                elif model == "M-PIDX" or model == "MP":
                    evaluator.change_model(M_PIDX())
                    break
                elif model == "W-PIDX" or model == "WP":
                    evaluator.change_model(W_PIDX())
                    break
                elif model == "C-PIDX" or model == "CP":
                    evaluator.change_model(C_PIDX())
                    break
                elif model == "S":
                    path = input("set path: ")
                    login.store_data(path)
                
       
            
            advice = evaluator.advice()
            while 1:
                print("Evaluate - E | Get advice - A | Back - B | Quit - Q")

                action = input(">")
                if action == "Evaluate" or action == "E":
                    print("Your privacy score: "+str(evaluator.apply_model()))
                elif action == "Advise" or action == "A":
                    print("Try to change: " +next(advice))
                elif action == "Back" or action == "B":
                    break
                elif action == "Quit" or action == "Q":
                    exit(0)

        elif mode == "Quit" or mode == "Q":
            exit(0)

        else:
            pass
    exit(0)
    
    evaluator = Evaluator(C_PIDX(),fb,fb_data.get_data())
    print (evaluator.apply_model())
    mygen = evaluator.advice()
    print (next(mygen))
    print (next(mygen))

    evaluator.change_model(M_PIDX())
    print(evaluator.apply_model())
    evaluator.change_model(W_PIDX())
    print(evaluator.apply_model())
    evaluator.change_model(Weight_visibility_model())
    print(evaluator.apply_model())
    


    """
    test = GoogleLogin()
    try:
        test.login("y","Y")
    except (ElementNotInteractableException, ElementClickInterceptedException) as e:
        test.login("y","Y")
    try:
        test.parse()
    except (ElementNotInteractableException, ElementClickInterceptedException) as e:
        test.parse()
    """
    #test = LoginHandle()
    #test.load_data("facebook_data.json")
    
   # print(test.get_data())

    #ext = Extractor()
    #ext.add_social_network("facebook","jmeno","heslo")
    #data = list(ext.run())
    #mymodel = Weight_visibility_model(data[0][0],Constants.get_profil(),Constants.get_evaluation())
    #print (mymodel.evaluate(operator.mul))

    #myExtractor = Extractor()
    #myExtractor.add_social_network(name = "facebook",file_name="facebook_data.json")
   # myExtractor.add_social_network(name = "facebook",username="test",password="test")
    #extractor_data = list(myExtractor.run())[0][0]
    
    #myEvaluator = Evaluator(Weight_visibility_model(),extractor_data,Constants.get_facebook_profil(),Constants.get_facebook_evaluation())
    #print(myEvaluator.apply_model())
    #my_gen = myEvaluator.advise_settings()
    
    #print(next(my_gen))
    #print(next(my_gen))
   # print(next(my_gen))

    #for key,value in Constants.FacebookWeights.items():
    #    print (key+":"+str(value))
    #print("--------------------------------")

    #for key,value in collections.OrderedDict(sorted(Constants.FacebookWeights.items(), key=lambda x: x[1], reverse=True)).items():
