
from flask import *
from shared import *

album = Blueprint('album', __name__, template_folder='views')


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'bmp', 'gif'])
UPLOAD_FOLDER = 'pictures'

def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@album.route('/album')
def album_route():
	albumid= request.args.get('id')

	# Error: no albumid specified in url
	if albumid is None:
		print "ERROR: no albumid on url"
		return render_template("404.html")

	album_result = shared.execute_and_fetch_query('''SELECT title, username, access FROM album WHERE albumid="%s"''' % albumid)

	# Error: albumid does not texist
	if len(album_result) == 0:
		print "ERROR: albumid doesn't exist on db"
		return render_template("404.html")

	album_title = album_result[0]["title"]
	album_owner = album_result[0]["username"]
	album_access = album_result[0]["access"]

	#default HTML arguments?
	options = {
		"album_title": album_title,
		"session_username": None,
		"edit": False,
		"album_owner": album_owner,
		"loggedin": False,
		"access_denied": True
	}

	# No session
	if 'username' not in session :
		# Public Access, No Session
		if album_access == "public" :
			options["access_denied"] = False
			pictures = shared.execute_and_fetch_query('''SELECT * FROM photo P, contain C WHERE C.albumid = "%s" AND P.picid = C.picid ORDER BY C.sequencenum''' % albumid)
			return render_template("album.html", pictures=pictures, **options)
		# Private Access, No Session
		else :
			return render_template("please_login.html", path=request.url)

	# There is a session
	
	# Private Access, Session
	if album_access != "public" :
		# User not owner of Private Album
		if session['username'] != album_owner :
			hasAccess = shared.execute_and_fetch_query('''SELECT COUNT(*) AS hasAccess FROM albumaccess WHERE albumid = "%s" AND username = "%s"''' % (albumid, session['username']))

			# User not owner && no access to Private Album
			if hasAccess[0]["hasAccess"] == 0 :
				return render_template("invalid_perms.html", session_username=session['username'])
			# Else: User not owner && has access to Private Album
		# Else: User is owner of Private Album
	# Else: Public Access, Session

	pictures = shared.execute_and_fetch_query('''SELECT * FROM photo P, contain C WHERE C.albumid = "%s" AND P.picid = C.picid ORDER BY C.sequencenum''' % albumid)
	
	options["albumid"] = albumid
	options["session_username"] = session['username']
	options["loggedin"] = 1
	options["access_denied"] = False

	return render_template("album.html", pictures=pictures, **options)
