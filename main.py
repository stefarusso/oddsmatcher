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



#data_pokerstar,competitions=ps.dataframe_load()
#data_pokerstar['date'] = pd.to_datetime(data_pokerstar['date'], format='%Y-%m-%d %H:%M:%S') #INSERIRE IN SCARAPERP#S
#data_pokerstar = data_pokerstar.sort_values(by='date')
#data_pokerstar.to_csv("pokerstar.csv",index=False)
#save_json_file("competitions.json",json.dumps(competitions.tolist()))

data_pokerstar=pd.read_csv('pokerstar.csv')
comps_ps=open_json_file("competitions.json")
comps_ps=json.loads(comps_ps)


#competitions=['Italia - Serie A' ,'Italia - Serie B' ,'Champions League' ,'Europa League' ,'Conference League' ,'Inghilterra - Premier League' ,'Spagna - La Liga' ,'Germania - Bundesliga' ,'Francia - Ligue 1' ,'Portogallo - Primeira Liga']
#print(competitions)
#print(type(competitions))

data_betfair=betfair.load_dataframe(comps_ps)
#data_betfair['date'] = pd.to_datetime(data_betfair['date'], format='%Y-%m-%d %H:%M:%S') #INSERIRE IN SCARAPERPS

data_betfair['date'] = pd.to_datetime(data_betfair['date'], format='%d-%m-%Y %H:%M:%S') #INSERIRE IN SCARAPERPS
data_betfair= data_betfair.sort_values(by='date')
data_betfair.to_csv("betfair.csv",header=False,index=False)

#print("test competizioni")
#print([(i,len(data_pokerstar[data_pokerstar.league==str(i)])) for i in data_pokerstar.league.unique()]) #check number of line for competition
#print("---")
print([(i,len(data_betfair[data_betfair.league==str(i)])) for i in data_betfair.league.unique()])

print(data_pokerstar[data_pokerstar.league=='Germania - Bundesliga']["date"].min())
print(data_pokerstar[data_pokerstar.league=='Germania - Bundesliga']["date"].max())

print(data_betfair[data_betfair.league=='Germania - Bundesliga 2']["date"].min())
print(data_betfair[data_betfair.league=='Germania - Bundesliga 2']["date"].max())

