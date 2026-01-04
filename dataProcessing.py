#It processes the data retrieved from the API and makes JSONs and Dataframes
#for analysis

from turtle import done
import requests
import json
import configparser
import os
import pandas as pd
from fantasyApi import APIUtils

class dataProccesses():

    def __init__(self):
        self.JSONpath = "./JSON/"
        self.API = APIUtils()

        done
       
    #reads JSON file
    def readJson(self,fileName):
        with open(self.JSONpath+fileName, "r") as file:
            data = json.load(file)
        return data
    
    #writes JOSN
    def writeJSON(self,data,fileName,indent_num):
        with open(self.JSONpath+fileName, "w") as file:
            json.dump(data,file,indent=indent_num)
        done
    
    #populates JSON file of team, opponent, and weekly performance by week
    def popTeamByweek(self):
        teams = self.getTeamPerfByWeek()
        week = self.API.getWeek()
        perfRpt = self.getPlayerPtsByWeek()

        for team in teams.keys():
            for player in perfRpt[team]["roster"]:
    
                for stat_report in perfRpt[team]["roster"][player]["Stats"]:
   
                
                    if str(stat_report["scoringPeriodId"]) in teams[team]["weeklyReport"].keys() and str(stat_report["seasonId"]) == self.API.year:
                        
                        teams[team]["weeklyReport"][str(stat_report["scoringPeriodId"])]["teamStats"][player] = {"Name":perfRpt[team]["roster"][player]["Name"],"position":perfRpt[team]["roster"][player]["position"],"Stats":stat_report}
   
                        
            self.writeJSON(teams,"teams.json",4)

        done
    
    #builds JSON of total points scored by a team in a given week
    def writeTotalTeamPts(self):
        aggData = self.readJson("teams.json")
        totTeamPts = {}
        for team in aggData.keys():
            
            totTeamPts[team] = {"totalByWeek": {}, "Avg": 0, "PlayedWeeks": 0, "total": 0}
            
            for week in aggData[team]["weeklyReport"].keys():
                totalPts = 0
                totTeamPts[team]["totalByWeek"][week] = {"opponent": aggData[team]["weeklyReport"][week]["opponent"]}
                for player in aggData[team]["weeklyReport"][week]["teamStats"].keys():
                    totalPts = totalPts + aggData[team]["weeklyReport"][week]["teamStats"][player]["Stats"]["appliedTotal"]
                
                totTeamPts[team]["totalByWeek"][week]["Points"] = totalPts
                
                if totalPts != 0:
                    totTeamPts[team]["total"] = totTeamPts[team]["total"] + totalPts
                    totTeamPts[team]["PlayedWeeks"] = totTeamPts[team]["PlayedWeeks"] + 1
                    
            if totTeamPts[team]["PlayedWeeks"] != 0:
                totTeamPts[team]["Avg"] = totTeamPts[team]["total"] / totTeamPts[team]["PlayedWeeks"]
            
        self.writeJSON(totTeamPts,"totTeamPts.json",2)
        done
    
    
    #builds JSON of points scored against a team in a given week
    def writeTotalPtsAgainst(self):
        ptsData = self.readJson("totTeamPts.json")

        ptsAgainst = {}


           
        for team in ptsData.keys():
            
            for week in ptsData[team]["totalByWeek"].keys():
                if ptsData[team]["totalByWeek"][week]["opponent"] not in ptsAgainst.keys():
                    ptsAgainst[ptsData[team]["totalByWeek"][week]["opponent"]] = {week:{"PointsAgainst": ptsData[team]["totalByWeek"][week]["Points"]}}
                else:
                    ptsAgainst[ptsData[team]["totalByWeek"][week]["opponent"]][week] ={ "PointsAgainst": ptsData[team]["totalByWeek"][week]["Points"]}
                
                if ptsData[team]["totalByWeek"][week]["Points"] != 0:
                    if "GamesPlayed" in ptsAgainst[ptsData[team]["totalByWeek"][week]["opponent"]].keys():
                    
                        ptsAgainst[ptsData[team]["totalByWeek"][week]["opponent"]]["GamesPlayed"] = ptsAgainst[ptsData[team]["totalByWeek"][week]["opponent"]]["GamesPlayed"] + 1
                        
                        ptsAgainst[ptsData[team]["totalByWeek"][week]["opponent"]]["Total"] = ptsAgainst[ptsData[team]["totalByWeek"][week]["opponent"]]["Total"] + ptsData[team]["totalByWeek"][week]["Points"]
                        
                        
                    else:
                        ptsAgainst[ptsData[team]["totalByWeek"][week]["opponent"]]["GamesPlayed"] = 1
                        ptsAgainst[ptsData[team]["totalByWeek"][week]["opponent"]]["Total"] = ptsData[team]["totalByWeek"][week]["Points"]
                        
        
            
        self.writeJSON(ptsAgainst,"ptsAgainst.json",2)
        done

    #builds final data set of data to used in regression models
    def regressionDataFrame(self):
        aggData = self.readJson("teams.json")
        teamPtsData = self.readJson("totTeamPts.json")
        ptsAgainst = self.readJson("ptsAgainst.json")
    
        period = self.API.getWeek()
        
        finalOut = []
        #makes a dict entry with all the data that will be made into row for data frame
        for team in aggData.keys():
            
            for week in aggData[team]["weeklyReport"].keys():
               
                for player in aggData[team]["weeklyReport"][str(week)]["teamStats"].keys():
                    
                    entry = {
                        "week": int(week),
                        "PlayerID": player,
                        "PlayerName": aggData[team]["weeklyReport"][str(week)]["teamStats"][player]["Name"],
                        "teamName": aggData[team]["team"],
                        "teamID": team,
                        "Points": aggData[team]["weeklyReport"][str(week)]["teamStats"][player]["Stats"]["appliedTotal"],
                        "TeamPoints": teamPtsData[team]["totalByWeek"][str(week)]["Points"],
                        "TeamPointsAvg": teamPtsData[team]["Avg"],
                        "PercentTotal":aggData[team]["weeklyReport"][str(week)]["teamStats"][player]["Stats"]["appliedTotal"] / teamPtsData[team]["totalByWeek"][str(week)]["Points"],
                        "PercentTotalAvg": 0,
                        "Opponent": teamPtsData[team]["totalByWeek"][str(week)]["opponent"],
                        "OppPoints": ptsAgainst[str(teamPtsData[team]["totalByWeek"][str(week)]["opponent"])][str(week)]["PointsAgainst"],
                        "OppPtsAvg": ptsAgainst[str(teamPtsData[team]["totalByWeek"][str(week)]["opponent"])]["Total"] / ptsAgainst[str(teamPtsData[team]["totalByWeek"][str(week)]["opponent"])]["GamesPlayed"],
                        "Position":aggData[team]["weeklyReport"][str(week)]["teamStats"][player]["position"][0],
                        
                        }
        
                    
                    finalOut.append(entry)
                    
                    
         #converts the dict to dataframe
        df = pd.json_normalize(finalOut)
        
        #makes set of unique player ids
        players = set(df["PlayerID"])
        
        #sets average percentage of total points scored by team
        for player in players:
          df.loc[df["PlayerID"] == player,"PercentTotalAvg"] = df.loc[df["PlayerID"] == player, "PercentTotalAvg"].mean()
        done
        

        
    def JSONToDf(self,json):
        data = self.readJson(json)
        df = pd.json_normalize(data)
        
        return df
        
    #gets performance of players by week and their postion
    def getPlayerPtsByWeek(self,week=0):
      
        players = {}
        pc = self.API.getPlyaerCard(week)

        for entry in pc["players"]:
           
            if str(entry["player"]["proTeamId"]) not in players.keys():
                players[str(entry["player"]["proTeamId"])] = {"roster":{entry["player"]["id"] : {"Name":entry["player"]["fullName"], "position": [sum(entry["player"]["eligibleSlots"])],"Stats": entry["player"]["stats"]}}}
            else:
                players[str(entry["player"]["proTeamId"])]["roster"].update({entry["player"]["id"]: {"Name":entry["player"]["fullName"], "position": [sum(entry["player"]["eligibleSlots"])],"Stats": entry["player"]["stats"]}})
        return players
        
        
    #builds dictionary of team and performance of players by week and against what opponent
    def getTeamPerfByWeek(self):
        teams = {}
        sc = self.API.getNflSchedules()

        for teamSched in sc["settings"]["proTeams"]:
            
            teams[str(teamSched["id"])] = {"team": teamSched["name"], "teamId": teamSched["id"], "weeklyReport": {}}
                
            for week in teamSched["proGamesByScoringPeriod"].keys():
                if teamSched["proGamesByScoringPeriod"][week][0]["awayProTeamId"] == teamSched["id"]:
                    teams[str(teamSched["id"])]["weeklyReport"][str(week)] = {"opponent": teamSched["proGamesByScoringPeriod"][week][0]["homeProTeamId"], "teamStats":{}}
                else:
                    teams[str(teamSched["id"])]["weeklyReport"][str(week)] = {"opponent": teamSched["proGamesByScoringPeriod"][week][0]["awayProTeamId"], "teamStats":{}}
        return teams
        
        

    def setJSONS(self):
        self.popTeamByweek()
        self.writeTotalTeamPts()
        self.writeTotalPtsAgainst()
        
        
        done
