# importing requests and json
import requests, json
import pandas as pd

def getWetterBayreuth():
    
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
    CITY = "Bayreuth"
    API_KEY = "617894bbf9a9019b4f70056a84ddefff"
    URL = BASE_URL + "q=" + CITY + "&appid=" + API_KEY
    response = requests.get(URL)
    data = response.json()
    df = pd.DataFrame(columns=['Temp','Temp Max','Temp Min','Humidity','Wind Speed','Wind Degree','Clouds','Weather'])
    df.loc[0,'Temp'] = data['main']['temp']
    df.loc[0,'Temp'] = df.loc[0,'Temp'] - 273.15
    df.loc[0,'Temp Max'] = data['main']['temp_max']
    df.loc[0,'Temp Max'] = df.loc[0,'Temp Max'] - 273.15
    df.loc[0,'Temp Min'] = data['main']['temp_min']
    df.loc[0,'Temp Min'] = df.loc[0,'Temp Min'] - 273.15
    df.loc[0,'Humidity'] = data['main']['humidity']
    df.loc[0,'Wind Speed'] = data['wind']['speed']
    df.loc[0,'Wind Degree'] = data['wind']['deg']
    df.loc[0,'Clouds'] = data['clouds']['all']
    df.loc[0,'Weather'] = data['weather'][0]['main']
    return df