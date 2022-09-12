import scraperPS as ps
import betfair as betfair
import pandas as pd
pd.set_option('display.max_row', None) #FOR DEBUG

data_pokerstar,competitions=ps.dataframe_load()
data_pokerstar['date'] = pd.to_datetime(data_pokerstar['date'], format='%Y-%m-%d %H:%M:%S') #INSERIRE IN SCARAPERPS
data_pokerstar= data_pokerstar.sort_values(by='date')
data_pokerstar.to_csv("pokerstar.csv",header=False,index=False)

#data_betfair=betfair.load_dataframe(competitions)
#data_betfair['date'] = pd.to_datetime(data_betfair['date'], format='%Y-%m-%d %H:%M:%S') #INSERIRE IN SCARAPERPS
#data_betfair= data_betfair.sort_values(by='date')
#data_betfair.to_csv("betfair.csv",header=False,index=False)
