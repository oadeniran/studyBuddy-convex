import os
from dotenv import load_dotenv
from convex import ConvexClient
load_dotenv(".env.local")
load_dotenv()

client = ConvexClient(os.getenv("CONVEX_URL"))

def login(login_details):
    res = client.query("tasks:get_login", {"username":login_details["username"]})
    if len(res) != 1:
        return {
            "status_code" : 404,
            'message' : "User not found",
        }
    else:
        
        if login_details["password"] != res[0]["password"]:
            return {
            "status_code" : 400,
            'message' : "Password incorrect",
        }
        else:
            return {
            "status_code" : 200,
            'message' : "Sign In successful",
            "uid" : res[0]["_id"]
        }

def signup(signup_details):
    res = client.query("tasks:get_login", {"username":signup_details["username"]})
    if len(res) > 0:
        return {
            "status_code" : 400,
            'message' : "User Exists already, please sign in",
        }
    else:
        res = client.mutation("tasks:complete_signup", signup_details)
        print(res)
        if res:
            return {
            "status_code" : 200,
            'message' : "User Created",
        }
        else:
            return {
            "status_code" : 400,
            'message' : "Signup Error",
        }

def get_user_categories(uid):
    res = client.query("tasks:get_categories", {"uid":uid})
    if len(res) != 1:
        return {
            "status_code" : 404,
            'message' : "Categories not found",
        }
    else:
        return {
            "status_code" : 200,
            "categories" :res[0]["categories"],
            "category_det" : res[0]["category_det"],
            "categories_dict" : res[0]["categories_dict"],
            "history_dict" : res[0]["history_dict"]
        }

def create_user_categories(category_data):
    res = client.mutation("tasks:create_categories", category_data)
    if res:
        return {"status_code" : 200}
    
