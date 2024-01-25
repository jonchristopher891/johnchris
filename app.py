import os
import openai
#from dotenv import load_dotenv
import dotenv
import streamlit as st
from streamlit_chat import message
import json

dotenv.load_dotenv()

endpoint = os.environ.get("AOAIEndpoint")
api_key = os.environ.get("AOAIKey")
deployment = os.environ.get("AOAIDeploymentId")

st.set_page_config(
    page_title="Streamlit OpenAI Chat",
    page_icon=":Query Financial data:"
)

st.header("Generative AI - Query Financial data Chatbot")


# Storing GPT-4 responses for easy retrieval to show on Chatbot UI in Streamlit session
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

# Storing user responses for easy retrieval to show on Chatbot UI in Streamlit session
if 'past' not in st.session_state:
    st.session_state['past'] = []

# Storing entire conversation in the required format of GPT-4 in Streamlit session
if 'messages' not in st.session_state:
    st.session_state['messages'] = [{'role':'system','content':'Financial Data'}]

def update_chat(messages, role, content):
    messages.append({"role": role, "content": content})
    return messages

query = st.text_input("Query: ", key="input")

client = openai.AzureOpenAI(
    base_url=f"{endpoint}/openai/deployments/{deployment}/extensions",
    api_key=api_key,
    api_version="2023-08-01-preview",
)
if query:
     with st.spinner("generating..."):
        messages = st.session_state['messages']
        messages = update_chat(messages, "user", query)
        try:

            completion = client.chat.completions.create(
                model=deployment,
                messages=[
                    {
                        "role": "user",
                        "content": query,
                    },
                ],
                extra_body={
                    "dataSources": [
                        {
                            "type": "AzureCognitiveSearch",
                            "parameters": {
                                "endpoint": os.environ["SearchEndpoint"],
                                "key": os.environ["SearchKey"],
                                "indexName": os.environ["SearchIndex"]
                            }
                        }
                    ]
                }
            )
            #print(completion.model_dump_json(indent=2))
            output = completion.model_dump_json(indent=2)
            data = completion.choices[0].message.content
            print(data)
            messages = update_chat(messages, "assistant", completion)
            st.session_state.past.append(query)
            st.session_state.generated.append(data)
            if st.session_state['generated']:

                for i in range(len(st.session_state['generated'])-1, -1, -1):
                    message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
                    message(st.session_state["generated"][i], key=str(i))
                #message(st.session_state["updated_df"][i], key=str(i)+ '_df')
            #st.dataframe = df

            with st.expander("Show Messages"):
                st.write(messages)
        except Exception as e:
            st.write(f"Error: {e}")