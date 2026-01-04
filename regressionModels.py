import pandas as pd
from fantasyApi import APIUtils
from dataProcessing import dataProccesses
import scikit-learn as sk




class linRegression():
    
    def __init__(self):
        #sets data methods
        self.dm = dataProccesses()
        
        self.data = pd.dataFrame()
        done
    
    def setData(self):
        self.dm.setJSONS()
        
    
    def popDataFrame(self):
        self.data = self.dm.regressionDataFrame()
    
    