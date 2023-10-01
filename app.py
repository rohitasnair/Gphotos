import firebase
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os 
from add_image import other_routes
from configv import *
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = Flask(__name__)       #Initialze flask constructor
app.register_blueprint(other_routes)


#Add your own details


#initialize firebase
firebase_app = firebase.initialize_app(config)
auth = firebase_app.auth()
db = firebase_app.database()

#Initialze person as dictionary
#person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}

#Login
@app.route("/")
def login():
    return render_template("login.html")

#Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route('/google_auth')
def google_auth():
    creds = load_credentials()  # Load existing credentials
    if creds and creds.valid:
        print("Google authentication successful!")
        return 'Google authentication successful!'

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        save_credentials(creds)
        print("Google authentication successful after refresh!")
        return 'Google authentication successful after refresh!'

    flow = InstalledAppFlow.from_client_secrets_file(
        '_secrets_/client_secret.json', scopes, redirect_uri=url_for('google_auth_callback', _external=True)
    )
    auth_url, _ = flow.authorization_url()
    return redirect(auth_url)

@app.route('/google_auth_callback')
def google_auth_callback():
    creds = load_credentials()  # Load existing credentials
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            '_secrets_/client_secret.json', scopes, redirect_uri=url_for('google_auth_callback', _external=True)
        )
        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials

        # Save the credentials for later use
        save_credentials(creds)

    # Redirect to a success page or perform any other actions
    return 'Google authentication successful!'

def load_credentials():
    if os.path.exists('_secrets_/token.json'):
        creds = Credentials.from_authorized_user_file('_secrets_/token.json', scopes)
        if creds.valid:
            return creds

    return None

def save_credentials(creds):
    # Save the credentials for the next run
    with open('_secrets_/token.json', 'w') as token:
        token.write(creds.to_json())

#Welcome page
@app.route("/invoke")
def invoke():
    return render_template("invoke.html")



#If someone clicks on login, they are redirected to /result
@app.route("/result", methods = ["POST", "GET"])
def result():
    if request.method == "POST":        #Only if data has been posted
        result = request.form           #Get the data
        email = result["email"]
        password = result["pass"]
        try:
            #Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)
            print(user)
            #Insert the user data in the global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            #Get the name of the user
            data = db.child("users").get()
            person["name"] = data.val()[person["uid"]]["name"]
            #Redirect to welcome page
            return redirect(url_for('other_routes.welcome'))
        except:
            print("ERROR")
            #If there is any error, redirect back to login
            return redirect(url_for('login'))
    else:
        print("LOGGED IN WELCOME")
        if person["is_logged_in"] == True:
            return redirect(url_for('other_routes.welcome'))
        else:
            print("LOGIN")
            return redirect(url_for('login'))

#If someone clicks on register, they are redirected to /register
@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":        #Only listen to POST
        result = request.form           #Get the data submitted
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        try:
            #Try creating the user account using the provided data
            auth.create_user_with_email_and_password(email, password)
            #Login the user
            user = auth.sign_in_with_email_and_password(email, password)
            #Add data to global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["name"] = name
            #Append data to the firebase realtime database
            data = {"name": name, "email": email}
            db.child("users").child(person["uid"]).set(data)
            #Go to welcome page
            return redirect(url_for('welcome'))
        except:
            #If there is any error, redirect to register
            return redirect(url_for('register'))

    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('register'))

if __name__ == "__main__":
    app.run(debug=True)
