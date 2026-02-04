from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import pandas
import numpy as np
from dataProcessing import dataProccesses
from Models import Models



class ProbOverModel():

    def __init__(self):
        
        self.modelSize = 10000
        self.OverRatio = 0.5
    
        #establishes values needed for Under average points data
        self.UnderMean = 0.0
        self.UnderStd = 0.0
        self.UnderSkew = 0.0
        self.UnderKurt = 0.0
        self.UnderFCoeff = [0.0,0.0,0.0]
        self.UnderSimData = []
        self.UnderRealData = []
        self.UnderN = int((1-self.OverRatio) * self.modelSize)
        
        #establishes values needed for over average points data
        self.OverMean = 0
        self.OverStd = 0.0
        self.OverSkew = 0.0
        self.OverKurt = 0.0
        self.OverFCoeff = [0.0,0.0,0.0]
        self.OverRealData = []
        self.OverSimData = []
        self.OverN = int(self.OverRatio * self.modelSize)
        
        self.binCnt = 12
        self.modelValues = np.arange(self.binCnt*2,dtype=float).reshape(self.binCnt,2)
        
    def genSimData(self): #generates model data
        #sets over coeffeceints
        self.OverFCoeff[0], self.OverFCoeff[1], self.OverFCoeff[2] = fsolve(
        lambda vars: [
            vars[0]**2 + 6*vars[0]*vars[2] + 2*vars[1]**2 + 15*vars[2]**2 - 1,
            2*vars[1]*(vars[0]**2 + 24*vars[0]*vars[2] + 105*vars[2]**2) - self.OverSkew,
            24*vars[2]*(vars[0]**2 + 36*vars[0]*vars[2] + 225*vars[2]**2)
            + 6*vars[1]**2*(vars[0]**2 + 28*vars[0]*vars[2]) - self.OverKurt
        ],
        x0=[1, 0, 0]
        )
        OverZ = np.random.normal(size=self.OverN)
        self.OverSimData = self.OverMean + self.OverStd * (self.OverFCoeff[0]*OverZ + self.OverFCoeff[1]*OverZ**2 + self.OverFCoeff[2]*OverZ**3)
        
        #sets under coeffeceints
        self.UnderFCoeff[0], self.UnderFCoeff[1], self.UnderFCoeff[2] = fsolve(
        lambda vars: [
            vars[0]**2 + 6*vars[0]*vars[2] + 2*vars[1]**2 + 15*vars[2]**2 - 1,
            2*vars[1]*(vars[0]**2 + 24*vars[0]*vars[2] + 105*vars[2]**2) - self.UnderSkew,
            24*vars[2]*(vars[0]**2 + 36*vars[0]*vars[2] + 225*vars[2]**2)
            + 6*vars[1]**2*(vars[0]**2 + 28*vars[0]*vars[2]) - self.UnderKurt
        ],
        x0=[1, 0, 0]
        )

        UnderZ = np.random.normal(size=self.UnderN)
        self.UnderSimData = self.UnderMean + self.UnderStd * (self.UnderFCoeff[0]*UnderZ + self.UnderFCoeff[1]*UnderZ**2 + self.UnderFCoeff[2]*UnderZ**3)
        

    def modelGen(self):
    
        self.modelValues = np.arange(self.binCnt*2,dtype=float).reshape(self.binCnt,2)
        bins = np.linspace(self.UnderMean - 2.75 * self.UnderStd,self.OverMean + 2.75 * self.OverStd,self.binCnt)
        #generate model values i.e. value,P
        for i,AvgDelta in enumerate(bins):
           
            self.modelValues[i,0] = AvgDelta
            
            if i != 0:
                OverPort = (np.mean(self.OverSimData <= AvgDelta) - np.mean(self.OverSimData <= self.modelValues[i-1,0])) * self.OverRatio
                UnderPort = (np.mean(self.UnderSimData <= AvgDelta) - np.mean(self.UnderSimData <= self.modelValues[i-1,0])) * (1-self.OverRatio)
            else:
                OverPort = np.mean(self.OverSimData <= AvgDelta) * self.OverRatio
                UnderPort = np.mean(self.UnderSimData <= AvgDelta) * (1-self.OverRatio)
                
            self.modelValues[i,1] = OverPort / (OverPort + UnderPort)
        
  
    # x is input of cdf function #interprets calculated model values to return probility of over average
    def giveProbOver(self,x):
    
        if x < min(self.modelValues[:,0]):
            pf = self.modelValues[min(self.modelValues[:,0]),1]
        elif x > max(self.modelValues[:,0]):
            pf = self.modelValues[max(self.modelValues[:,0]),1]
        else:
        
            delta0 = max(self.modelValues[self.modelValues[:,0] < x,0])
            delta1 = min(self.modelValues[self.modelValues[:,0] > x,0])
            
            p0 = max(self.modelValues[self.modelValues[:,0] < x,1])
            p1 = min(self.modelValues[self.modelValues[:,0] > x,1])
            
            m = (p1-p0)/(delta1-delta0)
            
            dx = m * (m - delta0)/(delta1-delta0)
            
            pf = p0 + m*dx
        
        return pf #final probability
        
