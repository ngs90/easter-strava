import streamlit as st
from config import Config 
from py2neo import Graph
import datetime 
from utils.conversions import ms_to_kmh
import pandas as pd 
import ast 

cnfg = Config()
graph = Graph(uri=cnfg.neo4j_uri, auth=(cnfg.neo4j_user, cnfg.neo4j_pw))

st.set_page_config(page_title = "Activity Statistics")

with st.sidebar:
    st.markdown('📖 Statistics on your Strava Activities')

st.markdown("More Statistics")

data = graph.run("""MATCH (a:MetaAthlete)<-[:PERFORMED_BY]-(n:Activity)
WHERE n.sportType = 'Ride'
RETURN n.id as id, n.name AS RideName, n.averageWatts AS AvgWatt, n.averageSpeed AS AvgSpeed, n.distance AS Distance, n.elapsedTime AS Time, n.startDate as StartDate
ORDER BY n.distance DESC"""
          ).to_data_frame()

data = data.assign(start_date = [datetime.datetime(year=x.year, month=x.month, day=x.day, hour=x.hour, minute=x.minute, second=int(x.second) ) for x in data['StartDate']] )
data = data.assign(duration_h = [int(x.seconds)/3600 for x in data['Time']] )
data = data.assign(avg_speed_kmh = [ms_to_kmh(x) for x in data['AvgSpeed']])
data = data.assign(distance_km = [x/1000 for x in data['Distance']])

min_date = data['start_date'].min().to_pydatetime().replace(hour=0, minute=0, second=0)
max_date = data['start_date'].max().to_pydatetime().replace(day=data['start_date'].max().day+1, hour=0, minute=0, second=0)

# Generating a list of months
months_range = pd.date_range(min_date, max_date, freq='D') ## MS

months_range_datetime = [date.to_pydatetime() for date in months_range]

# Using the list of months as options for the slider
start_date, end_date = st.sidebar.select_slider(
    'Select range of dates to show activities',
    options=months_range_datetime,
    value=(months_range_datetime[-1], months_range_datetime[0])
)

st.write('You selected dates between', start_date, end_date)

data = data[(data['start_date'] >= start_date) & (data['start_date'] <= end_date)]

st.write('Selected activities')
# st.write(data)

activity_ids = st.sidebar.multiselect(
    label='Select activity to show',
    options=data['id'].sort_values(ascending=False),
    format_func=lambda x: data[data['id']==x]['RideName'].values[0] + ' - ' + pd.to_datetime(data[data['id']==x]['start_date'].values[0]).strftime('%Y-%m-%d'),
    )

# print('activity_ids', activity_ids, len(activity_ids))
if activity_ids is not None and len(activity_ids) > 0:

    st.write('You selected', activity_ids)
    data = data[data['id'].isin(activity_ids)]

    st.write(data[['id', 'RideName', 'AvgWatt', 'avg_speed_kmh', 'start_date', 'duration_h']].sort_values('start_date', ascending=False))
    st.scatter_chart(data=data, x='AvgWatt', y='avg_speed_kmh', color='RideName', width=0, height=0, use_container_width=True)
    st.bar_chart(data=data, x='RideName', y='distance_km', width=0, height=0, use_container_width=True)


    st.write('Streams information')

    streams = graph.run(f"""MATCH (a:Activity)-[hs:HAS_STREAM]->(s:Stream)
                            WHERE a.id IN $ids
                            RETURN a.id as id,s.type as stream_type, s.data as values;""",
    parameters={"ids": data['id'].to_list()}
            ).to_data_frame()

    def literal_streams_converter(row, stream_type='altitude'):
        if stream_type == 'latlng':
            pair_strings = row[stream_type][1:-1].split('],[')
            values = [y.replace(']','').replace('[', '').split(',') for y in pair_strings]
            return values
        else:
            values = row[stream_type][1:-1].split(',')
            return values

    #streams['values_conv'] = streams.apply(lambda x: literal_streams_converter(row=x), axis=1)
    #st.write(streams)
    stream_types = streams['stream_type'].drop_duplicates()
    streams_pivot = streams.pivot(index='id', columns='stream_type', values='values')
    for stream_type in stream_types:
        streams_pivot[stream_type] = streams_pivot.apply(lambda x: literal_streams_converter(row=x, stream_type=stream_type), axis=1)

   # print(streams_pivot.dtypes)
    # st.write(streams_pivot['heartrate'].iloc[0])
    # st.write(type(streams_pivot['heartrate'].iloc[0]))
    # st.write(streams_pivot.dtypes)
    st.write(streams_pivot)

    stream_type_selected = st.sidebar.selectbox(label='Select stream type', 
                         options=stream_types
                         )
    
    # print('ok')
    # print(data)
    # print(streams_pivot)

    data_streams_selected = data[['id', 'RideName']].merge(streams_pivot[[stream_type_selected, 'time']], left_on='id', right_index=True, how='left')

    st.write('data_streams_selected')
    st.write(data_streams_selected)

    data_exploded = data_streams_selected.explode([stream_type_selected, 'time'])

    # Sort data by time 
    data_exploded['time'] = data_exploded['time'].astype(int)
    data_exploded = data_exploded.sort_values(['RideName', 'time'], ascending=True) # RideName is important to sort by here!

    # calculate moving averages
    
    # handle missing values
    def missing_values_handler(data, stream_type_selected):
        if stream_type_selected == 'moving':
            return 1 if 'true' else 0
        else:
            if pd.isna(data[stream_type_selected]) or data[stream_type_selected] in ('null', 'false'):
                return 0
            else:
                return float(data[stream_type_selected])

    data_exploded[stream_type_selected] = data_exploded.apply(lambda x: missing_values_handler(data=x, stream_type_selected=stream_type_selected), axis=1)

    column_lengths = {
        stream_type_selected+'_MA_1sec': 1,
        stream_type_selected+'_MA_5sec': 5,
        stream_type_selected+'_MA_10sec': 10,
        stream_type_selected+'_MA_30sec': 30,
        stream_type_selected+'_MA_1min': 60,
        stream_type_selected+'_MA_5min': 5*60,
        stream_type_selected+'_MA_10min': 10*60,
        stream_type_selected+'_MA_15min': 15*60,
        stream_type_selected+'_MA_20min': 20*60,
        stream_type_selected+'_MA_30min': 30*60,
        stream_type_selected+'_MA_60min': 60*60
    }

    # print(data_exploded)
    def rolling_means(x, column_lengths):
        windows = column_lengths.values()
        columns = column_lengths.keys()
        data = pd.concat([x.rolling(window).mean() for window in windows], axis=1)
        print('this is x')
        print(x)
        print(x.shape[0])
        data['time'] = pd.Series([range(0,x.shape[0])])
        data.columns = [f'{col}' for col in columns] + ['time']
        return data

    # Apply the rolling means calculation
    MAs = data_exploded.groupby(['id'])[stream_type_selected].apply(lambda x: rolling_means(x, column_lengths)).reset_index(drop=False)
    data_exploded = data_exploded.reset_index(drop=True)

    print(MAs)


    print(data_exploded)

    MAs = pd.merge(left=data_exploded, right=MAs, left_on=['id','time'], right_on=['id','time'], how='left')
    # MAs = pd.concat([data_exploded, MAs], axis=1)

    print(MAs)


    # for key, value in column_lengths.items():
    #     print(key, value)
    #     if value == 1:
    #         data_exploded[key] = data_exploded.groupby('id')[stream_type_selected].max()
    #     else:
    #         data_exploded[key] = data_exploded.groupby('id')[stream_type_selected].rolling(value).mean().reset_index(0,drop=True)

    #print('MAs exploded')
    # print(MAs)

    st.write(MAs)
    
    st.line_chart(data=MAs, x='time', y=stream_type_selected, color='RideName')
    st.scatter_chart(data=MAs, x='time', y=stream_type_selected+'_MA_5min', color='RideName', size=5)

    # power curve 
    power_curve_data = MAs.groupby(['id', 'RideName']).agg({k: 'max' for (k, v) in column_lengths.items()}).reset_index(drop=False)
    power_curve_data_melted = power_curve_data.melt(id_vars=['id', 'RideName'], value_vars=column_lengths.keys())

    st.write('power curve data')
    st.write(power_curve_data)
    st.write(power_curve_data_melted)

    # power_values = [(v, data_exploded[k]) for k, v in column_lengths.items()]

    # power_values_df = pd.DataFrame(power_values, columns=['time', 'value'])
    power_curve_data_melted['time'] = power_curve_data_melted['variable'].apply(lambda x: column_lengths[x]).astype(int)
    power_curve_data_melted = power_curve_data_melted.sort_values('time', ascending=True)

    st.scatter_chart(data=power_curve_data_melted, x='time', y='value', color='RideName') 





