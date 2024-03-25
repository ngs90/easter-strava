# https://neo4j.com/developer-blog/generating-cypher-queries-with-chatgpt-4-on-any-graph-schema/
# https://community.neo4j.com/t/best-private-llm-for-creating-cypher-queries/63798/3 
# https://towardsdatascience.com/fine-tuning-an-llm-model-with-h2o-llm-studio-to-generate-cypher-statements-3f34822ad5

from config import Config
from utils.auth import create_session
from utils.cypher import _get_schema_node_properties, _get_schema_rel_properties
from neo4j import GraphDatabase
from openai import OpenAI

conf = Config()
client = OpenAI(
    api_key=conf.openai_key
)
# openai.api_key = conf.openai_key

_ = create_session(conf, verify_token=True)

uri = conf.neo4j_uri
driver = GraphDatabase.driver(uri=uri, auth=("neo4j", conf.neo4j_pw))

def get_schema_description(node_props, rels):
    text = f"""
    This is the schema representation of the Neo4j database.
    Node properties are the following:
    {node_props}
    Relationships from source to target nodes:
    {rels}
    Additionally the following directions on relationsships are valid:
        (n:Activity)-[pb:PERFORMED_BY]->(a:MetaAthlete)
        (n:Activity)-[hs:HAS_STREAM]->(s:Stream)
        (n:Activity)-[hs:HAS_MAP]->(p:PolylineMap)
    Make sure to respect relationship types and directions.
    """
    return text 

def get_system_message(schema_text):

    examples =  """Here is an example query that is valid and respects the directions: 
    match (a:MetaAthlete)<-[pb:PERFORMED_BY]-(n:Activity)-[hs:HAS_STREAM]->(s:Stream)
    return a, pb, n, hs, s"""

    # text = f"""
    #     You are an assistant with an ability to generate Cypher queries.
    #     Task: Generate Cypher queries to query a Neo4j graph database based on the provided schema definition.
    #     Instructions:
    #     Use only the provided relationship types.
    #     Do not use any other relationship types or properties that are not provided.
    #     If you cannot generate a Cypher statement based on the provided schema, explain the reason to the user.
    #     Schema:
    #     {schema_text}
    #     Example cypher queries are:
    #     {examples}
    #     """
    
    text = f"""
            Task: Generate Cypher queries to query a Neo4j graph database based on the provided schema definition.
            Instructions:
            Use only the provided relationship types and properties.
            Do not use any other relationship types or properties that are not provided.
            If you cannot generate a Cypher statement based on the provided schema, explain the reason to the user.
            The return part of the query should consist of simple datatypes that can be represented in a table, i.e. types such as string, int, float etc.
            Schema:
            {schema_text}
            Example cypher queries are:
            {examples}
            Note: Do not include any explanations or apologies in your responses. Only return a valid Cypher query if you can.            
            """

    return text

def get_sys_prompts():
    with driver.session() as session:
        print('Get db schema...')
        node_props = session.execute_read(_get_schema_node_properties)
        #print(result)
        rels = session.execute_read(_get_schema_rel_properties)
        #print(result)

        node_probs = session.execute_read(_get_schema_node_properties)
    schema_txt = get_schema_description(node_props, rels)
    return get_system_message(schema_txt)

def read_query(query, params={}):
        with driver.session() as session:
            try:
                result = session.run(query, params)
                response = [r.values() for r in result]
                if response == []:
                        return "Either there is no result found for your question Or please help me with additional context."
                return response
            except Exception as inst:
                if "MATCH" in query:
                    return "Either there is no result found for your question Or please help me with additional context!"
                else:
                    return query

def generate_cypher(messages):
    messages = [
        {"role": "system", "content": get_sys_prompts()}
    ] + messages
    # Make a request to OpenAI
    completions = client.chat.completions.create(
        model="gpt-3.5-turbo", # gpt-4, gpt-3.5-turbo
        messages=messages,
        temperature=0.0
    )
    response = completions.choices[0].message.content
    return response

def generate_response(prompt, cypher=True):
    usr_input = [{"role": "user", "content": prompt}]
    cypher_query = generate_cypher(usr_input)
    message = read_query(cypher_query)
    return message, cypher_query



