import pandas as pd
import numpy as np

# Download the csv file from GitHub account
manuscripts_url = "https://raw.githubusercontent.com/ameliemcc/sevensages/main/datacsvfiles/complete_manuscripts.csv"

manuscripts_all = pd.read_csv(manuscripts_url, sep=';', skipinitialspace = True)

# make a copy of the full dataframe, just in case we need it again
manuscripts_all_map = manuscripts_all

manuscripts_all_map = manuscripts_all_map.set_index('language', drop=False)
manuscripts_all_map.index.names = ['index']

# replace empty date spaces with nan
manuscripts_all_map['date_start'].replace(' ', np.nan, inplace=True)
manuscripts_all_map['date_end'].replace(' ', np.nan, inplace=True)
manuscripts_all_map['language'].replace(' ', np.nan, inplace=True)

# remove whitespaces where necessary
manuscripts_all_map['iso-3'].str.strip()
manuscripts_all_map['language'].str.strip()

# drop rows which don't have a value for date_start
manuscripts_all_map.dropna(subset=['date_start'], inplace=True)

# manuscripts_all_map.dropna(subset=['iso-3'], inplace=True)

# if no value for date_end, give it the same as date_start
manuscripts_all_map['date_end'] = pd.to_numeric(manuscripts_all_map['date_end']).fillna(
        manuscripts_all_map['date_start']).astype(float)

# calculate a date mean
manuscripts_all_map['new_mean'] = (manuscripts_all_map['date_start'] + manuscripts_all_map['date_end']) / 2

# deduce the century of production of the manuscript
rx = r'^(\d\d)'
manuscripts_all_map['date_mean_str'] = manuscripts_all_map['new_mean'].astype(str)
manuscripts_all_map['cent'] = manuscripts_all_map['date_mean_str'].str.extract(rx)
manuscripts_all_map['cent'] = pd.to_numeric(manuscripts_all_map['cent']).astype(float) + 1

# make a new dataframe in which the languages are counted by century
df_manuscripts = (manuscripts_all_map.groupby(['cent', 'language'])
                  .size().reset_index(name='count')
                  )

df_manuscripts = df_manuscripts.set_index('language', drop=False)
df_manuscripts.index.names = ['index']
# df_manuscripts['cent'] = pd.to_numeric(df_manuscripts['cent']).astype(float)
print(df_manuscripts)
# latitude column
df_manuscripts = df_manuscripts.assign(lati=0)
df_manuscripts = df_manuscripts.assign(longi=0)

# get latitude from prints_all_map and add it to new df_prints
for index in df_manuscripts['language']:
        seriess = (manuscripts_all_map.loc[index, 'lat'])
        results = []
        try:
                for y in seriess:
                        results.append(y)
        except TypeError:
                results.append(seriess)
        df_manuscripts['lati'].loc[index] = results[0]
        # get longitude from prints_all_map and add it to new df_prints

for index in df_manuscripts['language']:
        seriess = (manuscripts_all_map.loc[index, 'lon'])
        results = []
        try:
                for y in seriess:
                        results.append(y)
        except TypeError:
                results.append(seriess)
        df_manuscripts['longi'].loc[index] = results[0]

df_manuscripts['cent'] = pd.to_numeric(df_manuscripts['cent']).astype(float)

df_manuscripts = df_manuscripts.reset_index()

print('before:')
print(df_manuscripts)


def check(cent, language):
        if not df_manuscripts[
                (df_manuscripts['cent'] == cent) & (df_manuscripts['language'] == language)].index.tolist():
                df_manuscripts.loc[len(df_manuscripts.index)] = [len(df_manuscripts.index), cent, language, 0, 0, 0]
        else:
                pass


for x in range(13, 19):
        check(x, 'Catalan')
        check(x, 'Spanish')
        check(x, 'French')
        check(x, 'Latin')
        check(x, 'High German')
        check(x, 'Occitan')
        check(x, 'English')
        check(x, 'Italian')
        check(x, 'Scots')

print('after:')
print(df_manuscripts)
