import pandas as pd
import numpy as np

# Download the csv file from GitHub account
manuscripts_url = "https://raw.githubusercontent.com/ameliemcc/sevensagesapp/master/complete_manuscripts_csv.csv"

manuscripts_all = pd.read_csv(manuscripts_url, sep=';', skipinitialspace = True)

# make a copy of the full dataframe, just in case we need it again
manuscripts_all_map = manuscripts_all

# replace empty date spaces with nan
manuscripts_all_map['date_start'].replace(' ', np.nan, inplace=True)
manuscripts_all_map['date_end'].replace(' ', np.nan, inplace=True)
manuscripts_all_map['iso-3'].replace(' ', np.nan, inplace=True)

# remove whitespaces where necessary
manuscripts_all_map['iso-3'].str.strip()

# drop rows which don't have a value for date_start
manuscripts_all_map.dropna(subset=['date_start'], inplace=True)

manuscripts_all_map.dropna(subset=['iso-3'], inplace=True)

# if no value for date_end, give it the same as date_start
manuscripts_all_map['date_end'] = pd.to_numeric(manuscripts_all_map['date_end']).fillna(manuscripts_all_map['date_start']).astype(float)

# calculate a date mean
manuscripts_all_map['new_mean'] = (manuscripts_all_map['date_start'] + manuscripts_all_map['date_end']) / 2

# deduce the century of production of the print
rx = r'^(\d\d)'
manuscripts_all_map['date_mean_str'] = manuscripts_all_map['new_mean'].astype(str)
manuscripts_all_map['cent'] = manuscripts_all_map['date_mean_str'].str.extract(rx)
manuscripts_all_map['cent'] = pd.to_numeric(manuscripts_all_map['cent']).astype(float) + 1

# make a new dataframe in which the towns are counted by century
df_manuscripts = (manuscripts_all_map['iso-3'].groupby(manuscripts_all_map['cent'])
        .value_counts()
        .reset_index(name='count'))

df_manuscripts['language'] = manuscripts_all_map['language']

df_manuscripts['cent'] = pd.to_numeric(df_manuscripts['cent']).astype(float)

df_manuscripts = df_manuscripts.reset_index()


def check(cent, label):
        if not df_manuscripts[(df_manuscripts['cent'] == cent)&(df_manuscripts['iso-3'] == label)].index.tolist() :
                df_manuscripts.loc[len(df_manuscripts.index)] = [len(df_manuscripts.index), cent, label, 0, 'lang']
        else :
                pass


for x in range(13, 19):
        check(x, 'ITA')
        check(x, 'FRA')
        check(x, 'ESP')
        check(x, 'GBR')
        check(x, 'DEU')

