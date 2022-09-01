# oddsmatcher
Oddsmatcher for betfair/bookers matchbetting

inspect XHR GET Response on the website
find the usefull json 
copy as cURL
paste on Insomnia APP 
you can send the request and get the same exact json
from all the headers the only one crucial is the cookie
so you can un-tick all beside cookie

right click on the file "generate code" export the XHR GET request in python lenguage

```python
import requests

url = "https://www.eurobet.it/prematch-homepage-service/sport-schedule/services/prematch-homepage/highlight"

payload = ""
headers = {"cookie": "__cflb=02DiuH88gCYcfmbdqvQi1MWhJpunfebM5aXYuYpoXRJEG; at_check=true; AMCVS_45F10C3A53DAEC9F0A490D4D%40AdobeOrg=1; s_ecid=MCMID%7C56697673792615612723365559671204177017; AMCV_45F10C3A53DAEC9F0A490D4D%40AdobeOrg=-1124106680%7CMCIDTS%7C19237%7CMCMID%7C56697673792615612723365559671204177017%7CMCAAMLH-1662641506%7C6%7CMCAAMB-1662641506%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1662043906s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.2.0; s_cc=true; showSplash=false; _gcl_au=1.1.2065704931.1662036708; qcSxc=1662036709399; __qca=P0-1998962082-1662036709393; OptanonAlertBoxClosed=2022-09-01T12:52:03.836Z; _ga=GA1.2.710537802.1662036724; _gid=GA1.2.2009221847.1662036724; User-Type=registered; s_sq=%5B%5BB%5D%5D; __cf_bm=FAb4wcjvSKUD0SBCXgzthBLQeNx6qVjQ9CEU0__lzc4-1662040394-0-ASUlDwyegDae9G9zouvCOy32PBHiJAjnuUBLJJyy9ZkWXxOoRFDtQjvsCHFnjjxpGYBeHevxRV02li31ml62YzA=; RT="z=1&dm=eurobet.it&si=db55e631-0dc6-4e6f-8792-cf35dfd5e79b&ss=l7j3fjo3&sl=1&tt=ky&bcn=%2F%2F684dd327.akstat.io%2F&ul=nojw&hd=nopr"; mbox=PC#bcc26809e6de4316a003401c8b05bf2b.37_0#1725285452|session#cc155bdf32aa4b17a0a3aadfbafd04e8#1662041408; OptanonConsent=isIABGlobal=false&datestamp=Thu+Sep+01+2022+15%3A57%3A31+GMT%2B0200+(Ora+legale+dell%E2%80%99Europa+centrale)&version=6.31.0&consentId=7b5d2a8f-d20b-432c-86cb-75e6d8d8c0d6&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0004%3A1%2CBG143%3A1%2CC0002%3A1%2CBG144%3A1%2CC0003%3A1&hosts=H644%3A1%2CH67%3A1%2CH600%3A1%2CH621%3A1%2CH622%3A1%2CH601%3A1%2CH624%3A1%2CH243%3A1%2CH625%3A1%2CH572%3A1%2CH627%3A1%2CH645%3A1%2CH330%3A1%2CH628%3A1%2CH9%3A1%2CH370%3A1%2CH22%3A1%2CH29%3A1%2CH43%3A1%2CH44%3A1%2CH61%3A1%2CH65%3A1%2CH66%3A1%2CH76%3A1%2CH464%3A1%2CH81%3A1%2CH665%3A1%2CH100%3A1%2CH103%3A1%2CH670%3A1%2CH106%3A1%2CH114%3A1%2CH115%3A1%2CH116%3A1%2CH134%3A1%2CH142%3A1%2CH158%3A1%2CH164%3A1%2CH422%3A1%2CH169%3A1%2CH171%3A1%2CH623%3A1%2CH181%3A1%2CH184%3A1%2CH189%3A1%2CH191%3A1%2CH208%3A1%2CH222%3A1%2CH225%3A1%2CH386%3A1%2CH236%3A1%2CH238%3A1%2CH244%3A1%2CH571%3A1%2CH372%3A1%2CH261%3A1%2CH263%3A1%2CH264%3A1%2CH268%3A1%2CH413%3A1%2CH277%3A1%2CH279%3A1%2CH298%3A1%2CH300%3A1%2CH301%3A1%2CH302%3A1%2CH304%3A1%2CH573%3A1%2CH308%3A1%2CH312%3A1%2CH325%3A1%2CH331%3A1%2CH340%3A1%2CH351%3A1%2CH353%3A1%2CH355%3A1%2CH569%3A1%2CH297%3A1%2CH620%3A1%2CH568%3A1%2CH570%3A1%2CH626%3A1%2CH629%3A1&genVendors=V1%3A0%2C&geolocation=IT%3B62&AwaitingReconsent=false; _gat_6b58af785afa202392214d906f47a454=1"}

response = requests.request("GET", url, data=payload, headers=headers)

print(response.text)
```

the cookie expire so we need a procedure that update the cookie at the start of the program
the script using playwright https://github.com/jhnwr/billionaires-scraper works like a charm so we use it for that task
