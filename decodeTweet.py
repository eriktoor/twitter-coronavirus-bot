from logger import *
from utils import countries, states, counties, state_names, state_abbreviations

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
            if combo in j.title() and len(combo) > 3: 
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

def getState(tweet, allCombos): 

    for combo in allCombos: 
        word = combo.split(" ")
        for i in range(len(word)): 
            w = word[i]
            if w.upper() in state_abbreviations and i > 0 and len(word[i-1]) > 2: 
                return w.upper()
            elif w.title() in state_names and i > 0 and len(word[i-1]) > 2: 
                return w.title()



def decodeTweet(tweet):
    logging.info('=============================================================================')
    logging.info("In Decode Tweet with input tweet= " + str(tweet))


    tweet = tweet.title()

    country, city, state, travel = 0, "", "", False 

    words = tweet.split(" ")
    # print(words)

    for abbrev, country_name in countries: 

        if country_name in words: 
            print(country_name)
            tweet = tweet.replace(country, "")
            country = country_name

    for abbrev, state_name in states: 

        if state_name in words: 
            # words.remove(state)
            state = state_name
            tweet = tweet.replace(state, "")
            print(tweet)

    allCombos = allAdjacentWords(tweet.title())

    country = getCountry(tweet, allCombos)
    city = getCity(tweet, allCombos)
    
    if city and not state: 
        city_p0 = city.split(" ")[0]
        tweet_parts = tweet.split(city_p0)
        if len(tweet_parts) > 1: 
            current_part = tweet_parts[1]
            words = current_part.split(" ")
            for abbrev, state_name in states: 
                if abbrev.title() in words: 
                    print(abbrev.title())
                    state = state_name


    if "Miami" in city and state == "Florida": 
        city = "Miami-Dade County"


    travel = True if "travel" in tweet or "flight" in tweet else False  

    logging.info("Output city=" + str(city) + " travel=" + str(travel) + " country=" + str(country))
    logging.info('=============================================================================')

    return country, city, state, travel 


if __name__ == "__main__":
    tweet = "where can i get tested"
    print(decodeTweet(tweet))
