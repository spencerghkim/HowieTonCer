from flask import Flask

app = Flask(__name__, template_folder='views')
# mysql = MySQL()
# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = ''
# app.config['MYSQL_DATABASE_DB'] = 'group108'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# app.config.from_object('config')
# mysql = MySQL(app)

UPLOAD_FOLDER = '/static/pictures/'
app.config['UPLOAD FOLDER'] = UPLOAD_FOLDER

# mysql.init_app(app)
# cursor = mysql.connect().cursor()

# from app import 

# from app import views