from flask import Flask,render_template,request,redirect,url_for,session
import mysql.connector

conn=mysql.connector.connect(host='localhost',name='root',password='',database='user')
cursor=conn.cursor

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('paras.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
    return render_template('signup.html')
    
@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run()
