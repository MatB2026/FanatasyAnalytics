#Class that makes API calls to build data to be used
#for further analysis

from turtle import done
import requests
import json
import configparser
import os


class APIUtils():
    def __init__(self):
        #reads properties file
        config_path = os.path.join(os.path.dirname(__file__), "config.properties")
        self.props = configparser.ConfigParser()
        self.props.read(config_path)

        #sets league values
        self.leagueID = self.props["League"]["leagueID"]
        self.year = self.props["League"]["year"]
        self.url = self.props["League"]["url"].format(year = self.year, leagueID = self.leagueID)
        self.SeasonUrl = self.props["League"]["SeasonUrl"].format(year = self.year)
        
        #sets cookies
        self.cookies = {
            "swid": self.props["Cookies"]["swid"],
            "espn_s2": self.props["Cookies"]["espn_s2"].format(percent = "%")
        }

        #sets headers
        self.headers = {
            "User-Agent": self.props["Headers"]["UserAgent"]
        }
        

    #function to send GET request
    def sendRequest(self, param):

        #sends get rquest
        resp = requests.get(self.url, headers=self.headers, cookies=self.cookies,params=param)
        #converts repsonse to json
        data = resp.json()

        return data

#gets player data and performance data for the latest or specified week
    def getPlyaerCard(self,week=0):
        if week:
            params = {
                "view": "kona_playercard",
                "scoringPeriodId": str(week)
            }
        else:
            params = {
                "view": "kona_playercard"
            }
       
       #sets special headers for the playercard API call
        self.headers = {
            "User-Agent": self.props["Headers"]["UserAgent"],
            "X-Fantasy-Filter": self.props["Headers"]["filter"]
            }
        
        return self.sendRequest(params)

   #gets current week
    def getWeek(self):

        return self.sendRequest({})["scoringPeriodId"]
        
    #gets matchup for teams
    #not currently used but may be useful in later versions
    def getMatchup(self,week=None):
        if week:
            params = {
                "view": "mMatchup",
                "scoringPeriodId": str(week)
            }
        else:
            params = {
                "view": "mMatchup"
            }
        return self.sendRequest(params)

    #gets roster for teams
    def getRoster(self):
        params = {
            "view": "mRoster"
        }
        return self.sendRequest(params)

    #gets team schedule
    def getNflSchedules(self):
        parameters = {
            "view": "proTeamSchedules_wl"
        }
        resp = requests.get(self.SeasonUrl, headers=self.headers, cookies=self.cookies, params = parameters)
        data = resp.json()
        return data
    
 
