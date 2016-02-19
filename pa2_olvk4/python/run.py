import os
import controllers
from flask import *
from datetime import *
import time

app = Flask(__name__, template_folder='views')

url_prefix_string = '/olvk4/pa2'
# number of seconds to timeout
session_timeout = 300

app.register_blueprint(controllers.album, url_prefix = url_prefix_string)
app.register_blueprint(controllers.album_edit)
app.register_blueprint(controllers.albums, url_prefix = url_prefix_string)
app.register_blueprint(controllers.albums_edit)
app.register_blueprint(controllers.pic)
app.register_blueprint(controllers.main, url_prefix = url_prefix_string)
app.register_blueprint(controllers.user, url_prefix = url_prefix_string)
app.register_blueprint(controllers.user_edit, url_prefix = url_prefix_string)

UPLOAD_FOLDER = '/static/pictures/'
app.config['UPLOAD FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(seconds=3000)

@app.before_request
def make_session_five():
	session.permanent = True
	session.modified = True
	if 'username' in session:
		lastAct = session['lastactivity']
		session['lastactivity'] = (int)(time.time())
		if session['lastactivity'] - lastAct > session_timeout:
			session.pop('username', None)
			session.pop('lastactivity', None)
			return render_template("session_expired.html", path=request.url)

# comment this out using a WSGI like gunicorn
# if you dont, gunicorn will ignore it anyway
if __name__ == '__main__':
	# listen on external IPs
	#app.secret_key = os.urandom(24)

	app.run(host='0.0.0.0', port=3000, debug=True)


