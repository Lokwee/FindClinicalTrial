from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL, MySQLdb
from flaskext.mysql import MySQL

myapp = Flask(__name__)
# myapp.secret_key= 'secret'

myapp.config['MYSQL_DATABASE_USER'] = 'b370f35fcbd089'
myapp.config['MYSQL_DATABASE_PASSWORD'] = '75e4c0cb'
myapp.config['MYSQL_DATABASE_DB'] = 'heroku_638c08cf00f0d78'
myapp.config['MYSQL_DATABASE_HOST'] = 'us-cdbr-east-03.cleardb.com'

# my_sql = MySQL(myapp)
my_sql = MySQL()
my_sql.init_app(myapp)


@myapp.route("/")
def index():
  return render_template("index.html")

@myapp.route("/ajaxlivesearch", methods=["POST","GET"])
def ajaxlivesearch():
  mycursor = my_sql.get_db().cursor()
  if request.method == 'POST':
    search_word = request.form.get('query')
    if search_word == '':
      query = "SELECT * from GeneticDisorders ORDER BY Names"
      mycursor.execute(query)
      numrows = int(mycursor.rowcount)
      trial = mycursor.fetchall()
    else:
      query = "SELECT * from GeneticDisorders WHERE Names or Conditions LIKE '%{}%' ORDER BY Names DESC LIMIT 20".format(search_word)
      mycursor.execute(query)
      numrows = int(mycursor.rowcount)
      trial = mycursor.fetchall()
  # return(jsonify(trial))
  return jsonify({'htmlresponse':render_template("response.html", trial=trial, numrows=numrows)})
  

if __name__ == "__main__":
  myapp.run()