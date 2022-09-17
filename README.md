# Oddsmatcher APP
It scrapes pokerstars sport event odds and betfair lay odds and return a dataframe sorted by the %rating for the event.

```
Requirement
pip install playwright
playwright install
pip install betfairlightweight
pip install python-Levenshtein
```
#### POKERSTARS SCRAPER

we need to inspect XHR GET Response on the website

-find the usefull json file

-copy as cURL

-paste on a API-request editor like Insomnia APP 

-you can send the request and get the same exact json. from all the headers the only one crucial is the cookie so you can un-tick all beside cookie

-right click on the file "generate code" export the XHR GET request in python language

```python
import requests

url = "https://www.eurobet.it/prematch-homepage-service/sport-schedule/services/prematch-homepage/highlight"

payload = ""
headers = {"cookie": "__cflb=02DiuH88gCYcfmbdqvQi1MWhJpunfebM5aXYuYpoXRJEG"}

response = requests.request("GET", url, data=payload, headers=headers)

print(response.text)
```

the cookie expire so we need a procedure that update the cookie at the start of the program

the script using playwright https://github.com/jhnwr/billionaires-scraper works like a charm so we use it for that task

when we have the json file we can start extracting only the info we need:

- date and time
- name event
- league
- odds
	- 1 X 2
    - U2.5 =2.5 
    - GOAL NOGOAL

then we iterate the same procedure for all the main leagues

we get a pandas dataframe with all the info we need.

#### BETFAIR SCRAPER

It is much simpler because Betfair offers free API request for all the information on the website so we don't need to scrape from the front end. Really nice :)

basically we only need:

-name of the event

-league 

-date and time

-selection name

-lay odds

-lay size

and the return dataframe will be merged with the pokerstars one.
