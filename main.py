#!/opt/miniconda3/bin/python

import requests
from playwright.sync_api import sync_playwright
import json
from datetime import datetime

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

def odds_1x2(json_object):
	home_team = json_object['participants']['participant'][1]['name']  # HOME TEAM NAME
	away_team = json_object['participants']['participant'][0]['name']  # AWAY TEAM NAME
	t = json_object['eventTime'] / 1000 + 7200  # ms -> s   and then +2h since time is in unixstamp UTC, (I live in Rome UTC+2)
	t = datetime.utcfromtimestamp(t).strftime('%d-%m-%Y %H:%M:%S')  # from timestamp to date/time
	odd_home = json_object['markets'][0]['selection'][0]['odds']['dec']  # HOME WIN
	odd_draw = json_object['markets'][0]['selection'][1]['odds']['dec']  # DRAW
	odd_away = json_object['markets'][0]['selection'][2]['odds']['dec']  # AWAY WIN
	return [home_team,away_team],[t],[odd_home,odd_draw,odd_away]

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
#download_json(url,headers,querystring,payload,"dati.json")
dati_1x2 = open_json_file("dati.json")
odds=[]
for event in dati_1x2['event']:
	odds.append(odds_1x2(event))

#THEN U25 O25


for event in odds:
	print(f'{event[0][0]:^25} - {event[0][1]:^25} | {event[1][0]:^20} | 1:{event[2][0]:5}  X:{event[2][1]:5}  2:{event[2][2]:5}')


#info=odds_1x2(dati['event'][0])
#print(f'{info[0][0]:^15} - {info[0][1]:^15} | {info[1][0]:^15} | 1:{info[2][0]:3}  X:{info[2][1]:3}  2:{info[2][2]:3}')