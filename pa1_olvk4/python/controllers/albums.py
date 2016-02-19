from flask import *
import MySQLdb, platform
from datetime import *
import os

albums = Blueprint('albums', __name__, template_folder='views')

@albums.route('/olvk4/pa1/albums/edit', methods=['GET', 'POST'])
def albums_edit_route():
	username = request.args.get('username')
	if username is None:
		# error - no username
		print "Error: Invalid username"
		return render_template("404.html")
	
	# db connection
	if platform.system() == 'Darwin':
		db = MySQLdb.connect(host="localhost", user="root", passwd="hmcc", db="group108")
	else:
		db = MySQLdb.connect(host="localhost", user="group108", passwd="hmcc", db="group108")
	cursor = db.cursor(MySQLdb.cursors.DictCursor)

	# check user exists
	cursor.execute('''SELECT * FROM user WHERE username="%s"''' % username)
	user = cursor.fetchall()
	if len(user) != 0:
		if request.method == 'POST':
			op = request.form.get('op')
			if op == "Delete":
				albumid = request.form.get('albumid')
				cursor.execute('''SELECT picid FROM contain WHERE albumid="%s"''' % albumid)
				picids = cursor.fetchall()
				# delete all contain tuples that associate with the albumid
				cursor.execute('''DELETE FROM contain WHERE albumid="%s"''' % albumid)

				# delete all photos in the album from photo table
				for item in picids:
					# remove from fs
					cursor.execute('''SELECT * from photo where picid="%s"''' % item['picid'])
					photodata = cursor.fetchall()
					if len(photodata) != 0:
						ext = photodata[0]['format']
						url2 = 'pictures/' + item['picid'] + '.' + ext
						try:
							os.remove(url2)
						except OSError:
							print "ERROR: File " + url2 + " doesn't exist"	
					else:
						print "ERROR: picid " + item['picid'] + " doesn't exist"
					# remove from db
					cursor.execute('''DELETE FROM photo WHERE picid="%s"''' % item['picid'])
				
				# delete the album from table
				cursor.execute('''DELETE FROM album WHERE albumid="%s"''' % albumid)
				db.commit()

			elif op == "Add":
				title = request.form.get('title')
				if title != "":
					date = datetime.now().date()
					# Find next album_id 
					cursor.execute('''SELECT MAX(albumid) AS max_albumid FROM album''')
					current_max_albumid = cursor.fetchall()
					if current_max_albumid[0]["max_albumid"] is None:
						next_album_id = 1
					else:
						next_album_id = current_max_albumid[0]["max_albumid"] + 1

					cursor.execute('''INSERT INTO album VALUES ("%d", "%s", "%s", "%s", "%s")''' % (next_album_id, title, date, date, username))
					db.commit()
		# end of POST

		cursor.execute('''SELECT * FROM album WHERE username="%s"''' % username)
		albumids = cursor.fetchall()

		options = {
			"edit": True,
			"username": username,
			"albumids": albumids
		}
		# TODO: better redirect upon finishing POST request
		return render_template("albums.html", **options)
	
	# error - user not in DB
	print "Error: user not in db"
	return render_template("404.html")


@albums.route('/olvk4/pa1/albums', methods=['GET'])
def albums_route():
	username = request.args.get('username')
	if username is not None:
		if platform.system() == 'Darwin':
			db = MySQLdb.connect(host="localhost", user="root", passwd="hmcc", db="group108")
		else:
			db = MySQLdb.connect(host="localhost", user="group108", passwd="hmcc", db="group108")
		cursor = db.cursor(MySQLdb.cursors.DictCursor)
		
		# check user exists
		cursor.execute('''SELECT * FROM user WHERE username="%s"''' % username)
		user = cursor.fetchall()
		if len(user) != 0:
		
			# query album info
			cursor.execute('''SELECT * FROM album WHERE username="%s"''' % username)
			albumids = cursor.fetchall()

			options = {
				"edit": False,
				"username": username,
				"albumids": albumids,
				"albumsflag": len(albumids) != 0
			}
			return render_template("albums.html", **options)

	print "Error: Invalid username"
	return render_template("404.html")
