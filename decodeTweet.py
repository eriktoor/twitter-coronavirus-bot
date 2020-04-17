from geotext import GeoText
from logger import *
from utils import countries, counties, state_names

def allAdjacentWords(sentence): 
    res = []
    
    s = sentence.title().replace("?", "").replace("!", "").replace(".", "").replace("@", "")
    s = s.split(" ")

    n = len(s)

    for Len in range(1,n + 1): 
        # Pick ending point 
        for i in range(n - Len + 1): 
            # Print characters from current 
            # starting point to current ending 
            # point.  
            j = i + Len - 1
  
            currString = ""
            for k in range(i,j + 1): 
                currString += s[k] + " "

            finalString = currString.strip().title()
            if finalString == "Sf" or finalString == "La": 
                res.append(finalString)
            if len(finalString) >= 3 and len(finalString) < 60 and "Are " not in finalString and "The " not in finalString and "What " not in finalString and "Who" not in finalString and "What " not in finalString and "This " not in finalString and "The" != finalString and "What" != finalString and "Is " not in finalString and "In " not in finalString:
                res.append(finalString)

    return set(res)


def similarity(combo, city): 

    if not city: return 0

    sim = 0

    from collections import Counter

    c = combo.split(" ")
    city = city.split(" ")
    for word in c: 
        for word2 in city: 
            if word == word2 and word != "County":
                sim  += 1  

    return sim


def getCountry(tweet, allCombos): 
    country =""

    for i, j in countries: 
        for combo in allCombos: 
            if combo in j.title(): 
                country = combo

            if j.title() in allCombos: 
                country = j.title()
                return country 

    return country 

def getCity(tweet, allCombos):

    city = ""

    if "Austin" in allCombos: 
        return "Austin County"
    elif "Nyc" in allCombos:
        return "New York City County"
    elif "Sf" in allCombos:
        return "San Francisco County"

    for county in counties:
        for combo in allCombos: 
            if combo == county and county not in state_names: 
                city = county 
                return city

            if combo == county.split("County")[0] and county.split("County")[0] not in state_names: 
                city = county 
                return city

            if similarity(combo, county) >= 1 and (similarity(combo, county) > similarity(city, county) or not city): 
                # print(similarity(combo, county))
                city = county

    return city 


def decodeTweet(tweet):
    logging.info('=============================================================================')
    logging.info("In Decode Tweet with input tweet= " + str(tweet))

    # Get an Object with the Country, City, and other information 
    places = GeoText(tweet.title())

    country, city, travel = 0, "", False 

    for key, item in places.country_mentions.items(): 
        country = key 
        city =  "" if len(places.cities) == 0 else places.cities[0] 


    allCombos = allAdjacentWords(tweet.title())

    other_country = getCountry(tweet, allCombos)
    country = other_country if not country else country

    other_city = getCity(tweet, allCombos)
    city =  other_city if len(other_city) > len(city) else city

    travel = True if "travel" in tweet or "flight" in tweet else False  

    logging.info("Output city=" + str(city) + " travel=" + str(travel) + " country=" + str(country))
    logging.info('=============================================================================')

    return country, city, travel 


if __name__ == "__main__":
    tweet = "what is going on in charlottesville va"
    print(decodeTweet(tweet))
