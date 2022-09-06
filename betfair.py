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


certificate_root='oddsmatcher/certificates/' #local position of my XRC certificates and secret key

trading = betfairlightweight.APIClient(usr, psw, app_key=ap_key, certs=certificate_root,locale="italy")
trading.login()

#SOCCER ID
results  = trading.betting.list_event_types()
soccer_id=[[result.event_type.id,result.event_type.name] for result in results if result.event_type.name=="Soccer"]
print(soccer_id)
soccer_id = soccer_id[0][0]


datetime_in_a_week = (datetime.datetime.utcnow() + datetime.timedelta(weeks=3)).strftime("%Y-%m-%dT%TZ")
print(datetime_in_a_week)

competition_filter = betfairlightweight.filters.market_filter(
    event_type_ids=[1], # Soccer's event type id is 1
    market_start_time={
        'to': datetime_in_a_week
    })
competitions = trading.betting.list_competitions(
    filter=competition_filter
)


soccer_competitions = pd.DataFrame({
    'Competition': [competition_object.competition.name for competition_object in competitions],
    'ID': [competition_object.competition.id for competition_object in competitions]
})

id_serieA=soccer_competitions[soccer_competitions.Competition.str.contains('Serie A' and 'Italian')].iloc[0,:]
print([id_serieA.ID, id_serieA.Competition])


event_filter = betfairlightweight.filters.market_filter(
    event_type_ids=[soccer_id],
    competition_ids=[id_serieA.ID],
    market_start_time={
        'to': (datetime.datetime.utcnow() + datetime.timedelta(weeks=1)).strftime("%Y-%m-%dT%TZ")
    }
)


events = trading.betting.list_events(filter=event_filter)
events = pd.DataFrame({
    'Event_Name': [event_object.event.name for event_object in events],
    'Event_ID': [event_object.event.id for event_object in events],
    'Country_Code': [event_object.event.country_code for event_object in events],
    'Time_Zone': [event_object.event.time_zone for event_object in events],
    'Open_Date': [event_object.event.open_date for event_object in events],
    'Market_Count': [event_object.market_count for event_object in events]
})

id_partita=events[events.Event_Name.str.contains("Samp")].iloc[0:]
print([id_partita.Event_Name,id_partita.Event_ID])

print('...........')

market_catalogue_filter = betfairlightweight.filters.market_filter(event_ids=[str(id_partita.Event_ID.item())])

#I HAVE TO INTRODUCE THE Additional_Data=RUNNER_DESCRIPTION for optaining the selectionid  RUNNER_DESCRIPTION

print(market_catalogue_filter)
#market_projection='RUNNER_DESCRIPTION'


market_catalogues = trading.betting.list_market_catalogue(
    filter=market_catalogue_filter,
    max_results='100',
    sort='FIRST_TO_START'
)

print(market_catalogues[0])
# Create a DataFrame for each market catalogue
market_types = pd.DataFrame({
    'market_name': [market_cat_object.market_name for market_cat_object in market_catalogues],
    'market_id': [market_cat_object.market_id for market_cat_object in market_catalogues],
})

id_market = market_types[market_types.market_name=="Match Odds"]
id_market = id_market.market_id.item()
print(["market_id",id_market])





def process_runner_books(markets):
    for market in markets:
        best_lay_prices = [runner_book.ex.available_to_lay[0].price if runner_book.ex.available_to_lay.price else 1000.0 for runner_book in runner_books]
        best_lay_sizes = [runner_book.ex.available_to_lay[0].size if runner_book.ex.available_to_lay.size else 1.01 for runner_book in runner_books]
        selection_ids = [runner_book.selection_id for runner_book in runner_books]
        df = pd.DataFrame({
            'selection_id': selection_ids,
            'best_lay_price': best_lay_prices,
            'best_lay_size': best_lay_sizes,
        })
    return df



print('-------------')

# Create a price filter. Get all traded and offer data
price_filter = betfairlightweight.filters.price_projection(
    price_data=['EX_BEST_OFFERS']
)
print("PRICE PROJECTION\n")
print(price_filter)
# Request market books
market_books = trading.betting.list_market_book(
    market_ids=['1.202965175'],
    price_projection=price_filter
)

#DEBUG
#runners=json.dumps(json.loads(market_books[0].json()), indent=2)
#print(runners)

print(market_books[0]["runners"][0]["ex"]["availableToLay"][0])
lay_ods=[selection["ex"]["availableToLay"][0]['price'] for selection in market_books[0]["runners"]]
lay_selection_id=[selection["selectionId"] for selection in market_books[0]["runners"]]
print(lay_ods,lay_selection_id)
