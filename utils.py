#some code was here
from azure.storage.blob import BlobServiceClient
import os
import streamlit as st
from dotenv import load_dotenv
import streamlit as st
import os
import re
import random
import traceback
import streamlit as st
from dotenv import load_dotenv
from streamlit_chat import message
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OBJECTIVE="Objective"
TRUE_OR_FALSE="True/False"
OBJECTIVE_DEFAULT_VALUE=5
TRUE_OR_FALSE_DEFAULT_VALUE=5
blob_conn_str = os.getenv("BLOLB_CONNECTION_STRING")

llm = ChatOpenAI(    
        openai_api_key=OPENAI_API_KEY, 
        model_name="gpt-4", 
        temperature=0.0
    )

llm = ChatOpenAI(    
        openai_api_key=OPENAI_API_KEY, 
        model_name="gpt-4", 
        temperature=0.0
    )

class Agency:
    def __init__(self):
        self.pdf_agent=None
        self.tools = None
        self.agent = None
    
    def initialize_tools(self,pdf_agent,pdf_name):
        self.pdf_agent = pdf_agent
        tools = [
            Tool(
                name = "PDF Question and Answering Assistant",
                func=self.pdf_agent.run,
                description=f"""
                Useful for answering questions related to the uploaded pdf, the name of the pdf file is {pdf_name}
                """
            )
        ]
        self.tools = tools
    def load_agent_details(self,memory):
        agent_kwargs = {
            'prefix': f"""
            You are a friendly PDF Question and Answering Assistant.
            You are tasked to assist the current user on questions related to the uploaded PDF file.
            You have access to the following tools:{self.tools}.
             Try as much as possible to get your answers only from the tools provided to you. If you can not answer correctly, respond appropriately"""}
        # initialize the LLM agent
        agent = initialize_agent(self.tools, 
                                llm, 
                                agent="chat-conversational-react-description", 
                                verbose=True, 
                                agent_kwargs=agent_kwargs,
                                handle_parsing_errors=True,
                                memory=memory
                                )
        self.agent = agent
    def get_response(self,user_input):
        response = self.agent({"input":user_input,"chat_history":[]})
        return response


def load_cont(container_name):
    blob_service_client = BlobServiceClient.from_connection_string(blob_conn_str)
    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client = container_client.create_container()
    return container_client

def load_blob(container_client, blob_name):
    blob_client = container_client.get_blob_client(blob_name)
    return blob_client

def load_VS_from_azure(container_client, blob_name):
    bc = load_blob(container_client, blob_name)
    f = bc.download_blob()
    return f.read()

def bot_from_load(loaded_bytes, pdf_name):
    embeddings = OpenAIEmbeddings()
    db = FAISS.deserialize_from_bytes(embeddings=embeddings, serialized=loaded_bytes) 
    retriever = db.as_retriever()
    qa = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=retriever,
                )
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agency = Agency()
    agency.initialize_tools(qa,pdf_name)
    agency.load_agent_details(memory)
    return agency


# Upload Section
def upload(uid, category_name, category_dict):
    st.header('Upload Your PDF')
    st.write("Drag and drop your PDF file here or click to upload. Please ensure that the text in the PDF is selectable and not a scanned image.")
    uploaded_file = st.file_uploader("", type="pdf")

    if uploaded_file is not None:
        # Check if the uploaded file is a PDF
        pdf = uploaded_file.name
        pdf_name = '.'.join(pdf.split('.')[:-1])
        with open(pdf, mode='wb') as f:
            f.write(uploaded_file.getbuffer()) # save pdf to disk
        st.success("Uploading File.....")
        loader = PyPDFLoader(pdf)
        #category_dict['pages'] = loader.load_and_split()
        documents = loader.load()
        text_splitter = CharacterTextSplitter(
                chunk_size=400,
                chunk_overlap=20)
        texts = text_splitter.split_documents(documents)
        if len(texts) == 0:
            st.error("Please ensure your uploaded  document is selectable (i.e not scanned)")
        else:
            st.success("File uploaded successfully!")
            st.write("Processing Uploaded PDF..........")
            # Create the dict for uploaded pdf
            embeddings = OpenAIEmbeddings()
            try:
                db = FAISS.from_documents(texts,embeddings)
                retriever = db.as_retriever()
                qa = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=retriever,
                )
                pkl = db.serialize_to_bytes()
                with open(f"my_file.txt", "wb") as binary_file:
                    # Write bytes to file
                    binary_file.write(pkl)
                cont = load_cont(uid)
                blob_client = load_blob(cont, blob_name=f"{category_name}_{pdf_name}")

                with open("my_file.txt", "rb") as f:
                    res = blob_client.upload_blob(f, overwrite=True)
                    
                category_dict[pdf_name] = f"{category_name}_{pdf_name}"
                memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
                agency = Agency()
                agency.initialize_tools(qa,pdf_name)
                agency.load_agent_details(memory)
                if category_name not in st.session_state["bots"]:
                    st.session_state["bots"][category_name] = []
                st.session_state["bots"][category_name].append(agency)
                st.success("PDF processed Successfully!!!")
                
                return "done"
            except Exception as e:
                print(f"An error occurred: {e}")
                traceback.print_exc()
                st.error("A network error occured, Please check your internet connection and try again")


def chatbot(pdf_name, category_name,ind, history_dict):
        st.header("StudyBud")
        qa = st.session_state['bots'][category_name][ind]
        st.markdown(f"Ask questions related to the uploaded file here : {pdf_name}")
        message("Hiiiiii!!, I am your studyBud, your personal reading buddy  😊 😊 😊!!!!")
        if "past" not in history_dict:
            history_dict['past'] = []
        if "generated" not in history_dict:
            history_dict["generated"] = []
        if "input_message_key" not in history_dict:
            history_dict["input_message_key"] = str(random.random())
        chat_container = st.container()
        user_input = st.text_input("Type your question here.", key=history_dict["input_message_key"])
        if st.button("Send"):
            response = qa.get_response(user_input)
            history_dict["past"].append(user_input)
            history_dict["generated"].append(response['output'])
            history_dict["input_message_key"] = str(random.random())
            st.rerun()
        if history_dict["generated"]:
             with chat_container:
                  for i in range(len(history_dict["generated"])):
                    message(history_dict["past"][i], is_user=True, key=str(i) + "_user")
                    message(history_dict["generated"][i], key=str(i))