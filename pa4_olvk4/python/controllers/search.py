import requests
from flask import *
from shared import *
import MySQLdb, platform
# import json

search = Blueprint('search', __name__, template_folder='views')

@search.route('/search', methods=['GET', 'POST'])
def search_route():

	# Receive query
	if request.method == 'POST':
		query = request.form.get('query')
		return redirect(url_for("search.search_route", q=query));
	else:
		query = request.args.get('q')

	# Convert query to ids
	if query is not None:
		print "Query: " + query
		result = requests.get('http://localhost:4000/olvk4/pa4/search?q=' + query);
		print "result: " + result.text
		hits = result.json().get("hits")
	else :
		options = {
			"queried": False
		}
		return render_template("search.html", **options)


	# db connection
	if platform.system() == 'Darwin':
		db = MySQLdb.connect(host="localhost", user="root", passwd="hmcc", db="group108")
	else:
		db = MySQLdb.connect(host="localhost", user="group108", passwd="hmcc", db="group108pa3")
	cursor = db.cursor(MySQLdb.cursors.DictCursor)

	# get data for each id in the hits
	if hits is not None: 
		cursor.execute('''SELECT * FROM search_photos where sequencenum = "%s"''' % hits[0]["id"])
		searchpicdata = cursor.fetchall()

		for i in range(1, len(hits)) :
			cursor.execute('''SELECT * FROM search_photos where sequencenum = "%s"''' % hits[i]["id"])
			searchpicdata += cursor.fetchall()

		if searchpicdata is not None:
			queried = True

			options = {
				"num_hits": len(hits),
				"query": query,
				"queried": queried,
				"queried_data": searchpicdata
			}
		else :
			options = {
				"queried": queried,
				"no_result": True
			}

		return render_template('search.html', **options)

	return render_template('search.html')




