from credentials import ap_key, usr, psw #For obvious reason those are not uploaded on github ;)
import requests
import json
import scraperPS as sps
from datetime import datetime
import pandas as pd
pd.set_option('display.max_columns', None) #FOR DEBUG
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

def api_request(url,ap_key,ssoid,query,params='{"filter":{ }}',save=False,filename='data.json'):
    headers = {'X-Application': ap_key, 'X-Authentication': ssoid, 'content-type': 'application/json'}
    methods = "SportsAPING/v1.0/"
    methods = methods + query
    json_req = '{  "jsonrpc" : "2.0" ' + ', "method" : "'  + methods + '" , "params" :' + '{  "filter":{ }  }' + '  }'
    response = requests.post(url, data=json_req.encode('utf-8'), headers=headers)
    if save:
        sps.save_json_file(filename, response)
    return json.loads(response.text)

def get_soccer_id(json_object):
    for sport in json_object['result']:
        if sport['eventType']['name'] == 'Soccer':
            soccer_id = sport['eventType']['id']
        break
    return soccer_id



#GET THE SESSION TOKEN
non_interactive_login_url='https://identitysso-cert.betfair.it/api/certlogin'    #Just for get the session token SSOID on the italian website
certificates=('/media/2TB/oddsmatcher/certificate_xca/betfair_api.crt','/media/2TB/oddsmatcher/certificate_xca/betfair_api.key') #local position of my XRC certificates and secret key
ssoid=get_ssoid(usr,psw,ap_key,certificates,non_interactive_login_url)

#GET EVENT TYPE ID FOR API REQUEST
betting_api_url='https://api.betfair.com/exchange/betting/json-rpc/v1'
response=api_request(betting_api_url,ap_key,ssoid,'listEventTypes')
soccer_id=get_soccer_id(response)
print(soccer_id)

#GET EVENT TYPE ID FOR API REQUEST


