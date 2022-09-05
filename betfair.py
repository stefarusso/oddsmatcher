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



'''#GET THE SESSION TOKEN
non_interactive_login_url='https://identitysso-cert.betfair.it/api/certlogin'    #Just for get the session token SSOID on the italian website
certificates=('/media/2TB/oddsmatcher/certificate_xca/betfair_api.crt','/media/2TB/oddsmatcher/certificate_xca/betfair_api.key') #local position of my XRC certificates and secret key
ssoid=get_ssoid(usr,psw,ap_key,certificates,non_interactive_login_url)
print(f'ssoid: {ssoid}')
#GET EVENT TYPE ID FOR API REQUEST
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

certificate_root='/media/2TB/oddsmatcher/certificate_xca' #local position of my XRC certificates and secret key

trading = betfairlightweight.APIClient(usr, psw, app_key=ap_key, certs=certificate_root,locale="italy")
trading.login()

#SOCCER ID
results  = trading.betting.list_event_types()
print( [[result.event_type.id,result.event_type.name] for result in results if result.event_type.name=="Soccer"])


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

print(soccer_competitions["Competition"][51])
print(soccer_competitions["Competition"].filter(like="Italian Serie A",axis=0))

