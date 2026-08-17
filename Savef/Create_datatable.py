#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 14 14:21:12 2025
@author: Ryoichi Koga
"""
import pandas as pd
import numpy as np
import datetime
import tqdm
import os
from apexpy import Apex
from scipy.interpolate import interp1d

#Input period
year = "2019"

#Load Hisaki radiation data
dir_h = "/media/user/Data/Timeline/HisakiRad/"
df_h = pd.read_csv(dir_h+"Hisaki_geometry_radiation"+year+".csv")
#print(df_h.head())

#Load GOES data
dir_e = "/media/user/Data/Timeline/GOES15/Elec/"
dir_p = "/media/user/Data/Timeline/GOES15/Proton/"
dir_x = "/media/user/Data/Timeline/GOES15/Xray/"
dir_m = "/media/user/Data/Timeline/GOES15/Mag/"

data_e = np.load(dir_e+f"GOES_elec_{year}.npz")
data_p = np.load(dir_p+f"GOES_proton_{year}.npz")
data_x = np.load(dir_x+f"GOES_xray_{year}.npz")
data_m = np.load(dir_m+f"GOES_mag_{year}.npz")

#print(df_e)

#Load SYM-H data
dir_s = "/media/user/Data/Timeline/ae_index/"
df_s = pd.read_csv(dir_s+f"SYM-H_1min_{year}.csv")

#print(df_s.head())

f_elec = interp1d(data_e["DOY"],data_e["flux"], bounds_error=False, fill_value=np.nan)
# get the data during the valid period
min_doy, max_doy = data_e["DOY"].min(), data_e["DOY"].max()
# Interpolate the data within the range 
mask = (df_h["DOY"] >= min_doy) & (df_h["DOY"] <= max_doy)
df_h.loc[mask, "Elec"] = f_elec(df_h.loc[mask, "DOY"])
df_h.loc[~mask, "Elec"] = np.nan

### Proton
f_prot = interp1d(data_p["DOY"], data_p["flux"], bounds_error=False, fill_value=np.nan)
mask_p = (df_h["DOY"] >= data_p["DOY"].min()) & (df_h["DOY"] <= data_p["DOY"].max())
df_h.loc[mask_p, "Prot"] = f_prot(df_h.loc[mask_p, "DOY"])
df_h.loc[~mask_p, "Prot"] = np.nan

### X-ray
f_xray = interp1d(data_x["DOY"], data_x["flux"], bounds_error=False, fill_value=np.nan)
mask_x = (df_h["DOY"] >= data_x["DOY"].min()) & (df_h["DOY"] <= data_x["DOY"].max())
df_h.loc[mask_x, "Xray"] = f_xray(df_h.loc[mask_x, "DOY"])
df_h.loc[~mask_x, "Xray"] = np.nan

### Magenotometer
f_mag = interp1d(data_m["DOY"], data_m["flux"], bounds_error=False, fill_value=np.nan)
mask_m = (df_h["DOY"] >= data_m["DOY"].min()) & (df_h["DOY"] <= data_m["DOY"].max())
df_h.loc[mask_m, "Mag"] = f_mag(df_h.loc[mask_m, "DOY"])
df_h.loc[~mask_m, "Mag"] = np.nan

# ===== SYM-H (df_s) =====
f_s = interp1d(df_s["DOY"], df_s["SYM-H"], bounds_error=False, fill_value=np.nan)
min_doy_s, max_doy_s = df_s["DOY"].min(), df_s["DOY"].max()
mask_s = (df_h["DOY"] >= min_doy_s) & (df_h["DOY"] <= max_doy_s)
df_h.loc[mask_s, "SYM-H"] = f_s(df_h.loc[mask_s, "DOY"])
df_h.loc[~mask_s, "SYM-H"] = np.nan

#print(df_h.head())
#Calculate mag lon. and lat.
MLat, MLon = [],[]
# set the year
apex = Apex(date=int(year))

# Convert geographic coordinates to magnetic coordinates for each row
for i in tqdm.tqdm(range(len(df_h))):
    lat = df_h.loc[i, "Lat"]
    lon = df_h.loc[i, "Lon"]
    alt = df_h.loc[i, "Geocenter"] - 6378.1  # convert altitude [km]

    mag_lat, mag_lon = apex.convert(lat, lon, 'geo', 'apex', height=alt)
    MLat.append(mag_lat)
    MLon.append(mag_lon)
    
MLat = np.asarray(MLat)
MLon = np.asarray(MLon)
df_h["MLat"] = MLat
df_h["MLon"] = MLon

# Dictionary to store interpolated columns (column name -> interpolated data)
shifted_cols = {}

timeshift = range(3,)
for shift in tqdm.tqdm(range(1, 49)):  # 1〜48 hours later
    h_shift = shift / 24.0
    shifted_cols[f"SYM-H_t-{shift}h"] = f_s(df_h["DOY"] - h_shift)
    shifted_cols[f"Mag_t-{shift}h"]   = f_mag(df_h["DOY"] - h_shift)
    shifted_cols[f"Xray_t-{shift}h"]  = f_xray(df_h["DOY"] - h_shift)
    shifted_cols[f"Prot_t-{shift}h"]  = f_prot(df_h["DOY"] - h_shift)
    shifted_cols[f"Elec_t-{shift}h"]  = f_elec(df_h["DOY"] - h_shift)

# Create DataFrame from dictionary
df_shifted = pd.DataFrame(shifted_cols, index=df_h.index)

# Concatenate with the original df_h along the column axis (axis=1)
df_h = pd.concat([df_h, df_shifted], axis=1)


# save directory and file name
save_dir = "/media/user/Data/Timeline/Data_table/"
save_file = f"Datatable_{year}_shift48hver2.csv"

# save CSV file (no index)
df_h.to_csv(os.path.join(save_dir, save_file), index=False)

print(save_file)
print(df_h.head())


