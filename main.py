#!/opt/miniconda3/bin/python

import requests
from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import pandas as pd
pd.set_option('display.max_columns', None) #FOR DEBUG


#with sync_playwright() as p:
#    browser = p.chromium.launch()
#    context = browser.new_context()
#    page = context.new_page()
#    page.goto("https://www.forbes.com/billionaires")
#    page.click("button.trustarc-agree-btn")
#    # print(context.cookies())
#    cookie_for_requests = context.cookies()[3]['value']
#    browser.close()

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

def download_json(url,headers,querystring,payload="",filename="dati.json"):
	response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
	save_json_file(filename, response)

def list_to_dataframe(list,col_names):
	list=dict(zip(col_names,list))
	list=pd.DataFrame([list])
	return list
def odds_1x2(json_object):
	for team in json_object['participants']['participant']:
		if team['type']=="AWAY":
			away_team = team['name']
		elif team['type']=="HOME":
			home_team = team['name']
	t = json_object['eventTime'] / 1000 + 7200  # ms -> s   and then +2h since time is in unixstamp UTC, (I live in Rome UTC+2)
	t = datetime.utcfromtimestamp(t).strftime('%d-%m-%Y %H:%M:%S')  # from timestamp to date/time
	for market in json_object['markets'][0]['selection']:
		if market['type']=='A':
			odd_home=market['odds']['dec']
		elif market['type']=='Draw':
			odd_draw = market['odds']['dec']
		elif market['type'] == 'B':
			odd_away = market['odds']['dec']
	return home_team,away_team,t,odd_home,odd_draw,odd_away

def odds_UO25(json_object):
	for team in json_object['participants']['participant']:
		if team['type']=="AWAY":
			away_team = team['name']
		elif team['type']=="HOME":
			home_team = team['name']
	for market in json_object['markets']:
		if market['line']==2.5:
			for selection in market['selection']:
				if selection['type']=='Under':
					odd_u = selection['odds']['dec']
				elif selection['type']=='Over':
					odd_o = selection['odds']['dec']
			break
	return list_to_dataframe([home_team,away_team,odd_o,odd_u],['home_team','away_team','over25','under25'])



url_cookie='https://www.pokerstars.it/sports/#/soccer/competitions' #URL for cookie assigment
cookie = get_cookie_playwright_pokerstar(url_cookie) #URL generic for the cookie
url = "https://sports.pokerstars.it/sportsbook/v1/api/getSportTree" #URL for the json
querystring = {"sport":"SOCCER","channelId":"3","locale":"it-it"}
payload = ""
headers = {"Cookie": cookie}
#download_json(url,headers,querystring,payload,"event_tree.json")  #Competition Tree


#EVENT TREE INITIALIZATION
#The ID of the competition is required for extract the corrispondent JSON for each competation
comp_tree_data=open_json_file("event_tree.json")
#ONLY MOST IMPORTAT
comp_id=[]
comp_name=[]
for comp in comp_tree_data['popularCompetitions']:
	comp_id.append(comp["id"])
	comp_name.append(comp["name"])

#print(dict(zip(comp_name,comp_id)))

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
querystring = {"competitionId": id,"marketTypes":"SOCCER:FT:AXB,MRES","channelId":"3","locale":"it-it"}
payload = ""
headers = {"Cookie": cookie}
download_json(url,headers,querystring,payload,"dati.json")
dati_1x2 = open_json_file("dati.json")

col_names=['home_team','away_team','date','home','x','away']
home_away=pd.DataFrame(columns=col_names) #DATAFRAME FOR 1x2

for event in dati_1x2['event']:
	new=odds_1x2(event)
	new=list_to_dataframe(new,col_names)
	home_away = pd.concat([home_away, new], ignore_index=True)



#THEN U25 O25
#different querystring
querystring = {"competitionId":"15414240","marketTypes":"SOCCER:FT:OU,OVUN","channelId":"3","locale":"it-it"}
download_json(url,headers,querystring,payload,"dati.json") #overide the same file
dati=open_json_file("dati.json")




col_names=['home_team','away_team','over25','under25']
u_o_25_dataset=pd.DataFrame(columns=col_names)
for event in dati['event']:
	new=odds_UO25(event)
	u_o_25_dataset = pd.concat([u_o_25_dataset, new], ignore_index=True)


print(pd.merge(home_away,u_o_25_dataset, how='outer'))