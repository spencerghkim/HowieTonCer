from functools import wraps
from flask import *
from datetime import *
from shared import *
import MySQLdb, platform

pic = Blueprint('pic', __name__, template_folder='views')

# def check_auth(username):
# 	#result = shared.execute_and_fetch_query('''SELECT * from albumAccess where username = "%s"''' % username)
# 	#if len(result):
# 	#	return True
# 	picid = request.args.get('id')
# 	result = shared.execute_and_fetch_query('''SELECT A.albumid from contain C, album A where C.picid = "%s" and C.albumid = A.albumid and A.username = "%s"''' % (picid, username))
# 	if result is not None:
# 		return True
# 	return False

# def authenticate():
# 	return "pls authenticate noob"

# def requires_auth(f):
# 	@wraps(f)
# 	def decorated():
# 		if 'username' in session:
# 			username = session['username']
# 			if check_auth(username):
# 				return f()
# 		return authenticate()
# 	return decorated

@pic.route('/olvk4/pa2/pic', methods=['GET', 'POST'])
def pic_route():
	picid = request.args.get('id')
	
	#check pic in url
	if picid is None:
		print "ERROR: Invalid picid"
		return render_template("404.html")

	caption = request.form.get('caption')
	if platform.system() == 'Darwin':
		db = MySQLdb.connect(host="localhost", user="root", passwd="hmcc", db="group108pa2")
	else:
		db = MySQLdb.connect(host="localhost", user="group108", passwd="hmcc", db="group108pa2")
	cursor = db.cursor(MySQLdb.cursors.DictCursor)

	cursor.execute('''SELECT * FROM photo where picid = "%s"''' % picid)
	picdata = cursor.fetchall()
	
	# check pic exists
	if len(picdata) == 0:
		print "ERROR: Invalid picid"
		return render_template("404.html")		

	# grab albumid
	cursor.execute('''SELECT * from contain where picid="%s"''' % picid)
	containdata = cursor.fetchall()
	albumid = containdata[0]["albumid"]

	cursor.execute('''SELECT * from album where albumid="%s"''' % albumid)
	albumdata = cursor.fetchall()
	access = albumdata[0]["access"]
	
	cursor.execute('''SELECT username from album where albumid="%s"''' % albumid)
	ownerdata = cursor.fetchall()
	owner = ownerdata[0]["username"]

	# no session
	if 'username' not in session:
		if request.method == "POST":
			return render_template("please_login.html", path=request.url)
		if access != 'public':
			return render_template("please_login.html", path=request.url)
		
		# good GET request: see bottom


	# session exists
	else:
		session_username = session['username']
		cursor.execute('''SELECT count(*) as perms from albumaccess where albumid="%s" and username="%s"''' % (albumid, session_username))
		albumAccessData = cursor.fetchall()
		perms = albumAccessData[0]["perms"]

		# user doesn't have access to album
		if access == 'private' and perms == 0 and session_username != owner:
			return render_template("invalid_perms.html", session_username=session_username)

		#else, have permissions
		if request.method == "POST":
			if session_username != owner:
				return render_template("invalid_perms.html", session_username=session_username)
			
			# user is owner of album
			cursor.execute('''UPDATE contain SET caption="%s" WHERE picid="%s"''' % (caption, picid))

			# update album last updated
			datestr = datetime.now().date().isoformat()
			cursor.execute('''UPDATE album SET lastupdated="%s" WHERE albumid="%s"''' % (datestr, albumid))
			db.commit()
			return redirect(url_for("pic.pic_route", id=picid))

		# else it's a GET that user has access to

	# Good get request
	cursor.execute('''SELECT picid FROM contain WHERE sequencenum = (SELECT MIN(C.sequencenum) FROM contain C where C.albumid = (SELECT albumid FROM contain WHERE picid="%s") AND C.sequencenum > (SELECT sequencenum FROM contain WHERE picid="%s"));''' %(picdata[0]['picid'], picdata[0]['picid']))
	nextdata = cursor.fetchall()

	if nextdata:
		nextid = nextdata[0]["picid"]
		nextflag = True
	else:
		nextid = False
		nextflag = False

	cursor.execute('''SELECT picid FROM contain WHERE sequencenum = (SELECT MAX(C.sequencenum) FROM contain C where C.albumid = (SELECT albumid FROM contain WHERE picid="%s") AND C.sequencenum < (SELECT sequencenum FROM contain WHERE picid="%s"));''' %(picdata[0]['picid'], picdata[0]['picid']))
	prevdata = cursor.fetchall()

	if prevdata:
		previd = prevdata[0]["picid"]
		prevflag = True
	else:
		previd = False
		prevflag = False

	options = {
		"url": picdata[0]["url"],
		"picid": picdata[0]["picid"],
		"caption": containdata[0]["caption"],
		"nextid": nextid,
		"nextflag": nextflag,
		"previd": previd,
		"prevflag": prevflag
	}

	if 'username' not in session:
		options["loggedin"] = False
		options["session_username"] = None

	else:
		useralbums = shared.execute_and_fetch_query('''SELECT A.albumid from contain C, album A where C.picid = "%s" and C.albumid = A.albumid and A.username = "%s"''' % (picid, session['username']))
		options["loggedin"] = True
		options["session_username"] = session_username
		if len(useralbums) != 0:
			options["authorized"] = True
		else:
			options["authorized"] = False

	cursor.execute('''SELECT albumid from contain where picid="%s";''' % picdata[0]["picid"])
	albumidset = cursor.fetchall()
	return render_template("pic.html", albumid = albumidset[0]["albumid"], **options)

