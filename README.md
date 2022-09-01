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
import http.client

conn = http.client.HTTPSConnection("www.eurobet.it")

payload = ""

headers = { 'cookie': "__cflb=02DiuH88gCYcfmbdqvQi1MWhJpunfebM5aXYuYpoXRJEG; __cf_bm=jK3Tb9geGUAKvMmWZWpH9rrHbeBwT17sGMbJbTgoeBM-1662036703-0-AWDFUcfCZojv32eW5vqlviafb+BQAVfN/ErIHDqHcvvjiSKcA7bJic4/1MdCcntN9hYrOBn3b8Jj1bOE6G/DpT4=; at_check=true; AMCVS_45F10C3A53DAEC9F0A490D4D%40AdobeOrg=1; s_ecid=MCMID%7C56697673792615612723365559671204177017; AMCV_45F10C3A53DAEC9F0A490D4D%40AdobeOrg=-1124106680%7CMCIDTS%7C19237%7CMCMID%7C56697673792615612723365559671204177017%7CMCAAMLH-1662641506%7C6%7CM" }
conn.request("GET", "/prematch-homepage-service/sport-schedule/services/prematch-homepage/highlight", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
```

the cookie expire so we need a procedure that update the cookie at the start of the program
the script using playwright https://github.com/jhnwr/billionaires-scraper works like a charm so we use it for that task
