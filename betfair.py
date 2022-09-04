from credentials import ap_key, usr, psw #For obvious reason those are not uploaded on github ;)
import requests
import json
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
    return response['sessionToken']

non_interactive_login_url='https://identitysso-cert.betfair.it/api/certlogin'    #Just for get the session token SSOID on the italian website
certificates=('/media/2TB/oddsmatcher/certificate_xca/betfair_api.crt','/media/2TB/oddsmatcher/certificate_xca/betfair_api.key') #local position of my XRC certificates and secret key
print(get_ssoid(usr,psw,ap_key,certificates,non_interactive_login_url))