import scraperPS as ps
import betfair as betfair
import pandas as pd
import datetime
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

def request_dataframe(pokerstar_save_filename,competitions_save_filename,betfair_save_filename):
	# request pokerstar data
	data_pokerstar, competitions = update_pokerstar(pokerstar_save_filename, competitions_save_filename)
	# read HD saved files
	competitions = open_list(competitions_save_filename)
	data_pokerstar = pd.read_csv(pokerstar_save_filename)
	max_date = data_pokerstar["date"].max()
	# request betfair data                                         AFTER INCLUDE IN update_pokerstar
	data_betfair = betfair.load_dataframe(competitions, max_date)
	data_betfair.to_csv(betfair_save_filename,header=True, index=False)
	data_betfair = pd.read_csv(betfair_save_filename)
	return data_pokerstar,data_betfair,competitions

def update_dataframes(pokerstar_save_filename,competitions_save_filename,betfair_save_filename):
	try:
		competitions = open_list(competitions_save_filename)
		data_pokerstar = pd.read_csv(pokerstar_save_filename)
		data_betfair = pd.read_csv(betfair_save_filename)
	except FileNotFoundError:
		data_pokerstar, data_betfair, competitions = request_dataframe(pokerstar_save_filename,competitions_save_filename,betfair_save_filename)
	return data_pokerstar, data_betfair, competitions

pokerstar_save_filename="pokerstar.csv"
competitions_save_filename="competitions.json"
betfair_save_filename="betfair.csv"

#ONLY DEBUG
non_interactive_login_url='https://identitysso-cert.betfair.it/api/certlogin'    #Just for get the session token SSOID on the italian website
certificates=('certificates/betfair_api.crt','certificates/betfair_api.key') #local position of my XRC certificates and secret key
print(betfair.get_ssoid(betfair.usr,betfair.psw,betfair.ap_key,certificates,non_interactive_login_url))
print(betfair.ap_key)

#UPDATE THE CSV
#data_pokerstar,data_betfair,competitions=request_dataframe(pokerstar_save_filename,competitions_save_filename,betfair_save_filename)
#ONLY READ THE EXISTING CSV
data_pokerstar,data_betfair,competitions=update_dataframes(pokerstar_save_filename,competitions_save_filename,betfair_save_filename)

#print("test competizioni")
print([(i,len(data_pokerstar[data_pokerstar.league==str(i)])) for i in data_pokerstar.league.unique()]) #check number of line for competition
print("---")
print([(i,len(data_betfair[data_betfair.league==str(i)])) for i in data_betfair.league.unique()])
print('-------------------------------')
print(data_pokerstar.info())
print(data_pokerstar.league.unique())
#---------------------------------------------------------------------------
#START AT LINKING THE TWO DATAFRAME
#JUST ONE COMPETITION

#
#
# BISOGNA AGGIUNGERE POKER_NAME AL COMPETITION_DICT
#
print("---------------------------LINKING")
print("betfair:",len(data_betfair["league"]),"    pokerstar:",len(data_pokerstar["league"]))
#if len(data_betfair["league"]) < len(data_pokerstar["league"]): #parte dadataframe che ha meno entry

first_comp=data_betfair["league"].unique()[0]
print("first competition:",first_comp)

tmp_poker=data_pokerstar[data_pokerstar["league"]==first_comp] #SUB DATAFRAME WITH ONLY THE COMPETITIOn
tmp_betfair=data_betfair[data_betfair["league"]==first_comp]
print("pokerstar:"+ str(len(tmp_poker))+"   betfair:"+str(len(tmp_betfair)))  #USE THE ONE WITH LESS ENTRY AS GUIDE
#if len ==0 break
# start with the one with less entry
#if len(tmp_betfair["league"]) < len(tmp_poker["league"]): #parte dadataframe che ha meno entry


#CYCLE OVER HOURS
dates=tmp_betfair["date"].unique() #LISTS OF EVENTS
data_1=dates[0]
print(data_1)


events=tmp_betfair.loc[(tmp_betfair["date"]==data_1,["home_team","away_team"])].value_counts() # ALL COUPLES IN THAT HOUR
#CYCLE OVER COUPLES IF THERE ARE MORE THAN ONE EVENT AT THAT TIME
print(events.keys()[0][0]) #1° couple, home_team
teams_dict={} # {betfair_team_name:pokerstar_team_name} TO SAVE IF THERE ARE NAME DIFFERENT
if events.keys()[0][0] in tmp_poker.loc[tmp_poker["date"]==data_1,"home_team"].values:
	teams_dict[events.keys()[0][0]]=events.keys()[0][0]
	print(tmp_poker.loc[ tmp_poker["home_team"]==events.keys()[0][0]].loc[tmp_poker["date"]==data_1]) #slice of tmp_poker in data_1 and with home_team 0
print(teams_dict)



