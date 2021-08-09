from flask import Flask, render_template, url_for, flash, redirect, request
from forms import RegistrationForm, AdminLogin, ContactRequestForm
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy
from audio_file import printWAV
import time, random, threading
from turbo_flask import Turbo
from flask_login import login_user, current_user, logout_user, login_required, LoginManager, UserMixin
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

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

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(username):
   return User.query.get(username)


class visitors_to_contact(db.Model, UserMixin):
  firstName = db.Column(db.String(20), unique=False, nullable=False)
  lastName = db.Column(db.String(20), unique=False, nullable=False)
  email = db.Column(db.String(120), primary_key=True, nullable=False)
  phoneNumber = db.Column(db.Integer, nullable=False)

  def __repr__(self):
    return f"VisitorsToContact('{self.firstName}', '{self.lastName}', '{self.email}', '{self.phoneNumber}')"
  
class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(60), nullable=False)

  def __repr__(self):
    return f"User('{self.id}', '{self.username}', '{self.email}', '{self.password}')"


#db.create_all()
#the instruction below is used to add new table to an existing database  
#visitors_to_contact.__table__.create(db.session.bind)
  
@app.route("/", methods=['GET', 'POST']) # this tells you the URL the method below is related to
#@app.route("/home")
def home():
    return render_template('home.html', subtitle='Hello, I\'m Jesse and this is my website')


@app.route("/about", methods=['GET', 'POST'])
def about():
    TITLE = "GOD HAS A PLAN FOR YOU (Chadwick Boseman)"
    return render_template('about.html', subtitle='About', text='This is the about me page', songName=TITLE, file=FILE_NAME)

@app.route("/resume")
def resume():
    return render_template('resume.html', subtitle='Resume', text='This is the resume page')

@app.route("/requestforcontactpage", methods=['GET', 'POST'])
def requestforcontact():
    form = ContactRequestForm()
    if form.validate_on_submit(): # checks if entries are valid
        visitors = visitors_to_contact(firstName=form.firstName.data, lastName=form.lastName.data, email=form.email.data, phoneNumber=form.phoneNumber.data)
        db.session.add(visitors)
        try:
          db.session.commit()
        except Exception  as e:
          flash(f'Your request for contact is already submitted.', e)
        else:
          flash(f'Your request was submitted {form.firstName.data}!', 'success')
        finally:
          return redirect(url_for('home')) # if so - send to home page
    return render_template('requestforcontactpage.html', title='Request For Contact', form=form)
  
@app.route("/addWebAdmin", methods=['GET', 'POST'])
@login_required
def addWebAdmin():
    form = RegistrationForm()
    if form.validate_on_submit(): # checks if entries are valid
        pw_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=pw_hash)
        db.session.add(user)
        try:
          db.session.commit()
        except Exception:
          flash(f'Try a different credential.')
        else:
          flash(f'Account created for {form.username.data}!', 'success')
        finally:
          return redirect(url_for('home')) # if so - send to home page
    return render_template('addAdmin.html', title='Add Administrator', form=form)

#add the ability to add new authorized users when the current user is logged in @login_required
  
@app.route("/webAdminPage", methods=['GET', 'POST'])
@login_required
def webadminpage():
  return render_template('webAdminPage.html', admins=User.query.all(), visitors=visitors_to_contact.query.all())
  
@app.route("/webadmin", methods=['GET', 'POST'])
def webadminLogin():
    form = AdminLogin()
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
      
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if not user or not bcrypt.check_password_hash(user.password, password):
          flash('Please check your login details and try again.')
          return redirect(url_for('webadminLogin'))
        login_user(user)
        flash('Logged in successfully!')
        return redirect(url_for('webadminpage'))

    return render_template('webadmin.html', form=form)
  
@app.route("/webadminLogout")
def webadminLogout():
  return 'Logout'
  
#@app.route("/captions")
#def captions():
#    TITLE = "GOD HAS A PLAN FOR YOU"
#    return render_template('captions.html', songName=TITLE, file=FILE_NAME)

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