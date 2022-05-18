#Python native
import sys
import logging
from pathlib import Path

#Part of Project
import config

#External
import praw

#TODO: Inifile location in config.py verschieben


#Pull Authentication info
clientID = config.readini("REDDIT","clientID")
clientSecret = config.readini("REDDIT","clientSecret")

# Creating User Agent String
platform = str(sys.platform)
appID = "GustelBOT"
version_string = "v0.1.1" #getVersion()
redditusername = config.readini("REDDIT", "creatorUsername")

userAgent = platform+":"+appID+":"+version_string+" by /u/"+str(redditusername)


def youtubehaiku(*args):
    
    #default time and amount values:
    time = "month"
    amount = 15 
    
    
    #Filter out parameters for further processing
    try:
        #If 4 arguments
        if len(args[0]) == 4:
            
            #If 4 arguments are given, 0-1 and 0-3 have to be the numbers/keywords
            if args[0][0] == "-time" and args[0][2] == "-amount" or args[0][0] == "-amount" and args[0][2] == "-time":
                if args[0][0] == "-time":
                    time = args[0][1]
                    amount = args[0][3]
                else:
                    time = args[0][3]
                    amount = args[0][1]
            else:
                return "Unzulaessiges Format: youtubehaiku -time [hour, day, week, month, year, all] -amount [1-50]"
            
        #second possible option is 2 arguments
        elif len(args[0]) == 2:
            #first has to be a valid option
            if args[0][0] == "-time" or args[0][0] == "-amount":
                if [0][0] == "-time":
                    time = args[0][1]
                else:
                    amount = args[0][1]
                    
        #last valid option is no arguments given, options remain default
        elif len(args[0]) == 0:
            pass
        
        else:
            return "Unzulaessige Zahl an Argumenten, du Hurensohn!"
        
            
    except Exception as e:
        print(str(e)+" Was zum Arsch!")
        pass
    
    #Check if arguments are valid
    #time
    allowedTimes = ["hour", "day", "week", "month", "year", "all"]
    #default result
    result = False
    
    
    for x in allowedTimes:
        if x == time:
            result = True
            
    if not result:
        return "Es wurde keine valide Zeit angegeben: youtubehaiku -time [hour, day, week, month, year, all] -amount [1-50]"
    
    #amount
    try:
        amount = int(amount)
    except Exception as e:
        logging.error(e)
        return "Amount muss einer Zahl zwischen 1 und 50 entsprechen"
    if amount <= 50 and amount >= 1:
        pass
    else:
        return "Der Wert nach -amount muss zwischen 1 und 50 liegen!"
    
    print(getPosts(time,amount))
    return "Ergebnis"+str(time)+str(amount)
    
    
    #ToDo: Youtube playlist erstellen


def getPosts(time,amount):
    
    #Creating Reddit instance
    reddit = praw.Reddit(
    client_id = clientID,
    client_secret = clientSecret,
    user_agent = userAgent
    )
    
    #List for YouTube Link results
    YTLinks = []
    
    #day,week,month,year,all
    for submission in reddit.subreddit("youtubehaiku").top(time,limit=amount):
        if not submission.is_self:
            YTLinks.append(submission.url)
            
    
    return YTLinks