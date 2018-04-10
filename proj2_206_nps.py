## proj_nps.py
## Skeleton for Project 2, Winter 2018
## ~~~ modify this file, but don't rename it ~~~

#Google API Key: AIzaSyCA_H7Ht8GzI2RgYfZJeyPLz8O8c0soCig

import requests
from bs4 import BeautifulSoup
import json
from requests_oauthlib import OAuth1Session
import secrets
import operator

STATE_FILE_NAME = "state_urls"
SITES_FILE_NAME = "site_data"
NEARBY_PLACES_FILE = "nearby_places"
SITE_TWEETS = "tweets_by_site"
nps_baseurl = "https://www.nps.gov"


class NationalSite:
    #initializes national sites returned by function get_sites_for_state with basic info
    def __init__(self, type_ = None , name = None, desc = None, url=None, street = None, city = None, state = None, zip_code = None ):

            self.type = type_
            self.name = name
            self.description = desc
            self.url = url
            self.address_street = street
            self.address_city = city
            self.address_state = state
            self.address_zip = zip_code

    def __str__(self):
        statement = str(self.name) + " (" + str(self.type) + "): " + str(self.address_street) + ", " + str(self.address_city)
        statement += ", " + str(self.address_state) + " " + str(self.address_zip)
        return statement


class NearbyPlace():
    #initiatlizes nearby places to national sites returned by get_nearby_places_for_site
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class Tweet:
    #initializes tweets returned by get_tweets_for_site
    def __init__(self, tweet_dict, is_retweet = False, screen_name = None, retweet_count = None, favorites = None, popularity_score = None, text = None, date = None, id = None):

        self.screen_name = tweet_dict['screen_name']
        self.retweet_count = tweet_dict['retweets']
        self.favorites = tweet_dict['favorites']
        self.popularity_score = tweet_dict['pop_score']
        self.text = tweet_dict['text']
        self.date = tweet_dict['tweet_date']
        self.id = tweet_dict['id']
        self.is_retweet = tweet_dict['is_retweet'] #becuase i've already filtered out retweets before placinag into json_dict

    #allows us to print tweets in a nice format
    def __str__(self):
        statement = "@" + self.screen_name + ":" + self.text
        statement += "\n" + "[retweeted " + str(self.retweet_count) + " times]"
        statement += "\n" + "[favorited " + str(self.favorites) + " times]"
        statement += "\n" + "[popularity " + str(self.popularity_score) + "]"
        statement += "\n" + "[tweeted on " + str(self.date) + " | " + "id:" + str(self.id) + "]"
        return statement

#this function crawls the main nps page to get the right site_url
#that corresponds to that page of each state that is being looked up by
#get_sites_for_state and caching it in state_url file with the key being state_abbr
def get_state_url(state_abbr):
    try:
        state_url_cache = open(STATE_FILE_NAME, 'r')
        state_url_contents = state_url_cache.read()
        state_urls_json = json.loads(state_url_contents)
        state_url_cache.close()
        return(state_urls_json[str(state_abbr)])
    except:
        state_urls = {}
        nps_baseurl = "https://www.nps.gov"
        initial_ext = "/index.htm"
        resp1 = requests.get(nps_baseurl  + initial_ext).text
        page_soup = BeautifulSoup(resp1, "html.parser")
        state_search = page_soup.find('div', class_ = "SearchBar-keywordSearch input-group input-group-lg")
        state_search_lists = state_search.find_all('li')
        for i in state_search_lists:
            state_urls[i.find('a')['href'][7:9]] = i.find('a')['href']
        state_urls_json = json.dumps(state_urls)
        fw = open(STATE_FILE_NAME, 'w')
        fw.write(state_urls_json)
        fw.close()
        return(state_urls[str(state_abbr)])

## Must return the list of NationalSites for the specified state
## param: the 2-letter state abbreviation, lowercase
##        (OK to make it work for uppercase too)
## returns: all of the NationalSites
##        (e.g., National Parks, National Heritage Sites, etc.) that are listed
##        for the state at nps.gov

#this function crawls the web for the specific state (state_abbr) and finds
#different details of that site. Passes it to the site class to get initialized
#then is caches the info per site in a cache file and returns a list of site objects
def get_sites_for_state(state_abbr):
    specific_state_url = nps_baseurl + get_state_url(state_abbr)
    i = 1
    try:
        sites_cache = open(SITES_FILE_NAME, 'r')
        sites_contents = sites_cache.read()
        sites_json = json.loads(sites_contents)
        sites_cache.close()
        site_list = sites_json[state_abbr]
        site_object_list = []
        for x in site_list:
            site = NationalSite(x['type'],x['name'],x['desc'],x['url'],x['street'],x['city'],x['state'],x['zip'])
            site_object_list.append(site)
        return site_object_list
    except:
        site_list = []
        site_info = []
        state_site_info = {}
        print("requesting site data on specific state")
        resp = requests.get(specific_state_url).text
        page_soup = BeautifulSoup(resp, "html.parser")
        site_search = page_soup.find('div', id = "parkListResultsArea")
        site_search_lists = site_search.find_all('li')
        for li in site_search_lists:
            site_type = li.find('h2')
            site_name = li.find('h3')
            site_desc = li.find('div')
            site_desc = li.find('p')
            site_desc = str(site_desc)
            site_desc = site_desc.replace("\n", "")
            site_desc = site_desc.replace("<p>", "")
            site_url = li.find('a')['href']
            site_full_url = nps_baseurl + site_url
            if site_type and site_name is not None: #might need a better check for this
                site_list.append({'url': site_full_url,'name': site_name.text, 'type' : site_type.text, 'desc': site_desc})
        for x in site_list:
            url = x['url']
            resp3 = requests.get(url).text
            page_soup = BeautifulSoup(resp3, "html.parser")
            address_search = page_soup.find(class_ = "adr")
            street_addressA = address_search.find('span', itemprop = "streetAddress")
            if street_addressA is not None:
                street_addressF = street_addressA.text
                street_addressF = street_addressF.replace("\n", "")
            else:
                street_addressF = "NA"
            city = address_search.find(itemprop = "addressLocality").text
            state = address_search.find(itemprop = "addressRegion").text
            zip_code = address_search.find(itemprop = "postalCode").text
            zip_code = zip_code.replace(" ","")
            x['street'] = street_addressF
            x['city'] = city
            x['state'] = state
            x['zip'] = zip_code
        site_object_list = []
        for x in site_list:
            site = NationalSite(x['type'],x['name'],x['desc'],x['url'],x['street'],x['city'],x['state'],x['zip'])
            site_object_list.append(site)
        state_site_info[state_abbr] = site_list
        update_cache(SITES_FILE_NAME, state_site_info)
        return site_object_list

#this function allows us to update cache files that already have content in them
#so that we don't ovverride their existing content and simply update the file
def update_cache(file_name, new_content): #new content shouldnt be json
    try:
        fw = open(file_name,"r")
        file_contents = fw.read()
        file_contents2 = json.loads(file_contents)
        fw.close()
        file_contents2.update(new_content)
        contents_combined = json.dumps(file_contents2)
        fw = open(file_name,"w")
        fw.write(contents_combined)
        fw.close()
    except:
        new_content_json = json.dumps(new_content)
        fw = open(file_name,"w")
        fw.write(new_content_json)
        fw.close()
    return 0


## Must return the list of NearbyPlaces for the specified NationalSite
## param: a NationalSite object
## returns: a list of NearbyPlaces within 10km of the given site
##          if the site is not found by a Google Places search, this should
##          return an empty list

def get_nearby_places_for_site(site_object):
    site_object = site_object.name + " " + site_object.type

    try:
        fw = open(NEARBY_PLACES_FILE, "r")
        contents = fw.read()
        nearby_json_contents = json.loads(contents)
        fw.close()
        nearby_list = nearby_json_contents[site_object]
        nearby_object_list = []
        for x in nearby_list:
            place = NearbyPlace(x)
            nearby_object_list.append(place)
        return nearby_object_list


    except:
        G1_baseurl = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        parameters = {'key':secrets.google_places_key, 'query' : site_object} #change to text
        resp1 = requests.get(G1_baseurl, parameters).text
        location = json.loads(resp1)
        Lat = (location['results'][0]['geometry']['location']['lat'])
        Long = (location['results'][0]['geometry']['location']['lng'])
        location = str(Lat) + "," + str(Long)


        G2_baseurl = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        parameters = {'key':'AIzaSyCA_H7Ht8GzI2RgYfZJeyPLz8O8c0soCig', 'location': location, 'radius': 10000}
        resp2 = requests.get(G2_baseurl, parameters).text
        results = json.loads(resp2)
        nearby_places_by_site = {}
        nearby_places =  []
        nearby_place_cache = []
        for i in results['results']:
            nearby_place = NearbyPlace(str(i['name']))
            nearby_places.append(nearby_place)
            nearby_place_cache.append(i['name'])
        nearby_places_by_site[site_object] = nearby_place_cache #site object could be replaced by site name and type
        update_cache(NEARBY_PLACES_FILE, nearby_places_by_site)
        return nearby_places

## Must return the list of Tweets that mention the specified NationalSite
## param: a NationalSite object
## returns: a list of up to 10 Tweets, in descending order of "popularity"
def get_tweets_for_site(site_object):
    site_object = site_object.name + " " + site_object.type
    try:
        tweets = []
        tweet_objects = []
        fw = open(SITE_TWEETS, "r")
        contents = fw.read()
        json_contents = json.loads(contents)
        fw.close()
        tweets = json_contents[site_object]
        tweet_objects = []
        for i in tweets:
            tweet_object = Tweet(i) #you're passing in a specific tweet dictionary for 1 tweet and creating a tweet object
            tweet_objects.append(tweet_object)
        return tweet_objects

    except:
        client_key = secrets.twitter_api_key
        client_secret = secrets.twitter_api_secret

        resource_owner_key = secrets.twitter_access_token
        resource_owner_secret = secrets.twitter_access_token_secret

        protected_url = 'https://api.twitter.com/1.1/account/settings.json'

        oauth = OAuth1Session(client_key,
                                  client_secret=client_secret,
                                  resource_owner_key=resource_owner_key,
                                  resource_owner_secret=resource_owner_secret)

        protected_url = 'https://api.twitter.com/1.1/search/tweets.json'
        params = {'q': site_object, 'count' : 100}
        r = oauth.get(protected_url, params=params)
        json_format = json.loads(r.text)
        tweet_list = []
        tweet_dictionary_by_site = {} #this is for caching

        for i in json_format["statuses"]:
            if i["text"][0:2] == "RT":
                continue
            else:
                tweet_dictionary = {}
                tweet_populatiry_score = i["user"]["favourites_count"] * 3 + i["retweet_count"] * 2
                tweet_dictionary['screen_name'] = i["user"]["screen_name"]
                tweet_dictionary['id'] = i["id_str"]
                tweet_dictionary['tweet_date'] = i["created_at"]
                tweet_dictionary['retweets'] = i["retweet_count"]
                tweet_dictionary['is_retweet'] = i["retweeted"]
                tweet_dictionary['favorites'] = i["user"]["favourites_count"]
                tweet_dictionary['pop_score'] = tweet_populatiry_score
                tweet_dictionary['text'] = i["text"]
                tweet_list.append(tweet_dictionary)
        tweet_list = sorted(tweet_list, key=lambda k:k['pop_score'], reverse = True)
        if len(tweet_list) >= 10:
            tweet_dictionary_by_site[site_object] = tweet_list[0:10]
        elif len(tweet_list) == 0:
            print("There are no original tweets currently at this site")
        else:
            tweet_dictionary_by_site[site_object] = tweet_list
    update_cache(SITE_TWEETS,tweet_dictionary_by_site)
    tweet_obects = []
    for t in tweet_dictionary_by_site[site_object]:
        tweet_object = Tweet(t) #you're passing in a specific tweet dictionary for 1 tweet and creating a tweet object
        tweet_objects.append(tweet_object)
    return tweet_objects


if __name__ == "__main__":


    states1 = ['al', 'ak', 'as', "az", "ar", "ca", "co", "ct", "de", "dc", "fl"]
    states2 = ["ga", "gu", "hi", "id", "il", "in", "ia", "ks", "ky", "la", "me"]
    states3 = ["md", "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", "nh", "nj"]
    states4 = ["nm", "ny", "nc", "nd", "mp", "oh", "ok", "or", "pa", "pr", "ri"]
    states5 = ["sc", "sd", "tn", "tx", "ut", "vt", "vi", "va", "wa", "wv", "wi", "wy"]
    states = states1 + states2 + states3+ states4 + states5

    search_term = input("Enter a command or type help for options: ")
    while search_term.lower()[0:4] == "list":
        if search_term.lower()[-2:] in states:
            sites = get_sites_for_state(search_term.lower()[-2:])
            i = 1
            site_dict = {}
            for x in sites:
                print("(" + str(i) + ")", x)
                site_dict[i] = x
                i = i + 1
            result_num = len(site_dict)
        else:
            print("you did not enter a valid state abbreviation. Please re-run the program.")
            exit()

        search_term = input("Enter a command or type help for options: ")

        if search_term.isdigit():
             print("You only entered a digit. That is not a valid input. Try again!")
             exit()

        elif search_term.lower()[0:4] == "list":
            continue
        elif search_term.lower()[0:6] == "nearby" or search_term.lower()[0:6] == "tweets":

             if result_num > 9:
                 result_pick = int(search_term[-2:])
             else:
                 result_pick = int(search_term[-1:])
             if (result_pick >= 0) and (result_pick <= result_num):
                 site = site_dict[result_pick]
                 if search_term.lower()[0:6] == "nearby":
                     nearby_places = get_nearby_places_for_site(site)
                     n = 1
                     for y in nearby_places:
                         print("(" + str(n) + ")" , y)
                         site_dict[n] = y
                         n = n + 1
                 elif search_term.lower()[0:6] == "tweets":
                       site_tweets = get_tweets_for_site(site)
                       z = 0
                       for d in site_tweets:
                            print("------------------")
                            print("(" + str(z) + ")", d)
                            print("\n")
                            site_dict[z] = d
                            z = z + 1
             else:
                 print("invalid result digit input. please re-reun the program")
                 exit()
             search_term = input("you can now request a new list for sites, type exit or help: ")

    if search_term.lower() == "exit":
        print("Peace out. Come again.")
        exit()

    elif search_term.lower() == "":
        print("You did not enter anything. Please re-run the program with a valid entry.")
        exit()

    elif search_term.isdigit():
        print("You entered a number. This is not a valid commmand. Please re-run program.")
        exit()

    elif search_term.lower() == "help":
        statement1 = "list <stateabbr> : Available anytime lists all National Sites in a state. "
        statement1 += "Valid inputs: a two-letter state abbreviation."
        statement1 += "nearby <result_number>: Available only if there is an active result set."
        statement1 += "Lists all Places nearby a given result. Valid inputs: an integer 1-len(result_set_size)."
        statement1 += "\ntweets <result_number>: Available only if there is an active results set. "
        statement1 += "Lists up to 10 most popular tweets that mention the selected Site."
        statement1 += "\nexit: exits the program "
        statement1 += "help: lists available commands (these instructions)"
        statement1 += "\n***** please re-run the program for a new entry*****"
        statement1 += "\n bye bye!"
        print(statement1)

    else:
        print("Something went wront. Please re-run the program with a revised or different input")

    pass
