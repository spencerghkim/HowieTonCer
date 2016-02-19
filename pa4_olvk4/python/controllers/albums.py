
from flask import *
from shared import *

albums = Blueprint('albums', __name__, template_folder='views')

@albums.route('/albums', methods=['GET'])
def albums_route():
	# both in session and not in session shows public_albums
	public_albums = shared.execute_and_fetch_query('''SELECT * FROM album WHERE access = "public"''')

	# default options for "no session"
	options = { 
		"loggedin": False,
		"edit": False,
		"viewing": True,
		"public_albums": public_albums,
		"public_albums_flag": len(public_albums) != 0 # in case there isn't a public album to display
	}

	if 'username' in session:
		session_username = session['username']
		
		options["loggedin"] = True
		options["session_username"] = session_username

		# check to see if there are personal albums
		personal_albums = shared.execute_and_fetch_query('''SELECT * FROM album WHERE username="%s"''' % session_username)
		options["personal_albums"] = personal_albums
		options["personal_albums_flag"] = len(personal_albums) != 0

		# Check to see if there are accessible_private_albums
		accessible_private_albums = shared.execute_and_fetch_query('''SELECT A.title, A.username, A.albumid FROM album A, albumaccess X WHERE X.username = "%s" AND X.albumid = A.albumid ORDER BY username''' % session_username)
		options["accessible_private_albums_flag"] = len(accessible_private_albums) != 0
		options["accessible_private_albums"] = accessible_private_albums

	return render_template("albums.html", **options)
