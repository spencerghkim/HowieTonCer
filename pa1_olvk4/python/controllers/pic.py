
from flask import *
import MySQLdb, platform

pic = Blueprint('pic', __name__, template_folder='views')

@pic.route('/olvk4/pa1/pic')
def pic_route():
	picid = request.args.get('id')
	if platform.system() == 'Darwin':
		db = MySQLdb.connect(host="localhost", user="root", passwd="hmcc", db="group108")
	else:
		db = MySQLdb.connect(host="localhost", user="group108", passwd="hmcc", db="group108")
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	
	if picid is not None:
		cursor.execute('''SELECT * FROM photo where picid = "%s"''' % picid)
		picdata = cursor.fetchall()
		if len(picdata) != 0:
			
			cursor.execute('''SELECT picid FROM contain WHERE sequencenum = (SELECT MIN(C.sequencenum) FROM contain C where C.albumid = (SELECT albumid FROM contain WHERE picid="%s") AND C.sequencenum > (SELECT sequencenum FROM contain WHERE picid="%s"));''' %(picdata[0]['picid'], picdata[0]['picid']))
			nextdata = cursor.fetchall()

			if nextdata:
				nextid = nextdata[0]["picid"]
				nextflag = 1
			else:
				nextid = 0
				nextflag = 0

			cursor.execute('''SELECT picid FROM contain WHERE sequencenum = (SELECT MAX(C.sequencenum) FROM contain C where C.albumid = (SELECT albumid FROM contain WHERE picid="%s") AND C.sequencenum < (SELECT sequencenum FROM contain WHERE picid="%s"));''' %(picdata[0]['picid'], picdata[0]['picid']))
			prevdata = cursor.fetchall()

			if prevdata:
				previd = prevdata[0]["picid"]
				prevflag = 1
			else:
				previd = 0
				prevflag = 0

			options = {
				"url": picdata[0]["url"],
				"picid": picdata[0]["picid"],
				"nextid": nextid,
				"nextflag": nextflag,
				"previd": previd,
				"prevflag": prevflag
			}

			cursor.execute('''SELECT albumid from contain where picid="%s";''' % picdata[0]["picid"])
			albumidset = cursor.fetchall()
			return render_template("pic.html", albumid = albumidset[0]["albumid"], **options)

	# something failed
	print "ERROR: Invalid picid"
	return render_template("404.html")

