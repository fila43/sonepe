import requests
from bs4 import BeautifulSoup
import urllib.parse
import json
import operator

class LoginError(Exception):
    """Raised when failed login into Social network """
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
        "Zapnout historii polohy v mobilním zařízení?":"Turn on Location History for your mobile devices?"

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
    @staticmethod
    def cz_to_en_translate(self,word):
        return self.CzEnDict[word]

    @staticmethod
    def en_to_cz_translate(self,world):
        pass

    @staticmethod
    def is_english(word):
        return word == Constants.ENGLISH

class Model:
    def __init__(self,ext_data,profil,evaluation_array):
        self._ex_data = ext_data
        self._profil = profil
        self._eval_array = evaluation_array

    def evaluate(self):
        pass

    def update_profil(self,profil):
        """ profil holds weights"""
        self._profil = profil

class Weight_visibility_model(Model):
    def __init__(self,ext_data,profil,evaluation_array):
        super.__init(ext_data,profil,evaluation_array)

    def evaluate(self,operator):
        result = 0
        for key, value in self._ex_data:
            result = result + operator(self._profil[key], self._eval_array[value])
        return result
            



class LoginHandle:
    def __init__(self, name, passwd):
        self.name = name
        self.passwd = passwd
        self._data = dict()

    def login(self):
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


    def __init__(self, name, passwd):
        super().__init__(name, passwd)
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

    def login(self):
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
        language = settings[0].find("span", class_="fbSettingsListItemContent fcg").find("div", class_="_nlm fwb").string
        result = {}

        for item in self.__endpoints:
            data = self.__session.get(item).text
            soup = BeautifulSoup(data, 'html.parser')
      #      result[soup.find("span", class_="_c24")] = None
            settings = soup.findAll("a", class_="fbSettingsListLink clearfix pvm phs")
            for x in settings:
                result[x.find("span", class_="fbSettingsListItemContent fcg").find("div", class_="_nll").string] = \
                x.find("span", class_="fbSettingsListItemContent fcg").find("div", class_="_nlm fwb").string

        # page with location has different structure then others
        #data = self.__session.get(self._location_endpoint).text
        #soup = BeautifulSoup(data,'html.parser')
        #setting = soup.find("div", class_="_4-u3 _2ph-").find("span", class_="_c24").string
        #result[setting] = True


        # remove unusable settings with None value
        result = dict(filter(lambda a:a[1] is not None , result.items()))
        self._data = result

class TwitterLogin(LoginHandle):

    def __init__(self, name, passwd):
        super().__init__(name, passwd)
        proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

        username = "fila.konemet@gmail.com"
        password = "P5pv71ja&"
        # login url
        post = "https://twitter.com/sessions"
        url = "https://twitter.com"
        url_mobile = "https://mobile.twitter.com"

        data = {"session[username_or_email]": username,
                "session[password]": password,
                "redirect_after_login": "/",
                "remember_me": 1,
                "wfa":1}

        s = requests.Session()
        s.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Connection': 'close',
            "Accept-Language": "en-GB,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            'Upgrade-insecure-requests': '1',
            "User-Agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0",
            "DNT": "1"
        })

        r = s.get(url,proxies=proxies, verify=False)
        #print(s.cookies)
        
        s.headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer":"https://twitter.com/"
            })
        r = s.post(url_mobile+"/i/nojs_router?path=/",proxies=proxies,verify=False)
       # print(s.cookies)

        r = s.get(url_mobile,proxies=proxies,verify=False)
        #print(s.cookies)
        #print(r.content)


        #####

       # r = s.get(url,proxies=proxies, verify=False)
       # print(s.cookies)

        #  exit(0)
        #print(r.content)
        # get auth token
        soup = BeautifulSoup(r.content, "lxml")
        AUTH_TOKEN = soup.select_one("input[name=authenticity_token]")["value"]
        images = soup.findAll('img')
        MOBILE_TOKEN = 0
        for item in images:
            if item["src"][0:12] == "/i/anonymize":
                #MOBILE_TOKEN = item["src"][18:]
                MOBILE_TOKEN = item["src"]
        #print(urllib.parse.unquote(MOBILE_TOKEN))
        r = s.get(url_mobile+MOBILE_TOKEN,proxies=proxies,verify=False)
        print(s.cookies) 
        data["authenticity_token"] = AUTH_TOKEN
        
        r = s.post(url_mobile+"/sessions",proxies=proxies,data=data,verify=False)
        r = s.get(url_mobile,proxies=proxies,verify=False)
        r = s.get("https://twitter.com/settings/safety",proxies=proxies,verify=False)
        print (s.cookies)
        #print(r.content)
        # update data, post and you are logged in.
        #r = s.post(post, data=data,proxies=proxies, verify=False)
        #print(s.cookies)
      #  r = s.get("https://twitter.com", proxies=proxies, verify=False)
       # r = s.get("https://twitter.com", proxies=proxies, verify=False)

        #print(r.content)





if __name__ == '__main__':
    test = FacebookLogin("y","y")
    test.login()
    test.parse()
    test.store_data("facebook_data.json")
