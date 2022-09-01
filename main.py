#!/opt/miniconda3/bin/python
'''
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


with sync_playwright() as p:
	browser = p.chromium.launch()
	context = browser.new_context()
	page = context.new_page()
	page.goto("https://www.eurobet.it/it/scommesse/#!/")
	print(context.cookies())
	browser.close()

dump=[{'name': '__cflb', 'value': '02DiuH88gCYcfmbdqvQi1MWhJpunfebM5TEYSQdLf1WdA', 'domain': 'www.eurobet.it', 'path': '/', 'expires': 1662123461.535754, 'httpOnly': True, 'secure': False, 'sameSite': 'Lax'}, {'name': '__cf_bm', 'value': 'IcB_xKy3Ew7Qntg6OBOT_X.ybzLuWXGN6spRgL0MTog-1662040661-0-AfLYNudma86KYh/KKepeajfaBWs7QAhq2dZ2QDAKsvLD2+QXI1LaG4Fl4JqvAYvRwFsgfSJ96i8y2giif0TjfNc=', 'domain': '.eurobet.it', 'path': '/', 'expires': 1662042461.535925, 'httpOnly': True, 'secure': True, 'sameSite': 'None'}]
print(dump)
print(f'{dump[0]["name"]}={dump[0]["value"]}; {dump[1]["name"]}')

'''


import requests

url = "https://www.eurobet.it/prematch-homepage-service/sport-schedule/services/prematch-homepage/highlight"

payload = ""
headers = {"cookie": "__cflb=02DiuH88gCYcfmbdqvQi1MWhJpunfebM5aXYuYpoXRJEG"}

response = requests.request("GET", url, data=payload, headers=headers)
import json
print(json.dumps(json.loads(response.text),indent=2))



