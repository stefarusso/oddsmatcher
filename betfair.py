from credentials import ap_key, usr, psw #For obvious reason those are not uploaded on github ;)
import requests
import json
import scraperPS as sps
import datetime
import betfairlightweight
import pandas as pd




#USEFULL ONLY IN DEBUGGING----------------------------------------------------------------------------------------------------------------------------------------
#pd.set_option('display.max_columns', None) #FOR DEBUG
#pd.set_option('display.max_row', None) #FOR DEBUG

def get_ssoid(usr,psw,ap_key,certificates,url):
    payload = 'username=' + usr + '&password=' + psw
    headers = {'X-Application': ap_key, 'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(url, data=payload,cert=certificates,headers=headers)
    response=response.json()
    if response['loginStatus'] == 'SUCCESS':
        sessontoken = response['sessionToken']
    else:
        print('Houston we have a problem!!!')
        print('login status betfair API = ' + resp_json['loginStatus'])
        print('all the return codes are available here https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/Non-Interactive+%28bot%29+login')
    return response['sessionToken']


#GET THE SESSION TOKEN
#non_interactive_login_url='https://identitysso-cert.betfair.it/api/certlogin'    #Just for get the session token SSOID on the italian website
#certificates=('certificates/betfair_api.crt','certificates/betfair_api.key') #local position of my XRC certificates and secret key
#ssoid=get_ssoid(usr,psw,ap_key,certificates,non_interactive_login_url)
#print("ssoid:" + ssoid)
#USEFULL ONLY IN DEBUGGING-------------------------------------------------------------------------------------------------------------------------------------------






def open_json_file(filename):
	with open(filename) as json_file:
		json_data = json.load(json_file)
	return json_data

def save_json_file(filename,object):
	with open(filename, 'w') as outfile:
		json.dump(object, outfile,indent=2)

def init_data(col_names = ['league', 'home_team', 'away_team', 'date', 'selection', 'lay_price','lay_size']):
    data = pd.DataFrame(columns=col_names)  # DATAFRAME FOR 1x2
    return data

def list_to_dataframe(List,col_names=['league', 'home_team', 'away_team', 'date', 'selection', 'lay_price','lay_size']):
    List=dict(zip(col_names,List))
    List=pd.DataFrame([List])
    return List

#FUNTION USED BY initialize_competition_dict()
#CHECK WOMAN (F) F=Femminile COMPETITIONS
def filter_competition_id(pokerstar_name,competitions,dictionary):
    for object in competitions :
        if not "(F)" in object.competition.name:
            dictionary[pokerstar_name]=object.competition.id
    return dictionary

#FUNTION USED BY initialize_competition_dict()
#API REQUEST OF THE COMPETITION ID
def extract_1_competition_id(competition_dict,competitions_pokerstar,soccer_id,datetime_in_a_week):
    competition_filter = betfairlightweight.filters.market_filter(event_type_ids=soccer_id,text_query=competitions_pokerstar,market_start_time={'to': datetime_in_a_week})
    competitions = trading.betting.list_competitions(filter=competition_filter, locale="it")
    competition_dict = filter_competition_id(competitions_pokerstar, competitions, competition_dict)
    return competition_dict

#FUNTION USED BY initialize_competition_dict()
def extract_all_competition_id(competition_dict, competitions_pokerstar, soccer_id,datetime_in_a_week):
    for competition in competitions_pokerstar:
        if competition not in competition_dict:
            competition_dict = extract_1_competition_id(competition_dict, competition, soccer_id,datetime_in_a_week)
    return competition_dict


#CREATE THE DICTIONARY CONTAINING {COMPETITION NAME : COMPETITION ID}
def initialize_competition_dict(filename,competitions_pokerstar, soccer_id,datetime_in_a_week):
    try:
        competition_dict = open_json_file(filename)
    except:
        competition_dict = {}
    competition_dict = extract_all_competition_id(competition_dict, competitions_pokerstar, soccer_id,datetime_in_a_week)
    save_json_file(filename, competition_dict)
    return competition_dict

#API REQUEST OF THE COMPETITIONS ID. LIKE SERIE A , CHAMPIONS LEAUGE...
def request_event_list(trading,soccer_id,competition_id):
    event_filter = betfairlightweight.filters.market_filter(event_type_ids=soccer_id,competition_ids=competition_id,market_start_time={'to': (datetime.datetime.utcnow() + datetime.timedelta(weeks=1)).strftime("%Y-%m-%dT%TZ")})
    events=trading.betting.list_events(filter=event_filter)
    return events

#FROM LIST OF STRING FROM scraperPS TO A LIST OF STRING WITH CORRECT COMPETITION ID
def dict_to_list(competition_dict,competitions_pokerstar):
    out_list=[]
    for comp in competitions_pokerstar:
        try:
            out_list.append(competition_dict[comp])
        except KeyError as err:
            print(comp + " Not found on Betfair !!!")
    return out_list

#FORMATTING THE EVENT ID LIST AS A LIST OF STRINGS
def extract_event(event_list):
    event_l = []
    for event in event_list:
        event_l.append(str(event.event.id))
    return event_l

#FUNCTION WHO EXCTRACT THE MARKET IDS FOR THE EVENT WE WONT
def extract_market_catalogue(trading,event_id):
    markets_set = ["MATCH_ODDS", "OVER_UNDER_25", "BOTH_TEAMS_TO_SCORE"]
    betfair_to_pokerstars = {'Over 2,5 goal': 'Over 2.5', 'Under 2,5 goal': 'Under 2.5', 'Sì': 'GOAL', 'No': 'NOGOAL'}
    market_catalogue_filter = betfairlightweight.filters.market_filter(event_ids=event_id,market_type_codes=markets_set)
    market_catalogues = trading.betting.list_market_catalogue(filter=market_catalogue_filter, locale="it", max_results='1000',market_projection=['RUNNER_DESCRIPTION', 'EVENT','COMPETITION'],sort='FIRST_TO_START')
    selection_dict = {}
    market_dict= {}
    #print(market_catalogues)
    #print(event_id)
    #print(json.dumps(json.loads(market_catalogues[2].json()), indent=2))
    for market in market_catalogues:
        market_id = market.market_id
        name = market.event.name
        date = market.event.open_date + datetime.timedelta(hours=2)
        date = date.strftime('%d-%m-%Y %H:%M:%S')  ### TO DELEATE ###
        comp = market.competition.name
        for runner in market.runners:
            market_dict[str(market_id)] = { "event_name" : name,  "date" : date, "competition_name" : comp }
            selection_name=runner.runner_name
            if selection_name in betfair_to_pokerstars:
                selection_dict[str(runner.selection_id)] = betfair_to_pokerstars[selection_name]
            else:
                selection_dict[str(runner.selection_id)] = selection_name
    return selection_dict, market_dict

#API REQUEST FOR MARKET BOOKS WITH LAY PRICE AND LAY SIZE FOR ALL THE MARKET IDs
def request_market_book(trading,market_ids):
    price_filter = betfairlightweight.filters.price_projection(price_data=['EX_BEST_OFFERS'])
    market_books = trading.betting.list_market_book(market_ids=market_ids,price_projection=price_filter)
    return market_books

#WORK FOR SINGLE RUNNER e.a. UNDER 2.5, GOAL YES, THE DRAW....
def extract_runner_lay(runner_book,market_id,market_dict,selection_dict):
    selection_id=str(runner_book.selection_id)
    selection_name = selection_dict[selection_id]
    home, away = market_dict[market_id]['event_name'].split(" - ")
    date = market_dict[market_id]['date']
    comp = market_dict[market_id]['competition_name']
    try:
        price=runner_book.ex.available_to_lay[0].price
        size=runner_book.ex.available_to_lay[0].size
    except IndexError:
        price="NA"
        size="NA"
    #return comp,home, away,date,selection_name, price, size
    return [comp , home , away , date , selection_name , price , size]

#DOWNLOAD THE FILE WITH ALL THE MARKET ID WE HAVE. 40 ENTRY AT TIME BECAUSE BETFAIR API HAS MAX DATA IN THE REQUESTS
def export_market_book(trading,market_dict):
    market_ids = list(market_dict.keys())
    market_len = len(market_ids)
    market_books = []
    if market_len > 40:
        start = 0
        stop = 40
        market_books.extend(request_market_book(trading,market_ids[start:stop]))
        for i in range(market_len // 40 - 1):
            start += 40
            stop += 40
            market_books.extend(request_market_book(trading,market_ids[start:stop]))
        modulus = market_len % 40
        if modulus != 0:
            start += 40
            stop += market_len % 40
            market_books.extend(request_market_book(trading,market_ids[start:stop]))
    return market_books

#FINAL FUNCTION WHICH EXPORT FINAL DATAFRAME
def export_runners(market_books,market_dict,selection_dict):
    export_dataframe=init_data()
    for market in market_books:
        market_id=str(market.market_id)
        #export_list=[]
        #print(market_dict["1.203229165"])
        #print(json.dumps(json.loads(market.json()), indent=2))
        for runner in market.runners:
            runner_lay=extract_runner_lay(runner,market_id,market_dict,selection_dict)
            #export_list.append(runner_lay)
            export_dataframe = pd.concat([export_dataframe, list_to_dataframe(runner_lay)], ignore_index=True)   
    return export_dataframe



def load_dataframe(usr, psw, ap_key):
    #LOGIN IN THE API
    certificate_root='oddsmatcher/certificates/' #local position of my XRC certificates and secret key
    trading = betfairlightweight.APIClient(usr, psw, app_key=ap_key, certs=certificate_root,locale="italy")
    
    #FOR OBVIOUS REASON MY AP_KEY AND CERTIFICATES ARE NOT UPLOADED ON GITHUB
    # THE AP_KEY CAN BE REQUESTED FOR EVERYONE WHO HAVE A VERIFIED ACCOUNT ON BETFAIR
    #THE CERTIFICATES ARE PRETTY EASY TO BEING PRODUCED
    #REFERENCE MATERIAL IS WELL DESCRIBED
    #https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/Getting+Started
    
    trading.login()
    
    #SOCCER ID
    results  = trading.betting.list_event_types()
    soccer_id=[result.event_type.id for result in results if result.event_type.name=="Soccer"] # Betfair API wants id in a list
    
    #COMPETITION ID
    datetime_in_a_week = (datetime.datetime.utcnow() + datetime.timedelta(weeks=4)).strftime("%Y-%m-%dT%TZ")

    #This is given by scraperPS
    #DA AGGIUNGERE COME ARGOMENTO DELLA FUNZIONE!!!!! DA RETURN DI SCRAPERPS
    competitions_pokerstar=['Italia - Serie A','Italia - Serie B','Champions League','Europa League','Conference League','Inghilterra - Premier League','Spagna - La Liga','Germania - Bundesliga','Francia - Ligue 1','Portogallo - Primeira Liga']
    competitions_pokerstar=[i.replace(" - "," ") for i in competitions_pokerstar]
    memory_filename="competition_dict.json" #file where id competition ids are stored for minimizing the number of requests to the api
    competition_dict=initialize_competition_dict(memory_filename,competitions_pokerstar, soccer_id,datetime_in_a_week)
    competition_ids=dict_to_list(competition_dict,competitions_pokerstar)

    #EVENTS ID
    events=request_event_list(trading,soccer_id,competition_ids)
    event_id=extract_event(events)

    #MARKET ID AND SELECTION_NAMES
    selection_dict,market_dict=extract_market_catalogue(trading,event_id)

    #MARKET BOOKS WITH THE FINAL DATA WE WANT
    market_books=export_market_book(trading,market_dict)
    all_runners=export_runners(market_books,market_dict,selection_dict)
    return(all_runners)


if __name__ == "__main__":
    print(load_dataframe(usr, psw, ap_key))










