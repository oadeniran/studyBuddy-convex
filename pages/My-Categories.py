import streamlit as st
import requests
from dotenv import load_dotenv
import os
import json
from utils import upload, chatbot
import convex_helper as cvh



load_dotenv()

categories = ["Add New category"]

def post_save_cat():
    payload = { "uid": st.session_state["loggedIn"]["uid"],
                    "categories" : st.session_state["categories"],
                    "category_det": st.session_state["category_det"],
                    "categories_dict": st.session_state["categories_dict"],
                    "history_dict" : st.session_state["history_dict"]
                }
    #url = f"{base_url}/update-user-categories"
    result = cvh.create_user_categories(category_data=payload,)

def run_interact(curr_cat):
    sub_opt = st.sidebar.radio("What action ?", ["interact", "generate_quiz"])
    if sub_opt == "interact":
        st.sidebar.write("Select what pdf you want to interact with")
        book = st.sidebar.radio("Select book", [k for k in st.session_state["categories_dict"][f"cat_{curr_cat}"].keys()])
        if book:
            if curr_cat not in st.session_state["history_dict"]:
                st.session_state["history_dict"][curr_cat] = {}
            if book not in st.session_state["history_dict"][curr_cat]:
                st.session_state["history_dict"][curr_cat][book] = {}
            
            ind = [k for k in st.session_state["categories_dict"][f"cat_{curr_cat}"].keys()].index(book)
            
            chatbot(book, curr_cat, ind, st.session_state["history_dict"][curr_cat][book])


def delete_file():
    pass

def run_upload(curr_cat):
    cat_dict = st.session_state["categories_dict"][f"cat_{curr_cat}"]
    if upload(st.session_state['loggedIn']["uid"], curr_cat, cat_dict) == "done":
        post_save_cat()
        st.write("Please Proceed")


def run_cat_selection(selection):
    ind = st.session_state["categories"].index(selection)
    st.title(selection)
    st.subheader(st.session_state["category_det"][ind-1])
    st.sidebar.title("Options")
    opt_sel = st.sidebar.selectbox("Actions", ["Interact", "Upload file", "Delete file"])
    if opt_sel == "Interact":
        post_save_cat()
        run_interact(selection)
    elif opt_sel == "Upload file":
        run_upload(selection)
    else:
        delete_file()



def add_new_ctegory(categories):
    with st.form("Details",clear_on_submit=True):
        category_name = st.text_input("Name")
        category_details = st.text_input("Description")
        submit_button = st.form_submit_button('CREATE')

        if submit_button:
            if not category_name:
                st.error("Name field is required")
            else:
                if not category_details:
                    category_details = ""
                categories.append(category_name)
                st.session_state['categories'].append(category_name)
                st.session_state["category_det"].append(category_details)
                if "categories_dict" not in st.session_state:
                    st.session_state["categories_dict"] = {}
                    st.session_state["categories_dict"][f"cat_{category_name}"] = {}
                else:
                    st.session_state["categories_dict"][f"cat_{category_name}"] = {}
                
                #print(st.session_state["categories_dict"]["cat_Mee 303"])
                #print(st.session_state["ret"])
                post_save_cat()
                st.success("Category created", icon="👌")

if 'loggedIn' not in st.session_state:
    st.error("Please Login to Use feature......Return Home to login")
else:
    st.sidebar.title("Navigation")
    if "categories" not in st.session_state:
        st.session_state['categories'] = categories
        st.session_state["category_det"] = []

    selection = st.sidebar.radio("Go to", st.session_state['categories'])
    if selection == "Add New category":
        add_new_ctegory(categories)
    else:
        run_cat_selection(selection)