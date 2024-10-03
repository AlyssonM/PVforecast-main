import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import math
import random
from datetime import datetime,timedelta
import sys 


dfs = pd.read_excel('../../data/Dados_inv_Sungrow/2022/Out22_Nov22_15min_SG5K-D_001_001.xls', 
                    sheet_name="Parâmetro do ponto de medição", 
                    engine="xlrd",
                    skiprows=1)

dfs['PeriodStart'] = pd.to_datetime(dfs['Horário'])
dfs.set_index('PeriodStart', inplace=True)


# Load CSV data file
df15M = pd.read_csv('../../data/Solcast/Ifes_Solcast_PT15M.csv')
#df30M = pd.read_csv('../../data/ES_Linhares.tmy3', skiprows=1)

# Set date and time as index
df15M['PeriodStart'] = pd.to_datetime(df15M['PeriodStart'])
df15M.set_index('PeriodStart', inplace=True)

#df30M['Timestamp'] = pd.to_datetime(df30M['Date (MM/DD/YYYY)'] + ' ' + df30M['Time (HH:MM)'])
#df30M.set_index('Timestamp', inplace=True)

# Select relevant columns for PV generation prediction
df15M = df15M[['Dni','Dhi', 'Ghi', 'AirTemp', 'DewpointTemp', 'WindSpeed10m', 'WindDirection10m', 'RelativeHumidity']]
# df30M = df30M[['DNI (W/m^2)','DHI (W/m^2)','GHI (W/m^2)', 'Dry-bulb (C)', 'Dew-point (C)', 'Wspd (m/s)', 'Wdir (degrees)', 'RHum (%)', 'Alb (unitless)']]
# columns_labels = {'DNI (W/m^2)': 'Dni',
#                   'DHI (W/m^2)': 'Dhi', 
#                   'GHI (W/m^2)' : 'Ghi', 
#                   'Dry-bulb (C)' : 'AirTemp', 
#                   'Dew-point (C)' : 'DewpointTemp', 
#                   'Wspd (m/s)' : 'WindSpeed10m', 
#                   'Wdir (degrees)' : 'WindDirection10m', 
#                   'RHum (%)' : 'RelativeHumidity', 
#                   'Alb (unitless)' : 'AlbedoDaily'}
# df30M  = df30M.rename(columns=columns_labels)
df = df15M

print(sys.argv[0])
print(sys.argv[1])
if (sys.argv[1] == '1'):
    print('Training New Model')
    mask = ((df.index.hour  > 19) | (df.index.hour < 5))
    dftrain = df.loc[~mask]['2016-01-01 00:00:00':'2021-12-31 23:00:00']

    # Define target variable as PV power generation in kW
    pv_ghi = dftrain['Ghi']

    # Define input features
    X = dftrain.drop('Ghi', axis=1)

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, pv_ghi, test_size=0.2, random_state=42)

    # Train random forest regression model
    rf = RandomForestRegressor(n_estimators=8, random_state=23)
    rf.fit(X_train, y_train)

    # Make PV power generation predictions on testing data
    y_pred = rf.predict(X_test)

    # Calculate mean absolute error (MAE)
    mae = np.mean(abs(y_test - y_pred))
    rmse = np.sqrt(np.mean((y_test - y_pred)**2))
    print('Mean Absolute Error:', round(mae, 2), 'W/m^2')
    print('Root Mean Squared Error:', round(rmse, 2), 'W/m^2')

    joblib.dump(rf, 'random_forest_model.pkl')
    
# Select relevant columns for PV generation
rf = joblib.load('random_forest_model.pkl') 
mask = ((df.index.hour  > 19) | (df.index.hour < 5))
df_pred = df.loc[~mask]['2022-01-01 00:00:00':'2022-12-31 23:00:00']
X = df_pred.drop('Ghi', axis=1)

# Make PV power generation predictions for the next day
pv_ghi_pred = rf.predict(X)

df_pred = df.loc[~mask]['2022-01-01 00:00:00':'2022-12-31 23:00:00']

# Save PV power generation predictions to a file
df_pred['GHI pred (W/m^2)'] = pv_ghi_pred
header = ["Ghi", "GHI pred (W/m^2)"]
df_pred.to_csv('ghi_predictions_2022b.csv', columns = header)


def calculate_POA(df, tilt, azimuth, dayOfYear, latitude):
    # Converter graus para radianos
    tilt_rad = np.deg2rad(tilt)
    azimuth_rad = np.deg2rad(azimuth)
    latitude_rad = np.deg2rad(latitude)
    
    # Declinação solar
    solarDeclination = 0.409 * np.sin(2 * np.pi * (dayOfYear - 81) / 368)
    
    # Inicialização da coluna POA no DataFrame (96 intervalos de 15 minutos em um dia)
    df['POA'] = 0

    # Filtrar o DataFrame para incluir apenas os horários entre 05:00 e 19:45
    df_filtered = df.between_time('05:00', '19:45')
    
    for index, row in df_filtered.iterrows():
        # Calcular a hora a partir do índice ou de uma coluna de horários
        hour = index.hour + index.minute / 60.0

        hourAngle = np.deg2rad(15 * (hour - 12))  # Subtrair 12 para centralizar o meio-dia

        # Cálculo do ângulo de elevação solar
        solarElevationAngle = np.arcsin(np.sin(latitude_rad) * np.sin(solarDeclination) + 
                                        np.cos(latitude_rad) * np.cos(solarDeclination) * np.cos(hourAngle))

        # Cálculo do ângulo de incidência
        cosIncidenceAngle = (np.sin(solarElevationAngle) * np.cos(tilt_rad) + 
                             np.cos(solarElevationAngle) * np.sin(tilt_rad) * np.cos(azimuth_rad - hourAngle))

        # Plano do Array (POA) para o intervalo atual
        df.loc[index, 'POA'] = df.loc[index, 'GHI pred (W/m^2)'] * max(cosIncidenceAngle, 0)  # usando max para evitar valores negativos
    
    return df

def calculate_POA_for_year(df, tilt, azimuth, latitude):
    # Converter graus para radianos
    tilt_rad = np.deg2rad(tilt)
    azimuth_rad = np.deg2rad(azimuth)
    latitude_rad = np.deg2rad(latitude)
    
    # Inicialização da coluna POA no DataFrame
    df['POA'] = 0
    
    # Iterar sobre cada dia único no DataFrame
    for day in df.index.normalize().unique():
        # Filtrar o DataFrame para o dia atual e horários entre 05:00 e 19:45
        df_day = df.loc[(df.index >= day + pd.Timedelta(hours=5)) & 
                        (df.index <= day + pd.Timedelta(hours=19, minutes=45))]
        
        # Calcular o dia do ano para o cálculo da declinação solar
        dayOfYear = day.dayofyear
        
        # Declinação solar
        solarDeclination = 0.409 * np.sin(2 * np.pi * (dayOfYear - 81) / 368)
        
        for index, row in df_day.iterrows():
            # Calcular a hora a partir do índice datetime
            hour = index.hour + index.minute / 60.0

            hourAngle = np.deg2rad(15 * (hour - 12))  # Subtrair 12 para centralizar o meio-dia

            # Cálculo do ângulo de elevação solar
            solarElevationAngle = np.arcsin(np.sin(latitude_rad) * np.sin(solarDeclination) + 
                                            np.cos(latitude_rad) * np.cos(solarDeclination) * np.cos(hourAngle))

            # Cálculo do ângulo de incidência
            cosIncidenceAngle = (np.sin(solarElevationAngle) * np.cos(tilt_rad) + 
                                 np.cos(solarElevationAngle) * np.sin(tilt_rad) * np.cos(azimuth_rad - hourAngle))

            # Plano do Array (POA) para o intervalo atual
            df.at[index, 'POA'] = row['GHI pred (W/m^2)'] * max(cosIncidenceAngle, 0)  # usando max para evitar valores negativos
    
    return df

def PVGeneration(df, Npv, Vmpp, Impp, Voc, Isc, Kv, Ki):
    # Fator de Forma (Fill Factor)
    FF = (Vmpp * Impp) / (Voc * Isc)
    Not = 42
    
    # Cálculo de Tc, V, I e Ppv
    df['Tc'] = df['DewpointTemp'] + (df['POA']/1000) * (Not - 20) / 0.8
    df['V'] = Voc * (1 + Kv * (df['Tc'] - 25) / 100)
    df['I'] = (df['POA']/1000) * Isc * (1 + Ki * (df['Tc'] - 25) / 100)
    df['Ppv'] = 0.9 * Npv * df['V'] * df['I'] * FF / 1000
    
    # Retorna apenas a coluna de Ppv ou o DataFrame inteiro
    return df['Ppv']
# Parâmetros físicos do modelo do módulo PV

Npv = 12            # number of modules
Efficiency = 0.204   # module efficiency
tilt = 10            # Tilt angle
azimuth = 12          # Azimuth angle
# Module data
Vmpp = 41.1
Impp = 10.96
Voc = 49.1
Isc = 11.60
Kv = -0.27
Ki = 0.05




df_pred['Power pred (kw)'] = 0
df_pred = calculate_POA_for_year(df_pred, 12, 23, -19.39)
df = PVGeneration(df_pred, Npv, Vmpp, Impp, Voc, Isc, Kv, Ki)

start_day = 29
end_day = 31
mask_time = ((dfs.index.hour >= 5) & (dfs.index.hour <= 19))
mask_day = ((dfs.index.month == 10) & (dfs.index.day >= start_day) & (dfs.index.day <= end_day))
# Substituir vírgulas por pontos e converter para float, lidando com erros
filtered_data = dfs.loc[mask_time & mask_day]['SG5K-D_001_001/Potência ativa total(kW)']
filtered_data = filtered_data.str.replace(',', '.').replace('--', 'NaN').astype(float)

# Remover valores NaN
filtered_data = filtered_data.fillna(0)

df_filtered = df.loc[(df.index.month == 10) & (df.index.day >= start_day) & (df.index.day <= end_day) & (df.index.hour >= 5) & (df.index.hour <= 19)]

# Calculate mean absolute error (MAE)
mae = np.mean(abs(filtered_data - df_filtered))
rmse = np.sqrt(np.mean((filtered_data - df_filtered)**2))
print('Mean Absolute Error:', round(mae, 2), 'kW')
print('Root Mean Squared Error:', round(rmse, 2), 'kW')
    
plt.plot(filtered_data, label='Sungrow SG5K-D')
plt.plot(df_filtered, label='Geração Prevista')
plt.xlabel('Data e hora')
plt.ylabel('Potência (kW)')


# Adicionar a legenda
plt.legend()

plt.show()

