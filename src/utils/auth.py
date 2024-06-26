from requests_oauthlib import OAuth2Session
from config import write_env

def create_session(conf, verify_token: bool=True):

    session = OAuth2Session(client_id=conf.client_id, 
                            redirect_uri=conf.redirect_url,
                            token=conf.token
                            )
    
    if verify_token:
        response = session.get('https://www.strava.com/api/v3/athlete')
        print(f"Response Status: {response.status_code}")
        print(f"Response Reason: {response.reason}")

        if response.status_code == 401 and response.reason == 'Unauthorized':
            print('Updating token...')
            session = update_token_interactive(session, conf)
            conf.token = session.token
            print('token', conf.token)
            write_env(conf)
        
    return session 

def update_token_interactive(session, conf):

    session.scope = ['profile:read_all']
    auth_link = session.authorization_url(conf.auth_base_url)

    print(f"Click here to authorize: {auth_link[0]}")

    redirect_response = input("Paste redirect url here:")

    
    session.fetch_token(
        token_url=conf.token_url,
        client_id=conf.client_id,
        client_secret=conf.client_secret,
        authorization_response=redirect_response,
        include_client_id=True
    )

    return session
