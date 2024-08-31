import calendar
from pymongo import MongoClient
from flask import Flask, request, jsonify, redirect, Response, url_for, render_template , flash , session , request
#from flask_login import login_user, LoginManager, login_required, logout_user, current_user, UserMixin
import pymongo
from bson import ObjectId
import json,os,sys
from datetime import *
from datetime import date
import secrets
from datetime import *
from datetime import date,datetime,time
import requests



# Connect to our local MongoDB
mongodb_hostname = os.environ.get("MONGO_HOSTNAME","localhost")
client = MongoClient("mongodb://localhost:27017/")

# Choose InfoSys database
Gym = client['Gym']
Users = Gym['Users']
Request = Gym['Request']
Trainers = Gym['Trainers']
Programs = Gym['Programs']
Classes = Gym['Classes']
Offer = Gym['Offer']
Announcement = Gym['Announcement']
Appointment = Gym['Appointment']
Instructions = Gym['Instructions']
Schedule = Gym['Schedule']
OlderApp = Gym['OlderAppointments']
Cancellations=Gym['Cancellations']

COUNTRIES_API_URL = "https://countriesnow.space/api/v0.1/countries"
# Initiate Flask App
app = Flask(__name__)
app.secret_key = str(secrets.token_hex(16))  # Set a secret key for session security

#---------------- MAIN PAGE/ROOT ----------------#

# Root page. 
@app.route('/', methods=['POST', 'GET'])
def index():
    try:
        # return the url for the mainpage
        return redirect(url_for('mainpage'))

    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('User creation was not successfull!', 'warning')      

# Route to get the main page of the gym site.
@app.route('/mainpage', methods=['POST', 'GET'])
def mainpage():
    try:
        # return the html file for the General Main Page of the site (no login needed).
        return render_template('General-Main-Page.html')

    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('User creation was not successfull!', 'warning')

#---------------- LOGIN/LOGOUT ----------------#

# Login for the User
@app.route('/userlogin', methods=['POST', 'GET'])
def userlogin():
    try:
        # If user already logged in 
        if 'username' in session:
            # redirect him to the User Main Page
            return render_template('User/Main/User-Main-Page.html')
        
        # If user is not logged in and the request is a POST
        elif request.method == 'POST':

            # Store Login Data
            username_input = request.form['username']
            password_input = request.form['password']

            #Find the user with the credentials he entered
            user = Users.find_one({'username': username_input, 'password': password_input, 'role': 'user'})

            # Check if the username and password match a user in the database
            if user:
                # Redirect the user to the User Main Page
                session['username'] = username_input
                return render_template('User/Main/User-Main-Page.html')
            
            else:
                # Stay at Login Page and pop an error message
                flash('Λάθος username ή password. Ελέγξτε ξανά τα στοιχεία σας και προσπαθήστε πάλι.', 'wrongloginuser')
                return render_template('User/Login/User-Login-Page.html')
            
        return render_template('User/Login/User-Login-Page.html')
    
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('User creation was not successfull!', 'warning')      

# Login for the Admin
@app.route('/adminlogin', methods=['POST', 'GET'])
def adminlogin():

    # If admin already logged in go to main page. 
    if 'username' in session:
        return render_template('Admin/Main/Main-Page.html')
    
    # If admin is not logged in and the request is a POST
    elif request.method == 'POST':

        # Store Login Data
        username_input = request.form['username']
        password_input = request.form['password']

        # Find the user in the database with the credentials he provided and check if the role is admin
        user = Users.find_one({'username': username_input, 'password': password_input, 'role': 'admin'})

        # If the admin exists 
        if user:
            # Redirect to the Admin Main Page
            session['username'] = username_input
            return render_template('Admin/Main/Main-Page.html')
        
        else:
            # Stay at Login Page and pop an error message
            flash('Λάθος Username ή Password! Προσπαθήστε ξανά', 'wronglogin')
            return render_template('Admin/Login/Login-Page.html')    
    return render_template('Admin/Login/Login-Page.html')

# Logout 
@app.route('/logout', methods=['GET'])
def logout():

    if request.method == 'GET':

        #if admin already logged in 
        if 'username' in session:

            #Remove the username from the session and return to General Main Page
            session.pop('username', None)  
            return render_template('General-Main-Page.html')
    else:
        flash('Invalid request method for logout', 'danger')
        return render_template('General-Main-Page.html')

@app.route('/userlogout', methods=['GET'])
def userlogout():

    #if user already logged in 
    if request.method == 'GET':
        if 'username' in session:
            #Remove the username from the session and return to General Main Page
            session.pop('username', None)  
            return redirect(url_for('mainpage'))
    else:
        flash('Invalid request method for logout', 'danger')
        return redirect(url_for('mainpage'))

#---------------- ADMIN ----------------#

#------- Requests-Page -------#

# Get the Requests List
@app.route('/getRequests', methods=['POST','GET'])
def getRequests():

    try:
        # If admin is already logged in
        if 'username' in session:
            # If there are no active Requests in collection return empty table with a message
            if Request.count_documents({}) == 0:

                flash('Δεν υπάρχουν ενεργά Requests αυτή τη στιγμή!', 'emptydb')
                return render_template('Admin/Requests/Requests-Page.html', data=[])
            
            # Find Requests in collection
            findRequest = Request.find({})

            # Store Requests in list
            requestList = [{'name': req['name'], 'surname': req['surname'], 'email': req['email'], 'address': req['address']}
                for req in findRequest]
            
            # Return the html with a table containing the Requests
            return render_template('Admin/Requests/Requests-Page.html', data=requestList)
        # If admin is not logged in
        else:
            # Redirect to login page
            return redirect(url_for('adminlogin'))

    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Trainer list receival was not successfull!')

# Decline request with specific email sent by the html
@app.route('/requests/decline/<email>', methods=['POST', 'GET'])
def decline(email):

    try:
        # If admin is already logged in
        if 'username' in session:
            if request.method == 'POST' or request.method == 'GET':

                # Delete the Request with the specific email
                Request.delete_one({'email':email})
                # Return to the Request list and pop message
                flash('Επιτυχής απόρριψη του Αιτήματος εγγραφής του χρήστη!', 'declined')
                return redirect(url_for('getRequests'))
    
        # If admin is not logged in
        else:
            # Redirect to login page
            return redirect(url_for('adminlogin'))
        
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Request examination was not successfull', 'warning')
    
    return render_template('Admin/Requests/Requests-Page.html')

# Return user info with specific email sent by the html
@app.route('/oneUser/<email>', methods=['GET','POST'])
def oneUser(email):

    try:
        # If admin is already logged in
        if 'username' in session:
            if request.method == 'POST' or request.method == 'GET':
                # Check if a user exists with this specific email    
                if Request.count_documents({'email':email}) == 0:
                    # Return to the Request list and pop message
                    flash('Δεν υπάρχει χρήστης με το συγκεκριμένο email!', 'declined')
                    return redirect(url_for('getRequests'))
            
                # Find user information with the specific email
                foundUser = Request.find({'email':email})

                usList = []

                for user in foundUser:

                    user['_id'] = str(user['_id'])
                    usList.append(user)

                # Return the html with the user information
                return render_template('Admin/Requests/Request-Accept.html', data=usList, req={'email': email})
        # If admin is not logged in
        else:
            # Redirect to login page
            return redirect(url_for('adminlogin'))
    
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Request examination was not successfull', 'warning')
    
    return render_template('Admin/Requests/Requests-Page.html')

# Accept request with specific email sent by the html
@app.route('/requests/accept/<email>', methods=['POST', 'GET'])
def accept(email):

    try:
        # If admin is already logged in
        if 'username' in session:
            if request.method == 'POST' or request.method == 'GET':

                # Store data from the html form
                role = str(request.form['role'])

                # Check how many request and users are in the base
                beforeUpUsers = Users.count_documents({})
                beforeUpRequests = Request.count_documents({})

                # Add User
                getRequestInfo = Request.find_one({'email':email})

                # Set USer id
                user_id = -1
                
                # If it is the first user of the database give ID 1 
                if beforeUpUsers == 0:

                    user_id = 1

                # Else get the last existing id and add 1 
                else:

                    userIdSetup = Users.find({})

                    for user in userIdSetup:

                        if int(user['user_id']) > user_id :

                            user_id = int(user['user_id'])
                    
                    user_id += 1
                
                # Insert User
                Users.insert_one(
                    {
                        'user_id' : str(user_id),
                        'name' : getRequestInfo['name'],
                        'surname': getRequestInfo['surname'],
                        'country' : getRequestInfo['country'],
                        'town' : getRequestInfo['town'],
                        'username' : getRequestInfo['username'],
                        'password' : getRequestInfo['password'],
                        'email' : getRequestInfo['email'],
                        'address' : getRequestInfo['address'],
                        'role' : role
                    }
                )

                # Delete Request
                Request.delete_one({'email':email})

                # Check if we deleted request and appended user
                if Request.count_documents({}) == beforeUpRequests - 1 and Users.count_documents({}) == beforeUpUsers + 1:
                    # Return to the Request list html with message
                    flash('Επιτυχής αποδοχή του αιτήματος εγγραφής του χρήστη!', "accepted")
                    return redirect(url_for('getRequests'))
        # If admin is not logged in
        else:
            # Redirect to login page
            return redirect(url_for('adminlogin'))
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Request examination was not successfull', 'warning')
    
    return redirect(url_for('getRequests'))

#------- Users-Page -------#

# Get the Users List (flag is for the error message that will appear after the update)
@app.route('/userlist/<flag>', methods=['POST','GET'])
def getUserList(flag):

    try:
        # If admin is already logged in
        if 'username' in session:

            # If there are no active Users in collection return empty table with a message 
            if Users.count_documents({}) == 0:

                flash('Δεν υπάρχουν εγγεγραμμένοι χρήστες αυτή τη στιγμή!', 'emptydb')
                return render_template('Admin/Users/Users-List.html', data=[])
                
            # Find users
            findUser = Users.find({})

            # Store users in list
            user_list = [{'user_id':req['user_id'],'name': req['name'], 'surname': req['surname'],'country':req['country'],'town':req['town'],'address':req['address'],'email': req['email'], 'username': req['username'],'role':req['role']}
                for req in findUser] #req for req in findRequest
            # Return html file with table containing all users
            return render_template('Admin/Users/Users-List.html', data=user_list, flag=flag)
        
        # If admin is not logged in
        else:
            # Redirect to login page
            return redirect(url_for('adminlogin'))

    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Trainer list receival was not successfull!')

# Delete User with specific user_id sent by the html
@app.route('/deleteUser/<user_id>', methods=['DELETE', 'GET'])
def delete_user(user_id):

    try:
        # If admin is already logged in
        if 'username' in session:
            if request.method == 'DELETE' or request.method == 'GET': 

                # Check if user exists
                if Users.count_documents({'user_id':user_id}) == 0:
                    # Return to User List html with message
                    flash('Ο χρήστης με ID ' + user_id + ' δεν υπάρχει!', 'nonexistantus')
                    return redirect(url_for('getUserList', flag=0))
        
                # Delete User
                userCount = Users.count_documents({})
                Users.delete_one({'user_id':user_id})

                # Check if user deleted            
                if Users.count_documents({}) < userCount :
                    # Return to User list html with message
                    flash('Επιτυχής διαγραφή του χρήστη', 'deleteduser')
                    return redirect(url_for('getUserList', flag=0))
                # If user not deleted
                else:
                    # Return to User list html with message    
                    flash('Μη επιτυχής διαγραφή του χρήστη', 'deleteduser')
                    return redirect(url_for('getUserList', flag=0))
        # If admin is not logged in
        else:
            # Redirect to login page
            return redirect(url_for('adminlogin'))
        
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Deletetion was not successfull!', 'warning')
    return flash('Deletetion was not successfull!', 'warning')

# Return user info with specific user_id sent by the html
@app.route('/edit/<user_id>', methods=['GET','POST'])
def edit(user_id):

    try:
        # If admin is already logged in
        if 'username' in session:
            if request.method == 'POST' or request.method == 'GET':
                # Check if a user exists with this specific user_id    
                if Users.count_documents({'user_id':user_id}) == 0:
                    # Return to the Request list and pop message
                    flash('Δεν υπάρχει χρήστης με το συγκεκριμένο User ID!', 'declined')
                    return redirect(url_for('getUserList', flag=0))
            
                # Find user information
                foundUser = Users.find({'user_id':user_id})

                usList = []

                for user in foundUser:

                    user['_id'] = str(user['_id'])
                    usList.append(user)

                # Return the html with the user information
                return render_template('Admin/Users/Users-Update.html', data=usList, req={'user_id': user_id})
        # If admin is not logged in
        else:
            # Redirect to login page
            return redirect(url_for('adminlogin'))
    
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Request examination was not successfull', 'warning')
    
    return render_template('Admin/Users/Users-List.html')

# Update user list with specific user_id sent by the html
@app.route('/updateuser/<user_id>', methods=['POST', 'GET'])
def update_user(user_id):
    try:
        flag=0
        # If admin is already logged in
        if 'username' in session:
            if request.method == 'POST' or request.method == 'GET':
                # Get the user info from the form of the html
                rcv_name = str(request.form.get('name'))
                rcv_surname = str(request.form.get('surname'))
                rcv_country = str(request.form.get('country'))
                rcv_town = str(request.form.get('town'))
                rcv_username = str(request.form.get('username'))
                rcv_password = str(request.form.get('password'))
                rcv_email = str(request.form.get('email'))
                rcv_address = str(request.form.get('address'))
                rcv_role = str(request.form.get('role'))
                
                # Search for the user with specific id
                user = Users.find_one({'user_id': user_id}) 
                
                # if user is found get his stored email and username
                if user: 
                    email = user.get('email')
                    username = user.get('username')
                    
                # Check if new email exists
                if (rcv_email != email and Users.count_documents({'email': rcv_email}) != 0) and (rcv_username != username and Users.count_documents({'username': rcv_username}) != 0):
                    # Return flag in order for correct error message to appear
                    flag=1
                # Check if new username exists
                elif rcv_username != username and Users.count_documents({'username': rcv_username}) != 0:
                    # Return flag in order for correct error message to appear
                    flag=2
                elif rcv_email != email and Users.count_documents({'email': rcv_email}) != 0:
                    # Return flag in order for correct error message to appear
                    flag=3
                else:
                    # No errors exist so flag = 0 
                    flag=0            
                    # Update User      
                    Users.update_one({'user_id':user_id},
                                {'$set':
                                    {
                                        'user_id' : user_id,
                                        'name' : rcv_name,
                                        'surname' : rcv_surname,
                                        'country' : rcv_country,
                                        'town' : rcv_town,
                                        'username' : rcv_username,
                                        'password' : rcv_password,
                                        'email' : rcv_email,
                                        'address' : rcv_address,
                                        'role' : rcv_role
                                    }
                                }
                            )
                    # Return to user list html with message
                    flash('Επιτυχής ενημέρωση του χρήστη', 'edituser')
            return redirect(url_for('getUserList', flag=flag))                
        # If admin is not logged in
        else:
            # Redirect to login page
            return redirect(url_for('adminlogin'))
        
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Update was not successfull!', 'warning')

# Get the countries from the online api
@app.route('/api/countries', methods=['POST', 'GET'])
def get_countries():
    try:
        # Get the countries from the api and return them as a list
        response = requests.get(COUNTRIES_API_URL)
        data = response.json()
        countries = [country['country'] for country in data['data']]
        return countries
    except Exception as e:
        return jsonify({"error": str(e)})

# Get the cities from the online api
@app.route('/api/cities/<country>', methods=['POST', 'GET'])
def get_cities(country):
    try:
        response = requests.get(COUNTRIES_API_URL)
        data = response.json()
        # Convert country name characters to lowercsase
        target_country = country.lower()
        
        # Search for wanted country
        for entry in data['data']:
            if entry.get('country', '').lower() == target_country:
                cities = entry.get('cities', [])
                return cities

        # If country is not found return empty list
        return []

    except Exception as e:
        return jsonify({"error": str(e)})

# Get the cities from the online api
@app.route('/dropcancels', methods=['POST', 'GET'])
def dropcancel(): 
    try:
        # If admin is already logged in
        if 'username' in session:
            Cancellations.drop()
            flash('Επιτυχής ανανέωση των ακυρώσεων.', 'refresh')
            return redirect(url_for('getUserList', flag=0))

        # If admin is not logged in
        else:
            # Redirect to login page
            return redirect(url_for('adminlogin'))

    except Exception as e:
        return jsonify({"error": str(e)})

#------- Announcements -------#

# Receive announcement list
@app.route('/announcementlist', methods=['POST','GET'])
def getAnnouncements():

    try:
        # If admin is already logged in
        if 'username' in session:
            # Check if announcement exists
            if Announcement.count_documents({}) == 0:
                # If there are no announcements  in collection return empty table with a message 
                flash('Δεν υπάρχουν ανακοινώσεις αυτή τη στιγμή!', 'emptydb')
                return render_template('Admin/Announcements/Announcements-List.html', data=[])
            
            # Find announcements
            findAnnouncement = Announcement.find({})
            # Store announcemenets in a list
            announcement_list = [{'ann_id':req['ann_id'],'title': req['title'], 'text': req['text']}
                for req in findAnnouncement]
            
            # Return to the Announcement List html with the stored data
            return render_template('Admin/Announcements/Announcements-List.html', data=announcement_list)
        # If admin is not logged in
        else:
            # Redirect to login page
            return redirect(url_for('adminlogin'))
        
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Announcement list receival was not successfull!', 'warning')

# Delete Announcement with specific id sent by the html
@app.route('/deleteAnnouncement/<ann_id>', methods=['DELETE', 'GET'])
def delete_announcement(ann_id):

    try:
        # If admin is already logged in
        if 'username' in session:
            if request.method == 'DELETE' or request.method == 'GET':

                # Check if announcement exists
                if Announcement.count_documents({'ann_id':ann_id}) == 0:
                    # Return to Announcement List html with message
                    flash('Η Ανακοίνωση με ID ' + ann_id + ' δεν υπάρχει!', 'nonexistantann')
                    return redirect(url_for('getAnnouncements'))
        
                # Delete announcement
                classAnnouncement = Announcement.count_documents({})
                Announcement.delete_one({'ann_id':ann_id})

                # Check if announcement deleted
                if Announcement.count_documents({}) < classAnnouncement:
                    # Return to Announcement List html with message
                    flash('Επιτυχής διαγραφή ανακοίνωσης!', 'deleteann')
                    return redirect(url_for('getAnnouncements'))
                else:

                    return flash('Announcement deletetion was not successfull!', 'warning')
        # If admin is not logged in
        else:
            # Redirect to login page
            return redirect(url_for('adminlogin'))
        
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Deletetion was not successfull!', 'warning')

# Return announcement info with specific id sent by the html
@app.route('/editAnnouncement/<ann_id>', methods=['GET','POST'])
def editAnnouncement(ann_id):

    try:
        # If admin is already logged in
        if 'username' in session:
            if request.method == 'POST' or request.method == 'GET':
                    
                if Announcement.count_documents({'ann_id':ann_id}) == 0:
                    # Return to Announcement List html with message
                    flash('Η Ανακοίνωση με ID ' + ann_id + ' δεν υπάρχει!', 'nonexistantann')
                    return redirect(url_for('getAnnouncements'))
            
                # Find Announcement information
                foundAnnouncement = Announcement.find({'ann_id':ann_id})

                announcement_list = []

                for ann in foundAnnouncement:

                    ann['_id'] = str(ann['_id'])
                    announcement_list.append(ann)

                # Return the html with the announcement information    
                return render_template('Admin/Announcements/Announcements-Update.html', data=announcement_list, req={'ann_id': ann_id})
        # If admin is not logged in
        else:
            # Redirect to login page
            return redirect(url_for('adminlogin'))
    
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Request examination was not successfull', 'warning')
    
    return render_template('Admin/Users/Users-List.html')

# Update announcement list with specific id sent by the html
@app.route('/updateAnnouncement/<ann_id>', methods=['POST'])
def update_announcement(ann_id):
    try:
        # If admin is already logged in
        if 'username' in session:
            if request.method == 'POST':

                # Get the announcement info from the form of the html
                rcv_title = str(request.form['title'])
                rcv_text = str(request.form['text'])

                # Search for the announcement with specific id
                announcement = Announcement.find_one({'ann_id': ann_id})

                # if announcement is found
                if announcement: 
                    # Update announcement
                    Announcement.update_one({'ann_id':ann_id},
                                            {'$set':
                                                {
                                                    'ann_id' : ann_id,
                                                    'title' : rcv_title,
                                                    'text' : rcv_text
                                                }
                                            }
                                        )
                    # Return to announcement list html with message
                    flash('Επιτυχής ενημέρωση της ανακοίνωσης', 'editann')
                return redirect(url_for('getAnnouncements'))
        # If admin is not logged in
        else:
            # Redirect to login page
            return redirect(url_for('adminlogin'))            
            
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
                   
    except Exception:

        return flash('Update was not successfull!', 'warning')

# Form to create new announcement
@app.route('/newannouncement', methods=['POST', 'GET'])
def new_announcement():
    try:
        # If admin is already logged in
        if 'username' in session:

            return render_template('Admin/Announcements/Announcements-New.html')
        # If admin is not logged in
        else:
            # Redirect to login page
            return redirect(url_for('adminlogin'))  
         
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
    
    except Exception:

        return flash('Announcement creation was not successfull!', 'warning')

# Create announcement 
@app.route('/createannouncement', methods=['POST', 'GET'])
def create_announcement():

    try:
        # If admin is already logged in
        if 'username' in session:

            if request.method == 'POST' or request.method == 'GET':

                # Check how many announcements are in the base
                beforeUpAnnouncements = Announcement.count_documents({})

                # Set announcement id
                ann_id = -1
                
                # If it is the first announcement of the database give ID 1 
                if beforeUpAnnouncements == 0:

                    ann_id = 1

                # Else get the last existing id and add 1 
                else:

                    announcementIdSetup = Announcement.find({})

                    for announcmenet in announcementIdSetup:

                        if int(announcmenet['ann_id']) > ann_id :

                            ann_id = int(announcmenet['ann_id'])
                    
                    ann_id += 1
                # Insert Announcement into database
                Announcement.insert_one(
                    {
                        'ann_id' : str(ann_id),
                        'title' : request.form['title'],
                        'text': request.form['text']
                    }
                )
                # Check if announcements is entered
                if Announcement.count_documents({}) == beforeUpAnnouncements + 1:
                    # Return to the Request list html with message
                    flash('Επιτυχής δημιουργία ανακοίνωσης', 'addedann')
                    return redirect(url_for('getAnnouncements'))
        # If admin is not logged in
        else:
            # Redirect to login page
            return redirect(url_for('adminlogin')) 
            
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
    
    except Exception:

        return flash('Announcement creation was not successfull!', 'warning')  
    
    return render_template('Admin/Announcements/Announcements-New.html')

#------- Offers -------#

# Receive offer list
@app.route('/offerlist', methods=['POST','GET'])
def getOffers():

    try:
        # If admin is already logged in
        if 'username' in session:

            # Check if offer exists
            if Offer.count_documents({}) == 0:
                # If there are no announcements  in collection return empty table with a message 
                flash('Δεν υπάρχουν προσφορές αυτή τη στιγμή!', 'emptydb')
                return render_template('Admin/Offers/Offers-List.html', data=[])
            
            # Find offers
            findOffer = Offer.find({})
            # Store offers in a list
            offer_list = [{'offer_id':req['offer_id'],'title': req['title'], 'text': req['text']}
                for req in findOffer]
            
            # Return to the Offers List html with the stored data
            return render_template('Admin/Offers/Offers-List.html', data=offer_list)
        # If admin is not logged in
        else:
            # Redirect to login page
            return redirect(url_for('adminlogin'))

    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Announcement list receival was not successfull!', 'warning')

# Delete offer with specific id sent by the html
@app.route('/deleteOffer/<offer_id>', methods=['DELETE', 'GET'])
def delete_offer(offer_id):

    try:
        # If admin is already logged in
        if 'username' in session:

            if request.method == 'DELETE' or request.method == 'GET':

                # Check if offer exists
                if Offer.count_documents({'offer_id':offer_id}) == 0:
                    # Return to Offers List html with message
                    flash('Η Προσφορά με ID ' + offer_id + ' δεν υπάρχει!', 'nonexistantoff')
                    return redirect(url_for('getOffers'))
        
                # Delete offer
                classOffer = Offer.count_documents({})
                Offer.delete_one({'offer_id':offer_id})

                # Check if offer deleted
                if Offer.count_documents({}) < classOffer:
                    # Return to Offer List html with message
                    flash('Επιτυχής διαγραφή προσφοράς!', 'deleteoffer')
                    return redirect(url_for('getOffers'))
                else:

                    return flash('Offer deletetion was not successfull!', 'warning')
        # If admin is not logged in
        else:
            # Redirect to login page
            return redirect(url_for('adminlogin'))
        
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Deletetion was not successfull!', 'warning')

# Return offer info with specific id sent by the html
@app.route('/editOffer/<offer_id>', methods=['GET','POST'])
def editOffer(offer_id):

    try:
        # If admin is already logged in
        if 'username' in session:

            if request.method == 'POST' or request.method == 'GET':
                # Check if a offer exists with this specific offer_id    
                if Offer.count_documents({'offer_id':offer_id}) == 0:
                    # Return to Offers List html with message
                    flash('Η Προσφορά με ID ' + offer_id + ' δεν υπάρχει!', 'nonexistantoff')
                    return redirect(url_for('getOffers'))
            
                # Find offer information
                findOffer = Offer.find({'offer_id':offer_id})

                offer_list = []

                for off in findOffer:

                    off['_id'] = str(off['_id'])
                    offer_list.append(off)

                # Return the html with the offer information    
                return render_template('Admin/Offers/Offers-Update.html', data=offer_list, req={'offer_id': offer_id})
        # If admin is not logged in
        else:
            # Redirect to login page
            return redirect(url_for('adminlogin'))
    
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Request examination was not successfull', 'warning')
    
    return render_template('Admin/Offers/Offers-List.html')

# Update specific offer with specific id sent by the html
@app.route('/updateOffer/<offer_id>', methods=['POST'])
def update_offer(offer_id):
    try:
        # If admin is already logged in
        if 'username' in session:

            if request.method == 'POST':

                # Get the offer info from the form of the html
                rcv_title = str(request.form['title'])
                rcv_text = str(request.form['text'])

                # Search for the offer with specific id
                offer = Offer.find_one({'offer_id': offer_id})

                # If offer is found
                if offer:
                    # Update offer
                    Offer.update_one({'offer_id':offer_id},
                                            {'$set':
                                                {
                                                    'offer_id' : offer_id,
                                                    'title' : rcv_title,
                                                    'text' : rcv_text
                                                }
                                            }
                                        )
                    # Return to offer list html with message
                    flash('Επιτυχής ενημέρωση της προσφοράς', 'editoffer')            
                return redirect(url_for('getOffers'))
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))
            
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
                   
    except Exception:

        return flash('Update was not successfull!', 'warning')
    
# Form to create new offer
@app.route('/newoffer', methods=['POST', 'GET'])
def new_offer():
    try:
        # If admin is already logged in
        if 'username' in session:

            return render_template('Admin/Offers/Offers-New.html')
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))
         
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
    
    except Exception:

        return flash('Offer creation was not successfull!', 'warning')

# Create an offer 
@app.route('/createoffer', methods=['POST', 'GET'])
def create_offer():

    try:
        # If admin is already logged in
        if 'username' in session:

            if request.method == 'POST' or request.method == 'GET':

                # Check how many offers are in the base
                beforeUpOffers = Offer.count_documents({})

                # Set offer id
                offer_id = -1

                # If it is the first offer of the database give ID 1 
                if beforeUpOffers == 0:

                    offer_id = 1

                # Else get the last existing id and add 1 
                else:

                    offerIdSetup = Offer.find({})

                    for off in offerIdSetup:

                        if int(off['offer_id']) > offer_id :

                            offer_id = int(off['offer_id'])
                    
                    offer_id += 1

                # Insert Offer into database
                Offer.insert_one(
                    {
                        'offer_id' : str(offer_id),
                        'title' : request.form['title'],
                        'text': request.form['text']
                    }
                )
                # Check if offer is entered
                if Offer.count_documents({}) == beforeUpOffers + 1:
                    # Return to the Offers list html with message
                    flash('Επιτυχής δημιουργία προσφοράς!', 'addedoffer')
                    return redirect(url_for('getOffers'))
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))
            
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
    
    except Exception:

        return flash('Announcement creation was not successfull!', 'warning')  
    
    return render_template('Admin/Offers/Offers-New.html')

#------- Trainers -------#

# Receive trainers list
@app.route('/trainerlist', methods=['POST','GET'])
def getTrainers():

    try:
        # If admin is already logged in
        if 'username' in session:

            #Check if trainers exists
            if Trainers.count_documents({}) == 0:
                # If there are no announcements  in collection return empty table with a message 
                flash('Δεν υπάρχουν γυμναστές αυτή τη στιγμή!', 'emptydb')
                return render_template('Admin/Trainers/Trainers-List.html', data=[])
            
            # Find trainers
            findTrainer = Trainers.find({})

            # Store trainers in a list
            trainer_list = [{'trainer_id':req['trainer_id'],'name': req['name'], 'surname': req['surname'],'programs' :req['programs'],'bio': req['bio'], 'email': req['email'], 'phone' : req['phone']}
                for req in findTrainer]
            
            # Return to the Trainers List html with the stored data
            return render_template('Admin/Trainers/Trainers-List.html', data=trainer_list)
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))

    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Announcement list receival was not successfull!', 'warning')

# Delete trainer with specific id sent by the html
@app.route('/deleteTrainer/<trainer_id>', methods=['DELETE', 'GET'])
def delete_trainer(trainer_id):

    try:
        # If admin is already logged in
        if 'username' in session:
            
            if request.method == 'DELETE' or request.method == 'GET':

                #Check if trainer exists
                if Trainers.count_documents({'trainer_id':trainer_id}) == 0:
                    # Return to Trainers List html with message
                    flash('Ο Γυμναστής με ID ' + trainer_id + ' δεν υπάρχει!', 'nonexistanttrn')
                    return redirect(url_for('getTrainers'))
        
                # Delete trainer
                classTrainer = Trainers.count_documents({})
                Trainers.delete_one({'trainer_id':trainer_id})

                # Check if trainer deleted
                if Trainers.count_documents({}) < classTrainer:
                    # Return to Trainers List html with message
                    flash('Επιτυχής διαγραφή γυμναστή!', 'deletetrainer')
                    return redirect(url_for('getTrainers'))
                else:

                    return flash('Trainer deletetion was not successfull!', 'warning')
                
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))
        
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Deletetion was not successfull!', 'warning')

# Return trainer info with specific id sent by the html
@app.route('/editTrainer/<trainer_id>', methods=['GET','POST'])
def editTrainer(trainer_id):

    try:
        # If admin is already logged in
        if 'username' in session:

            if request.method == 'POST' or request.method == 'GET':
                # Check if a trainer exists with this specific offer_id    
                if Trainers.count_documents({'trainer_id':trainer_id}) == 0:
                    # Return to Trainers List html with message
                    flash('Ο Γυμναστής με ID ' + trainer_id + ' δεν υπάρχει!', 'nonexistanttrn')
                    return redirect(url_for('getTrainers'))
            
                # Find trainer information
                findTrainer = Trainers.find({'trainer_id':trainer_id})

                trainer_list = []

                for tre in findTrainer:

                    tre['_id'] = str(tre['_id'])
                    trainer_list.append(tre)

                # Return the html with the trainers information    
                return render_template('Admin/Trainers/Trainers-Update.html', data=trainer_list, req={'trainer_id': trainer_id})
            
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))
    
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Request examination was not successfull', 'warning')
    
    return render_template('Admin/Trainers/Trainers-List.html')

# Update trainer list with specific id sent by the html
@app.route('/updateTrainer/<trainer_id>', methods=['POST'])
def update_trainer(trainer_id):
    try:
        # If admin is already logged in
        if 'username' in session:

            if request.method == 'POST':

                # Get the trainer info from the form of the html
                rcv_name = str(request.form['name'])
                rcv_surname = str(request.form['surname'])
                rcv_programs = str(request.form['programs'])
                rcv_bio = str(request.form['bio'])
                rcv_email = str(request.form['email'])
                rcv_phone = str(request.form['phone'])

                # Search for the trainer with specific id
                trainer = Trainers.find_one({'trainer_id': trainer_id})

                # If trainer is found
                if trainer:
                    # Update trainer
                    Trainers.update_one({'trainer_id': trainer_id},
                                            {'$set':
                                                {
                                                    'trainer_id' : trainer_id,
                                                    'name' : rcv_name,
                                                    'surname' : rcv_surname,
                                                    'programs' : rcv_programs,
                                                    'bio' : rcv_bio,
                                                    'email' : rcv_email,
                                                    'phone' : rcv_phone
                                                }
                                            }
                                        )
                    # Return to trainer list html with message
                    flash('Επιτυχής ενημέρωση γυμναστή!', 'edittrainer')    
                return redirect(url_for('getTrainers'))
            
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))
            
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
                   
    except Exception:

        return flash('Update was not successfull!', 'warning')
    
# Go to new trainer form
@app.route('/newtrainer', methods=['POST', 'GET'])
def new_trainer():
    try:
        # If admin is already logged in
        if 'username' in session:
        
            return render_template('Admin/Trainers/Trainers-New.html')
        
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))
        
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
    
    except Exception:

        return flash('Announcement creation was not successfull!', 'warning')

# Create a trainer 
@app.route('/createtrainer', methods=['POST', 'GET'])
def create_trainer():

    try:
        # If admin is already logged in
        if 'username' in session:
            
            if request.method == 'POST' or request.method == 'GET':

                # Check how many trainers are in the base
                beforeUpTrainers = Trainers.count_documents({})

                # Set trainer id
                trainer_id = -1
                
                # If it is the first trainer of the database give ID 1 
                if beforeUpTrainers == 0:

                    trainer_id = 1
                # Else get the last existing id and add 1 
                else:

                    trainerIdSetup = Trainers.find({})

                    for tre in trainerIdSetup:

                        if int(tre['trainer_id']) > trainer_id :

                            trainer_id = int(tre['trainer_id'])
                    
                    trainer_id += 1

                # Insert trainer into database
                Trainers.insert_one(
                    {
                        'trainer_id' : str(trainer_id),
                        'name' : request.form['name'],
                        'surname': request.form['surname'],
                        'programs' : request.form['programs'],
                        'bio' : request.form['bio'],
                        'email' : request.form['email'],
                        'phone' : request.form['phone']
                    }
                )
                # Check if trainer is entered
                if Trainers.count_documents({}) == beforeUpTrainers + 1:
                    # Return to the Trainers list html with message
                    flash('Επιτυχής εισαγωγή γυμναστή!', 'addedtrainer')
                    return redirect(url_for('getTrainers'))
                
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))
            
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
    
    except Exception:

        return flash('Announcement creation was not successfull!', 'warning')  
    
    return render_template('Admin/Trainers/Trainers-New.html')
    

    #Delete Announcement
 
#------- Programs -------#

# Receive program list
@app.route('/programlist', methods=['POST','GET'])
def getPrograms():

    try:
        # If admin is already logged in
        if 'username' in session:

            #Check if program exists
            if Programs.count_documents({}) == 0:
                flash('Δεν υπάρχουν υπηρεσίες αυτή τη στιγμή!', 'emptydb')
                return render_template('Admin/Programs/Programs-List.html', data=[])
            
            # Find program
            findProgram = Programs.find({})

            # Store programs in a list
            program_list = [{'program_id':req['program_id'],'name': req['name']}
                for req in findProgram]
            
            # Return to the programs List html with the stored data
            return render_template('Admin/Programs/Programs-List.html', data=program_list)
    
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))

    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Announcement list receival was not successfull!', 'warning')

# Delete program with specific id sent by the html
@app.route('/deleteProgram/<program_id>', methods=['DELETE', 'GET'])
def delete_program(program_id):

    try:
        # If admin is already logged in
        if 'username' in session:

            if request.method == 'DELETE' or request.method == 'GET':

                #Check if program exists
                if Programs.count_documents({'program_id':program_id}) == 0:
                    # Return to Trainers List html with message
                    flash('Το Πρόγραμμα με ID ' + program_id + ' δεν υπάρχει!', 'nonexistantprgrm')
                    return redirect(url_for('getPrograms'))
        
                # Delete program
                programCount = Programs.count_documents({})
                Programs.delete_one({'program_id':program_id})

                #Check if program deleted
                if Programs.count_documents({}) < programCount:
                    # Return to program List html with message
                    flash('Επιτυχής διαγραφή υπηρεσίας!', 'deletetrainer')
                    return redirect(url_for('getPrograms'))
                else:

                    return flash('Program deletetion was not successfull!', 'warning')
                
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))
        
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Deletetion was not successfull!', 'warning')

# Return program info with specific id sent by the html
@app.route('/editProgram/<program_id>', methods=['GET','POST'])
def editProgram(program_id):

    try:
        # If admin is already logged in
        if 'username' in session:

            if request.method == 'POST' or request.method == 'GET':
                # Check if a program exists with this specific offer_id    
                if Programs.count_documents({'program_id':program_id}) == 0:
                    # Return to Trainers List html with message
                    flash('Το Πρόγραμμα με ID ' + program_id + ' δεν υπάρχει!', 'nonexistantprgrm')
                    return redirect(url_for('getPrograms'))
            
                #Find program information
                findPrograms = Programs.find({'program_id':program_id})

                program_list = []

                for prg in findPrograms:

                    prg['_id'] = str(prg['_id'])
                    program_list.append(prg)

                # Return the html with the program information    
                return render_template('Admin/Programs/Programs-Update.html', data=program_list, req={'program_id': program_id})
            
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))
    
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Request examination was not successfull', 'warning')
    
    return render_template('Admin/Programs/Programs-List.html')

# Update program list with specific id sent by the html
@app.route('/updateProgram/<program_id>', methods=['POST'])
def update_program(program_id):
    try:
        # If admin is already logged in
        if 'username' in session:

            if request.method == 'POST':

                # Get the program info from the form of the html
                rcv_name = str(request.form['name'])
                rcv_text = str(request.form['text'])

                # Search for the trainer with specific id
                program = Programs.find_one({'program_id': program_id})
                
                # If program is found
                if program:
                    # Update program
                    Programs.update_one({'program_id':program_id},
                                            {'$set':
                                                {
                                                    'program_id' : str(program_id),
                                                    'name' : rcv_name,
                                                    'text' : rcv_text
                                                }
                                            }
                                        )
                    # Return to program list html with message
                    flash('Επιτυχής ενημέρωση υπηρεσίας!', 'editprogram')
                return redirect(url_for('getPrograms'))
            
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))            
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
                   
    except Exception:

        return flash('Update was not successfull!', 'warning')
    
# Go to new program form
@app.route('/newprogram', methods=['POST', 'GET'])
def new_program():
    try:
        # If admin is already logged in
        if 'username' in session:

            return render_template('Admin/Programs/Programs-New.html')
        
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))
        
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
    
    except Exception:

        return flash('Announcement creation was not successfull!', 'warning')

# Create a program 
@app.route('/createprogram', methods=['POST', 'GET'])
def create_program():

    try:
        # If admin is already logged in
        if 'username' in session:

            if request.method == 'POST' or request.method == 'GET':

                # Check how many programs are in the base
                beforeUpProgram = Programs.count_documents({})

                # Set program id
                program_id = -1

                # If it is the first program of the database give ID 1 
                if beforeUpProgram == 0:

                    program_id = 1
                # Else get the last existing id and add 1 
                else:

                    programIdSetup = Programs.find({})

                    for prg in programIdSetup:

                        if int(prg['program_id']) > program_id :

                            program_id = int(prg['program_id'])
                    
                    program_id += 1

                # Insert program into database
                Programs.insert_one(
                    {
                        'program_id' : str(program_id),
                        'name' : request.form['name'],
                        'text' : request.form['text']
                    }
                )
                # Check if program is entered
                if Programs.count_documents({}) == beforeUpProgram + 1:
                    # Return to the program list html with message
                    flash('Επιτυχής εισαγωγή υπηρεσίας!', 'addedprogram')
                    return redirect(url_for('getPrograms'))
                
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))
            
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
    
    except Exception:

        return flash('Announcement creation was not successfull!', 'warning')  
    
    return render_template('Admin/Programs/Programs-New.html')

#------- Classes -------#

# Receive Classes list
@app.route('/classlist', methods=['POST','GET'])
def getClasses():

    try:
        # If admin is already logged in
        if 'username' in session:

            #Check if Class exists
            if Classes.count_documents({}) == 0:
                flash('Δεν υπάρχουν τάξεις αυτή τη στιγμή!', 'emptydb')
                return render_template('Admin/Classes/Classes-List.html', data=[])
            
            # Find Classes
            findClass = Classes.find({})

            # Store Classes in a list
            class_list = [{'class_id':req['class_id'],'program': req['program'], 'day': req['day'],'time' :req['time'],'type' : req['type'], 'max_people': req['max_people'], 'availablespots' : req['availablespots']}
                for req in findClass]
            
            # Return to the programs List html with the stored data
            return render_template('Admin/Classes/Classes-List.html', data=class_list)
        
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))     

    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Announcement list receival was not successfull!', 'warning')

# Delete Classes with specific id sent by the html
@app.route('/deleteClass/<class_id>', methods=['DELETE', 'GET'])
def delete_class(class_id):

    try:
        # If admin is already logged in
        if 'username' in session:

            if request.method == 'DELETE' or request.method == 'GET':

                # Check if Class exists
                if Classes.count_documents({'class_id':class_id}) == 0:
                    # Return to Trainers List html with message
                    flash('Η Τάξε με ID ' + class_id + ' δεν υπάρχει!', 'nonexistantcls')
                    return redirect(url_for('getClasses'))
        
                # Delete Class
                classTrainer = Classes.count_documents({})
                Classes.delete_one({'class_id':class_id})

                # Check if Class deleted
                if Classes.count_documents({}) < classTrainer:
                    # Return to program List html with message
                    flash('Επιτυχής διαγραφή τάξης!', 'deleteclass')
                    return redirect(url_for('getClasses'))
                else:

                    return flash('Class deletetion was not successfull!', 'warning')
                
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))   
        
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Deletetion was not successfull!', 'warning')

# Return class info with specific id sent by the html
@app.route('/editClass/<class_id>', methods=['GET','POST'])
def editClass(class_id):

    try:
        # If admin is already logged in
        if 'username' in session:

            if request.method == 'POST' or request.method == 'GET':
                # Check if a class exists with this specific offer_id    
                if Classes.count_documents({'class_id':class_id}) == 0:
                    # Return to Trainers List html with message
                    flash('Η Τάξε με ID ' + class_id + ' δεν υπάρχει!', 'nonexistantcls')
                    return redirect(url_for('getClasses'))
            
                # Find class information
                findClass = Classes.find({'class_id':class_id})

                class_list = []

                for clss in findClass:

                    clss['_id'] = str(clss['_id'])
                    class_list.append(clss)

                # Return the html with the class information    
                return render_template('Admin/Classes/Classes-Update.html', data=class_list, req={'class_id': class_id})
            
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))
    
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('Request examination was not successfull', 'warning')
    
    return render_template('Classes-List.html')

# Update class with specific id sent by the html
@app.route('/updateClass/<class_id>', methods=['POST'])
def update_class(class_id):
    try:
        # If admin is already logged in
        if 'username' in session:

            if request.method == 'POST':

                # Get the class info from the form of the html
                rcv_program = str(request.form['program'])
                rcv_day = str(request.form['day'])
                rcv_time = str(request.form['time'])
                rcv_type = str(request.form['type'])
                rcv_max_people = str(request.form['max_people'])
                rcv_availablespots = str(request.form['availablespots'])

                # Search for the class with specific id
                classes = Classes.find_one({'class_id': class_id})

                # If class is found
                if classes:
                    # Update class
                    Classes.update_one({'class_id':class_id},
                                            {'$set':
                                                {
                                                    'class_id' : str(class_id),
                                                    'program' : rcv_program,
                                                    'day': rcv_day,
                                                    'time' : rcv_time,
                                                    'type' : rcv_type,
                                                    'max_people' : rcv_max_people,
                                                    'availablespots' : rcv_availablespots
                                                }
                                            }
                                        )
                    # Return to class list html with message
                    flash('Επιτυχής ενημέρωση τάξης!', 'editclass')
                return redirect(url_for('getClasses'))
            
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))
            
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
                   
    except Exception:

        return flash('Update was not successfull!', 'warning')

# Go to new class form
@app.route('/newclass', methods=['POST', 'GET'])
def new_class():
    try:
        # If admin is already logged in
        if 'username' in session:

            return render_template('Admin/Classes/Classes-New.html')
        
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin')) 
         
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
    
    except Exception:

        return flash('Announcement creation was not successfull!', 'warning')

# Create a class 
@app.route('/createclass', methods=['POST', 'GET'])
def create_class():

    try:
        # If admin is already logged in
        if 'username' in session:

            if request.method == 'POST' or request.method == 'GET':

                # Check how many classes are in the base
                beforeUpClass = Classes.count_documents({})

                # Set class id
                class_id = -1

                # If it is the first class of the database give ID 1 
                if beforeUpClass == 0:

                    class_id = 1
                # Else get the last existing id and add 1 
                else:

                    classIdSetup = Classes.find({})

                    for clss in classIdSetup:

                        if int(clss['class_id']) > class_id :

                            class_id = int(clss['class_id'])
                    
                    class_id += 1

                # Insert class into database
                Classes.insert_one(
                    {
                        'class_id' : str(class_id),
                        'program' : request.form['program'],
                        'day': request.form['day'],
                        'time' : request.form['time'],
                        'type' : request.form['type'],
                        'max_people' : request.form['max_people'],
                        'availablespots' : request.form['availablespots']
                    }
                )
                # Check if class is entered
                if Classes.count_documents({}) == beforeUpClass + 1:
                    # Return to the program list html with message
                    flash('Επιτυχής εισαγωγή τάξης!', 'addedclass')
                    return redirect(url_for('getClasses'))
                
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))
            
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
    
    except Exception:

        return flash('Announcement creation was not successfull!', 'warning')  
    
    return redirect(url_for('getClasses'))

# Refresh available spots
@app.route('/refreshclass/<class_id>', methods=['POST','GET'])
def refresh_class(class_id):
    try:
        # If admin is already logged in
        if 'username' in session:
            classes = Classes.find_one({'class_id': class_id})

            # If class is found
            if classes:
                # Update the available spots back to maximum
                Classes.update_one({'class_id': class_id},
                                            {'$set':
                                                {
                                                    'availablespots' : int(classes['max_people'])                                                }
                                            }
                                        )
                flash('Επιτυχής ανανέωση ατόμων τάξης!', 'refresh_class')
            return redirect(url_for('getClasses'))
        # if admin is not logged in
        else:
            # go to login page
            return redirect(url_for('adminlogin'))
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
    
    except Exception:

        return flash('Announcement creation was not successfull!', 'warning')  
    
    return redirect(url_for('getClasses'))

#---------------- USER ----------------#

# User Register Form
@app.route('/formregister', methods=['POST','GET'])
def formregister():
    try: 
        return render_template('User/Register/Register.html')

    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
                   
    except Exception:

        return flash('Update was not successfull!', 'warning')

# Create a user
@app.route('/register', methods=['POST','GET'])
def register():

    try:
        
        if request.method == 'POST' or request.method == 'GET':

            # Get the user info from the form of the html
            name = str(request.form['name'])
            surname = str(request.form['surname'])
            country = str(request.form['country'])
            town = str(request.form['town'])
            email = str(request.form['email'])
            address = str(request.form['address'])
            username=str(request.form['username'])
            password=str(request.form['password'])

            # Search in the database if there is another user with the entered username or email
            existing_user = Users.find_one({'username':username})
            existing_email = Users.find_one({'email':email})

            # if username and/or email exist for another user return to main page with message
            if existing_user:
                flash('Το Username που εισάγατε κατά την εγγραφή σας δεν είναι διαθέσιμο!', 'username')
                return redirect(url_for('mainpage'))  
            elif existing_email:
                flash('Το Email που εισάγατε κατά την εγγραφή σας δεν είναι διαθέσιμο!', 'email')
                return redirect(url_for('mainpage'))
            elif existing_user and existing_email:
                flash('Το Email και το username που εισάγατε κατά την εγγραφή σας δεν είναι διαθέσιμο!', 'both')
                return redirect(url_for('mainpage'))
            else: 
                # Insert User
                Request.insert_one({
                    'name' : name,
                    'surname' : surname,
                    'country' : country,
                    'town' : town,
                    'email' : email,
                    'address' : address,
                    'username': username,
                    'password': password,
                })
                # Return to main page
                return redirect(url_for('mainpage'))
       
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning')
    
    except Exception:

        return flash('User creation was not successfull!', 'warning')      

# Browse programs, no login required.
@app.route('/browsePrograms',methods=['GET'])
def browse():
    try: 

        # Fetch all entries from the collection
        entries = Programs.find()

        # Pass the entries to the template for rendering
        return render_template('User/Programs/Programs-Logout.html', entries=entries)
    
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
                   
    except Exception:

        return flash('Update was not successfull!', 'warning')

# Browse programs, user login required.
@app.route('/userbrowsePrograms',methods=['GET'])
def userbrowse():
    try:
        if 'username' in session:

            # Fetch all entries from the collection
            entries = Programs.find()

            # Pass the entries to the template for rendering
            return render_template('User/Programs/Browse-loggedin.html', entries=entries)
        else:
            return redirect(url_for('userlogin'))
    
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
                   
    except Exception:

        return flash('Update was not successfull!', 'warning')

# Browse announcements, login required.
@app.route('/AnnouncementsBrowse',methods=['GET'])
def annBrowse():
    try:

        if 'username' in session:
            # Fetch all entries from the collection
            entries = Announcement.find()
            # Pass the entries to the template for rendering
            return render_template('User/Announcements/User-Announcement-Page.html', entries=entries)
        else:
            flash('Please log in first.')
            return redirect(url_for('userlogin'))
    except KeyError as e:

        return flash(f'The key {e} is not present in the dictionary', 'warning') 
                   
    except Exception:

        return flash('Update was not successfull!', 'warning')

# Browse offers, login required.
@app.route('/OffersBrowse',methods=['GET'])
def offBrowse():
    try:

        if 'username' in session:
            # Fetch all entries from the collection
            entries = Offer.find()
            # Pass the entries to the template for rendering
            return render_template('User/Offers/User-Offer-Page.html', entries=entries)
        else:
            flash('Please log in first.')
            return redirect(url_for('userlogin'))
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
                   
    except Exception:

        return flash('Update was not successfull!', 'warning')

#---------------- BOOK APPOINTMENT ----------------#

# Form to choose program for appointment
@app.route('/formofBook', methods=['GET', 'POST'])
def formBook():
    try:
        if 'username' in session:

            if request.method == 'POST' or request.method == 'GET':
                # Search available classes in databae
                classesfind=Classes.find()
                # store them in a list
                available_classes = []
                for classes in classesfind:
                    if classes['program'] not in available_classes:
                        # store classes for different 'programs' 
                        available_classes.append(classes['program'])
                # return the html for appointment book with available classes
                return render_template('User/Appointments/formbook.html', available_classes=available_classes)
        else:
            return redirect(url_for('userlogin'))
        
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
                   
    except Exception:

        return flash('Update was not successfull!', 'warning')    

# Form to choose hour for appointment
@app.route('/showtimes', methods=['GET', 'POST'])
def showtimes():
    try:
        if 'username' in session:

            if request.method == 'POST' or request.method == 'GET':
                class_picked = request.form.get('available_classes')
                date_str = request.form.get('date')
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                # Convert date string to datetime object
                date_name = date_obj.strftime('%A')
                username = session['username']
                user = Users.find_one({'username': username})
                userId = user['user_id']
                # Find classes with the specified name and date
                matching_classes = list(Classes.find({"program": class_picked, "day": date_name}))
                


                # Extract available times for the specified class and date
                available_times = []
                for class_entry in matching_classes:
                    print(class_entry)
                    if int(class_entry['availablespots']) != 0:
                        print("yes")
                        available_times.append(class_entry['time'])
                        
                print("available times:", available_times)
                
                # check specific user's cancellations
                cancellations= Cancellations.find({'userid':userId})
                cancellations_list = list(cancellations)
                num_cancellations = len(cancellations_list)
                # if user has completed 2 cancellations this week
                if num_cancellations >=2:
                    # return to Program choose html with message
                    flash("Έχετε κάνει πάνω από 2 ακυρώσεις αυτή την εβδομάδα συνεπώς δεν έχετε δικαίωμα για δημιουργία άλλης κράτησης μέχρι το τέλος της εβδομάδας", 'denied')
                    return redirect(url_for('formBook'))
                else:
                    return render_template('User/Appointments/book.html',class_name=class_picked, date=date_str, available_times=available_times)
        else:
            flash('Please log in first.')
            return redirect(url_for('userlogin'))
        
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
                   
    except Exception:

        return flash('Update was not successfull!', 'warning')     
    





# Submit the appointment
@app.route('/submitAppointment', methods=['POST'])
def submit_appointment():
    try:
        if 'username' in session:

            # Get the appointment data from the form
            class_name = request.form.get('class_name')
            date_str = request.form.get('date')
            time = request.form.get('times')

            # Check how many Appointments are in the base
            beforeApps = Appointment.count_documents({})

            # Set Appointment id
            app_id = -1

            # If it is the first Appointment of the database give ID 1         
            if beforeApps == 0:

                app_id = 1
            # Else get the last existing id and add 1 
            else:

                appIdSetup = Appointment.find({})

                for app in appIdSetup:

                    if int(app['app_id']) > app_id :

                        app_id = int(app['app_id'])
                        
                app_id += 1

            # Convert date string to datetime object
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day= date_obj.strftime('%A')
            var1=str(date_obj.day)
            var2=str(date_obj.month)
            var3=str(date_obj.year)
            date= var1+'/'+var2+'/'+ var3
            username = session['username']
            user = Users.find_one({'username': username})
            userId = user['user_id']
            #Get todays date 
            todayflag = datetime.today()
            todayflag2 = todayflag.strftime("%d/%m/%Y")
            date_format = '%d/%m/%Y'
            today = datetime.strptime(todayflag2, date_format)
            # Insert the appointment into the Appointments collection
            spots = Classes.find_one({'program' : class_name,'day':day,'time': time}) 
            avSpots = int(spots['availablespots']) - 1
            # Check for available spots of the class
            if avSpots<=0:
                flash('Δεν υπάρχουν διαθέσιμες θέσεις για το συγκεκριμένο μάθημα.', 'nospots')
                return redirect(url_for('formBook'))
            elif date_obj < today:
                flash('Δεν μπορείτε να κάνετε κράτηση για προηγούμενη ημερομηνία.', 'prevdate')
                return redirect(url_for('formBook'))
            else:

                # Calculate the number of days to add to the input date to get to the end of the week (Sunday)
                days_until_end_of_week = 6 - todayflag.weekday()

                # Calculate the end date of the week by adding the calculated days
                end_of_week_date = todayflag + timedelta(days=days_until_end_of_week)
                if date_obj <= end_of_week_date:
                    # Insert Appointment
                    Appointment.insert_one({
                        'app_id' : str(app_id),
                        'class_name': class_name,
                        'date': date,
                        'time':time,
                        'day':day,
                        'user_id': userId,
                        'type':spots['type'],
                        'class_id': spots['class_id']
                    })
                    
                    OlderApp.insert_one({
                        'app_id' : str(app_id),
                        'class_name': class_name,
                        'date': date,
                        'time':time,
                        'day':day,
                        'user_id': userId,
                        'type':spots['type'],
                        'class_id': spots['class_id']
                    })

                    # Update the max_people count in the Classes collection
                    Classes.update_one(
                        {'program' : class_name,'day':day,'time': time},
                        {"$set": {"availablespots": avSpots}}
                    )
                    flash('Επιτυχής κράτηση θέσης!', 'successapp')
                    return redirect(url_for('myAppointments'))
                else:
                    flash('Μπορείς να κλείσεις ραντεβού μόνο για τη βδομάδα που διανύουμε!', 'successapp')
                    return redirect(url_for('myAppointments'))
        else:
            flash('Please log in first.')
            return redirect(url_for('userlogin'))
    
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
                   
    except Exception:

        return flash('Update was not successfull!', 'warning') 

# User Appointments List
@app.route('/myAppointments', methods=['POST', 'GET'])
def myAppointments():
    try:
        if 'username' in session:

            # Get the username from session
            username = session['username']
            # Search for this specific user
            user = Users.find_one({'username': username})
            # Get this users id
            userId = user['user_id']
            date_format = '%d/%m/%Y'
            # set todays datetime       
            todayflag = datetime.today()
            todayflag2 = todayflag.strftime("%d/%m/%Y")
            today = datetime.strptime(todayflag2, date_format)
            iterable = Appointment.find({})
            # Get users Appointments
            for appointment in iterable:
                pastdate =appointment['date']
                pastdate = datetime.strptime(pastdate, date_format)
                # If this appointments date is previous to todays
                if pastdate<today:
                    # Insert to Older Appointments collection
                    OlderApp.insert_one(appointment)
                    # Delete from Appointments collection
                    Appointment.delete_one(appointment)
            # Store remaining appointments to output
            output=Appointment.find({'user_id':userId})
            # Pass the entries to the template for rendering
            return render_template('User/Appointments/User-Show-Appointments.html', data=output)
        else:
            flash('Please log in first.')
            return redirect(url_for('userlogin'))
        
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
                   
    except Exception:

        return flash('Update was not successfull!', 'warning') 
    
# View older appointments, login required.
@app.route('/olderAp',methods=['GET','DELETE'])
def older(): 
    try:
        if 'username' in session:

            # Get the username from session
            username = session['username']
            # Search for this specific user
            user = Users.find_one({'username': username})
            # Get this users id
            userId = user['user_id']
            date_format = '%d/%m/%Y'
            if request.method == 'GET' or request.method == 'DELETE':
                # set todays datetime       
                todayflag = datetime.today()
                todayflag2 = todayflag.strftime("%d/%m/%Y")
                today = datetime.strptime(todayflag2, date_format)
                iterable = Appointment.find({})
                # Get users Appointments
                for appointment in iterable:
                    pastdate =appointment['date']
                    pastdate = datetime.strptime(pastdate, date_format)
                    # If this appointments date is previous to todays
                    if pastdate<today:
                        # Insert to Older Appointments collection
                        OlderApp.insert_one(appointment)
                        # Delete from Appointments collection
                        Appointment.delete_one(appointment)
                # Store remaining appointments to output
                output=OlderApp.find({'user_id':userId})
        else:
            return render_template('User-Login-Page.html')
        # Pass the entries to the template for rendering
        return render_template('User/Appointments/Older-Appointments.html', data=output) 
    
    except KeyError as e:
        
        return flash(f'The key {e} is not present in the dictionary', 'warning') 
                   
    except Exception:

        return flash('Update was not successfull!', 'warning') 

# Cancel appointment
@app.route('/cancel/<app_id>', methods=['DELETE', 'POST', 'GET'])
def cancel(app_id):
    if 'username' in session:
        date_format = '%d/%m/%Y'
        time_format = '%H:%M'
        # Get the username from session
        username = session['username']
        # Search for this specific user
        user = Users.find_one({'username': username})
        # Get this user's id
        userid = user['user_id']
        # Set current datetime
        current_datetime = datetime.now()
        # Search for specific appointment via the id that html sent
        entry = Appointment.find_one({'app_id': app_id})
        
        if entry:
            pastdate = datetime.strptime(entry['date'], date_format)
            pasttime_str = entry['time']

            # Convert the string representation of time to a datetime object
            pasttime = datetime.strptime(pasttime_str, time_format).time()

            # Create a datetime object with the date from pastdate and the time from pasttime
            appointment_datetime = datetime.combine(pastdate, pasttime)
            app = appointment_datetime - timedelta(hours=2)
            
            # Check if appointment is already in OlderApp collection
            is_old_appointment = OlderApp.find_one({'app_id': app_id})

            # If appointment is in less than 2 hours
            if app <= current_datetime:
                if is_old_appointment:
                    # Return to Appointments List with message
                    flash("Δεν μπορείς να ακυρώσεις κάποιο ραντεβού, καθώς έχει πραγματοποιηθεί η προπόνηση.")
                else:
                    # Return to Appointments List with message
                    flash("Δεν μπορείς να ακυρώσεις κάποιο ραντεβού όταν είναι σε λιγότερο από 2 ώρες.")
                return redirect(url_for('myAppointments'))
            else:
                # Add one cancellation to the user
                Cancellations.insert_one({'userid': userid})

                # Delete the appointment from both collections
                Appointment.delete_one({'app_id': app_id})
                OlderApp.delete_one({'app_id': app_id})

                # Add the spot back to the class
                prevspots = Classes.find_one({'class_id': entry['class_id']})
                nowspots = prevspots['availablespots'] + 1
                Classes.update_one({'class_id': entry['class_id']},
                                   {
                                       '$set':
                                       {
                                           'availablespots': nowspots
                                       }
                                   })

                # Return to Appointments List with message
                flash('Επιτυχής ακύρωση ραντεβού!', 'cancelledapp')
                return redirect(url_for('myAppointments'))
    else:
        return redirect(url_for('userlogin'))




# Run Flask App
if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=5000)