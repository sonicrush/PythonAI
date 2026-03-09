import streamlit as streamlit
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

#pip install -U google-genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

streamlit.title("AI Document Asisstant")

if "client" not in streamlit.session_state:
    streamlit.session_state.client = genai.Client(api_key=api_key)

with streamlit.sidebar:
    streamlit.header("Setup")
    uploaded_file_ui = streamlit.file_uploader("Upload your document", type=["pdf","txt"])
    if uploaded_file_ui and "doc_ref" not in streamlit.session_state:
        with streamlit.spinner("Uploading your document"):
            mime_type = uploaded_file_ui.type

            #writing bytes to a temp file
            with open("temp_doc","wb") as file:
                file.write(uploaded_file_ui.getbuffer())

            doc_ref = streamlit.session_state.client.files.upload(
                file = "temp_doc",
                config = {'mime_type': mime_type}
            )
            streamlit.session_state.doc_ref = doc_ref

            streamlit.session_state.chat = streamlit.session_state.client.chats.create(
                model="gemini-3-flash-preview",
                config=types.GenerateContentConfig(
                    system_instruction="You are a expert on the document that has been uploaded to you."
                                       "Answer questions ONLY using the uploaded file."
                                        "If the answer isn't there, reply to the question with \"I Don't know.\" "
                )
            )

        streamlit.success("Document uploaded successfully!")
if "messages" not in streamlit.session_state:
    streamlit.session_state.messages = [] #Creates list of dictionaries, each containing role and content. These are messages.

for message in streamlit.session_state.messages:
    with streamlit.chat_message(message["role"]): #create a div block for eah role
        streamlit.markdown(message["content"])

prompt = streamlit.chat_input("Ask a question about the uploaded document:")
if prompt:
    if "chat" not in streamlit.session_state:
        streamlit.error("Please upload a document first!")

    else:
        streamlit.session_state.messages.append({"role":"user","content":prompt})

    with streamlit.chat_message("user", avatar="😎"):
        streamlit.markdown(prompt)

    with streamlit.chat_message("assistant"):
        response = streamlit.session_state.chat.send_message(
            message = [streamlit.session_state.doc_ref, prompt]
        )
        streamlit.markdown(response.text)
        streamlit.session_state.messages.append({"role":"assistant","content":response.text})