from credentials import ap_key, usr, psw #For obvious reason those are not uploaded on github ;)
import requests
import json
import scraperPS as sps
import datetime
import betfairlightweight
from betfairlightweight import filters

import pandas as pd
pd.set_option('display.max_columns', None) #FOR DEBUG
pd.set_option('display.max_row', None) #FOR DEBUG

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

'''OLD
    def api_request(url,ap_key,ssoid,request,save=False,filename='data.json'):
    headers = {'X-Application': ap_key, 'X-Authentication': ssoid, 'content-type': 'application/json'}
    response = requests.post(url, data=request.encode('utf-8'), headers=headers)
    if save:
        sps.save_json_file(filename, response)
    return json.loads(response.text)'''

def api_request(url,ap_key,ssoid,query,json_req,save=False,filename='data.json'):
    headers = {'X-Application': ap_key, 'X-Authentication': ssoid, 'content-type': 'application/json'}
    url = url + query
    response = requests.post(url, data=json_req, headers=headers)
    if save:
        sps.save_json_file(filename, response)
    return json.loads(response.text)

def get_soccer_id(json_object):
    for sport in json_object:
        if sport['eventType']['name'] == 'Soccer':
            soccer_id = sport['eventType']['id']
        break
    return soccer_id



#GET THE SESSION TOKEN
non_interactive_login_url='https://identitysso-cert.betfair.it/api/certlogin'    #Just for get the session token SSOID on the italian website
certificates=('certificates/betfair_api.crt','certificates/betfair_api.key') #local position of my XRC certificates and secret key
ssoid=get_ssoid(usr,psw,ap_key,certificates,non_interactive_login_url)
print("ssoid:" + ssoid)

'''#GET EVENT TYPE ID FOR API REQUEST
url = "https://api.betfair.com/exchange/betting/rest/v1.0/"
json_req = '{"filter":{ }}'
response=api_request(url,ap_key,ssoid,"listEventTypes/",json_req)
soccer_id=get_soccer_id(response)
print(soccer_id)


#GET MARKET TYPE ID FOR API REQUEST
#response=api_request(betting_api_url,ap_key,ssoid,'{  "jsonrpc" : "2.0" , "method" : "SportsAPING/v1.0/listMarketTypes" , "params" :{  "filter":{ }  },  "id" : 1 }')

json_req = '{"filter":{ "eventTypeIds" : ["' + soccer_id + '"]}}'
response=api_request(url,ap_key,ssoid,"listCompetitions/",json_req,save=True) #WE USE THAT FOR {"name league" : "id"}
#TRY WITH ONLY SERIE A
serie_A_id="81"
print("COMPETIZIONE = "+serie_A_id)

json_req = '{"filter":{ "competitionIds" : ["' + serie_A_id + '"]}}'
response=api_request(url,ap_key,ssoid,"listEvents/",json_req,save=True) #WE USE THAT FOR {"name league" : "id"}
print(response)
Torino_Lecce_id="31699484"
print("PARTITA = "+Torino_Lecce_id)

json_req = '{"filter":{ max_results="100",Eventid="31699484"}}'
response=api_request(url,ap_key,ssoid,"listMarketCatalogue/",json_req,save=True) #WE USE THAT FOR {"name league" : "id"}
print(response)'''

#----------------------------------------------------------------------------------------------------
#
#    BETFAIR API
#
#----------------------------------------------------------------------------------------------------
certificate_root='oddsmatcher/certificates/' #local position of my XRC certificates and secret key

trading = betfairlightweight.APIClient(usr, psw, app_key=ap_key, certs=certificate_root,locale="italy")
trading.login()

#SOCCER ID
results  = trading.betting.list_event_types()
soccer_id=[[result.event_type.id,result.event_type.name] for result in results if result.event_type.name=="Soccer"]
soccer_id = soccer_id[0][0]
print(f'SOCCER ID :  {soccer_id} , type :  {type(soccer_id)}' )

#CREARE FUNZIONE PER QUESTA QUI
datetime_in_a_week = (datetime.datetime.utcnow() + datetime.timedelta(weeks=3)).strftime("%Y-%m-%dT%TZ")
print(f'FORMAT DATE AND TIME : {datetime_in_a_week}')

competition_filter = betfairlightweight.filters.market_filter(
    event_type_ids=[soccer_id], # Soccer's event type id is 1
    market_start_time={
        'to': datetime_in_a_week
    })
competitions = trading.betting.list_competitions(
    filter=competition_filter
)

#For Competition and Events dataframe is useful for partial string search
soccer_competitions = pd.DataFrame({
    'Competition': [competition_object.competition.name for competition_object in competitions],
    'ID': [competition_object.competition.id for competition_object in competitions]
})

#RESAEARCH OF SERIE A COMPETITION ID
competition_ids=soccer_competitions[soccer_competitions.Competition.str.contains('(?=.*Serie A)(?=.*Italian)')]  #First match "SERIE A" than MATCH "Italian" if there is before "SERIE A"
#print([competition_id_serieA.ID, competition_id_serieA.Competition])
competition_id_serieA=competition_ids.ID.item()
print(f'COMPETITION ID SERIE A : {competition_id_serieA}')



#RESEARCH EVENT ID
event_filter = betfairlightweight.filters.market_filter(
    event_type_ids=[soccer_id],
    competition_ids=[competition_id_serieA],
    market_start_time={
        'to': (datetime.datetime.utcnow() + datetime.timedelta(weeks=1)).strftime("%Y-%m-%dT%TZ")
    }
)

events = trading.betting.list_events(filter=event_filter)
events = pd.DataFrame({
    'event_name': [event_object.event.name for event_object in events],
    'event_id': [event_object.event.id for event_object in events],
    'country_code': [event_object.event.country_code for event_object in events],
    'time_zone': [event_object.event.time_zone for event_object in events],
    'open_date': [event_object.event.open_date for event_object in events],
})

#TEST ONLY ONE EVENT
j=0
#event_id=events[events.event_name.str.contains("Samp")].iloc[0:].event_id.item()
event_id=events.event_id
event_id=event_id.tolist()
event_id=[event_id[j]] #CANCELLARE QUANDO SI PASSA A N EVENTI
print(event_id)

event_name=events.event_name
#event_name=events[events.event_name.str.contains("Samp")].iloc[0:].event_name.item()
print(f'EVENT ID OF {event_name[j]} : {event_id[j]}')
print(events)


#-------------
#
#
#RESEARCH ALL MARKETS SELECTION IDs FOR THE EVENT ID SELECTED
markets_set=["MATCH_ODDS","OVER_UNDER_25","BOTH_TEAMS_TO_SCORE"]
market_catalogue_filter = betfairlightweight.filters.market_filter(event_ids=event_id,market_type_codes=markets_set)

market_catalogues = trading.betting.list_market_catalogue(
    filter=market_catalogue_filter,
    max_results='100',
    market_projection=['RUNNER_DESCRIPTION','EVENT','COMPETITION'],
    sort='FIRST_TO_START'
)

print(market_catalogues)
print(json.dumps(json.loads(market_catalogues[0].json()) ,indent=2))


'''market_ids=[]
selection_id_to_name={}
for market in market_catalogues:
    market_ids.append(market.market_id)
    for runner in market.runners:
        selection_id_to_name[ str(runner.selection_id) ] = runner.runner_name'''

market_ids=[]
selection_id_dict={}
for market in market_catalogues:
    market_ids.append(market.market_id)
    name=market.event.name
    date=market.event.open_date
    comp=market.competition.name
    for runner in market.runners:
        selection_id_dict[str(runner.selection_id)] = { "runner_name" : runner.runner_name, "event_name" : name, "date" : date, "competition_name" : comp }

#print(market_ids)
print(selection_id_dict)



#DOWNLOAD THE FILE WITH ALL THE MARKET ID WE HAVE 
#WE REQUESTS IT ONLY ONE TIME
#

def request_market_book(market_ids):
    price_filter = betfairlightweight.filters.price_projection(price_data=['EX_BEST_OFFERS'])
    market_books = trading.betting.list_market_book(market_ids=market_ids,price_projection=price_filter)
    return market_books

#WORK FOR SINGLE RUNNER e.a. UNDER 2.5, GOAL YES, THE DRAW....
def extract_runner_lay(runner_book):
    selection_id=runner_book.selection_id
    selection_id=str(selection_id)
    selection_name = selection_id_dict[selection_id]['runner_name']
    event =  selection_id_dict[selection_id]['event_name']
    date = selection_id_dict[selection_id]['date']
    comp = selection_id_dict[selection_id]['competition_name']
    price=runner_book.ex.available_to_lay[0].price
    size=runner_book.ex.available_to_lay[0].size
    return comp,event,date,selection_name, price, size


market_books=request_market_book(market_ids)
#print(json.dumps(json.loads(market_books[1].json()),indent=2))
for market in market_books:               #BAD SOLUTION FOR AN SINGLE ITEM LIST 
        for runner in market.runners:
            runner_lay=extract_runner_lay(runner)
            print(runner_lay)

        






