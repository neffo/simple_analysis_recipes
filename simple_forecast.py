#from dateutil.relativedelta import relativedelta
import datetime
import pandas as pd
import numpy as np

# dataframe reference = https://pandas.pydata.org/pandas-docs/stable/reference/frame.html

# this is an extremely crude forecast technique that uses average q/q movements of data series
# this is intended to be extremely _unfancy_, and something that could be calculated with a pencil

# this is slightly less crude than bfill or ffill


# load data from one sheet in Excel or ODS file
# assume data in columns, with quarter in first column
# data from the 2nd row, but we could delete extraneous data with skip rows
# assume no footer or other garbage
def load_data_q(filename, sheetname, skiprows = 0):
    data = pd.read_excel(filename, parse_dates=True, sheet_name=sheetname, skiprows=skiprows)
    #print(data.columns)
    data.rename(columns={'Unnamed: 0': 'quarter'}, inplace=True)
    return data

def analyse_series_q(data, column_name, qonq = True, yony = True):
    df = pd.DataFrame(data, columns = ['quarter', column_name])
    if qonq:
        df = df.assign(qonq = df[column_name]/df[column_name].shift(periods=1)-1)
    if yony:
        df = df.assign(yony = df[column_name]/df[column_name].shift(periods=4)-1)
    df = df.assign(q = df['quarter'].dt.month, y = df['quarter'].dt.year)
    return df

def crude_forecast_qonq(data):
    qavg = data.groupby('q')['qonq'].mean()
    df = b.merge(qavg, how='inner', left_on='q', right_on='q', suffixes=(None, '_avg'))['qonq_avg']
    return df

def crude_forecast_yony(data):
    yavg = data.groupby('q')['yony'].mean()
    df = b.merge(yavg, how='inner', left_on='q', right_on='q', suffixes=(None, '_avg'))['yony_avg']
    return df

data = load_data_q('test series.ods', 'Sheet1')

# if we want to forecast a value we need to have a row for it, so we should also add rows here
# the dataset already has a blank row but we want to add 3 more
# this is hacky but Python/numpy/pandas is a terrible experience when using dates
#print(data.tail(n=1))
append_rows = 3
last_quarter = data.tail(n=1)['quarter'].to_list()[0]
#print(data.tail(n=1).index)
next_index = len(data.index)

#print(last_quarter)
delta = np.timedelta64(92,'D')
for i in range(append_rows):
    next_quarter = last_quarter + (delta * (i+1))
    #print('utc ', next_quarter.isoformat)
    df = pd.DataFrame(data=[[np.datetime64(next_quarter),None,None]], columns=['quarter', 'Series1', 'Series2'], index=[next_index+i])
    #print(df)
    data = pd.concat([data, df])
    #print(b.tail(n=1)['quarter'])



b = analyse_series_q(data, 'Series2', True, True)
#print(b)
c = crude_forecast_qonq(b)
d = crude_forecast_yony(b)

# create forecast series as new columns (these are distinct data sets because you wouldn't normally do both)
# we take the mean q/q or mean y/y growth rate and apply it to the previous quarter or previous year

#data.assign(fcq = b['Series2'], inplace=True)

bq= data.assign(fcq = b['Series2'].shift(periods=1)*(c+1)) # this only forecasts one quarter foreward
by= data.assign(fcy = b['Series2'].shift(periods=4)*(d+1))

fq = bq.bfill(axis=1)
fy = by.bfill(axis=1)

print('QoQ forecast:')
print(fq)
print('YoY forecast:')
print(fy)