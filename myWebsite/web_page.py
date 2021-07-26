from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy
from audio_file import printWAV
import time, random, threading
from turbo_flask import Turbo


# import secrets, then type secrets.token_hex(16) in a
# python interpreter to get a secret key (hint: type python3 in the terminal)

app = Flask(__name__)                    # this gets the name of the file so Flask knows it's name
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = '6e11de6809085499d0b65a8a00aeabc4'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

pos = 0
interval=10
FILE_NAME = "GOD HAS A PLAN FOR YOU _ Chadwick Boseman - Inspirational & Motivational Speech.wav"
turbo = Turbo(app)


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(60), nullable=False)

  def __repr__(self):
    return f"User('{self.username}', '{self.email}')"

@app.route("/") # this tells you the URL the method below is related to
#@app.route("/home")
def home():
    return render_template('home.html', subtitle='Hello, I\'m Jesse and this is my website', text='This is the home page')


@app.route("/about")
def about():
    return render_template('about.html', subtitle='About', text='This is the about me page')

@app.route("/resume")
def resume():
    return render_template('resume.html', subtitle='Resume', text='This is the resume page')


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    form = RegistrationForm()
    if form.validate_on_submit(): # checks if entries are valid
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home')) # if so - send to home page
    return render_template('contact.html', title='Contact', form=form)


@app.route("/captions")
def captions():
    TITLE = "GOD HAS A PLAN FOR YOU"
    return render_template('captions.html', songName=TITLE, file=FILE_NAME)

@app.before_first_request
def before_first_request():
    #resetting time stamp file to 0
    file = open("pos.txt","w") 
    file.write(str(0))
    file.close()

    #starting thread that will time updates
    threading.Thread(target=update_captions, daemon=True).start()
  
@app.context_processor
def inject_load():
    # getting previous time stamp
    file = open("pos.txt","r")
    pos = int(file.read())
    file.close()

    # writing next time stamp
    file = open("pos.txt","w")
    file.write(str(pos+interval))
    file.close()

    #returning captions
    return {'caption':printWAV(FILE_NAME, pos=pos, clip=interval)}

def update_captions():
    with app.app_context():
        while True:
            # timing thread waiting for the interval
            time.sleep(interval)

            # forcefully updating captionsPane with caption
            turbo.push(turbo.replace(render_template('captionsPane.html'), 'load')) 
  

#def hello_world():
    #return "<p>Hello, World!</p>"        # this prints HTML to the webpage
  
if __name__ == '__main__':               # this should always be at the end
    app.run(debug=True, host="0.0.0.0")