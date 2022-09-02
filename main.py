#!/opt/miniconda3/bin/python

import requests
from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import pandas as pd
pd.set_option('display.max_columns', None) #FOR DEBUG

def get_cookie_playwright():
	with sync_playwright() as p:
		#browser = p.chromium.launch(headless=None, slow_mo=50)   #for debugging
		browser = p.chromium.launch()
		context = browser.new_context()
		page = context.new_page()
		page.goto("https://www.eurobet.it/it/scommesse/#!/")
		cookie_for_requests=context.cookies()
		browser.close()
	return cookie_for_requests

def get_cookie_playwright_pokerstar(URL):
	with sync_playwright() as p:
		#browser = p.chromium.launch(headless=None, slow_mo=50)   #for debugging
		browser = p.chromium.launch()
		context = browser.new_context()
		page = context.new_page()
		page.goto(URL)
		cookie_for_requests=context.cookies()
		browser.close()
		cookie_for_requests = f"{cookie_for_requests[0]['name']}={cookie_for_requests[0]['value']}"
		#cookie=(f'{cookie_for_requests[0]["name"]}={cookie_for_requests[0]["value"]}') #Formatting the cookie in the correct format
	return cookie_for_requests

def save_json_file(filename,response):
	with open(filename, 'w') as outfile:
		json.dump(json.loads(response.text), outfile, indent=2)

def open_json_file(filename):
	with open(filename) as json_file:
		json_data = json.load(json_file)
	return json_data

def download_json(url,headers,querystring,filename="dati.json",payload=""):
	response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
	save_json_file(filename, response)

def list_to_dataframe(list,col_names=['league','home_team','away_team','date','selection','odd']):
	list=dict(zip(col_names,list))
	list=pd.DataFrame([list])
	return list

def init_data():
	col_names = ['league', 'home_team', 'away_team', 'date', 'selection', 'odd']
	data = pd.DataFrame(columns=col_names)  # DATAFRAME FOR 1x2
	return data

def t_timestamp(t):
	t = t / 1000 + 7200  # ms -> s   and then +2h since time is in unixstamp UTC, (I live in Rome UTC+2)
	t = datetime.utcfromtimestamp(t).strftime('%d-%m-%Y %H:%M:%S')  # from timestamp to date/time
	return t

def team_league_date(json_object):
	for team in json_object['participants']['participant']:
		if team['type']=="AWAY":
			away_team = team['name']
		elif team['type']=="HOME":
			home_team = team['name']
	league=json_object['compName']
	t = t_timestamp(json_object['eventTime'])
	return home_team,away_team,league,t

def loop_league(json_object,f):
	dataset=init_data()
	for event in json_object['event']:
		dataset = pd.concat([dataset,f(event)], ignore_index=True)
	return dataset

def odds_goal(json_object):
	home_team,away_team,league,t = team_league_date(json_object)
	for market in json_object['markets']:
		for selection in market['selection']:
				if selection['type']=='No':
					selection_no="NOGOAL"
					odd_no = selection['odds']['dec']
				elif selection['type']=='Yes':
					selection_goal = "GOAL"
					odd_goal = selection['odds']['dec']
	goal = [league, home_team, away_team, t, selection_goal, odd_goal]
	goal = list_to_dataframe(goal)
	nogoal = [league, home_team, away_team, t, selection_no, odd_no]
	nogoal = list_to_dataframe(nogoal)
	out = pd.concat([goal, nogoal], ignore_index=True)
	return out

def odds_1x2(json_object):
	home_team, away_team, league, t = team_league_date(json_object)
	for market in json_object['markets'][0]['selection']:
		if market['type']=='A':
			selection_1 = market['name']
			odd_1=market['odds']['dec']
		elif market['type']=='Draw':
			selection_x = market['name']
			odd_x = market['odds']['dec']
		elif market['type'] == 'B':
			selection_2 = market['name']
			odd_2 = market['odds']['dec']
	home=[league,home_team,away_team,t,selection_1,odd_1]
	home=list_to_dataframe(home)
	draw=[league,home_team,away_team,t,selection_x,odd_x]
	draw = list_to_dataframe(draw)
	away=[league,home_team,away_team,t,selection_2,odd_2]
	away = list_to_dataframe(away)
	odds=pd.concat([home,draw,away],ignore_index=True)
	return odds

def odds_UO25(json_object):
	home_team,away_team,league,t = team_league_date(json_object)
	for market in json_object['markets']:
		if market['line']==2.5:
			for selection in market['selection']:
				if selection['type']=='Under':
					selection_u=selection['name']
					odd_u = selection['odds']['dec']
				elif selection['type']=='Over':
					selection_o = selection['name']
					odd_o = selection['odds']['dec']
			break
	under = [league, home_team, away_team, t, selection_u, odd_u]
	under = list_to_dataframe(under)
	over = [league, home_team, away_team, t, selection_o, odd_o]
	over = list_to_dataframe(over)
	out = pd.concat([over, under], ignore_index=True)
	return out


url_cookie='https://www.pokerstars.it/sports/#/soccer/competitions' #URL for cookie assigment
cookie = get_cookie_playwright_pokerstar(url_cookie) #URL generic for the cookie
url = "https://sports.pokerstars.it/sportsbook/v1/api/getSportTree" #URL for the json
querystring = {"sport":"SOCCER","locale":"it-it"}
headers = {"Cookie": cookie}
download_json(url,headers,querystring,"event_tree.json")  #Competition Tree


#EVENT TREE INITIALIZATION
#The ID of the competition is required for extract the corrispondent JSON for each competation
comp_tree_data=open_json_file("event_tree.json")
#ONLY MOST IMPORTAT
comp_id=[]
comp_name=[]
for comp in comp_tree_data['popularCompetitions']:
	comp_id.append(comp["id"])
	comp_name.append(comp["name"])

print(dict(zip(comp_name,comp_id)))

'''#ALL COMPETITTIONA
comp_id=[]
comp_name=[]
for league in comp_tree_data['categories']:
	for comp in league["competition"]:
		comp_id.append(comp["id"])
		comp_name.append(comp["name"])

n_comp = 70
print(dict(zip(comp_name[0:n_comp],comp_id[0:n_comp])))'''


#1° COMPETIZIONE
#TEST for ID number 0  <----------------------------------------------------------------
id=comp_id[0]

# FIRST   HOME-DRAW-AWAY ODDS
url = "https://sports.pokerstars.it/sportsbook/v1/api/getCompetitionEvents"
querystring = {"competitionId": id,"marketTypes":"SOCCER:FT:AXB,MRES","locale":"it-it"}
headers = {"Cookie": cookie}
download_json(url,headers,querystring,"dati.json")
data_1x2 = open_json_file("dati.json")
dataset_1x2 = loop_league(data_1x2,odds_1x2)

#THEN U25 O25
#different querystring
querystring = {"competitionId":"15414240","marketTypes":"SOCCER:FT:OU,OVUN","locale":"it-it"}
download_json(url,headers,querystring,"dati.json") #overide the same file
data_uo=open_json_file("dati.json")
dataset_uo = loop_league(data_uo,odds_UO25)

#THEN GOALNOGOAL
#different querystring
querystring = {"competitionId":"15414240","marketTypes":"SOCCER:FT:BTS,BTSC","locale":"it-it"}
download_json(url,headers,querystring,"dati.json") #overide the same file
data_goal=open_json_file("dati.json")
dataset_goal=loop_league(data_goal,odds_goal)


#print(pd.concat([dataset_1x2,dataset_uo,dataset_goal], ignore_index=True))




