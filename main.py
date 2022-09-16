import scraperPS as ps
import betfair as betfair
import pandas as pd
import json
pd.set_option('display.max_row', None) #FOR DEBUG

def save_json_file(filename,object):
	with open(filename, 'w') as outfile:
		json.dump(object, outfile,indent=2)

def open_json_file(filename):
	with open(filename) as json_file:
		json_data = json.load(json_file)
	return json_data

def save_pandas(data,filename):
	data.to_csv(filename, index=False)

def save_list(filename,lista):
	save_json_file(filename, json.dumps(lista.tolist()))
def update_pokerstar(pokerstar_save_filename,competitions_save_filename):
	data_pokerstar, competitions = ps.dataframe_load()
	save_pandas(data_pokerstar, pokerstar_save_filename)
	save_list(competitions_save_filename, competitions)
	return data_pokerstar, competitions

def open_list(filename):
	comps_ps = open_json_file(filename)
	comps_ps = json.loads(comps_ps)
	return comps_ps


pokerstar_save_filename="pokerstar.csv"
competitions_save_filename="competitions.json"
betfair_save_filename="betfair.csv"



#request pokerstar data
data_pokerstar,competitions=update_pokerstar(pokerstar_save_filename,competitions_save_filename)

#read HD saved files
open_list(competitions_save_filename)
data_pokerstar=pd.read_csv(pokerstar_save_filename)

max_date=data_pokerstar["date"].max()
#request betfair data                                         AFTER INCLUDE IN update_pokerstar
data_betfair=betfair.load_dataframe(competitions,max_date)
data_betfair.to_csv("betfair.csv",header=False,index=False)


#print("test competizioni")
print([(i,len(data_pokerstar[data_pokerstar.league==str(i)])) for i in data_pokerstar.league.unique()]) #check number of line for competition
print("---")
print([(i,len(data_betfair[data_betfair.league==str(i)])) for i in data_betfair.league.unique()])

print(data_pokerstar[data_pokerstar.league=='Inghilterra - Premier League']["date"].min())
print(data_pokerstar[data_pokerstar.league=='Inghilterra - Premier League']["date"].max())

print(data_betfair[data_betfair.league=='Inghilterra - Premier League']["date"].min())
print(data_betfair[data_betfair.league=='Inghilterra - Premier League']["date"].max())

