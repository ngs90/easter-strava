import streamlit as st
from config import Config 
from py2neo import Graph

cnfg = Config()
graph = Graph(uri=cnfg.neo4j_uri, auth=(cnfg.neo4j_user, cnfg.neo4j_pw))

st.set_page_config(page_title = "Activity Statistics")

with st.sidebar:
    st.markdown('📖 Statistics on your Strava Activities')

st.markdown("More Statistics")

data = graph.run("""MATCH (a:MetaAthlete)<-[:PERFORMED_BY]-(n:Activity)
WHERE n.sportType = 'Ride'
RETURN n.name AS RideName, n.averageWatts AS AvgWatt, n.averageSpeed AS AvgSpeed, n.distance AS Distance, n.elapsedTime AS Time, n.startDate as StartDate
ORDER BY n.distance DESC"""
          ).to_data_frame()

st.write(data[['RideName', 'AvgWatt', 'AvgSpeed', 'Distance']])
st.write(data.dtypes)
st.scatter_chart(data=data, x='AvgWatt', y='AvgSpeed', color=None, width=0, height=0, use_container_width=True)
st.bar_chart(data=data, x='RideName', y='Distance', width=0, height=0, use_container_width=True)