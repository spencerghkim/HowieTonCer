from flask import *
import MySQLdb, platform, random, string
from datetime import *
from werkzeug import secure_filename
import os

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'bmp', 'gif'])
UPLOAD_FOLDER = 'pictures'

def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

album = Blueprint('album', __name__, template_folder='views')

@album.route('/olvk4/pa1/album/edit', methods=['GET', 'POST'])
def album_edit_route():
	# sql db connection based on OS
	if platform.system() == 'Darwin':
		db = MySQLdb.connect(host="localhost", user="root", passwd="hmcc", db="group108")
	else:
		db = MySQLdb.connect(host="localhost", user="group108", passwd="hmcc", db="group108")
	cursor = db.cursor(MySQLdb.cursors.DictCursor)

	albumid = request.args.get('id')

	cursor.execute('''SELECT title, username FROM album WHERE albumid="%s"''' % albumid)
	album_result = cursor.fetchall()

	if len(album_result) == 0:
		# error
		print "ERROR: Invalid albumid"
		return render_template("404.html")

	album_title = album_result[0]["title"]
	username = album_result[0]["username"]

	if request.method == 'POST':
		op = request.form.get('op')

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
			else:
				print "Error: picid " + picid + " does not exist"
		
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
					cursor.execute('''UPDATE album SET lastupdated="%s" WHERE albumid="%s"''' % (datestr, albumid))
					db.commit()

					# write contents of file to disk
					fout = open(url2,'w') 
					fout.write(file.read()) 
					fout.close() 
			
		# show page in every POST request
		# TODO: Better redirect upon finishing POST request
		cursor.execute('''SELECT * FROM photo P, contain C WHERE C.albumid = "%s" AND P.picid = C.picid ORDER BY C.sequencenum''' % albumid)
		pictures = cursor.fetchall()
		options = {
			"album_title": album_title,
			"albumid": albumid,
			"edit": True,
			"pictures": pictures,
			"username": username
		}
		return render_template("album.html", **options)
	
	else: # GET
		albumid = request.args.get('id')

		cursor.execute('''SELECT title, username FROM album WHERE albumid="%s"''' % albumid)
		album_result = cursor.fetchall()
		album_title = album_result[0]["title"]
		username = album_result[0]["username"]

		if albumid is not None:
			
			cursor = db.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('''SELECT * FROM photo P, contain C WHERE C.albumid = "%s" AND P.picid = C.picid ORDER BY C.sequencenum''' % albumid)
			pictures = cursor.fetchall()

			if len(albumid) != 0:
				options = {
					"album_title": album_title,
					"albumid": albumid,
					"edit": True,
					"pictures": pictures,
					"username": username
				}
				return render_template("album.html", **options)

		# error
		print "ERROR: Invalid albumid"
		return render_template("404.html")		

@album.route('/olvk4/pa1/album')
def album_route():
	albumid= request.args.get('id')
	
	if albumid is not None:
		if platform.system() == 'Darwin':
			db = MySQLdb.connect(host="localhost", user="root", passwd="hmcc", db="group108")
		else:
			db = MySQLdb.connect(host="localhost", user="group108", passwd="hmcc", db="group108")
		cursor = db.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('''SELECT * FROM photo P, contain C WHERE C.albumid = "%s" AND P.picid = C.picid ORDER BY C.sequencenum''' % albumid)
		pictures = cursor.fetchall()

		cursor.execute('''SELECT title, username FROM album WHERE albumid="%s"''' % albumid)
		album_result = cursor.fetchall()

		if len(album_result) != 0:
			album_title = album_result[0]["title"]
			username = album_result[0]["username"]
			options = {
				"album_title": album_title,
				"albumid": albumid,
				"edit": False,
				"username": username
			}
			return render_template("album.html", pictures=pictures, **options)

	# error
	print "ERROR: Invalid albumid"
	return render_template("404.html")

