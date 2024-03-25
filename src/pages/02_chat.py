import streamlit as st
from utils.chatbot import generate_response

st.set_page_config(page_title = "Q&A chat about activities")

with st.sidebar:
    st.markdown('📖 Learn more about your Strava activities')

st.markdown("More Q&A Chatting about activities and stuff")


if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
            st.write(message["content"])

if user_input := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
            st.write(user_input)

if st.session_state.messages[-1]["role"] != "assistant":
    
    # with st.chat_message("system"):
    #     input_message = {'role': "assistant", "content": user_input}
    #     st.write(input_message["content"]) 
    with st.spinner("generating..."):
        response, cypher_query = generate_response(user_input) 

    with st.chat_message("assistant"):
        # response, cypher_query = "this is my response cypher query", "MATCH (n) RETURN n; " 
        
        message = {"role": "assistant", "content": response}
        if "MATCH" in cypher_query:
            st.write('```\n'+cypher_query+'\n```')
            print('cypher query: ', cypher_query)
        print('message content: ', message["content"])
        st.write(message["content"])
        st.session_state.messages.append(message)

with st.expander("Show messages"):
    st.write(st.session_state.messages)
         
