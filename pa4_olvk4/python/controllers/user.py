
from flask import *
from shared import *
import os
from datetime import *
import time

user = Blueprint('user', __name__, template_folder='views')

@user.route('/user', methods=['GET', 'POST'])
def user_route():
	# if session already exists, redirect the user to /user/edit.
	if 'username' in session:
		return redirect(url_for("user_edit.user_edit_route"))
	
	# default options for GET request
	options = {
		"passwderr": False,
		"loggedin": False,
		"edit": False,
		"login": False,
		"signupfailed": False,
		"signup": True
	}

	# GET user signup page
	if request.method == 'GET':
		return render_template('user.html', **options)

	# POST request: signup form submission
	username = request.form.get('username')
	firstname = request.form.get('firstname')
	lastname = request.form.get('lastname') 
	password1 = request.form.get('password1')
	password2 = request.form.get('password2')
	email = request.form.get('email')

	if username == "" or firstname == "" or lastname == "" or password1 == "" or password2 == "" or email == "":
		# only reachable through modified HTML or custom POST request
		return redirect(url_for("user.user_route"))

	# if password1 and password2 doesn't match return back to singup page
	if password1 != password2:
		options["passwderr"] = True
		options["signupfailed"] = True
		return render_template('user.html', **options)
	
	options["session_username"] = username
	num_user = shared.execute_and_fetch_query('''SELECT Count(*) AS num_user FROM user WHERE username = "%s"''' % username)
		
	# Error: user already exists
	if num_user[0]["num_user"] != 0:
		options["userError"] = True
		options["signupfailed"] = True
		options["loggedin"] = False
		# Nice to have: helpful message that username already exists
		return render_template("user.html", **options)

	encrypted_password_to_insert = shared.encrypt(password1)

	# POST is successful
	shared.execute_and_commit_query('''INSERT INTO user VALUES ("%s", "%s", "%s", "%s", "%s")''' % (username, firstname, lastname, encrypted_password_to_insert, email))

	options["loggedin"] = True
	options["signup"] = False
	session['username'] = username
	session['lastactivity'] = (int)(time.time())

	# 302 to /
	return redirect(url_for('main.main_route'))



@user.route('/user/login', methods=['GET', 'POST'])
def user_login_route(): # Public

	oldpath = request.args.get('path')

	# IF session has username, redirect to /
	if 'username' in session:
		return redirect(url_for("main.main_route"))

	options = {
		"passwderr": False,
		"loggedin": False,
		"username": None,
		"edit": False,
		"login": True,
		"signupfailed": False,
		"signup": False
	}

	if request.method == 'GET':
		return render_template('user.html', **options)

	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password1') 
		
		usernameExists = shared.execute_and_fetch_query('''SELECT COUNT(username) AS num_user FROM user WHERE username="%s"''' % username)

		# username does not exist
		if usernameExists[0]["num_user"] == 0:
			options["nameerror"] = True
			return render_template('user.html', **options)

		# username exists
		request_password = request.form.get('loginpassword')

		# encrypt password for Login
		password = shared.encrypt(request_password)

		login_auth = shared.execute_and_fetch_query('''SELECT COUNT(*) AS auth FROM user WHERE username = "%s" AND password = "%s"''' % (username, password))
		
		# Success: give session bcookie
		if login_auth[0]["auth"] == True :
			session['username'] = username
			session['lastactivity'] = (int)(time.time())

			if oldpath is not None:
				print oldpath
				return redirect(oldpath)
			return redirect(url_for('main.main_route'))
		else :
			# login fail because password is wrong for the user
			options = {
				"userError": True,
				"passwderr": False,
				"loggedin": False,
				"edit": False,
				"login": True,
				"signupfailed": False,
				"signup": False,
				"wrongPass": True
			}
			return render_template('user.html', **options)

@user.route('/logout')
def logout_route():
	session.pop('username', None)
	session.pop('lastactivity', None)
	return redirect(url_for("main.main_route"))

user.secret_key = os.urandom(24)




