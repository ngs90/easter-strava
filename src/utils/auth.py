from requests_oauthlib import OAuth2Session
from config import write_env
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError


def create_session(conf, verify_token: bool=True):

    session = OAuth2Session(client_id=conf.client_id, 
                            redirect_uri=conf.redirect_url,
                            token=conf.token
                            )
    
    if verify_token:
        try:
            response = session.get(conf.verify_url)
        except TokenExpiredError as e:
            session = update_token_interactive(session, conf)
            conf.token = session.token
            write_env(conf)
            response = session.get(conf.verify_url)

        if response.status_code == 401 and response.reason == 'Unauthorized':
            print('Updating token...')
            session = update_token_interactive(session, conf)
            conf.token = session.token
            write_env(conf)
        
    return session 

def update_token_interactive(session, conf):

    session.scope = [conf.session_scope]
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
