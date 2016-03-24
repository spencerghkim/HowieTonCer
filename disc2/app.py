
from flask import Flask, render_template

app = Flask(__name__, template_folder='views')


###global variables for demo
name_1 = "Bob"
name_2 = "Alice"
age_1 = "23"
age_2 = "40"

people = [{"name":"Bob","age":23},{"name":"Alice","age":40},{"name":"Lucille","age":35},{"name":"Oscar","age":60},{"name":"Eric","age":2000}]




@app.route('/')
def homepage():
    return render_template("index.html")



@app.route('/variables')
def variables():
    return render_template("variables.html", name_1 = name_1, name_2 = name_2,
        age_1 = age_1, age_2 = age_2)


@app.route('/loops')
def loops():
    return render_template("loops.html",people = people)


@app.route('/conditionals')
def conditionals():
    return render_template("conditionals.html",people = people)


@app.route('/blocks')
def blocks():
    return render_template("blocks.html")





# comment this out using a WSGI like gunicorn
# if you dont, gunicorn will ignore it anyway
if __name__ == '__main__':
    # listen on external IPs
    app.run(host='0.0.0.0', port=3000, debug=True)
