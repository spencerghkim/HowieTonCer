from functools import wraps
from flask import *
from datetime import *
from shared import *
import MySQLdb, platform
# from flask.ext.api import status
import json

pic = Blueprint('pic', __name__, template_folder='views')

@pic.route('/pic', methods=['GET', 'POST'])
def pic_route():
	picid = request.args.get('id')
	
	#check pic in url
	if picid is None:
		print "ERROR: Invalid picid"
		return render_template("404.html")

	caption = request.form.get('caption')
	if platform.system() == 'Darwin':
		db = MySQLdb.connect(host="localhost", user="root", passwd="hmcc", db="group108pa3")
	else:
		db = MySQLdb.connect(host="localhost", user="group108", passwd="hmcc", db="group108pa3")
	cursor = db.cursor(MySQLdb.cursors.DictCursor)

	cursor.execute('''SELECT * FROM photo where picid = "%s"''' % picid)
	picdata = cursor.fetchall()

	# check pic exists
	if len(picdata) == 0:
		print "ERROR: Invalid picid"
		return render_template("404.html")		

	# grab albumid and current sequence_num
	cursor.execute('''SELECT * from contain where picid="%s"''' % picid)
	containdata = cursor.fetchall()
	albumid = containdata[0]["albumid"]
	current_sequencenum = containdata[0]["sequencenum"];

	cursor.execute('''SELECT * from album where albumid="%s"''' % albumid)
	albumdata = cursor.fetchall()
	access = albumdata[0]["access"]
	
	# cursor.execute('''SELECT username from album where albumid="%s"''' % albumid)
	# ownerdata = cursor.fetchall()
	owner = albumdata[0]["username"]

	# no session
	if 'username' not in session:
		if request.method == "POST":
			return render_template("please_login.html", path=request.url)
		if access != 'public':
			return render_template("please_login.html", path=request.url)
		
		# good GET request: see bottom
		already_favorited = False;

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

		cursor.execute('''SELECT * FROM Favorite WHERE picid = "%s" AND username = "%s"''' % (picid, session_username))
		already_favorited = cursor.fetchall()
		print already_favorited
		if len(already_favorited) != 0 :
			already_favorited = True
		else :
			already_favorited = False

		# else it's a GET that user has access to

	# Good get request
	cursor.execute('''SELECT picid FROM contain WHERE albumid = "%s" AND sequencenum = (SELECT MIN(C.sequencenum) FROM contain C where C.albumid = "%s" AND C.sequencenum > "%s")''' % (albumid, albumid, current_sequencenum))
	nextdata = cursor.fetchall()

	if nextdata:
		nextid = nextdata[0]["picid"]
		nextflag = True
	else:
		nextid = False
		nextflag = False

	cursor.execute('''SELECT picid FROM contain WHERE albumid = "%s" AND sequencenum = (SELECT MAX(C.sequencenum) FROM contain C where C.albumid = "%s" AND C.sequencenum < "%s")''' % (albumid, albumid, current_sequencenum))
	prevdata = cursor.fetchall()

	if prevdata:
		previd = prevdata[0]["picid"]
		prevflag = True
	else:
		previd = False
		prevflag = False

	# get num of favorites for the picture
	last_favorite = ""
	cursor.execute('''SELECT * FROM Favorite WHERE picid = "%s" ORDER BY favoriteid DESC''' % picid)
	last_favorite = cursor.fetchall()
	if len(last_favorite) != 0:
		last_favorite = last_favorite[0]["username"]

	num_favorites = 0
	cursor.execute('''SELECT COUNT(*) AS num FROM Favorite WHERE picid = "%s"''' % picid)
	num_favorites = cursor.fetchall()
	num_favorites = num_favorites[0]["num"]

	cursor.execute('''SELECT * from album where albumid="%s"''' % albumid)
	albumdata = cursor.fetchall()
	access = albumdata[0]["access"]
	pubAccess = False
	privAccess = False
	if access == "public":
		pubAccess = True

	# cursor.execute('''SELECT * FROM Favorites WHERE picid = "%s" AND ''' % )

	options = {
		"url": picdata[0]["url"],
		"picid": picdata[0]["picid"],
		"caption": containdata[0]["caption"],
		"nextid": nextid,
		"nextflag": nextflag,
		"previd": previd,
		"prevflag": prevflag,
		"num_favorites": num_favorites,
		"last_favorite": last_favorite,
		"already_favorited": already_favorited,
		"authorized": True,
		"pubAccess": pubAccess
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
		# else:
		# 	options["authorized"] = False

	cursor.execute('''SELECT albumid from contain where picid="%s";''' % picdata[0]["picid"])
	albumidset = cursor.fetchall()
	return render_template("pic.html", albumid = albumidset[0]["albumid"], **options)

@pic.route('/pic/caption', methods=['GET', 'POST'])
def pic_caption_route():
	if platform.system() == 'Darwin':
		db = MySQLdb.connect(host="localhost", user="root", passwd="hmcc", db="group108pa3")
	else:
		db = MySQLdb.connect(host="localhost", user="group108", passwd="hmcc", db="group108pa3")
	cursor = db.cursor(MySQLdb.cursors.DictCursor)

	if request.method == 'GET':
		picid = request.args.get('id')

		# verify picid exists
		if picid is None:
			response = jsonify(error="You did not provide an id parameter.", status=404)
			response.status_code = 404
			return response

		# checks that picid is in db
		cursor.execute('''SELECT * FROM photo where picid = "%s"''' % picid)
		picdata = cursor.fetchall()

		if len(picdata) == 0:
			response = jsonify(error="Invalid id parameter. The picid does not exist.", status=422)
			response.status_code = 422
			return response

		# find caption if picid exists
		cursor.execute('''SELECT caption FROM contain where picid = "%s"''' % picid)
		caption = cursor.fetchall()

		if len(caption) != 0:
			response = jsonify(caption=caption[0]["caption"])
			response.status_code = 200
		else:
			response = jsonify(caption="")
			response.status_code = 200

		return response

	# POST
	else:
		req_json = request.get_json()
		picid = req_json.get("id")
		caption = req_json.get("caption")

		# print json
		#verify picid and Caption exist
		if picid is None and caption is None:
			response = jsonify(error="You did not provide an id and caption parameter.", status=404)
			response.status_code = 404
			return response
		elif picid is None:
			response = jsonify(error="You did not provide an id parameter.", status=404)
			response.status_code = 404
			return response
		elif caption is None:
			response = jsonify(error="You did not provide a caption parameter.", status=404)
			response.status_code = 404
			return response	

		# checks that picid is in db
		cursor.execute('''SELECT * FROM photo where picid = "%s"''' % picid)
		picdata = cursor.fetchall()
		if len(picdata) == 0:
			response = jsonify(error="Invalid id. The picid does not exist.", status=422)
			response.status_code = 422
			return response
		
		response = jsonify(caption=caption, status=201)
		response.status_code = 201
		cursor.execute('''UPDATE contain SET caption="%s" WHERE picid="%s"''' % (caption, picid))
		db.commit()
		return response

@pic.route('/pic/favorites', methods=['GET', 'POST'])
def pic_favorite_route():
	if platform.system() == 'Darwin':
		db = MySQLdb.connect(host="localhost", user="root", passwd="hmcc", db="group108pa3")
	else:
		db = MySQLdb.connect(host="localhost", user="group108", passwd="hmcc", db="group108pa3")
	cursor = db.cursor(MySQLdb.cursors.DictCursor)

	if request.method == 'GET':
		picid = request.args.get('id')

		# verify picid exists
		if picid is None:
			response = jsonify(error="You did not provide an id parameter.", status=404)
			response.status_code = 404
			return response

		cursor.execute('''SELECT * FROM photo where picid = "%s"''' % picid)
		picdata = cursor.fetchall()
		
		if len(picdata) == 0:
			response = jsonify(error="Invalid id parameter. The picid does not exist.", status=422)
			response.status_code = 422
			return response

		# checks how many favorites are for one picture
		cursor.execute('''SELECT * FROM Favorite where picid = "%s" ORDER BY date DESC''' % picid)
		favdata = cursor.fetchall()

		if len(favdata) == 0:
			response = jsonify(id=picid, num_favorites=0, latest_favorite="")
			response.status_code = 200
			return response

		if len(favdata) != 0:
			print favdata
			response = jsonify(id=picid, num_favorites=len(favdata), latest_favorite=favdata[0]["username"])
			response.status_code = 200
			return response

		else:
			# not sure what the error message should be there
			# technically should never get here though
			response = jsonify(error="Invalid id. The picid does not exist.", status=422)
			response.status_code = 400
			return response

	# POST
	else:
		req_json = request.get_json()
		picid = req_json.get("id")
		username = req_json.get("username")

		#verify picid and username are there
		if picid is None and username is None:
			response = jsonify(error="You did not provide an id and username parameter.", status=404)
			response.status_code = 404
			return response
		elif picid is None:
			response = jsonify(error="You did not provide an id parameter.", status=404)
			response.status_code = 404
			return response
		elif username is None:
			response = jsonify(error="You did not provide a username parameter.", status=404)
			response.status_code = 404
			return response	

		# checks that picid is in db
		cursor.execute('''SELECT * FROM photo where picid = "%s"''' % picid)
		picdata = cursor.fetchall()
		if len(picdata) == 0:
			response = jsonify(error="Invalid id. The picid does not exist.", status=422)
			response.status_code = 422
			return response

		# checks if username exists
		cursor.execute('''SELECT * FROM user WHERE username="%s"''' % username)
		namedata = cursor.fetchall()
		if len(namedata) == 0:
			response = jsonify(error="Invalid username. The username does not exist.", status=422)
			response.status_code = 422
			return response

		#checks if user already favorited photo
		cursor.execute('''SELECT * FROM Favorite where username = "%s" AND picid = "%s"''' % (username, picid))
		userdata = cursor.fetchall()
		if len(userdata) > 0:
			response = jsonify(error="The user has already favorited this photo.", status=403)
			response.status_code = 403
			return response
		
		response = jsonify(id=picid, status=201)
		response.status_code = 201
		date = datetime.now()
		# remove microsec
		date = str(date).split(".")[0]
		# datestr = datetime.now().date().isoformat()
		query = '''INSERT INTO Favorite (picid, username, date) VALUES("%s", "%s", "%s")''' % (picid, username, date)
		print query
		cursor.execute(query)
		db.commit()
		return response
