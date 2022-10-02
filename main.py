import scraperPS as ps
import betfair as betfair
import pandas as pd
import datetime
import json
from Levenshtein import jaro_winkler as jaro
#pd.set_option('display.max_row', None) #FOR DEBUG

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
	max_date = data_pokerstar["date"].iloc[-1] #dataframe is sorted on date coloumn
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

#ONLY DEBUG----------------------------------------------------------
non_interactive_login_url='https://identitysso-cert.betfair.it/api/certlogin'    #Just for get the session token SSOID on the italian website
certificates=('certificates/betfair_api.crt','certificates/betfair_api.key') #local position of my XRC certificates and secret key
print(betfair.get_ssoid(betfair.usr,betfair.psw,betfair.ap_key,certificates,non_interactive_login_url))
print(betfair.ap_key)
#ONLY DEBUG----------------------------------------------------------


#UPDATE THE CSV    <------------------------------------------------------------------ MODIFY IN THE FINAL VERSION
#ONLY FOR DEBUG    <------------------------------------------------------------------ MODIFY IN THE FINAL VERSION 
#IT'S ONLY READ THE EXISTING CSV AND UPDATE ONLY IF IT DOESN'T EXIST THE FILE
data_pokerstar,data_betfair,competitions=update_dataframes(pokerstar_save_filename,competitions_save_filename,betfair_save_filename)

'''#ONLY FOR DEGUB------------------------------------------------------------
print("usefull for debugging:")
print(data_pokerstar.league.unique())
print('-------------------------------')
print("total pokerstars competitions scaraped:")
print([(i,len(data_pokerstar[data_pokerstar.league==str(i)])) for i in data_pokerstar.league.unique()]) #check number of line for competition
print("---")
print("total betfair competitions scaraped:")
print([(i,len(data_betfair[data_betfair.league==str(i)])) for i in data_betfair.league.unique()])
print('-------------------------------')
#ONLY FOR DEGUB------------------------------------------------------------'''

#PRUNING DATAFRAME TO HAVE THE SAME NUMBER OF LEAGUE AND DATES
data_pokerstar = pd.merge(data_pokerstar,data_betfair,on=["league","date"],how='outer',indicator=True,suffixes=("","_y"))
data_pokerstar = data_pokerstar.loc[data_pokerstar._merge=='both'].drop(["_merge","home_team_y","away_team_y","selection_y","lay_price","lay_size"],axis=1)
data_pokerstar = data_pokerstar.drop_duplicates()
#print(data_pokerstar.loc[data_pokerstar.league=="Portogallo - Primeira Liga"])
data_betfair = pd.merge(data_betfair,data_pokerstar,on=["league","date"],how='outer',indicator=True,suffixes=("","_y"))
data_betfair = data_betfair.loc[data_betfair._merge=='both'].drop(["_merge","home_team_y","away_team_y","selection_y","odd"],axis=1)
data_betfair = data_betfair.drop_duplicates()


'''#ONLY FOR DEGUB------------------------------------------------------------
print("pokerstars pruned :")
print([(i,len(data_pokerstar[data_pokerstar.league==str(i)])) for i in data_pokerstar.league.unique()]) #check number of line for competition
print("---")
print("betfair pruned :")
print([(i,len(data_betfair[data_betfair.league==str(i)])) for i in data_betfair.league.unique()])
print('-------------------------------')
#ONLY FOR DEGUB------------------------------------------------------------'''


#---------------------------------------------------------------------------
#START AT LINKING THE TWO DATAFRAME
#JUST ONE COMPETITION




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

#DATES LOOP
dates=tmp_betfair["date"].unique()
#LOOP OVER DATES<-------------------------
#for debug only 1
date_1=dates[0]
print("first date: ",date_1)


#SUBDATAFRAMES FOR THE DATE
events_bf = tmp_betfair.loc[(tmp_betfair["date"]==date_1,["home_team","away_team"])].value_counts()
events_bf=events_bf.keys().to_frame(index=False) #PANDAS SERIES to DATAFRAME
len_bf=len(events_bf)
print("----------------------")
print("EVENTS ON THIS SPECIFIC DATETIME : ",date_1)
print("betfair sub_dataframe:")
print(events_bf)

events_ps = tmp_poker.loc[(tmp_poker["date"]==date_1,["home_team","away_team"])].value_counts()
events_ps=events_ps.keys().to_frame(index=False) #PANDAS SERIES to DATAFRAME
len_ps=len(events_ps)
print("--------")
print("pokerstar sub_dataframe:")
print(events_ps)
print("---------------------")


def find_min_distance(event_ref,events_obs):
	# event_ref is the SINGLE EVENT use as reference PANDAS SERIES only one line
	# events_obs is the DATAFRAME with all the events of other tmp dataframe
	distance_home = {}
	distance_away = {}
	for event in events_obs.iloc:
		distance_home[event["home_team"]] = jaro(event_ref["home_team"], event["home_team"])
		distance_away[event["away_team"]] = jaro(event_ref["away_team"], event["away_team"])
	home_name = max(distance_home, key=distance_home.get)
	away_name = max(distance_away, key=distance_away.get)
	#home_name and away_name are from event_obs
	return home_name,away_name

def add_team_name(event,home_name,away_name,dict_teams,dict_team_filename,IS_BETFAIR_SHORTER):
	if IS_BETFAIR_SHORTER:
		dict_teams[event["home_team"]] = home_name
		dict_teams[event["away_team"]] = away_name
		save_json_file(dict_team_filename, dict_teams)
	else:
		dict_teams[home_name] = event["home_team"]
		dict_teams[away_name] = event["away_team"]
		save_json_file(dict_team_filename, dict_teams)

def slicing(dict_teams,tmp_poker,tmp_betfair,obs_events,home_index,competition,date,home_name,away_name):
	# CREATE SLICE TO ADD AT FINAL DATAFRAME
	# ONE FOR EVERY SELECTION
	slice_ps = tmp_poker.loc[(tmp_poker["league"] == competition) & (tmp_poker["home_team"] == home_name) & (
				tmp_poker["away_team"] == away_name) & (tmp_poker["date"] == date)]
	slice_bf = tmp_betfair.loc[
		(tmp_betfair["league"] == competition) & (tmp_betfair["home_team"] == dict_teams[home_name]) & (
					tmp_betfair["away_team"] == dict_teams[away_name]) & (tmp_betfair["date"] == date)]
	# THERE IS ALWAYS THE POSSIBILITIES THAT BETFAIR AND POKERSTAR DON'T SHARE SAME TEAM NAMES
	slice_bf = slice_bf.replace(dict_teams[home_name], home_name)
	slice_bf = slice_bf.replace(dict_teams[away_name], away_name)
	# SLICE OF FINAL DATABASE TO RETURN
	slice = pd.merge(slice_ps, slice_bf, on=["league", "home_team", "away_team", "date", "selection"])
	print(slice)
	# DROP EVENT FROM OBSERVED SUBDATAFRAME
	# can happen that it produce an empty dataframe<-----------------------------------ADD a CHECK AT THE BEGINING TO CHECK IF SUBDATAFRAME IS NOT EMPTY
	obs_events = obs_events.drop(home_index)
	# RETURN obs_events AND slice
	return slice, obs_events

'''def check_index(home_name, away_name,home_index,away_index,tmp_poker,first_comp,date_1,tmp_betfair,obs_events,event1_ref,dict_teams, dict_team_filename, IS_BETFAIR_SHORTER):
	if home_index == away_index:
		# SAVE NEW COUPLES IN TEAM_DICT
		add_team_name(event1_ref, home_name, away_name, dict_teams, dict_team_filename, IS_BETFAIR_SHORTER)
		slice, obs_events = slicing(dict_teams, tmp_poker, tmp_betfair, obs_events, home_index, first_comp, date_1,home_name, away_name)
		return slice, obs_events
	else:
		print("##########################################################################")
		print("#      WE HAVE A PROBLEM!!!! THE PROGRAM TRY TO FIND LINK BETWEEN: 		#")
		print("##########################################################################")
		print(event1_ref, obs_events)
		print("THE PROGRAM THINKS THAT :", event["home_team"], ":", home_name, "   and   ", event["away_team"], ":",
			  away_name)
		raise ValueError(
			"The Program didn't find an unique correlation between pokerstar and betfair subdataframe\ndate : ", date_1," leauge : ", first_comp)
'''
'''def link_single_event(event1_ref,obs_events,dict_teams, dict_team_filename, IS_BETFAIR_SHORTER):
	#FIRST CHECK IF THE TEAM ON THE EVENT ALREADY EXIST IN TEAM DICT
	if not event1_ref["home_team"] in dict_teams or not event1_ref["away_team"] in dict_teams:
		#find the index of the observed dataframe with closer team_name
		#use Levenshtein distance
		home_name, away_name = find_min_distance(event1_ref, obs_events)
		#INDEX OF CORRISPONDING ROW IN THE OBSERVED SUBDATAFRAME
		home_index = obs_events["home_team"].loc[lambda x: x == home_name].index
		away_index = obs_events["away_team"].loc[lambda x: x == away_name].index
		slice, obs_event = check_index(home_name, away_name, home_index, away_index, tmp_poker, first_comp, date_1, tmp_betfair,obs_events, event1_ref, dict_teams, dict_team_filename, IS_BETFAIR_SHORTER)
	else:
		#USE SIMPLY THE VALUE IN TEAM_DICT
		home_name = event1_ref["home_team"] 				#REFERENCE NOTATION
		home_name = dict_teams[event1_ref["home_team"]] 	#OBSERVED NOTATION
		away_name = event1_ref["away_team"]  # REFERENCE NOTATION
		away_name = dict_teams[event1_ref["away_team"]]  # OBSERVED NOTATION

		home_index = obs_events["home_team"].loc[lambda x: x == home_name].index
		away_index = obs_events["away_team"].loc[lambda x: x == away_name].index
		slice, obs_events = check_index(home_name, away_name, home_index, away_index, tmp_poker, first_comp, date_1, tmp_betfair,obs_events, event1_ref, dict_teams, dict_team_filename, IS_BETFAIR_SHORTER)
	return slice,obs_events
'''

#CONTINUARE A RIMUOVERE VARIABILI, PROSSIMO È add_team_name <------------------------------------------------------------------------------
def check_index(event,home_name, away_name,home_index,away_index,linking_data):
	if home_index == away_index:
		# SAVE NEW COUPLES IN TEAM_DICT
		add_team_name(event, home_name, away_name, linking_data.dict.team_dict, linking_data.dict.dict_team_filename, linking_data.IS_BETFAIR_SHORTER)
		slice, linking_data.obs_events = slicing(linking_data.dict.team_dict, linking_data.dataframe.tmp_ps, linking_data.dataframe.tmp_bf , linking_data.obs_events, home_index, linking_data.current_competition, linking_data.current_date,home_name, away_name)
		return slice, linking_data.obs_events #RETURN INUTILE!!!!!
	else:
		print("##########################################################################")
		print("#      WE HAVE A PROBLEM!!!! THE PROGRAM TRY TO FIND LINK BETWEEN: 		#")
		print("##########################################################################")
		print(event1_ref, linking_data.obs_events)
		print("THE PROGRAM THINKS THAT :", event["home_team"], ":", home_name, "   and   ", event["away_team"], ":",away_name)
		raise ValueError(
			"The Program didn't find an unique correlation between pokerstar and betfair subdataframe\ndate : ", linking_data.current_date," league : ", linking_data.current_competition)


def link_single_event(event1_ref,linking_data):
	#FIRST CHECK IF THE TEAM ON THE EVENT ALREADY EXIST IN TEAM DICT
	if not event1_ref["home_team"] in linking_data.dict.team_dict or not event1_ref["away_team"] in linking_data.dict.team_dict:
		#find the index of the observed dataframe with closer team_name
		#use Levenshtein distance
		home_name, away_name = find_min_distance(event1_ref, linking_data.obs_events)
		#INDEX OF CORRISPONDING ROW IN THE OBSERVED SUBDATAFRAME
		home_index = linking_data.obs_events["home_team"].loc[lambda x: x == home_name].index
		away_index = linking_data.obs_events["away_team"].loc[lambda x: x == away_name].index
		slice, linking_data.obs_events = check_index(event1_ref, home_name, away_name, home_index, away_index, linking_data) #RETURN INUTILE!!!!!
	else:
		#USE SIMPLY THE VALUE IN TEAM_DICT
		home_name = event1_ref["home_team"] 				#REFERENCE NOTATION
		home_name = linking_data.dict.team_dict[event1_ref["home_team"]] 	#OBSERVED NOTATION
		away_name = event1_ref["away_team"]  # REFERENCE NOTATION
		away_name = linking_data.dict.team_dict[event1_ref["away_team"]]  # OBSERVED NOTATION

		home_index = linking_data.obs_events["home_team"].loc[lambda x: x == home_name].index
		away_index = linking_data.obs_events["away_team"].loc[lambda x: x == away_name].index
		slice, linking_data.obs_events = check_index(event1_ref,home_name, away_name, home_index, away_index,linking_data) #RETURN INUTILE!!!!!
	return slice,obs_events

'''def link_date_subdataframe(final_dataframe,ref_events,obs_events,dict_teams, dict_team_filename, IS_BETFAIR_SHORTER):
	#Link team names over date subdataframe
	for event in ref_events.iloc:
		#loop over row of reference dataframe (the shortest)
		slice, obs_events = link_single_event(event, obs_events, dict_teams, dict_team_filename, IS_BETFAIR_SHORTER)
		#ADD pd.concat WITH final_database
		final_dataframe = pd.concat([final_dataframe, slice], ignore_index=True)
		print("------------------------------------\nFinal Dataframe:")
		print(final_dataframe)
'''

def link_date_subdataframe(linking_data):
	#Link team names over date subdataframe
	ref_events=linking_data.ref_events
	# obs_events == linking_data.obs_events
	for event in ref_events.iloc:
		#loop over row of reference dataframe (the shortest)
		slice, linking_data.obs_events = link_single_event(event, linking_data) #RETURN INUTILE!!!!!
		#ADD pd.concat WITH final_database
		linking_data.final_dataframe = pd.concat([linking_data.final_dataframe, slice], ignore_index=True)
		print("------------------------------------\nFinal Dataframe:")
		print(linking_data.final_dataframe)




#initialize the final dataframe
final_dataframe=pd.DataFrame(columns=['league','home_team','away_team','date','selection','odd','lay_price','lay_size'])

# WE USE THE SHORTEST DATAFRAME AS REFERENCE AND LOOP OVER THE OBSERVED DATAFRAME LINKING THE NAME OF TEAMS
#FIRST THE MOST COMMON CASE
#lenbf < lenps
if len_bf>=len_ps:
	IS_BETFAIR_SHORTER = True
	ref_events = events_bf
	obs_events = events_ps
#IN CASE lenbf>lenps
else:
	IS_BETFAIR_SHORTER = False
	ref_events = events_ps
	obs_events = events_bf

#----------------------------------------------------------------------
#CREATE CLASS OBJECT TO BEEN USED AS MEMEORY FOR ALL THE PARAMETERS NEEDED
class Dict():
	def __init__(self, team_dict, dict_team_filename):
		self.team_dict = team_dict
		self.dict_team_filename = dict_team_filename
class Dataframes():
	def __init__(self,tmp_ps,tmp_bf):
		self.tmp_ps=tmp_ps
		self.tmp_bf=tmp_bf
class LinkingVariables():
	def __init__(self,current_date,current_competition,tmp_ps,tmp_bf,ref_events,obs_events,dict_teams,dict_team_filename,IS_BETFAIR_SHORTER):
		self.dataframe=Dataframes(tmp_ps,tmp_bf)
		self.current_date=current_date
		self.current_competition=current_competition
		self.ref_events=ref_events
		self.obs_events=obs_events
		self.dict=Dict(dict_teams,dict_team_filename)
		self.IS_BETFAIR_SHORTER=IS_BETFAIR_SHORTER
	final_dataframe=pd.DataFrame(columns=['league','home_team','away_team','date','selection','odd','lay_price','lay_size'])

#-----------------------------------------------------

linking_data=LinkingVariables(date_1,first_comp,tmp_poker,tmp_betfair,ref_events,obs_events,dict_teams,dict_team_filename,IS_BETFAIR_SHORTER)

'''link_date_subdataframe(final_dataframe,ref_events,obs_events,dict_teams, dict_team_filename, IS_BETFAIR_SHORTER)
'''
link_date_subdataframe(linking_data)
