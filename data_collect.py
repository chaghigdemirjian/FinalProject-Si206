# from create_dbs import *
import requests
from bs4 import BeautifulSoup
import json
from requests_oauthlib import OAuth2Session
import secrets
import sqlite3
import plotly.plotly as py
import plotly.graph_objs as go

GOOGLE_CACHE_FILE = "google_info"
YELP_CACHE_FILE = "yelp_info"
DBNAME = 'ratings.db'
GOOGLE_TBL = 'Google'
YELP_TBL = 'Yelp'


####Action Items
 #Type / keyword (what if you want to search a bar? in that case, you would only need type = bar). Do some research on how search engines are responding

#analysis functions: user enteres city (STATE) and restaurant type
    #what typs of analysis will you provide?
#plotly

def get_google_data(city, state, keyword): #insert city object in here? - actually not sure how objects would be useful
    place = str(city + ", " + state) #need to ensure a specific format for place #ask for city and state two letter abbreviation
    keyword = keyword
    key = str(place + ", " +  keyword)
    # key = str(place + ", " + type + ", " + keyword)
    cache_try = get_cached_data(key, GOOGLE_CACHE_FILE)

    if cache_try == None:
        print("requesting new data")

        G1_baseurl = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        parameters = {'key':secrets.google_places_key, 'query' : place} #change to text
        resp1 = requests.get(G1_baseurl, parameters).text
        location = json.loads(resp1)
        Lat = (location['results'][0]['geometry']['location']['lat'])
        Long = (location['results'][0]['geometry']['location']['lng'])
        location = str(Lat) + "," + str(Long)


        G2_baseurl = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        parameters = {'key':'AIzaSyCA_H7Ht8GzI2RgYfZJeyPLz8O8c0soCig', 'location': location, 'radius': 40000, 'type':'restaurant', 'keyword':keyword}
        resp2 = requests.get(G2_baseurl, parameters).text
        results = json.loads(resp2)
        results = results["results"]
        restaurant_by_city = {}
        restaurant_dict_list =  []
        restaurant_dict = {}
        for i in results:
            restaurant_dict = {'city':city, 'state':state,'type':type,'keyword':keyword,'name':i['name'],'rating':i['rating']}
            # restaurant_dict = {'city':place.split()[0], 'state':place.split()[1],'type':type,'keyword':keyword,'name':i['name'],'lat':round(i['geometry']['location']['lat'],1), 'long': round(i['geometry']['location']['lng'],1), 'rating':i['rating']}
            restaurant_dict_list.append(restaurant_dict)
        restaurant_by_city[key] = restaurant_dict_list
        cache_this(key,restaurant_by_city, GOOGLE_CACHE_FILE)
        Update_table(restaurant_by_city[key], GOOGLE_TBL)

        return None

    # else:
    #     print("THIS DATA IS ALREADY IN CACHE SO IT SHOULD BE IN DATABSE")
    #     ####MAYBE DELETE THE ELSE PART

# Authorization: Basic YWxhZGRpbjpvcGVuc2VzYW1l

#scrape yelp - input place, type, keyword, in search request (place ex. = Ann Arbor. MI)
#get name, ratings for each place
#crawl to the next poge (like UMSI) to get the next page info
#create dict and cache and call update database


#insert into this the names of retaurants found by google in specific location to make API calls
#from Yelp API calls, see what matches names from google calls, and use those to populate database
def get_yelp_data(city, state, keyword):
    location = str(city + ", " + state) #need to ensure a specific format for place #ask for city and state two letter abbreviation
    keyword = keyword
    term = str(keyword + ", restaurant")
    key = str(location + ", " +  keyword) ###could make all keys lowercase
    # key = str(place + ", " + type + ", " + keyword)


    Y1_baseurl = 'https://api.yelp.com/v3/businesses/search'
    headers = {'Authorization': "Bearer JLoDNWdd_n4NzZbvZlueNFg5ucSuv7OCqTyb1_Q43O3U4pjQIuJoRqZgdgqo8oJkgusjeHmmuB3Y0__Vn4U9i4ljMB9_AAz8Q79KU_G1lTF-u4JMA7S5iMP_RxDNWnYx"}
    parameters = {'term': term, 'location': location, 'radius':40000}
    resp1 = requests.get(Y1_baseurl, headers = headers, params = parameters).text
    json_resp = json.loads(resp1)['businesses']
    restaurant_by_city = {}
    restaurant_dict_list =  []
    restaurant_dict = {}
    for i in json_resp:
        restaurant_dict = {'city':city, 'state':state,'type':'restaurant','keyword':keyword,'name':i['name'],'rating':i['rating']}
        restaurant_dict_list.append(restaurant_dict)
    restaurant_by_city[key] = restaurant_dict_list
    cache_this(key,restaurant_by_city, YELP_CACHE_FILE)
    Update_table(restaurant_by_city[key], YELP_TBL)


def cache_this(key, new_cache_content, file):
    try:
        print("caching new things")
        fw1 = open(file, "r")
        contents = fw1.read()
        contents_json = json.loads(contents)
        fw1.close()
        contents_json.update(new_cache_content)
        combined = json.dumps(contents_json)
        fw2 = open(file, "w")
        fw2.write(combined)
        fw2.close()

    except:
        print("exeption at caching new things")
        fw = open(file, "w")
        data = json.dumps(new_cache_content)
        fw.write(data)
        fw.close()


def get_cached_data(key, file):
    try:
        print("at cache try")
        fw = open(file, "r")
        contents = fw.read()
        contents_json = json.loads(contents)
        fw.close()
        if key in contents_json:
            return contents_json[key]
        else:
            return None
    except:
        print("exeption at cache try")
        return None


def create_db(DBNAME):
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except Error as e:
        print(e)

    query1 = 'DROP TABLE IF EXISTS "Google"'
    conn.execute(query1)
    conn.commit()

    query2 = '''
        CREATE TABLE Google (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'City' TEXT NOT NULL,
            'State' TEXT NOT NULL,
            'Type' TEXT NOT NULL,
            'Keyword' TEXT NOT NULL,
            'Name' TEXT NOT NULL,
            'Rating' FLOAT NOT NULL
            );
    '''
    cur.execute(query2)
    conn.commit()

    query1 = 'DROP TABLE IF EXISTS "Yelp"'
    conn.execute(query1)
    conn.commit()

    query2 = '''
        CREATE TABLE Yelp (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'City' TEXT NOT NULL,
            'State' TEXT NOT NULL,
            'Type' TEXT NOT NULL,
            'Keyword' TEXT NOT NULL,
            'Name' TEXT NOT NULL,
            'Rating' FLOAT NOT NULL
            );
    '''
    cur.execute(query2)
    conn.commit()
    conn.close()


def populate_tables(): #(takes list of dictionaries) (without the key- because this will populate per key)

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    fw = open(GOOGLE_CACHE_FILE,"r")
    contents = fw.read()
    contents_json = json.loads(contents)
    fw.close()

    for x in contents_json:
        for c in contents_json[x]:
            City = c['city']
            State = c['state']
            Type = c['type']
            Keyword = c['keyword']
            Name = c['name']
            Rating = c['rating']

            query = '''INSERT INTO Google Values (?,?,?,?,?,?,?)
            '''
            params = (None, City, State, Type, Keyword, Name, Rating)
            conn.execute(query, params)
            conn.commit()

     ##NEED TO REMOVE THIS LATER


    fw = open(YELP_CACHE_FILE, "r")
    contents = fw.read()
    contents_json = json.loads(contents)
    fw.close()

    for x in contents_json:
        for c in contents_json[x]:
            City = c['city']
            State = c['state']
            Type = c['type']
            Keyword = c['keyword']
            Name = c['name']
            Rating = c['rating']

            query = '''INSERT INTO Yelp Values (?,?,?,?,?,?,?)
            '''
            params = (None, City, State, Type, Keyword, Name, Rating)
            conn.execute(query, params)
            conn.commit()

    conn.close()

#the above function exists so that if someone looks up a new location with a new type of place then we are able to update the database with that info and automatically call
#the SQL query on it without having to recreat new tables from our cahche file
def Update_table(new_content,TABLE_NAME):

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    for c in new_content:
        City = c['city']
        State = c['state']
        Type = c['type']
        Keyword = c['keyword']
        Name = c['name']
        Rating = c['rating']

        query = '''INSERT INTO {} Values (?,?,?,?,?,?,?)
        '''.format(TABLE_NAME)
        params = (None, City, State, Type, Keyword, Name, Rating)

        conn.execute(query, params)
        conn.commit()
    conn.close()

def data_calls(city, state, company, type1, type2, type3):
    if company.lower() == "google":
        get_google_data(city, state, type1)
        get_google_data(city, state, type2)
        get_google_data(city, state, type3)
    else:
        get_yelp_data(city, state, type1)
        get_yelp_data(city, state, type2)
        get_yelp_data(city, state, type3)


def interactive_stuff():
    create_db(DBNAME)
    print('Greetings! This program will allow you to explore 3 different types of restaurant options in a city and state of your choice!')
    print('*'*25)
    user_input = ""
    cuisine_list = ["Indian", "German", "Mexican", "Chinese", "Italian", "Japanese", "Greek", "French","Thai", "Pizza", "Mediterranean", "Spanish"]
    while user_input != "exit":
        user_input = input("Please enter a city and a two letter state abbreviation seperated with a comma, like such: 'Ann Arbor, MI'")
        if user_input.lower == "exit":
            print("bye!")
            exit()
        print("You entered: ", user_input)
        ##check if the state is in this list
        states1 = ['al', 'ak', 'as', "az", "ar", "ca", "co", "ct", "de", "dc", "fl"]
        states2 = ["ga", "gu", "hi", "id", "il", "in", "ia", "ks", "ky", "la", "me"]
        states3 = ["md", "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", "nh", "nj"]
        states4 = ["nm", "ny", "nc", "nd", "mp", "oh", "ok", "or", "pa", "pr", "ri"]
        states5 = ["sc", "sd", "tn", "tx", "ut", "vt", "vi", "va", "wa", "wv", "wi", "wy"]
        states = states1 + states2 + states3+ states4 + states5
        print("Please pick 3 restaurant types from the below list (separated by commas)")
        count = 1
        for i in cuisine_list:
            print(str(count) + ") " + i)
            count += 1
        rest_opt = input("Input three options here: ")
        ###parse user input
        company = input("Would you like us to see Google or Yelp data? (please type 'Google' or 'Yelp')")

        city = user_input.split(",")[0].strip()
        state = user_input.split(",")[1].strip()
        type1 = rest_opt.split(",")[0].strip()
        type2 = rest_opt.split(",")[1].strip()
        type3 = rest_opt.split(",")[2].strip()
        data_calls(city, state, company, type1, type2, type3)

        ###here, you would let them know what the options for them are and they can see those options

        output = top_in_cat_query("Ann Arbor", "MI", "Indian", "Yelp", 5)
        for i in output:
            print(str(i) + ") " + str(output[i]))



def quantity_query(city, state, type1, type2, type3, table):

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    query = '''
        SELECT Keyword, count(*) FROM "{}" as T
        WHERE T.City == '{}' AND  T.State == '{}'
        AND T.Keyword in ('{}', '{}', '{}')
        group by Keyword
        order by count(*) DESC
    '''.format(table, city, state, type1, type2, type3)

    print(query)
    output = cur.execute(query).fetchall()
    for row in output:
        print(row)

def average_rating_query(city, state, type1, type2, type3, table):

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    query = '''
        SELECT Keyword, Round(AVG(Rating),1) FROM "{}" as T
        WHERE T.City == '{}' AND  T.State == '{}'
        AND T.Keyword in ('{}', '{}', '{}')
        group by Keyword
        order by Round(AVG(Rating),1) DESC
    '''.format(table, city, state, type1, type2, type3)

    print(query)
    output = cur.execute(query).fetchall()
    for row in output:
        print(row)

def top_in_cat_query(city, state,type, table, limit):
###Add functionality for top # number or bottom # number
###or just keep it the way it is?
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    query = '''
        SELECT Name FROM "{}" as T
        WHERE T.City == '{}' AND  T.State == '{}'
        AND T.Keyword in ('{}')
        order by Rating DESC
        limit {}
    '''.format(table, city, state, type, limit)

    output = cur.execute(query).fetchall()
    count = 1
    diction = {}
    list = []
    for row in output:
        # print(str(count) + ") " + str(row[0]))
        diction[count] = row[0]
        list.append(diction)
        count += 1
    return(diction)

def specific_rest_rating(city, state, type, name, table):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    query = '''
        SELECT Name, Rating FROM "{}" as T
        WHERE T.City == '{}' AND  T.State == '{}'
        AND T.Keyword in ('{}')
        AND T.Name in ('{}')
    '''.format(table, city, state, type, name)

    output = cur.execute(query).fetchall()
    for x in output:
        print(str(x[0]) + ": " + str(x[1]))


def plot_number():

    trace0 = go.Scatter(
        x=["Indian", "Mediterranean", "Mexican"],
        y=[10, 15, 13]
    )
    trace1 = go.Scatter(
        x=[1, 2, 3, 4],
        y=[16, 5, 11, 9]
    )
    data = go.Data([trace0, trace1])

    py.plot(data, filename = 'basic-line')

if __name__ == "__main__":
    # create_db(DBNAME)
    get_google_data("New York, NY", 'restaurant', "mexican")
    # get_yelp_data("Omaha, NE", 'restaurant', "mexican")
    # populate_tables()
    # plot_number()
    # quantity_query("Ann Arbor", "MI", "Indian", "German", "Mexican", "Yelp")
    # average_rating_query("Ann Arbor", "MI", "Indian", "German", "Mexican", "Yelp")
    # specific_rest_rating("Ann Arbor", "MI", "Indian", "Madras Masala", 'Yelp')

    # interactive_stuff()
    ##need to add except statements here in case there isn't any data in cache file


    # interactive_stuff()
    # get_google_data("New York, NY", 'restaurant', "mexican")
    # get_yelp_data("New York, NY", 'restaurant', "indian")
