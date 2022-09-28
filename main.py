import scraperPS as ps
import betfair as betfair
import pandas as pd
import datetime
import json
from Levenshtein import jaro_winkler as jaro
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


# START OF THE PROGRAM 

pokerstar_save_filename="pokerstar.csv"
competitions_save_filename="competitions.json"
betfair_save_filename="betfair.csv"

#ONLY DEBUG
non_interactive_login_url='https://identitysso-cert.betfair.it/api/certlogin'    #Just for get the session token SSOID on the italian website
certificates=('certificates/betfair_api.crt','certificates/betfair_api.key') #local position of my XRC certificates and secret key
print(betfair.get_ssoid(betfair.usr,betfair.psw,betfair.ap_key,certificates,non_interactive_login_url))
print(betfair.ap_key)

#UPDATE THE CSV
#ONLY FOR DEBUG    <------------------------------------------------------------------ MODIFY IN THE FINAL VERSION 
#IT'S ONLY READ THE EXISTING CSV AND UPDATE ONLY IF IT DOESN'T EXIST THE FILE

data_pokerstar,data_betfair,competitions=update_dataframes(pokerstar_save_filename,competitions_save_filename,betfair_save_filename)

#print("test competizioni")
print("pokerstars competitions scaraped:")
print([(i,len(data_pokerstar[data_pokerstar.league==str(i)])) for i in data_pokerstar.league.unique()]) #check number of line for competition
print("---")
print("betfair competitions scaraped:")
print([(i,len(data_betfair[data_betfair.league==str(i)])) for i in data_betfair.league.unique()])
print('-------------------------------')
print(data_pokerstar.league.unique())
#---------------------------------------------------------------------------
#START AT LINKING THE TWO DATAFRAME
#JUST ONE COMPETITION

print("--------------------------------------------LINKING PHASE")
print("BETFAIR LEAGUES:",len(data_betfair["league"]),"    POKERSTARS LEAGUES:",len(data_pokerstar["league"]),  "         #")
print("--------------------------------------------")
#if len(data_betfair["league"]) < len(data_pokerstar["league"]): #parte dadataframe che ha meno entry

#initialize the final dataframe
final_dataframe=pd.DataFrame(columns=['league','home_team','away_team','date','selection','odd','lay','lay_size'])

#initialize dict_teams. it links the pokerstar team name to the betfair team name. and it is save so every epoch the program became faster 
def initialize_dict_teams(filename):
    try:
        dict_teams = open_json_file(filename)
    except:
        dict_teams = {}
    save_json_file(filename, dict_teams)
    return dict_teams

dict_team_filename='dict_teams.json'
dict_teams=initialize_dict_teams(dict_team_filename)

#INSERT LOOP OVER data_betfair["league"].unique()
first_comp=data_betfair["league"].unique()[0]
print("first competition:",first_comp)

#create temporary dataframe with league
tmp_poker=data_pokerstar[data_pokerstar["league"]==first_comp] #SUB DATAFRAME WITH ONLY THE COMPETITIOn
tmp_betfair=data_betfair[data_betfair["league"]==first_comp]
print("pokerstar:"+ str(len(tmp_poker))+"   betfair:"+str(len(tmp_betfair)))  #USE THE ONE WITH LESS ENTRY AS GUIDE
tmp_len_ps=len(tmp_poker)
tmp_len_bf=len(tmp_betfair)
#add if condition to use as dataframe the smallest len1 < len2 <-----------------------------
#in this case they are the same normally betfair is smaller


dates=tmp_betfair["date"].unique()
#LOOP OVER DATES<-------------------------
#for debug only 1
date_1=dates[0]
print(date_1)
events_bf = tmp_betfair.loc[(tmp_betfair["date"]==date_1,["home_team","away_team"])].value_counts()
events_ps = tmp_poker.loc[(tmp_betfair["date"]==date_1,["home_team","away_team"])].value_counts()
#insert check IF len<len2: <----------------------------------

#LOOP OVER EVENTS<----------------------
event1_bf=events_bf.keys()[0] # (home,away)

#first home-home
distance_home={}
for event_ps in events_ps.keys():
	distance_home[event_ps[0]]=jaro(event1_bf[0],event_ps[0])
print(event1_bf[0],distance_home)


'''
#LOOP OVER DATETIME
dates=tmp_betfair["date"].unique() #LISTS OF EVENTS
#for testing <-------------------------------------------
data_1=dates[0]
print(data_1)


events=tmp_betfair.loc[(tmp_betfair["date"]==data_1,["home_team","away_team"])].value_counts() # ALL COUPLES IN THAT HOUR
#CYCLE OVER COUPLES IF THERE ARE MORE THAN ONE EVENT AT THAT TIME
print(events.keys()[0][0]) #1° couple, home_team
teams_dict={} # {betfair_team_name:pokerstar_team_name} TO SAVE IF THERE ARE NAME DIFFERENT
if events.keys()[0][0] in tmp_poker.loc[tmp_poker["date"]==data_1,"home_team"].values:
	teams_dict[events.keys()[0][0]]=events.keys()[0][0]
	print(tmp_poker.loc[ tmp_poker["home_team"]==events.keys()[0][0]].loc[tmp_poker["date"]==data_1]) #slice of tmp_poker in data_1 and with home_team 0
print(teams_dict)'''



