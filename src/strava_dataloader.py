from config import Config
from utils.auth import create_session
from pprint import pprint

conf = Config()
session = create_session(conf, verify_token=True)
athlete_id = session.token['athlete']['id']

# Athlete stats 
athlete_url = f'https://www.strava.com/api/v3/athletes/{athlete_id}/stats'
response = session.get(athlete_url)
pprint(response.json())

# Athlete 
athlete_url = 'https://www.strava.com/api/v3/athlete'
response = session.get(athlete_url)
pprint(response.json())

activities_url = f'https://www.strava.com/api/v3/athlete/activities'
response = session.get(activities_url)
print('Athlete activities')
pprint(response.json())

