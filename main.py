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
	data_betfair.to_csv(betfair_save_filename, index=False)
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

#---------------------------------------------------------------------------
#START AT LINKING THE TWO DATAFRAME
#JUST ONE COMPETITION
print("---------------------------LINKING")
first_comp=data_pokerstar["league"].unique()[0]
print(first_comp)
tmp_poker=data_pokerstar[data_pokerstar["league"]==first_comp] #SUB DATAFRAME WITH ONLY THE COMPETITION
dates=tmp_poker["date"].unique() #LISTS OF EVENTS
data_1=dates[0]
print(data_1)
events=tmp_poker.loc[(tmp_poker["date"]==data_1,["home_team","away_team"])] # BISOGNA ESTRARRE LE SINGLE COPPIE
home_teams=events["home_team"].unique() #BISOGNA FARE UNA COSA TIPO QUESTA MA SULLA COPPIA

#print(type(datetime.datetime.strptime(data_1, '%Y-%m-%d %H:%M:%S')))

tmp_betfair=data_betfair[data_betfair["league"]==first_comp]
#print(tmp_betfair[tmp_betfair["date"]==data_1])