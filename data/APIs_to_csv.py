import http.client
import requests
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime,timedelta
import os
from dotenv import load_dotenv

load_dotenv()

def hour_rounder(t):
    if t.minute >=30:
        return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour+1))
    else:
        return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour))


# conn = http.client.HTTPSConnection("api.solcast.com.au")
# payload = ''
# headers = {}
# conn.request("GET", "/world_radiation/forecasts?latitude=-19.407642&longitude=-40.045221&hours=48&format=json&api_key="+os.getenv("SOLCAST_API_KEY"), payload, headers)
# res = conn.getresponse()
# data = res.read()
# data_res = data.decode("utf-8")
 
# with open('forecastdata.txt', 'w+') as f:
#     f.write(data_res)
#     f.close()
    
with open('forecastdata.txt', 'r') as f:
    res_data = f.read()
    f.close()

 
# Weather API 
url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/-19.39%2C%20-40.40?unitGroup=metric&include=hours&key="+os.getenv("WHEATHER_API_KEY")+"&contentType=json"
print(url)
response = requests.request("GET", url)
if response.status_code!=200:
  print('Unexpected Status code: ', response.status_code)
  sys.exit()  

# Parse the results as JSON
jsonWeather = response.json()

with open('wheatherdata.txt', 'w+') as f:
    f.write(str(jsonWeather))
    f.close()
    
json_object = json.loads(res_data)
json_formatted_str = json.dumps(json_object, indent=2)
df_nested_list = pd.json_normalize(json_object, record_path =['forecasts'])
df_weather = pd.json_normalize(jsonWeather)
df_Weather = pd.DataFrame(columns=['Datetime', 'Dew point (C)', 'Wind Speed (m/s)','Pressure (mBar)'])

#start_datetime = hour_rounder(datetime.now()) + timedelta(hours=3, minutes=0)
start_datetime = hour_rounder(datetime(2023, 9, 6, 17, 0, 0)) + timedelta(hours=3, minutes=0)
day = int(datetime.today().strftime("%d"))
#day = int(start_datetime.strftime("%d"))
month = int(datetime.today().strftime("%m"))
#month = int(start_datetime.strftime("%m"))
new_datetime = start_datetime
dt = timedelta(hours=0, minutes=30)

for i in range(len(jsonWeather['days'])):
    for j in range(len(jsonWeather['days'][0]['hours'])):
        if(datetime.strptime(jsonWeather['days'][i]['datetime'],"%Y-%m-%d") == datetime(2023, month, day)):
            if(datetime.strptime(jsonWeather['days'][i]['hours'][j]['datetime'],"%H:%M:%S").time() >= start_datetime.time()): #datetime.strptime("12:00:00","%H:%M:%S")):
                timestamp = jsonWeather['days'][i]['datetime'] + " " + (datetime.strptime(jsonWeather['days'][i]['hours'][j]['datetime'], "%H:%M:%S") - timedelta(hours=0)).strftime("%H:%M:%S") 
                new_row = {'Datetime':timestamp, 'Dew point (C)':jsonWeather['days'][i]['hours'][j]['dew'], 
                           'Wind Speed (m/s)':jsonWeather['days'][i]['hours'][j]['windspeed'],
                           'Pressure (mBar)':jsonWeather['days'][i]['hours'][j]['pressure']}
                timestamp2 = jsonWeather['days'][i]['datetime'] + " " + (datetime.strptime(jsonWeather['days'][i]['hours'][j]['datetime'], "%H:%M:%S") + dt - timedelta(hours=0)).strftime("%H:%M:%S") 
                new_row2 = {'Datetime':timestamp2, 'Dew point (C)':jsonWeather['days'][i]['hours'][j]['dew'], 
                           'Wind Speed (m/s)':jsonWeather['days'][i]['hours'][j]['windspeed'],
                           'Pressure (mBar)':jsonWeather['days'][i]['hours'][j]['pressure'],
                           'Solarradiation':jsonWeather['days'][i]['hours'][j]['solarradiation'],
                           'Cloud cover (%)':jsonWeather['days'][i]['hours'][j]['cloudcover'],
                           'Humidity (%)':jsonWeather['days'][i]['hours'][j]['humidity']}
                #df_Weather = df_Weather.append(new_row, ignore_index=True)
                df_Weather = pd.concat([df_Weather, pd.DataFrame([new_row])],ignore_index=True)
                #df_Weather = df_Weather.append(new_row2, ignore_index=True)
                df_Weather = pd.concat([df_Weather, pd.DataFrame([new_row2])],ignore_index=True)
                
                
        else:
            if(datetime.strptime(jsonWeather['days'][i]['datetime'],"%Y-%m-%d") <= datetime(2023, month, day+1)): #and 
               #datetime.strptime(jsonWeather['days'][i]['hours'][j]['datetime'],"%H:%M:%S") >= datetime.strptime("00:00:00","%H:%M:%S")):
                timestamp = jsonWeather['days'][i]['datetime'] + " " + (datetime.strptime(jsonWeather['days'][i]['hours'][j]['datetime'], "%H:%M:%S") - timedelta(hours=0)).strftime("%H:%M:%S")
                new_row = {'Datetime':timestamp, 'Dew point (C)':jsonWeather['days'][i]['hours'][j]['dew'], 
                           'Wind Speed (m/s)':jsonWeather['days'][i]['hours'][j]['windspeed'],
                           'Pressure (mBar)':jsonWeather['days'][i]['hours'][j]['pressure']}
                timestamp2 = jsonWeather['days'][i]['datetime'] + " " + (datetime.strptime(jsonWeather['days'][i]['hours'][j]['datetime'], "%H:%M:%S") + dt - timedelta(hours=0)).strftime("%H:%M:%S") 
                new_row2 = {'Datetime':timestamp2, 'Dew point (C)':jsonWeather['days'][i]['hours'][j]['dew'], 
                           'Wind Speed (m/s)':jsonWeather['days'][i]['hours'][j]['windspeed'],
                           'Pressure (mBar)':jsonWeather['days'][i]['hours'][j]['pressure'],
                           'Solarradiation':jsonWeather['days'][i]['hours'][j]['solarradiation'],
                           'Cloud cover (%)':jsonWeather['days'][i]['hours'][j]['cloudcover'],
                           'Humidity (%)':jsonWeather['days'][i]['hours'][j]['humidity']}
                #df_Weather = df_Weather.append(new_row, ignore_index=True)
                df_Weather = pd.concat([df_Weather, pd.DataFrame([new_row])],ignore_index=True)
                #df_Weather = df_Weather.append(new_row2, ignore_index=True)
                df_Weather = pd.concat([df_Weather, pd.DataFrame([new_row2])],ignore_index=True)

print(df_Weather)    

forecast_df =pd.DataFrame() # df_nested_list.iloc[:1]

for k in range(len(df_nested_list)):
    #df_nested_list['period_end'][k] = (start_datetime+dt*k).strftime('%y-%m-%d %H:%M:%S')
    #df_nested_list['period_end'][k] = new_datetime - timedelta(hours=3, minutes=0)
    df_nested_list.loc[k, 'period_end'] = new_datetime - timedelta(hours=3, minutes=0)
    new_datetime = new_datetime + dt

for k in range(len(df_nested_list)):
    if(df_nested_list['period_end'][k] >= datetime(2023, month, day, 6, 0)  and df_nested_list['period_end'][k] <= datetime(2023, month, day+1, 19, 00)):
        forecast_df = pd.concat([forecast_df, df_nested_list.iloc[k,:14]], axis=1, ignore_index=True)

forecast_df = forecast_df.transpose()
print(forecast_df)    

# Definição do cabeçalho
header1 = ["99999","Ifes Linhares", "ES", "-19.23", "-40.41", "-03:00", "295"]
header2 = ["Date (MM/DD/YYYY),Time (HH:MM),ETR (W/m^2),ETRN (W/m^2),GHI (W/m^2),GHI source,GHI uncert (%),DNI (W/m^2),DNI source,DNI uncert (%),DHI (W/m^2),DHI source,DHI uncert (%),GH illum (lx),GH illum source,Global illum uncert (%),DN illum (lx),DN illum source,DN illum uncert (%),DH illum (lx),DH illum source,DH illum uncert (%),Zenith lum (cd/m^2),Zenith lum source,Zenith lum uncert (%),TotCld (tenths),TotCld source,TotCld uncert (code),OpqCld (tenths),OpqCld source,OpqCld uncert (code),Dry-bulb (C),Dry-bulb source,Dry-bulb uncert (code),Dew-point (C),Dew-point source,Dew-point uncert (code),RHum (%),RHum source,RHum uncert (code),Pressure (mbar),Pressure source,Pressure uncert (code),Wdir (degrees),Wdir source,Wdir uncert (code),Wspd (m/s),Wspd source,Wspd uncert (code),Hvis (m),Hvis source,Hvis uncert (code),CeilHgt (m),CeilHgt source,CeilHgt uncert (code),Pwat (cm),Pwat source,Pwat uncert (code),AOD (unitless),AOD source,AOD uncert (code),Alb (unitless),Alb source,Alb uncert (code),Lprecip depth (mm),Lprecip quantity (hr),Lprecip source,Lprecip uncert (code),PresWth (METAR code),PresWth source,PresWth uncert (code)"]

# Definição da data de início e intervalo de tempo
start_date = forecast_df['period_end'][0]
time_interval = timedelta(hours=0,minutes=30)
data = []

# Loop para gerar os dados de cada hora do dia para 1 ano
for i in range(len(forecast_df)):
    current_time = start_date + i*time_interval
    
    # Geração dos valores aleatórios para irradiância e temperatura
    etr = 0
    etrn = 0
    dew = df_Weather['Dew point (C)'][i]
    wspd = df_Weather['Wind Speed (m/s)'][i]
    pressure = df_Weather['Pressure (mBar)'][i]
    
    # Formatação dos valores para o padrão do arquivo TMY3
    date_str = current_time.strftime("%m/%d/%Y")
    time_str = current_time.strftime("%H:%M")
    etr_str = "{:.2f}".format(etr)
    etrn_str = "{:.2f}".format(etrn)
    ghi_str = str(forecast_df['ghi'][i])
    dni_str = str(forecast_df['dni'][i])
    dhi_str = str(forecast_df['dhi'][i])
    hr_str = str(df_Weather['Humidity (%)'][i])
    dry_bulb_temp_str = (str(forecast_df['air_temp'][i]))
    dew_point_temp_str = (str(dew))
    wspd_str = str(wspd)
    pressure_str = str(pressure)
    if pd.isna(df_Weather['Cloud cover (%)'][i]) and i > 0:
        cloud_cover_str =  str((df_Weather['Cloud cover (%)'][i-1]/10).round(2))
    else:
        if i == 0 and pd.isna(df_Weather['Cloud cover (%)'][i]):
            cloud_cover_str =  str(df_Weather['Cloud cover (%)'][i+1])
        else:
            cloud_cover_str =  str(df_Weather['Cloud cover (%)'][i])
    
    if pd.isna(df_Weather['Humidity (%)'][i]) and i > 0:
        hr_str =  str(df_Weather['Humidity (%)'][i-1])
    else:
        if pd.isna(df_Weather['Humidity (%)'][i]):
            hr_str =  str(df_Weather['Humidity (%)'][i+1])

    # Adição dos dados na lista de dados
    data.append([date_str, time_str, etr_str, etrn_str, ghi_str, "1", "10", dni_str,"1", "10", dhi_str, "", "", "", "", "", "", "", "", "", "", "", "", "", "", cloud_cover_str, "", "", "", "", "", dry_bulb_temp_str, "", "", dew_point_temp_str, "", hr_str, "", "", "", pressure_str, "", "", "", "", "", wspd_str, "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])

#Escrita dos dados no arquivo TMY3
with open("./ES_Linhares_forecast.tmy3", "w+") as file:
    # Escrita do cabeçalho
    file.write(", ".join(header1) + "\n")
    file.write(",".join(header2) + "\n")
    # Escrita dos dados
    for row in data:
        file.write(",".join(row) + "\n")
            
print("Arquivo gerado com sucesso!")
