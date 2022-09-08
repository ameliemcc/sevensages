import pandas as pd
import numpy as np

# Download the csv file from GitHub account

prints_url = "https://raw.githubusercontent.com/ameliemcc/sevensages/main/datacsvfiles/complete_prints.csv"
prints_all = pd.read_csv(prints_url, sep=';', skipinitialspace = True)
# make a copy of the full dataframe, just in case we need it again
prints_all_map = prints_all

#set index to town name
prints_all_map = prints_all_map.set_index('print_town', drop = False)
prints_all_map.index.names = ['index']

# replace empty date spaces with nan
prints_all_map['date_start'].replace(' ', np.nan, inplace=True)
prints_all_map['date_end'].replace(' ', np.nan, inplace=True)
prints_all_map['lat'].replace(' ', np.nan, inplace=True)

# remove whitespaces where necessary
prints_all_map['print_town'].str.strip()

# drop rows which don't have a value for date_start
prints_all_map.dropna(subset=['date_start'], inplace=True)

prints_all_map.dropna(subset=['language'], inplace=True)

# drop rows which don't have a value for lat
#prints_all_map.dropna(subset=['lat'], inplace=True)

# if no value for date_end, give it the same as date_start
prints_all_map['date_end'] = pd.to_numeric(prints_all_map['date_end']).fillna(prints_all_map['date_start']).astype(float)

# calculate a date mean
prints_all_map['date_mean'] = (prints_all_map['date_start'] + prints_all_map['date_end']) / 2

# deduce the century of production of the print
rx = r'^(\d\d)'
prints_all_map['date_mean_str'] = prints_all_map['date_mean'].astype(str)
prints_all_map['century'] = prints_all_map['date_mean_str'].str.extract(rx)
prints_all_map['century'] = pd.to_numeric(prints_all_map['century']).astype(float) + 1

# make a new dataframe in which the towns are counted by century
df_prints = (prints_all_map['print_town'].groupby(prints_all_map['century'])
        .value_counts()
        .reset_index(name='count'))

df_prints = df_prints.set_index('print_town', drop = False)
df_prints.index.names = ['index']
print('df prints')
print(df_prints)
# latitude column
df_prints = df_prints.assign(lati=0)
df_prints = df_prints.assign(longi=0)

# get latitude from prints_all_map and add it to new df_prints
for index in df_prints['print_town']:
    seriess = (prints_all_map.loc[index, 'lat'])
    results = []
    try:
        for y in seriess:
            results.append(y)
    except TypeError:
        results.append(seriess)
    df_prints['lati'].loc[index] = results[0]

# get longitude from prints_all_map and add it to new df_prints
for index in df_prints['print_town']:
    seriess = (prints_all_map.loc[index, 'long'])
    results = []
    try:
        for y in seriess:
            results.append(y)
    except TypeError:
        results.append(seriess)
    df_prints['longi'].loc[index] = results[0]

df_prints['century'] = pd.to_numeric(df_prints['century']).astype(float)

df_prints = df_prints.reset_index()


