import platform, MySQLdb, os

class Shared:
	def __init__(self):
		# print("Init shared")
		a=1


	def get_db_connection(self):
		if platform.system() == 'Darwin':
			db = MySQLdb.connect(host="localhost", user="root", passwd="hmcc", db="group108pa2")
		else:
			db = MySQLdb.connect(host="localhost", user="group108", passwd="hmcc", db="group108pa2")
		cursor = db.cursor(MySQLdb.cursors.DictCursor)
		return db, cursor
	
	def execute_and_fetch_query(self, query):
		if platform.system() == 'Darwin':
			db = MySQLdb.connect(host="localhost", user="root", passwd="hmcc", db="group108pa2")
		else:
			db = MySQLdb.connect(host="localhost", user="group108", passwd="hmcc", db="group108pa2")
		cursor = db.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute(query)
		result = cursor.fetchall()
		return result

	def execute_and_commit_query(self, query):
		if platform.system() == 'Darwin':
			db = MySQLdb.connect(host="localhost", user="root", passwd="hmcc", db="group108pa2")
		else:
			db = MySQLdb.connect(host="localhost", user="group108", passwd="hmcc", db="group108pa2")
		cursor = db.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute(query)
		db.commit()

	def delete_album_by_albumid(self, albumid):
		if platform.system() == 'Darwin':
			db = MySQLdb.connect(host="localhost", user="root", passwd="hmcc", db="group108pa2")
		else:
			db = MySQLdb.connect(host="localhost", user="group108", passwd="hmcc", db="group108pa2")
		cursor = db.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('''SELECT picid FROM contain WHERE albumid="%s"''' % albumid)
		picids = cursor.fetchall()
		# delete all contain tuples that associate with the albumid
		cursor.execute('''DELETE FROM contain WHERE albumid="%s"''' % albumid)

		# Delete all AlbumAccess tuples that associate with the albumid
		cursor.execute('''DELETE FROM albumaccess WHERE albumid = "%s"''' % albumid)

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

	# very basic encryption function: reverse the string
	def encrypt(self, input):
		return input[::-1]

shared = Shared()
