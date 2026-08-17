#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 17:27:25 2025

@author: Ryoichi Koga
"""
#Console
#%runfile(saveGOES_xray2.py 'start date (2018-08-01)'
#         'end date (2018-08-31)' 'directry (option)')
import pyspedas
from pytplot import get_data
import sys
import datetime
import numpy as np
import os
import matplotlib.pyplot as plt

args = sys.argv
print("Start day:", args[1])
print("End day:", args[2])

# Data acquistion（GOES-15 X-ray）
mag_vars = pyspedas.goes.fgm(trange=[args[1], args[2]], probe='15',
                             instrument='xrs', datatype='1min')

time1, data = get_data('g15_xrs_B_AVG')
time2, flag = get_data('g15_xrs_B_QUAL_FLAG')

#Mask the invalid data
mask = (flag == 0) & (data > -10000)
time3, flux3 = time1[mask], data[mask]

# args[1] => year
year = int(args[1].split('-')[0])

# Time conversion: time3 (UNIX) → datetime
Time = np.array([datetime.datetime.utcfromtimestamp(t) for t in time3])

# Day of year (DOY) calculation
doy_base = datetime.datetime(year, 1, 1)
DOY = np.array([(t - doy_base).total_seconds() / 86400.0 + 1 for t in Time])
print(DOY[3])
# print information
print("\n--- First 5 columns ---")
for i in range(min(5, len(Time))):
    print(f"{Time[i]} | DOY: {DOY[i]} | year: {year} | flux: {flux3[i]}")

# Scatter plot（DOY vs flux）
plt.figure(figsize=(10, 5))
plt.scatter(DOY, flux3, s=10, alpha=0.6)
plt.xlabel('Day of Year (DOY)')
plt.ylabel('X-ray Flux (XRS B AVG)')
plt.title(f'GOES-15 X-ray Flux in {year}')
plt.grid(True)
plt.tight_layout()
plt.show()

# Defect detection
delta_days = np.diff(DOY)
gap_indices = np.where(delta_days > 1)[0] # Identify data that is more than one day apart
for idx in gap_indices:
    print(f"Defect detection: DOY {DOY[idx]} → {DOY[idx+1]} (Difference: {delta_days[idx]}day)")

# Construct the output filename based on the year
if len(args) == 4:
    if os.path.exists(args[3]) and os.path.isdir(args[3]):
        filename = os.path.join(args[3], f"GOES_xray_{year}")
    else:
        print("Directory does not exist")
        sys.exit(1)
else:
    filename = f"GOES_xray_{year}"

# save file
np.savez(filename, Time=Time.astype(str), DOY=DOY, year=year, flux=flux3)
print(f"\nSave complete: {filename}.npz")
