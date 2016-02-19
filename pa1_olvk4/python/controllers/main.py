
from flask import *
import MySQLdb, platform

main = Blueprint('main', __name__, template_folder='views')

@main.route('/olvk4/pa1/')
def main_route():
	username = request.args.get('username')
	if platform.system() == 'Darwin':
		db = MySQLdb.connect(host="localhost", user="root", passwd="hmcc", db="group108")
	else:
		db = MySQLdb.connect(host="localhost", user="group108", passwd="hmcc", db="group108")
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	if username is None:
		# query list of users from db
		cursor.execute('''SELECT username FROM user''')
		users = cursor.fetchall()

		return render_template('index.html', users=users, loggedin=0)
	else:		
		# check if username exists
		cursor.execute('''select username from user where username = "%s"''' % username)
		result = cursor.fetchall()
		if len(result) == 0:
			# 404 if invalid username
			print "ERROR: Invalid Username"
			return render_template("404.html")			
		return render_template('index.html', username=username, loggedin=1)
