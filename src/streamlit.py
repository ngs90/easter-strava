import streamlit as st 
from streamlit_oauth import OAuth2Component 
import os 
from dotenv import load_dotenv
from config import Config 

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
redirect_url = "http://localhost:8501"
auth_base_url = "https://www.strava.com/oauth/authorize"
token_url = 'https://www.strava.com/api/v3/oauth/token'
deauthorize_url = 'https://www.strava.com/oauth/deauthorize'
scope = 'profile:read_all'

oauth2 = OAuth2Component(client_id=client_id, 
                         client_secret=client_secret,
                         authorize_endpoint=auth_base_url,
                         token_endpoint=token_url,
                         refresh_token_endpoint=token_url,
                         revoke_token_endpoint=deauthorize_url)


# st.markdown("""
#     <style>
#     button[class*="authorize_button"] {
#         height: 150px; /* Adjust the height */
#         width: 400px; /* Adjust the width */
#         font-size: 20px; /* Adjust the font size */
#     }
#     </style>
#     """, unsafe_allow_html=True)

if 'token' not in st.session_state:
  result = oauth2.authorize_button(name="Continue with Strava", 
                                   redirect_uri=redirect_url, 
                                   scope=scope,
                                   icon=Config.icon,
                                   height=800,
                                   width=600,
                                   use_container_width=True
                                   )
  if result:
    st.session_state.token = result.get('token')
    st.rerun()

else: 
    if st.button('Show token'):
        st.write(f'Hello, *World!* :sunglasses: Token: {st.session_state.token}')
