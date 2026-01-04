This project is being made to create a predictive model for fantasy points 
on a per player basis based upon their prior performance, their team's performance
and the performance of their opponent

The files in this project are:

config.properties:
	This conatains the properties read by the API file. It uses the properties
to interact with ESPN's API

fantasyAPI.py:
	This contains the class that interacts and pulls data
from the ESPN API

dataProcessing.py:
	This contains the classes used for putting the data into more conusmable
JSONs and making final dataFrames that can be more readibly used for data analysis 

regressionModels.py:
	This runs/will run the code to generate the models
