import requests
from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import pandas as pd
pd.set_option('display.max_columns', None) #FOR DEBUG
#pd.set_option('display.max_row', None) #FOR DEBUG

def get_cookie(URL):
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

def download_json(url,headers,querystring,filename="dati.json",payload="",save=False):
	response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
	json_object=json.loads(response.text)
	if save:
		save_json_file(filename, response)
	return json_object

def list_to_dataframe(list,col_names=['league','home_team','away_team','date','selection','odd']):
	list=dict(zip(col_names,list))
	list=pd.DataFrame([list])
	return list

def init_data(col_names = ['league', 'home_team', 'away_team', 'date', 'selection', 'odd']):
	data = pd.DataFrame(columns=col_names)  # DATAFRAME FOR 1x2
	return data

def name_id_tree(json_object):
	name = json_object['name']
	ID = json_object['id']
	data = list_to_dataframe([name, ID], ["name", "id"])
	return data

def tree_popular(json_object):
	data = init_data(col_names=["name","id"])
	for event in json_object['popularCompetitions']:
		data = pd.concat([data, name_id_tree(event)], ignore_index=True)
	return data

def extract_competition_id(url,headers,querystring):
	data_tree = download_json(url, headers, querystring)
	comp_id = tree_popular(data_tree)
	return comp_id

def t_timestamp(t):
	t = t / 1000 + 7200  # ms -> s   and then +2h since time is in unixstamp UTC, (I live in Rome UTC+2)
	#t = datetime.utcfromtimestamp(t).strftime('%d-%m-%Y %H:%M:%S')  # from timestamp to date/time
	t = datetime.utcfromtimestamp(t)
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
	selection_no=''
	selection_goal=''
	odd_no=0
	odd_goal=0
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
	selection_u=""
	selection_o=""
	odd_u=0
	odd_o=0
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

def extract_odds(competitionid,market,url_comp,headers,f,save=False):
	querystring = {"competitionId": str(competitionid), "marketTypes": market, "locale": "it-it"}
	data=download_json(url_comp,headers,querystring,"dati.json",save)
	dataset=loop_league(data,f)
	return dataset


def dataframe_load():
	# Constant Variables
	url_cookie = 'https://www.pokerstars.it/sports/#/soccer/competitions'  # URL for cookie assigment
	url_tree = 'https://sports.pokerstars.it/sportsbook/v1/api/getSportTree'  # URL for the json
	url_comp = 'https://sports.pokerstars.it/sportsbook/v1/api/getCompetitionEvents'
	# Headers don't change inside the program
	headers = {"Cookie": get_cookie(url_cookie)}
	markets = {"home_x_away": "SOCCER:FT:AXB,MRES", "under_over": "SOCCER:FT:OU,OVUN",
			   "goal_nogoal": "SOCCER:FT:BTS,BTSC"}
	quary_tree = {"sport": "SOCCER", "locale": "it-it"}
	# EVENT TREE
	# We need to extract the id for the competitions we want to track
	comp_id = extract_competition_id(url_tree, headers, quary_tree)   #Here other competitions can be added

	# COMPETITIONS SCRAPING 1X2, UNDER/OVER2.5, GOAL/NOGOAL
	# for downloading the json we need
	#				-The league ID
	#				-the market identification header <--- Always the same
	# Result is a DataFrame with columns = league', 'home_team', 'away_team', 'date', 'selection', 'odd'
	data_total = init_data()
	for id in comp_id['id']:
		dataset_1x2 = extract_odds(id, markets["home_x_away"],url_comp,headers, odds_1x2)						# FIRST   HOME-DRAW-AWAY ODDS
		dataset_uo = extract_odds(id, markets["under_over"],url_comp,headers, odds_UO25)						#THEN U25 O25
		dataset_goal = extract_odds(id, markets["goal_nogoal"],url_comp,headers, odds_goal)						#THEN GOALNOGOAL
		data_total = pd.concat([data_total, dataset_1x2, dataset_uo, dataset_goal], ignore_index=True)
	return data_total

if __name__ == "__main__":
	data=dataframe_load()
	print(data.league.unique())





'''
# TO DO
# add other important competitions from the generic list "categories"
comp_id=[]
comp_name=[]
for league in comp_tree_data['categories']:
	for comp in league["competition"]:
		comp_id.append(comp["id"])
		comp_name.append(comp["name"])
n_comp = 70
print(dict(zip(comp_name[0:n_comp],comp_id[0:n_comp])))'''