import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import math 
from scipy.io import savemat

filename = '/home/alynux/Results/2023-05-14/wrfout_d02_2023-05-14_09:00:00'
#filename = '/home/alynux/WRFV4.5/test/em_real/wrfout_d02_2023-12-06_12_00_00'
wrf_file = xr.open_dataset(filename)
lat_ponto = -19.407
lon_ponto = -40.044
latlon_indices = np.where((wrf_file.XLAT.values == lat_ponto) & (wrf_file.XLONG.values == lon_ponto))
#i = latlon_indices[0][0]
#j = latlon_indices[1][0]

i = 48
j = 48
#i = 63
#j = 63

fig, axs = plt.subplots(2)
swdown = wrf_file.SWDOWN[:, i, j]
DHI = wrf_file.SWDDIF[:, i, j]
DNI = wrf_file.SWDDNI[:, i, j]
COSZ = wrf_file.COSZEN[:, i, j].values
GHI = DNI*COSZ + DHI
temp = wrf_file.T2[:, i, j] - 273.15
wind_u = wrf_file.U10[:, i, j].values
wind_v = wrf_file.V10[:, i, j].values
wsp = np.sqrt(wind_u**2 + wind_v**2)
dew =  wrf_file.TH2[:, i, j] - 273.15
swdown_units = wrf_file.SWDOWN.units   
print(swdown.XLAT[0])
axs[0].plot(swdown.XTIME, GHI)
#axs[0].plot(swdown.XTIME, DNI)
#fig.xlabel('Tempo')
#fig.ylabel(f'irradiancia ({swdown_units})')
fig.suptitle('SWDOWN  e T2 ao longo do tempo')
axs[1].plot(dew.XTIME, dew)
axs[1].plot(dew.XTIME, wsp)
#axs[1].plot(wind_v.XTIME, wind_v)
axs[1].plot(temp.XTIME, temp)
axs[1].set_xlabel('Tempo')
plt.show()






