# https://neo4j.com/docs/getting-started/data-import/json-rest-api-import/
# https://www.markhneedham.com/blog/2018/06/12/neo4j-building-strava-graph/

from neo4j import GraphDatabase
from config import Config
from utils.auth import create_session
from utils.cypher import _get_ids, _delete_all, _get_activities, _get_stream
from neo4j.exceptions import ClientError

conf = Config()
_ = create_session(conf, verify_token=True)

uri = conf.neo4j_uri
driver = GraphDatabase.driver(uri=uri, auth=(conf.neo4j_user, conf.neo4j_pw))


# apoc.text.upperCamelCase('Stream '+json.type)

with driver.session() as session:
    print('Get and save activities...')
    result = session.execute_write(_get_activities, conf.token['access_token'])
    
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

    # result =session.execute_write(_delete_all)

print(values)
driver.close()
