from functools import wraps
from flask import *
from shared import *
import MySQLdb, platform, random, string
from datetime import *
from werkzeug import secure_filename
import os

album_edit = Blueprint('album_edit', __name__, template_folder='views')

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'bmp', 'gif'])
UPLOAD_FOLDER = 'pictures'


def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@album_edit.route('/album/edit', methods=['GET', 'POST'])
def album_edit_route():
	albumid = request.args.get('id')

	if albumid is None :
		print "ERROR: Invalid albumid"
		return render_template("404.html")

	if platform.system() == 'Darwin':
		db = MySQLdb.connect(host="localhost", user="root", passwd="hmcc", db="group108pa3")
	else:
		db = MySQLdb.connect(host="localhost", user="group108", passwd="hmcc", db="group108pa3")
	cursor = db.cursor(MySQLdb.cursors.DictCursor)

	cursor.execute('''SELECT title, username, access FROM album WHERE albumid="%s"''' % albumid)
	album_result = cursor.fetchall()
	album_owner = album_result[0]["username"]
	access = album_result[0]["access"]

	# No session
	if 'username' not in session :
		return render_template("please_login.html", path=request.url)

	# Session, but not owner of album
	if session['username'] != album_owner :
		return render_template("invalid_perms.html")

# ------------------------------------------------------------------------------

	album_title = album_result[0]["title"]
	cursor.execute('''SELECT * FROM photo P, contain C WHERE C.albumid = "%s" AND P.picid = C.picid ORDER BY C.sequencenum''' % albumid)
	pictures = cursor.fetchall()

	options = {
		"access": access,
		"album_title": album_title,
		"albumid": albumid,
		"edit": True,
		"pictures": pictures,
		"album_owner": album_owner,
		"loggedin": True,
		"cannotGiveAccess": False
	}

	# USER IN SESSION AND IS Album_Owner AND albumid is good
	if request.method == 'POST': # POST
		op = request.form.get('op')

		# Delete
		if op == "Delete":
			picid = request.form.get('picid')
			cursor.execute('''SELECT * from photo where picid="%s"''' % picid)
			photodata = cursor.fetchall()
			if len(photodata) != 0:
				ext = photodata[0]['format']
				url2 = 'pictures/' + picid + '.' + ext
				try:
					os.remove(url2)
				except OSError:
					print "ERROR: File " + url2 + " doesn't exist"

				cursor.execute('''DELETE FROM contain WHERE picid="%s"''' % picid)
				cursor.execute('''DELETE FROM photo WHERE picid="%s"''' % picid)
				date = datetime.now().date()
				cursor.execute('''UPDATE album SET lastupdated="%s" WHERE albumid="%s"''' % (date, albumid))
				db.commit()
				return redirect(url_for("album_edit.album_edit_route", id=albumid))
			else:
				print "Error: picid " + picid + " does not exist"
				# Nice to have: redirect to this page
		
		# Upload
		elif op == "Upload":
			file = request.files['pic']
			if file:
				caption = request.form.get('caption')
				filename = secure_filename(file.filename)
				datestr = datetime.now().date().isoformat()
				pic_input = filename.split('.')[0]
				ext = filename.split('.')[1]

				if allowed_file(filename):

					# generate hash
					while True:
						random_hash = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
						picid = pic_input + datestr + random_hash
						cursor.execute('''SELECT picid FROM photo WHERE picid="%s"''' % picid)
						result = cursor.fetchall()
						if result is not None:
							break

					cursor.execute('''SELECT MAX(sequencenum) AS seqnum FROM contain WHERE albumid="%s"''' % albumid)
					seq_query_result = cursor.fetchall()
					if seq_query_result[0]["seqnum"] is None:
						sequencenum = 1
					else:
						sequencenum = seq_query_result[0]["seqnum"] + 1

					url = "/pictures/" + picid + "." + ext
					url2 = 'pictures/' + picid + '.' + ext

					cursor.execute('''INSERT INTO photo VALUES ("%s", "%s", "%s", "%s")''' % (picid, url, ext, datestr))
					cursor.execute('''INSERT INTO contain VALUES ("%s", "%s", "%s", "%d") ''' % (albumid, picid, caption, sequencenum))
					# update album last updated
					cursor.execute('''UPDATE album SET lastupdated="%s" WHERE albumid="%s"''' % (datestr, albumid))
					db.commit()

					# write contents of file to disk
					fout = open(url2,'w') 
					fout.write(file.read()) 
					fout.close() 
					return redirect(url_for("album_edit.album_edit_route", id=albumid))
				else:
					# Nice to have: error message
					return redirect(url_for("album_edit.album_edit_route", id=albumid))
			else:
				#Nice to have: error message for no file
				return redirect(url_for("album_edit.album_edit_route", id=albumid))

		# Give user access
		elif op == "giveUserAccess" :
			if access == 'public':
				#Nice to have: Depending on if there are errors, give error messages
				return redirect(url_for("album_edit.album_edit_route", id=albumid))

			giveUserAccess = request.form.get('newUserAccess')

			cursor.execute('''SELECT COUNT(*) AS num FROM albumaccess WHERE username = "%s" AND albumid="%s"''' %(giveUserAccess, albumid))
			userExists = cursor.fetchall()
			userExists = userExists[0]["num"]

			if userExists != 0:
				options["alreadyHasAccess"] = True
				options["usernameAE"] = giveUserAccess
				print "ERROR USER ALREADY HAS ACCESS"
			else :
				cursor.execute('''SELECT COUNT(*) AS num FROM user WHERE username = "%s"''' % giveUserAccess)
				userExists = cursor.fetchall()
				userExists = userExists[0]["num"]
				if userExists == 0:
					print "ERROR: Username does not exist"
					options["cannotGiveAccess"] = True
					options["usernameDNE"] = giveUserAccess #username Does Not Exist
				else :
					cursor.execute('''INSERT INTO albumaccess VALUES ("%s", "%s")''' % (albumid, giveUserAccess))
					# update last updated for album
					datestr = datetime.now().date().isoformat()
					cursor.execute('''UPDATE album SET lastupdated="%s" WHERE albumid="%s"''' % (datestr, albumid))
					db.commit()

			#Nice to have: Depending on if there are errors, give error messages
			return redirect(url_for("album_edit.album_edit_route", id=albumid))

		# Revoke user
		elif op == "revoke":
			revokeUser = request.form.get("revokeUser")
			cursor.execute('''DELETE from albumaccess where albumid ="%s" and username="%s"''' % (albumid, revokeUser))

			# update last updated for album
			datestr = datetime.now().date().isoformat()
			cursor.execute('''UPDATE album SET lastupdated="%s" WHERE albumid="%s"''' % (datestr, albumid))
			db.commit()

			#Nice to have: Depending on if there are errors, give error messages
			return redirect(url_for("album_edit.album_edit_route", id=albumid))

		# Change Title
		elif op == "Change Title":
			new_title = request.form.get("new_title")
			
			# update title
			cursor.execute('''UPDATE album SET title="%s" WHERE albumid="%s"''' % (new_title, albumid))

			# update last updated for album
			datestr = datetime.now().date().isoformat()
			cursor.execute('''UPDATE album SET lastupdated="%s" WHERE albumid="%s"''' % (datestr, albumid))
			db.commit()
			return redirect(url_for("album_edit.album_edit_route", id=albumid))

		# Change Permission
		elif op == "Change Permission":
			new_permission = request.form.get("new_permission")

			if new_permission != 'public' and new_permission != 'private':
				return redirect(url_for("album_edit.album_edit_route", id=albumid))

			if new_permission == access:
				#Nice to have: Depending on if there are errors, give error messages
				print "new perms are same as old perms"
				return redirect(url_for("album_edit.album_edit_route", id=albumid))

			# remove all access
			print "new_permission: " + new_permission + " and access: " + access
			if new_permission == 'public' and access == 'private':
				# Delete all AlbumAccess tuples that associate with the albumid
				print "Deleting things from AlbumAccess"
				cursor.execute('''DELETE FROM albumaccess WHERE albumid = "%s"''' % albumid)

			#update permission
			cursor.execute('''UPDATE album SET access="%s" WHERE albumid="%s"''' % (new_permission, albumid))

			# update last updated for album
			datestr = datetime.now().date().isoformat()
			cursor.execute('''UPDATE album SET lastupdated="%s" WHERE albumid="%s"''' % (datestr, albumid))
			db.commit()
			return redirect(url_for("album_edit.album_edit_route", id=albumid))

		else: # some noob gave a bad op
			print "nooblord"

	# GET request

	cursor.execute('''SELECT username FROM albumaccess WHERE albumid = "%s"''' % albumid)
	users_with_access = cursor.fetchall()
	options["users_with_access"] = users_with_access
	options["session_username"] = session['username']
	return render_template("album.html", **options)
