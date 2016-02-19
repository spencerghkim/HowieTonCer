from functools import wraps
from flask import *
from shared import *
from datetime import *
import os

albums_edit = Blueprint('albums_edit', __name__, template_folder='views')

@albums_edit.route('/albums/edit', methods=['GET', 'POST'])
def albums_edit_route():
	
	# db connection
	if platform.system() == 'Darwin':
		db = MySQLdb.connect(host="localhost", user="root", passwd="hmcc", db="group108pa3")
	else:
		db = MySQLdb.connect(host="localhost", user="group108", passwd="hmcc", db="group108pa3")
	cursor = db.cursor(MySQLdb.cursors.DictCursor)

	# Nice to have: Return 404 if albumid does not exist



	if request.method == 'POST':
		if 'username' not in session:
			return render_template("please_login.html", path=request.url)

		if request.form.get('op') == "Delete" : #DELETE REQUEST
			albumid = request.form.get('albumid')
			shared.delete_album_by_albumid(albumid)
		else : # op == "Add"
			title = request.form.get('title')
			access = request.form.get('xcess')
			if title != "" and (access == "private" or access == "public" or access == "Private" or access == "Public"):
				date = datetime.now().date()
				# Find next album_id 
				cursor.execute('''SELECT MAX(albumid) AS max_albumid FROM album''')
				current_max_albumid = cursor.fetchall()
				if current_max_albumid[0]["max_albumid"] is None:
					next_album_id = 1
				else:
					next_album_id = current_max_albumid[0]["max_albumid"] + 1

				cursor.execute('''INSERT INTO album VALUES ("%d", "%s", "%s", "%s", "%s", "%s")''' % (next_album_id, title, date, date, session['username'], access))
				db.commit()
			else:
				# some field is not correct - redirect to same page 
				# Nice to have: give error message
				print "Some field is not correct"

		return redirect(url_for("albums_edit.albums_edit_route"))

	else: # GET
		if 'username' in session:
			cursor.execute('''SELECT * FROM album WHERE username="%s"''' % session['username'])
			personal_albums = cursor.fetchall()

			options = {
				"edit": True,
				"session_username": session['username'],
				"personal_albums": personal_albums,
				"loggedin": True
			}
			return render_template("albums.html", **options)
		else :
			#user not in session
			return render_template("please_login.html", path=request.url)

	return render_template("404.html")
