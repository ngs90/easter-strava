# https://neo4j.com/docs/getting-started/data-import/json-rest-api-import/
# https://www.markhneedham.com/blog/2018/06/12/neo4j-building-strava-graph/

from neo4j import GraphDatabase
from config import Config
from utils.auth import create_session
from utils.cypher import _get_ids, _delete_all, _get_and_save_activities
from neo4j.exceptions import ClientError

conf = Config()
_ = create_session(conf, verify_token=True)

uri = conf.neo4j_uri
driver = GraphDatabase.driver(uri=uri, auth=("neo4j", conf.neo4j_pw))


def _get_stream(tx, token, activity_id):
    # time, distance, latlng, altitude, velocity_smooth, heartrate, cadence, watts, temp, moving, grade_smooth

    result = tx.run("""
        WITH 'https://www.strava.com/api/v3/activities/'+$activity_id+'/streams?keys=watts,time,distance,latlng,altitude,velocity_smooth,heartrate,cadence,temp,moving,grade_smooth&keyByType=true' AS uri
        CALL apoc.load.jsonParams(uri, {Authorization: 'Bearer '+$token}, null) 
        YIELD value AS json

        // Merge on the Activity node based on the external 'id' property
        MERGE (activity:Activity {id: $activity_id})

        WITH activity, json
        CALL apoc.do.case([
            json.type = 'latlng', 
            "RETURN {label: apoc.text.upperCamelCase('Stream '+json.type), props: {id: $activity_id, type: json.type, data: apoc.convert.toJson(json.data), series_type: json.series_type, original_size: json.original_size, resolution: json.resolution}} AS nodeInfo",
            json.type <> 'latlng', 
            "RETURN {label: apoc.text.upperCamelCase('Stream '+json.type), props: {id: $activity_id, type: json.type, data: apoc.convert.toJson(json.data), series_type: json.series_type, original_size: json.original_size, resolution: json.resolution}} AS nodeInfo"
        ], null,{activity_id: $activity_id, json: json}) YIELD value AS caseResult

        WITH activity, caseResult.nodeInfo AS nodeInfo
        CALL apoc.create.node([nodeInfo.label], nodeInfo.props) YIELD node AS stream

        MERGE (activity)-[:HAS_STREAM]->(stream)
        RETURN activity, stream
        """,
        token=token,
        activity_id=activity_id)
    
    return result

with driver.session() as session:
    print('Get and save activities...')
    result = session.execute_write(_get_and_save_activities, conf.token['access_token'])
    
    print('Get activity ids...')
    values = session.execute_read(_get_ids)
    activity_ids = [x[0] for x in values]

    for activity_id in activity_ids:
        print('Get and save activity: ' + str(activity_id))
        try:
            result = session.execute_write(_get_stream, conf.token['access_token'], activity_id)
            print(result)
        except ClientError as e:
            print('Failed for activity: ' + str(activity_id) + ' - ClientError: ' + str(e))
    
    print(values)

    #result =session.execute_write(_delete_all)

print(values)
driver.close()
