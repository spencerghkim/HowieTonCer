from functools import wraps
from flask import *
from shared import *

user_edit = Blueprint('user_edit', __name__, template_folder='views')

# def authenticate(path):
# 	return render_template("please_login.html", path=request.url)
# def requires_auth(f):
# 	@wraps(f)
# 	def decorated():
# 		if 'username' in session:
# 			username = session['username']
# 			return f()
# 		return authenticate(path)
# 	return decorated

@user_edit.route('/user/edit', methods=['GET', 'POST'])
def user_edit_route(): # Sensitive
	if 'username' not in session:
		return render_template("please_login.html", path=request.url)

	username = session['username']

	# POST
	if request.method == "POST" :
		if request.form.get('op') == "Delete Account" :
			username = request.form.get('username')
			
			# delete contain, photo, album access, album, user.
			picids = shared.execute_and_fetch_query('''SELECT P.picid FROM photo P, contain C, album A WHERE A.username = "%s" AND A.albumid = C.albumid AND C.picid = P.picid''' % username)
			albumids = shared.execute_and_fetch_query('''SELECT albumid FROM album WHERE username = "%s"''' % username)
			
			db, cursor = shared.get_db_connection()

			# Delete all albumids owned by User
			for items in albumids :
				shared.delete_album_by_albumid(items['albumid'])

			# Delete all tuples in AlbumAccess with User
			cursor.execute('''DELETE FROM albumaccess WHERE username = "%s"''' % username)
			
			# Finally, delete User
			cursor.execute('''DELETE FROM user WHERE username = "%s"''' % username)
			db.commit()

			session.pop('username', None)
			session.pop('lastactivity', None)
			return redirect(url_for("main.main_route"))

		else: # op = Edit
			firstname = request.form.get('firstname')
			lastname = request.form.get('lastname')
			email = request.form.get('email')
			password1 = request.form.get('password1')
			password2 = request.form.get('password2')

			db, cursor = shared.get_db_connection()
			if firstname != "" :
				cursor.execute('''UPDATE user SET firstname="%s" WHERE username = "%s"''' % (firstname, username))
			if lastname != "" :
				cursor.execute('''UPDATE user SET lastname="%s" WHERE username = "%s"''' % (lastname, username))
			if email != "" :
				cursor.execute('''UPDATE user SET email="%s" WHERE username = "%s"''' % (email, username))

			if password1 != "" and password2 != "" :
				if password1 == password2 :
					encrypted_password_to_insert = shared.encrypt(password1)

					cursor.execute('''UPDATE user SET password="%s" WHERE username = "%s"''' % (encrypted_password_to_insert, username))
				else:
					# passwords don't match
					# Nice to have: error message
					return redirect(url_for("user_edit.user_edit_route"))
			db.commit()
			# Nice to have: should user see "Success!" message?
			return redirect(url_for("user_edit.user_edit_route"))

	# GET page showing user edit options... Flow is exactly same as POST edit
	userInfo = shared.execute_and_fetch_query('''SELECT * FROM user WHERE username = "%s"''' % username)

	# Ask yourself, is it possible to have a username session not in the database?
	# Nice to have: write a check, perhaps have check in requires_auth()
	options = {
		"edit": True,
		"firstname": userInfo[0]["firstname"],
		"lastname": userInfo[0]["lastname"],
		"email": userInfo[0]["email"],
		"username": username,
		"session_username": username,
		"loggedin": True
	}
	return render_template('user.html', **options)



