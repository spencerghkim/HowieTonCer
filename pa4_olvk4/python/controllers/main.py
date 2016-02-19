
from flask import *
from shared import *

main = Blueprint('main', __name__, template_folder='views')

# function for active session
def in_session(options):
	username = session['username']

	options["session_username"] = username
	options["loggedin"] = True

	# Check to see if you have personal albums
	personal_albums = shared.execute_and_fetch_query('''SELECT title, username, albumid FROM album where username="%s"''' % session['username'])
	options["personal_albums"] = personal_albums
	options["personal_albums_flag"] = len(personal_albums) != 0

	# Check to see if you have any accessible private albums
	accessible_private_albums = shared.execute_and_fetch_query('''SELECT A.title, A.username, A.albumid FROM album A, albumaccess X WHERE X.username = "%s" AND X.albumid = A.albumid ORDER BY username''' % username)
	options["accessible_private_albums"] = accessible_private_albums
	options["accessible_private_albums_flag"] = len(accessible_private_albums) != 0

	resp = make_response(render_template('index.html', **options))
	resp.set_cookie('username', username)
	return resp

# function for no active session
def not_in_session(options):

	options["public"] = True
	return render_template('index.html', **options)

@main.route('/')
def main_route():
	public_albums = shared.execute_and_fetch_query('''SELECT title, username, albumid FROM album where access = "public" ORDER BY username''')

	options = {
		# "users": shared.execute_and_fetch_query('''SELECT username FROM user ORDER BY username'''),
		"public_albums": public_albums
	}
	# If public albums exists, show in HTML
	if len(public_albums) == 0:
		options = {
			"public_albums_flag": 0
		}
		# options["public_albums_flag"] = 0
	else :
		options = {
			"public_albums": public_albums,
			"public_albums_flag": 1
		}
		# options["public_albums"] = public_albums
		# options["public_albums_flag"] = 1
	
	# active session - trivial authentication 
	if 'username' in session:
		return in_session(options)

	# no active session
	else: 
		return not_in_session(options)
		
	return render_template("404.html")
