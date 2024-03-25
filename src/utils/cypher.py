
def _get_schema_rel_properties(tx):
    result = tx.run("call db.schema.relTypeProperties")
    values = [record.values() for record in result]
    return values 

def _get_schema_node_properties(tx):
    result = tx.run("call db.schema.nodeTypeProperties")
    values = [record.values() for record in result]
    return values

def _delete_all(tx):
    tx.run("MATCH (n) DETACH DELETE n")

def _get_ids(tx):
    result = tx.run("""MATCH (n:Activity)
                       RETURN n.id
                    """)
    
    values = [record.values() for record in result]
    return values 


def _get_activities(tx, token):
    result = tx.run(
        """
        WITH 'https://www.strava.com/api/v3/athlete/activities' AS uri
        CALL apoc.load.jsonParams(uri, {Authorization: $token}, null)
        YIELD value

        MERGE (activity:Activity {id: value.id})
        SET activity.externalId = value.external_id,
            activity.uploadId = value.upload_id,
            activity.name = value.name,
            activity.distance = toFloat(value.distance),
            activity.movingTime = duration({seconds: value.moving_time}),
            activity.elapsedTime = duration({seconds: value.elapsed_time}),
            activity.totalElevationGain = toInteger(value.total_elevation_gain),
            activity.elevationHigh = toFloat(value.elev_high),
            activity.elevationLow = toFloat(value.elev_low),
            activity.sportType = value.sport_type,
            activity.startDate = datetime(value.start_date),
            activity.startDateLocal = datetime(value.start_date_local),
            activity.timezone = value.timezone,
            activity.achievementCount = toInteger(value.achievement_count),
            activity.kudosCount = toInteger(value.kudos_count),
            activity.commentCount = toInteger(value.comment_count),
            activity.athleteCount = toInteger(value.athlete_count),
            activity.photoCount = toInteger(value.photo_count),
            activity.totalPhotoCount = toInteger(value.total_photo_count),
            activity.trainer = value.trainer,
            activity.commute = value.commute,
            activity.manual = value.manual,
            activity.private = value.private,
            activity.flagged = value.flagged,
            activity.workoutType = toInteger(value.workout_type),
            activity.uploadIdStr = value.upload_id_str,
            activity.averageSpeed = toFloat(value.average_speed),
            activity.maximumSpeed = toFloat(value.max_speed),
            activity.hasKudoed = value.has_kudoed,
            activity.hideFromHome = value.hide_from_home,
            activity.gearId = value.gear_id,
            activity.kilojoules = toFloat(value.kilojoules),
            activity.averageWatts = toFloat(value.average_watts),
            activity.deviceWatts = value.device_watts,
            activity.maxWatts = toInteger(value.max_watts),
            activity.weightedAverageWatts = toInteger(value.weighted_average_watts),
            activity.startLat = value.start_latlng[0],
            activity.startLng = value.start_latlng[1],
            activity.endLat = value.end_latlng[0],
            activity.endLng = value.end_latlng[1]

        // Link to MetaAthlete
        MERGE (athlete:MetaAthlete {id: value.athlete.id})
        MERGE (activity)-[:PERFORMED_BY]->(athlete)

        // Link to PolylineMap
        MERGE (map:PolylineMap {id: value.map.id})
        ON CREATE SET map.polyline = value.map.polyline, map.summaryPolyline = value.map.summary_polyline
        MERGE (activity)-[:HAS_MAP]->(map)
        """,
        token="Bearer " + token)


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
            "RETURN {label: 'Stream', props: {id: $activity_id+'_'+json.type, type: json.type, data: apoc.convert.toJson(json.data), series_type: json.series_type, original_size: json.original_size, resolution: json.resolution}} AS nodeInfo",
            json.type <> 'latlng', 
            "RETURN {label: 'Stream', props: {id: $activity_id+'_'+json.type, type: json.type, data: apoc.convert.toJson(json.data), series_type: json.series_type, original_size: json.original_size, resolution: json.resolution}} AS nodeInfo"
        ], null,{activity_id: $activity_id, json: json}) YIELD value AS caseResult

        WITH activity, caseResult.nodeInfo AS nodeInfo
        CALL apoc.create.node([nodeInfo.label], nodeInfo.props) YIELD node AS stream

        MERGE (activity)-[:HAS_STREAM]->(stream)
        RETURN activity, stream
        """,
        token=token,
        activity_id=activity_id)
    
    return result 


# call db.schema.visualization

# def _create_test_data(tx, comment):
#     result = tx.run("""
#         CREATE (a:Activity)
#         SET a.comment = $comment
#         RETURN a.comment + ', from node ' + id(a)
#         """, 
#         comment=comment
#         )  
#     return result.single()[0]
    
# comment = "This was a fun activity"
# result = session.execute_write(_create_test_data, comment)
    

#     MATCH (n)
# OPTIONAL MATCH (n)-[r]-()
# WITH n,r LIMIT 50000
# DELETE n,r
# RETURN count(n) as deletedNodesCount