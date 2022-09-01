#!/opt/miniconda3/bin/python

import requests
from playwright.sync_api import sync_playwright


#with sync_playwright() as p:
#    browser = p.chromium.launch()
#    context = browser.new_context()
#    page = context.new_page()
#    page.goto("https://www.forbes.com/billionaires")
#    page.click("button.trustarc-agree-btn")
#    # print(context.cookies())
#    cookie_for_requests = context.cookies()[3]['value']
#    browser.close()

def get_cookie_playwright():
	with sync_playwright() as p:
		browser = p.chromium.launch()
		context = browser.new_context()
		page = context.new_page()
		page.goto("https://www.eurobet.it/it/scommesse/#!/")
		cookie_for_requests=context.cookies()
		browser.close()
	return cookie_for_requests

dump=get_cookie_playwright()
cook=(f'{dump[0]["name"]}={dump[0]["value"]}')

url = "https://www.eurobet.it/prematch-homepage-service/sport-schedule/services/prematch-homepage/highlight"
payload = ""
headers = {"cookie": cook}

response = requests.request("GET", url, data=payload, headers=headers)
import json
print(json.dumps(json.loads(response.text),indent=2))

