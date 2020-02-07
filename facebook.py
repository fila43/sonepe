import requests
from bs4 import BeautifulSoup
import urllib.parse

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
        "Historie vaší polohy je zapnutá": "Your location history is on"

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


class LoginHandle:
    def __init__(self, name, passwd):
        self.name = name
        self.passwd = passwd

    def login(self):
        pass

    def parse(self):
        pass

class FacebookLogin(LoginHandle):


    def __init__(self, name, passwd):
        super().__init__(name, passwd)
        self.__language = "https://www.facebook.com/settings?tab=language"
        self.__endpoints = [
            "https://www.facebook.com/settings?tab=privacy",
            "https://www.facebook.com/settings?tab=timeline",
            "https://www.facebook.com/settings?tab=stories"
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
        data = self.__session.get(self._location_endpoint).text
        soup = BeautifulSoup(data,'html.parser')
        setting = soup.find("div", class_="_4-u3 _2ph-").find("span", class_="_c24").string
        result[setting] = True


        # remove unusable settings with None value
        result = dict(filter(lambda a:a[1] is not None or a[1] in self.__useful_values, result.items()))
        print(result)


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
        #print (s.cookies)
        s.cookies["ct0"] = "3af5e1e75d2184a323bdcd20edc1211b"
        s.cookies["gt"] = "1225352815297617926"
        r = s.get("https://twitter.com/settings/safety",proxies=proxies,verify=False)

        print(r.content)
        # update data, post and you are logged in.
        #r = s.post(post, data=data,proxies=proxies, verify=False)
        #print(s.cookies)
      #  r = s.get("https://twitter.com", proxies=proxies, verify=False)
       # r = s.get("https://twitter.com", proxies=proxies, verify=False)

        #print(r.content)





if __name__ == '__main__':
    test = TwitterLogin("y","y")
   # test.login()
    #test.parse()
