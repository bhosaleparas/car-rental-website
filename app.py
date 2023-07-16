from flask import Flask,render_template,request,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
import MySQLdb.cursors




app = Flask(__name__)
app.config.update()

mysql=MySQL(app)

app.secret_key='parasxyz'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='user'
mysql.init_app(app)



app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:@localhost/user'
db = SQLAlchemy(app)


class Contact(db.Model):
    name = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120),nullable=True)
    msg = db.Column(db.String(120),nullable=True)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lName = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    crepassword=db.Column(db.String(100), nullable=False)

    

@app.route('/')
def home():
    return render_template('paras.html')

@app.route('/login')
def login():
    #connect
    conn=mysql.connect()
    cursor=conn.cursor(pymysql.cursors.DictCursor)
    
    #output messaege if wrong
    msg=''
    
    #cheking
    if request.method=='POST'and 'username' in request.form and 'password' in request.form:
        #creating variable
        username=request.form['username']
        password=request.form['password']
        #query
        cursor.execute("SELECT * FROM signup WHERE Email='%s' AND password='%s'",(username,password))
        #fetching
        account=cursor.fetchall()
        #if username and password is correct
        if account:
            #set session
            session['loggedin']=True
            session['id']=account['id']
            session['username']=account['username']

            return redirect(url_for('home'))
        #if username and password is wrong
        else:
            msg="Invalid username or password"
    return render_template('login.html',msg=msg)

@app.route('/index')
def index():
    #check if user is logged in 
    if 'loggedin' in session:
        return render_template('paras.html',username=session['username'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    #forgeting session
    session.pop('loggedin',None)
    session.pop('id',None)
    session.pop('username',None)
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get the form values
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Create a new Contact instance
        entry = Contact(name=name, email=email, msg=message)

        # Add the entry to the database
        db.session.add(entry)
        db.session.commit()

    return render_template('contact.html')

if __name__ == '__main__':
    app.run()




