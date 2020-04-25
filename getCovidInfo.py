from utils import countryCodeToName, nameToCountryCode, callApi, ERROR_MESSAGE

import datetime
from logger import *
 

def infoToTweet(information, country, city, travel): 

    updated = 20 # The TrackCorona.live creators scrape every 20 minutes, so this is the maximum update time!

    hashtags = ["#COVID19"]

    location = information["location"].replace(" ", "").replace("County", "")
    if ","  in location: 
        location = location.split(",")[0]

    hashtags.append("#" + location)

    if not travel and information["updated"]:
        now = int(datetime.datetime.now().minute)
        time_updated = int(information["updated"].split(" ")[1].split(":")[1])
        updated = now - time_updated if now > time_updated else 20 


    if travel: 

        travel_information = ""
        if len(information["data"]) > 200: 
            travel_information = information["data"][0:155] + "... for remainder, check the countries govt site for regulations"

        ret = "In the {0}, {1} -- Updated {2} minutes ago.".format(information["location"], travel_information, updated)
    elif city: 
        ret = "In {0}, there are {1} confirmed cases, {2} people recovered and {3} deaths -- Updated {4} minutes ago. {5}".format(information["location"], information["confirmed"], information["recovered"], information["dead"], updated, " ".join(hashtags))
    else: 

        hashtags.append("#" + information["country_code"].upper())

        ret = "In the {0} ({1}), there are {2} confirmed cases, {3} people recovered and {4} deaths -- Updated {5} minutes ago. {6}".format(information["country_code"].upper(), information["location"], information["confirmed"], information["recovered"], information["dead"], updated, " ".join(hashtags))
        if "doesnt_have_city" in information: 
            ret = "I don't have information on " + information["doesnt_have_city"] + ", however, in your country, the {0} ({1}), there are {2} confirmed cases, {3} people recovered and {4} deaths -- Updated {5} minutes ago. {6}".format(information["country_code"].upper(), information["location"], information["confirmed"], information["recovered"], information["dead"], updated, hashtags)

    print(ret)
    return ret


def getInfoFromResp(data, loc): 
    info = None

    for item in data: 

        city = None if "," not in item["location"] else item["location"].split(",")[0]

        if loc in item["location"]: 
            info = item
        
        if city and loc in city: 
            return item

        if loc in item["location"] and loc == city: 
            return item 
    
    return info




def getCovidInfo(country, city, travel):
    logging.info('=============================================================================')
    logging.info("In Get Corona Info Tweet with input country=" + str(country) + " city=" + str(city) + " travel=" + str(travel))
    logging.info('=============================================================================')

    if not country and not city and not travel: 
        return ERROR_MESSAGE 

    # Step 1: Request Information to TrackCorona.live API 
    url = {
        "countries_api": "https://www.trackcorona.live/api/countries", 
        "cities_api": "https://www.trackcorona.live/api/cities",
        "travel_api": "https://www.trackcorona.live/api/travel",
    }

    info = None 

    if travel: 
        try: 
            resp = callApi(url["travel_api"])

            if len(country) > 2: 
                country_name = country 
            else: 
                country_name = countryCodeToName(country)

            info = getInfoFromResp(resp["data"], country_name)

        except: 
            logging.error("Error in travel line 83 in getCoronaInfo.py")
            return ERROR_MESSAGE

    elif city:
        try:
            resp = callApi(url["cities_api"])
            info = getInfoFromResp(resp["data"], city)
        except:
            logging.error("Error in city line 98 in getCoronaInfo.py")
            return ERROR_MESSAGE

    elif country: 
        try:
            if len(country) > 2: 
                country = country if not nameToCountryCode(country) else nameToCountryCode(country) 
            
            resp = callApi(url["countries_api"] + "/" + country)
            info = resp["data"][0]

        except:
            logging.error("Error in city line 98 in getCoronaInfo.py")
            return ERROR_MESSAGE

    if not travel and city and not info and country: 
        try: 
            if len(country) > 2: 
                country = country if not nameToCountryCode(country) else nameToCountryCode(country) 
            
            resp = callApi(url["countries_api"] + "/" + country)
            info = resp["data"][0]
            info["doesnt_have_city"] = city
            city = None 

        except:
            logging.error("Error in city line 98 in getCoronaInfo.py")
            return ERROR_MESSAGE

    if not info: 
        logging.error("IN ERROR for getCoronaInfo.py")
        return ERROR_MESSAGE

    # Step 2: Clean information and turn it into tweet 
    tweet = infoToTweet(info, country, city, travel) 

    # Step 3: return 
    return tweet  







if __name__ == "__main__":  
    country = "United States"
    city = "Fairfax County"
    travel = True 
    getCovidInfo(country, city, travel)
    # getCounties()
