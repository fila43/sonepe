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
import time
import re

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
        "Jenom já":"Only me"

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

class Model:
    def __init__(self,ext_data=None,profil=None,evaluation_array=None):
        self._ex_data = ext_data
        self._profil = profil
        self._eval_array = evaluation_array
    
    def update_data(self,data):
        self._ex_data = data

    def update_evaluation(self,e):
        self._eval_array = e

    def evaluate(self):
        pass

    def update_profil(self,profil):
        """ profil holds weights"""
        self._profil = profil

class Weight_visibility_model(Model):
    def __init__(self,ext_data = None , profil = None , evaluation_array = None):
        super().__init__(ext_data,profil,evaluation_array)

    def evaluate(self,operator):
        if self._ex_data is None or self._profil is None or self._eval_array is None:
            return -1
        
        result = 0
        for key, value in self._ex_data.items():
            result = result + operator(self._profil[key], self._eval_array[value])
        return result
            
class PIDX(Model):
    def __init__(self, data = None, pif = None, separation = None):
        pass

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
    def __init__(self, data = None, pif = None, separation = None):
        super().__init__(data = data, pif = pif, separation = separation)
        
    def privacy_function(self):
        pass

class M_PIDX(PIDX):
    def __init__(self, data = None, pif = None, separation = None):
        super().__init__(data = data, pif = pif, separation = separation)

    def evaluate(self):
        #TODO maximum function
        pass

class C_PIDX(W_PIDX,M_PIDX):
    def __init__(self, data = None, pif = None, separation = None):
        super(W_PIDX, self).__init__(data = data, pif = pif, separation = separation)

    def evaluate(self):
        # TODO only build C-pidx from M-pidx and w-pidx
        pass



class Evaluator:
    def __init__(self,model,data,weights,evaluation):
        self._model = model
        self._weights = weights
        self._evaluation = evaluation
        self._data = data

        model.update_data(data)
        model.update_evaluation(evaluation)
        model.update_profil(weights)

    def apply_model(self):
        return self._model.evaluate(operator.mul) #operator only for easy model

    def change_model(self,new_model):
        self._model = new_model
        self._model.update_data(self._data)
        self._model.update_evaluation(self._evaluation) 
        self._model.update_profil(self._weights)

    def advise_settings(self):
        for key,value in collections.OrderedDict(sorted(Constants.FacebookWeights.items(), key=lambda x: x[1], reverse=True)).items():
            if Constants.get_facebook_evaluation()[self._data[key]] >= 1:
                yield key


class Extractor:
    def __init__(self):
        """acc dict contains all set up accounts for test"""
        self._acc = {}

    def add_social_network(self,name = None ,username = None,password = None,file_name = None):
        if name ==  "facebook":
            if file_name is None:
                self._acc[name] = FacebookLogin()
                self._acc[name].login(username,password)
                self._acc[name].parse()
            else:
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
        self._driver = webdriver.Firefox() #TODO need to be setup gecko
        self._endpoint = "https://twitter.com/settings/account"

    def login(self,name,passwd):
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
            print(str(item[35:])+str(Constants.LinkedInEvaluation[value]))
 


if __name__ == '__main__':
    test = LinkedInLogin()
    test.login("y","Y")
    test.parse()

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
