import sqlite3
import csv
import json

# proj3_choc.py
# You can change anything in this file you want as long as you pass the tests
# and meet the project requirements! You will need to implement several new
# functions.

# Part 1: Read data from CSV and JSON into a new database called choc.db
DBNAME = 'choc.db'
BARSCSV = 'flavors_of_cacao_cleaned.csv'
COUNTRIESJSON = 'countries.json'

def create_db(DBNAME):
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except Error as e:
        print(e)

    query1 = 'DROP TABLE IF EXISTS "Countries"'
    conn.execute(query1)
    conn.commit()

    query2 = '''
        CREATE TABLE Countries (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Alpha2' TEXT NOT NULL,
            'Alpha3' TEXT NOT NULL,
            'EnglishName' TEXT NOT NULL,
            'Region' TEXT NOT NULL,
            'Subregion' TEXT NOT NULL,
            'Population' INTEGER NOT NULL,
            'Area' REAL
            );
    '''
    cur.execute(query2)
    conn.commit()

    query3 = 'DROP TABLE IF EXISTS "Bars"'
    conn.execute(query3)
    conn.commit()


    query4 = '''
        CREATE TABLE Bars (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Company' TEXT NOT NULL,
            'SpecificBeanBarName' TEXT NOT NULL,
            'Ref' TEXT NOT NULL,
            'ReviewDate' TEXT NOT NULL,
            'CocoaPercent' REAL NOT NULL,
            'CompanyLocation' TEXT NOT NULL,
            'CompanyLocationId' INTEGER NOT NULL,
            'Rating' REAL NOT NULL,
            'BeanType' TEXT NOT NULL,
            'BroadBeanOrigin' TEXT NOT NULL,
            'BroadBeanOriginId' INTEGER NOT NULL
            );
        '''

        ## Foreign Key (CompanyLocationId) References Countries (Id),
        # Foreign Key (BroadBeanOriginId) References Countries (Id)
    cur.execute(query4)
    conn.commit()
    conn.close()

def populate_countries(DBNAME):
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except Error as e:
        print(e)
    country_info = open(COUNTRIESJSON, 'r', encoding="utf8")
    countries_data = json.loads(country_info.read())
    country_info.close()
    for c in countries_data:
        query1 = '''
            INSERT INTO Countries (Id, Alpha2, Alpha3, EnglishName, Region, Subregion, Population, Area)
            VALUES (?,?,?,?,?,?,?,?)
        '''
        data = (None, c['alpha2Code'],c['alpha3Code'],c['name'], c['region'], c['subregion'], c['population'], c['area'] )
        cur.execute(query1, data)
        conn.commit()

def populate_bars(DBNAME):
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except Error as e:
        print(e)

    with open(BARSCSV) as csvData:
        clean_data = csv.reader(csvData)
        next(clean_data, None)
        countryNameId = cur.execute('SELECT Id, EnglishName from Countries').fetchall()
        for stuff in clean_data:
                for x in countryNameId:
                    if stuff[5] == x[1]:
                        countryId = x[0]
                    if stuff[-1] == x[1]:
                        BroadBeanOriginId = x[0]
                data = (None, stuff[0],stuff[1], stuff[2], stuff[3], stuff[4], stuff[5], countryId, stuff[6], stuff[7], stuff[8], BroadBeanOriginId)
                query1 = '''
                    INSERT INTO "Bars" VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                '''
                cur.execute(query1, data)
        conn.commit()
        conn.close()

# Part 2: Implement logic to process user commands

def bars_query(user_input):

    limit = ""

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    if "=" in user_input:
        source_sell = user_input.split("=")[1].split()[0]
        limit = user_input.split("=")[-1]
    query1 = ''' SELECT SpecificBeanBarName, Company, CompanyLocation, Rating, CocoaPercent, BroadBeanOrigin FROM Bars '''
    query2 = '''JOIN Countries on Countries.Id = Bars.CompanyLocationId '''
    if "sellcountry" in user_input or "sourcecountry" in user_input:
        query2 = '''JOIN Countries on Countries.Id = Bars.CompanyLocationId WHERE Countries.Alpha2 = '{}' '''.format(source_sell)
    elif "sellregion" in user_input or "sourceregion" in user_input:
        query2 = '''JOIN Countries on Countries.Id = Bars.CompanyLocationId WHERE Countries.Region = '{}' '''.format(source_sell)
    if "cocoa" in user_input:
        query3 = "Order by CocoaPercent "
    else:
        query3 = "Order by Rating "
    if "bottom" in user_input or "top" in user_input:

        if "bottom" in user_input:
            print("who")
            query4 = "ASC Limit {}".format(limit)
        else:

            query4 = "DESC Limit {}".format(limit)
    else:
        query4 = "DESC limit 10"
    query = query1 + query2 + query3 + query4
    # print(query)
    output = cur.execute(query).fetchall()
    return output

def companies_query(user_input):

    limit = ""

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    if "=" in user_input:
        region_country = user_input.split("=")[1].split()[0]
        limit = user_input.split("=")[-1]
    query1 = ''' SELECT Company, CompanyLocation, ROUND(Avg(Rating),1) FROM Bars '''
    query2 = ""
    if "country" in user_input:
        query2 = '''JOIN Countries on Countries.Id = Bars.CompanyLocationId WHERE Countries.Alpha2 = '{}' '''.format(region_country)
        # query2 = '''JOIN Countries on Countries.EnglishName = Bars.CompanyLocation WHERE Countries.Alpha2 = '{}' '''.format(region_country)
    elif "region" in user_input:
        query2 = '''JOIN Countries on Countries.Id = Bars.CompanyLocationId WHERE Countries.Region = '{}' '''.format(region_country)
        # query2 = '''JOIN Countries on Countries.EnglishName = Bars.CompanyLocation WHERE Countries.Region = '{}' '''.format(region_country)
    if "cocoa" in user_input:
        query1 = ''' SELECT Company, CompanyLocation, ROUND(Avg(CocoaPercent),0) FROM Bars '''
        query3 = '''Group by Company, CompanyLocation HAVING count(SpecificBeanBarName) > 4 '''
        query4 = '''Order by AVG(CocoaPercent) '''
    elif "bars_sold" in user_input:
        query1 = ''' SELECT Company, CompanyLocation, count(SpecificBeanBarName) FROM Bars '''
        query3 = '''Group by Company, CompanyLocation HAVING count(SpecificBeanBarName) > 4 '''
        query4 = '''Order by count(SpecificBeanBarName) '''
    else:
        query3 = '''Group by Company, CompanyLocation HAVING count(SpecificBeanBarName) > 4 '''
        query4 = '''Order by AVG(Rating) '''
    if "bottom" in user_input or "top" in user_input:
        if "bottom" in user_input:
            query5= "Limit {}".format(limit)
        else:
            query5= "DESC Limit {}".format(limit)
    else:
        query5 = "DESC limit 10"

    query = query1 + query2 + query3 + query4 + query5
    # print(query)
    output = cur.execute(query).fetchall()
    return output

def countries_query(user_input):

    limit = ""

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    if "=" in user_input:
        region_country = user_input.split("=")[1].split()[0]
        limit = user_input.split("=")[-1]
    query1 = ''' SELECT CompanyLocation, Region, '''
    query2 = '''JOIN Countries on Countries.Id = Bars.CompanyLocationId '''
    query3 = ""
    if "region" in user_input:
        # query += '''JOIN Countries on Countries.id = Bars.CompanyLocationId WHERE Countries.Region = '{}' '''.format(source_sell)
        query3 = '''WHERE Countries.Region = '{}' '''.format(region_country)
    if "sources" in user_input:
        query1 = ''' SELECT BroadBeanOrigin, Region, '''
        query2 = '''JOIN Countries on Countries.Id = Bars.BroadBeanOriginId '''
    if "cocoa" in user_input:
        query1 += '''ROUND(AVG(CocoaPercent), 1) FROM Bars '''
        if "sources" in user_input:
            query4 = '''Group by BroadBeanOrigin, Region HAVING count(SpecificBeanBarName) > 4 '''
        else:
            query4 = '''Group by CompanyLocation, Region HAVING count(SpecificBeanBarName) > 4 '''
        query5 = '''Order by AVG(CocoaPercent) '''
    elif "bars_sold" in user_input:
        query1 += '''count(SpecificBeanBarName) FROM Bars '''
        if "sources" in user_input:
            query4 = '''Group by BroadBeanOrigin, Region HAVING count(SpecificBeanBarName) > 4 '''
        else:
            query4 = '''Group by CompanyLocation, Region HAVING count(SpecificBeanBarName) > 4 '''
        query5 = '''Order by count(SpecificBeanBarName) '''
    else:
        query1 += '''ROUND(AVG(Rating),1) FROM Bars '''
        if "sources" in user_input:
            query4 = '''Group by BroadBeanOrigin, Region HAVING count(SpecificBeanBarName) > 4 '''
        else:
            query4 = '''Group by CompanyLocation, Region HAVING count(SpecificBeanBarName) > 4 '''
        query5 = '''Order by AVG(Rating) '''
    if "bottom" in user_input or "top" in user_input:
        if "bottom" in user_input:
            query6= "Limit {}".format(limit)
        else:
            query6= "DESC Limit {}".format(limit)
    else:
        query6 = "DESC limit 10"

    query = query1 + query2 + query3 + query4 + query5 + query6
    # print(query)
    output = cur.execute(query).fetchall()
    return output

def regions_query(user_input):

    limit = ""

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    if "=" in user_input:
        region_country = user_input.split("=")[1].split()[0]
        limit = user_input.split("=")[-1]
    query1 = ''' SELECT Region, '''
    query2 = '''JOIN Countries on Countries.Id = Bars.CompanyLocationId '''

    if "sources" in user_input:
        query2 = '''JOIN Countries on Countries.Id = Bars.BroadBeanOriginId '''
    if "cocoa" in user_input:
        query1 += '''CocoaPercent FROM Bars '''
        query3 = '''Group by Region HAVING count(SpecificBeanBarName) > 4 '''
        query4 = '''Order by CocoaPercent '''
    elif "bars_sold" in user_input:
        query1 += '''count(specificBeanBarName) FROM Bars '''
        query3 = '''Group by Region HAVING count(SpecificBeanBarName) > 4 '''
        query4 = '''Order by count(SpecificBeanBarName) '''
    else:
        query1 += '''ROUND(AVG(Rating),1) FROM Bars '''
        query3 = '''Group by Region HAVING count(SpecificBeanBarName) > 4 '''
        query4 = '''Order by AVG(Rating) '''
    if "bottom" in user_input or "top" in user_input:
        if "bottom" in user_input:
            query5= "Limit {}".format(limit)
        else:
            query5= "DESC Limit {}".format(limit)
    else:
        query5 = "DESC limit 10"

    query = query1 + query2 + query3 + query4 + query5
    # print(query)
    output = cur.execute(query).fetchall()
    return output


def process_command(user_input):
    if user_input.split()[0] == "bars":
        return bars_query(user_input)
    elif user_input.split()[0] == "countries":
        return countries_query(user_input)
    elif user_input.split()[0] == "companies":
        return companies_query(user_input)
    else:
        return regions_query(user_input)


def load_help_text():
    with open('help.txt') as f:
        return f.read()

# # Part 3: Implement interactive prompt. We've started for you!
def interactive_prompt():
    help_text = load_help_text()
    user_input = ''
    while user_input != 'exit':
        user_input = input('Enter a command: ')
        if user_input == 'help':
            print(help_text)
            continue
        if user_input.isnumeric():
            print("A number is not a valid input. Please try again")
            continue
        if user_input == "" or user_input == " ":
            print("You did not enter anything. Please try again")
            continue
        if user_input.split()[0] == "exit" or user_input.split()[0] == "bars" or user_input.split()[0] == "countries" or user_input.split()[0] == "companies" or user_input.split()[0] == "regions":
            input_list = user_input.split()
            if len(input_list) > 1 and input_list[1] == "nothing":
                print("This Command was not recognized: ", user_input,  " Please try again.")
                continue
            if len(input_list) == 0:
                print("You did not enter anything. Please try again")
                continue
            if input_list[0] == "bars":
                if len(input_list) > 4:
                    print("This Command was not recognized: ", user_input,  " Please try again.")
                    continue
                else:
                    print_statement = ""
                    bars = process_command(user_input)
                    for b in bars:
                        print('{0:50} {1:35} {2:35} {3:10} {4:10} {5:20}'.format(b[0], b[1], b[2], b[3], b[4], b[5]))
            if input_list[0]  == "countries":
                if len(input_list) > 5:
                    print("This Command was not recognized: ", user_input,  " Please try again.")
                    continue
                else:
                    countries = process_command(user_input)
                    for c in countries:
                        print('{0:60} {1:35} {2:20}'.format(c[0],c[1],c[2]))

            if input_list[0] == "companies":
                if len(input_list) > 4:
                    print("This Command was not recognized: ", user_input,  " Please try again.")
                    continue
                else:
                    companies = process_command(user_input)
                    for c2 in companies:
                        print('{0:35} {1:60} {2:20}'.format(c2[0],c2[1],c2[2]))

            if input_list[0] == "regions":
                if len(input_list) > 4:
                    print("This Command was not recognized: ", user_input,  " Please try again.")
                    continue
                else:
                    regions = process_command(user_input)
                    for r in regions:
                        print('{0:20} {1:10}'.format(r[0],r[1]))

        else:
            print("This Command was not recognized: " + '"' + user_input,'"' + ". Please try again.")
            continue

    print("bye!")


# Make sure nothing runs or prints out when this file is run as a module
if __name__=="__main__":
    create_db(DBNAME)
    populate_countries(DBNAME)
    populate_bars(DBNAME)
    interactive_prompt()
