from flask import Flask, request, render_template, make_response, redirect, url_for, flash
import pymongo
from dbHelper import add, find, findOne, update
from datetime import datetime, timedelta
import html
import hashlib
import os
import bcrypt
import json
import os

client = pymongo.MongoClient("mongo")
db = client["CLUELESS"]

def validate_password(password):
    specialChar = {'!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '='}
    validChar = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&()-_=')
    if len(password) < 8:
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char in specialChar for char in password):
        return False
    if not all(char in validChar for char in password):
        return False
    return True

app = Flask(__name__)
app.config["IMAGE_UPLOADS"] = "/uploads"
 
@app.route("/")
def root():
    loggedin = False
    user_name_here = ""
    auth_token = request.cookies.get("authToken")
    TokensCol = db["Tokens"]
    if auth_token:
        auth = hashlib.sha256(auth_token.encode()).hexdigest()
        token = TokensCol.find_one({"authToken": auth})
        if token and token["expire"] > datetime.now():
            user_name_here = token["username"]
            loggedin = True
    return render_template("index.html", user_name_here=user_name_here, loggedin=loggedin)

@app.route("/register", methods=["POST"])
def register():
    if request.method == "POST":
        username = html.escape(request.form.get('username'))
        password = request.form.get('password')
        repeatPassword = request.form.get("confirmpassword")
        AccountCol = db["Accounts"]
        account = AccountCol.find_one({"username": username})
        if account:
            flash("Username taken", "error")
        else:
            if repeatPassword == password:
                if validate_password(password):
                    salt = bcrypt.gensalt()
                    hashed_password = hashlib.sha256(password.encode() + salt).hexdigest()
                    user_info = {
                        "username": username,
                        "password": hashed_password,
                        "salt": salt
                    }
                    AccountCol.insert_one(user_info)
                    flash("Account created", "success")
                else:
                    flash("Password needs: 1 uppercase, 1 lowercase, 1 special character, and one number", "error")
            else:
                flash("Passwords don't match", "error")
    return redirect(url_for("root"))

@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        username = html.escape(request.form.get('username'))
        password = request.form.get('password')
        AccountCol = db["Accounts"]
        TokensCol = db["Tokens"]
        account = AccountCol.find_one({"username": username})
        if account:
            hashed_password = account["password"]
            salt = account["salt"]
            check = hashlib.sha256(password.encode() + salt).hexdigest()
            if check == hashed_password:
                auth_token = bcrypt.gensalt().decode()
                hashed = hashlib.sha256(auth_token.encode()).hexdigest()
                expire = datetime.now() + timedelta(minutes=60)
                TokensCol.update_one({"username": username}, {"$set": {"authToken": hashed, "expire": expire}}, upsert=True)
                response = make_response(redirect(url_for("root")))
                response.set_cookie('authToken', auth_token, expires=expire, httponly=True, samesite='Strict')
                return response
            else:
                flash("Invalid credentials", "error")
        else:
            flash("Invalid credentials", "error")

    return redirect(url_for("root"))

@app.route("/logout", methods=["POST"])
def logout():
    TokensCol = db["Tokens"]
    auth_token = request.cookies.get("authToken")
    if auth_token:
        auth = hashlib.sha256(auth_token.encode()).hexdigest()
        token = TokensCol.find_one({"authToken": auth})
        if token and token["expire"] > datetime.now():
            TokensCol.update_one({"authToken": auth}, {"$set": {"expire": datetime.fromtimestamp(0)}})
    response = make_response(redirect(url_for("root")))
    response.delete_cookie("authToken")
    return response

@app.route("/chatroom", methods=["GET"])
def chatroom():
    print("redirect to chatroom")
    user_name_here = ""
    loggedin = False
    auth_token = request.cookies.get("authToken")
    TokensCol = db["Tokens"]
    filename = "/static/default.jpg"
    if auth_token:
        auth = hashlib.sha256(auth_token.encode()).hexdigest()
        token = TokensCol.find_one({"authToken": auth})
        if token and token["expire"] > datetime.now():
            loggedin = True
            user_name_here = token["username"]
            PfpCol = db["pfp"]
            pfp_doc = PfpCol.find_one({"username": user_name_here})
            if pfp_doc is not None:
                filename = pfp_doc["path"]
    MessagesCol = db["Messages"]
    messages = list(MessagesCol.find({}))
    return render_template("chat.html", messages = messages, authenticated = loggedin, username = user_name_here, file_name = filename)

@app.route("/chatroom-message", methods=["POST"])
def chatroom_post():
    AccountCol = db["Accounts"]
    TokensCol = db["Tokens"]
    MessagesCol = db["Messages"]
    IDCol = db["UID"]

    # Get unique ID from database and increment it by 1
    get_id = IDCol.find_one({"unique_id": {"$exists": True}})
    if get_id is None:
        IDCol.insert_one({"unique_id": 1})
    get_id = IDCol.find_one({"unique_id": {"$exists": True}})
    uid = get_id["unique_id"]
    uid += 1
    IDCol.update_one({"_id": get_id["_id"]}, {"$set": {"unique_id": uid}})

    #check if user authenticated
    found_user = "Guest"
    auth_token = request.cookies.get("authToken")
    if auth_token:
        auth = hashlib.sha256(auth_token.encode()).hexdigest()
        token = TokensCol.find_one({"authToken": auth})
        if token and token["expire"] > datetime.now():
            found_user = token["username"]

    if found_user == "Guest":
        temp_pfp_test = '''<img src="/static/default.jpg" alt="picture machine broke :(" class="chat-pfp-image">'''
        sent_message = html.escape(request.form.get("chat"))
        MessagesCol.insert_one({"username": temp_pfp_test + found_user, "message": sent_message, "id": uid, "likes": 0, "likers": []})
    else:
        sent_message = html.escape(request.form.get("chat"))
        PfpCol = db["pfp"]
        pfp_entry = PfpCol.find_one({"username": found_user})
        if pfp_entry is not None:
            path = pfp_entry["path"]
            temp_pfp_test = '<img src="' + path + '" alt="picture machine broke :(" class="chat-pfp-image">'
            MessagesCol.insert_one(
                {"username": temp_pfp_test + found_user, "message": sent_message, "id": uid, "likes": 0, "likers": []})
        else:
            temp_pfp_test = '''<img src="/static/default.jpg" alt="picture machine broke :(" class="chat-pfp-image">'''
            MessagesCol.insert_one(
                {"username": temp_pfp_test + found_user, "message": sent_message, "id": uid, "likes": 0, "likers": []})

    return redirect(url_for("chatroom"))

    
@app.route("/like/<int:id>")
def like(id):
    user_name_here = ""
    auth_token = request.cookies.get("authToken")
    TokensCol = db["Tokens"]
    if auth_token:
        auth = hashlib.sha256(auth_token.encode()).hexdigest()
        token = TokensCol.find_one({"authToken": auth})
        if token and token["expire"] > datetime.now():
            user_name_here = token["username"]
    messageCol = db["Messages"]
    message = messageCol.find_one({"id": id})
    if message:
        updateLikes = int(message["likes"]) + 1
        likers = message["likers"]
        if user_name_here not in likers:
            likers.append(user_name_here)
            messageCol.update_one({"id": id}, {"$set": {"likes": updateLikes, "likers": likers}})
    else:
        return "This page is not found.", 404
    return redirect(url_for("chatroom"))

@app.route("/unlike/<int:id>")
def unlike(id):
    user_name_here = ""
    auth_token = request.cookies.get("authToken")
    TokensCol = db["Tokens"]
    if auth_token:
        auth = hashlib.sha256(auth_token.encode()).hexdigest()
        token = TokensCol.find_one({"authToken": auth})
        if token and token["expire"] > datetime.now():
            user_name_here = token["username"]
    messageCol = db["Messages"]
    message = messageCol.find_one({"id": id})
    if message:
        updateLikes = int(message["likes"]) - 1
        likers = message["likers"]
        if user_name_here in likers:
            likers.remove(user_name_here)
            messageCol.update_one({"id": id}, {"$set": {"likes": updateLikes, "likers": likers}})
    else:
        return "This page is not found.", 404
    return redirect(url_for("chatroom"))
            
@app.route("/image-upload", methods = ["POST"])
def imageUpload():
    auth_token = request.cookies.get("authToken")
    TokensCol = db["Tokens"]
    if auth_token:
        auth = hashlib.sha256(auth_token.encode()).hexdigest()
        token = TokensCol.find_one({"authToken": auth})
        if token and token["expire"] > datetime.now():
            user_name_here = token["username"]
            if request.files and user_name_here != "Guest":
                upload = request.files["upload"]
                mimetype = upload.content_type
                if mimetype == "image/jpeg" or mimetype == "image/png":
                    if mimetype == "image/jpeg":
                        new_name = "./static/" + user_name_here + ".jpg"
                    else:
                        new_name = "./static/" + user_name_here + ".png"
                    upload.save(new_name)
                    PfpCol = db["pfp"]
                    PfpCol.insert_one({"username": user_name_here, "path": new_name})
                    # print(upload.name.replace("/",""))
    return redirect(url_for("chatroom"))


@app.after_request
def nosniff(response):
    paths200OK = ["/static/clue.JPG", "/static/style.css"]
    if(request.path in paths200OK):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.status_code = 200
        return response
    print(request.path)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.errorhandler(404)
def page_not_found(error):
    return "This page is not found.", 404

if __name__ == "__main__":
    secret_key = os.urandom(24)
    secret_key = str(secret_key)
    app.secret_key = secret_key
    app.run(debug=True,host='0.0.0.0',port=8080)