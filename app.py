import flask
from flask import Flask, Response, request, render_template, redirect, url_for, flash
from flaskext.mysql import MySQL
import flask_login
import time
from werkzeug.utils import secure_filename

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'cs460'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Salo5561!'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		first_name=request.form.get('first_name')
		last_name=request.form.get('last_name')
		dob=request.form.get('dob')
		hometown=request.form.get('hometown')
		gender=request.form.get('gender')
	except:
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Users (email, password, first_name, last_name, dob, hometown, gender) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(email, password, first_name, last_name, dob, hometown, gender)))
		conn.commit()
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() 

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		return False
	else:
		return True

@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		tags = request.form.get('tag')
		album_name = request.form.get('album_name')
		photo_data =imgfile.read()
		cursor = conn.cursor()
		
		cursor.execute("SELECT album_name FROM Albums WHERE user_id = '{0}'".format(uid))
		albums = cursor.fetchall()
		album_exists = False
		for i in range(len(albums)):
			if album_name == str(albums[i][0]):
				album_exists = True
		if album_exists == False:
			return render_template('hello.html', message='Album does not exist yet.')
		cursor.execute("SELECT album_id FROM Albums WHERE user_id = '{0}' AND album_name = '{1}'".format(uid, album_name))
		album_id = cursor.fetchone()[0]
		cursor.execute('''INSERT INTO Pictures (imgdata, user_id, caption, album_id) VALUES (%s, %s, %s, %s)''', (photo_data, uid, caption, album_id))
		conn.commit()
		
		pic_id = cursor.lastrowid

		tags = tags.split()
		num_tag = len(tags) - 1 
		cursor = conn.cursor()

		while num_tag >= 0:
			cursor.execute("INSERT INTO Tags(tag) VALUES ('{0}')".format(tags[num_tag]))
			conn.commit()
			tag_id = cursor.lastrowid
			cursor.execute("INSERT INTO Tagged_With(picture_id, tag_id) VALUES ('{0}', '{1}')".format(pic_id, tag_id))
			conn.commit()
			num_tag -= 1
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid), base64=base64)
	else:
		return render_template('upload.html')

@app.route('/create_album', methods=['GET', 'POST'])
def createAlbum():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		name = request.form.get('album_name')
		date = time.strftime('%Y-%m-%d')
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Albums(album_name, user_id, album_date) VALUES ('{0}','{1}','{2}')".format(name, uid, date))
		conn.commit()
		return render_template('hello.html', message='Your album has been created!')
	return render_template('create_album.html')

def mostRecentUserPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT P.imgdata, P.picture_id, P.caption, U.first_name, U.last_name, P.user_id FROM Pictures P, Users U WHERE P.user_id = U.user_id AND P.user_id = '{0}' ORDER BY P.picture_id DESC".format(uid))
	return cursor.fetchall()

@app.route('/display_pictures', methods=['GET', 'POST'])
def displayUserPhotos():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		photo_id = request.form.get('picture_id')
		deletePicture(photo_id)
		return render_template('display_pictures.html', name=flask_login.current_user.id, user= uid,message='Your photos', photos=mostRecentUserPhotos(uid), base64=base64)
	return render_template('display_pictures.html', name=flask_login.current_user.id, user= uid,message='Your photos', photos=mostRecentUserPhotos(uid), base64=base64)

def getUsersAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id, album_name, album_date FROM Albums WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall()

def getAlbumsPhotos(album_id):
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id, imgdata, caption FROM Pictures WHERE album_id = '{0}'".format(album_id))
	return cursor.fetchall() 

@app.route('/viewalbums', methods = ['GET']) 
@flask_login.login_required
def view_albums():
	uid =  getUserIdFromEmail(flask_login.current_user.id)
	myAlbums = getUsersAlbums(uid) 
	return render_template("albums.html", message="Here are all of your albums", name=flask_login.current_user.id, albums=myAlbums)

@app.route('/viewalbums/<album_id>', methods = ['GET']) # album_id here is album[0] in albums.html
@flask_login.login_required
def view_photos_in_album(album_id):
	myPhotos = getAlbumsPhotos(album_id)
	return render_template("photos.html", message="Photos in this album", albumid=album_id, photos=myPhotos, base64=base64)

@app.route('/deletealbum/<album_id>')
@flask_login.login_required
def delete_album(album_id):
	uid =  getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Albums WHERE album_id =('{0}')".format(album_id))
	conn.commit()
	myAlbums = getUsersAlbums(uid)
	return render_template("albums.html", message="Album deleted", albums=myAlbums)

@app.route('/deletephoto/<album_id>/<photo_id>')
@flask_login.login_required
def delete_photo(album_id, photo_id):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Tagged_With WHERE picture_id ='{0}'".format(photo_id))
	cursor.execute("DELETE FROM Pictures WHERE picture_id ='{0}'".format(photo_id))
	conn.commit()
	myPhotos = getAlbumsPhotos(album_id)
	return render_template("photos.html", message="Photo deleted", photos=myPhotos, albumid=album_id)

# FRIENDS #
def getEmailfromUid(uid):
	cursor = conn.cursor()
	if cursor.execute ("SELECT email FROM Users WHERE user_id = '{0}'".format(uid)):
		return False
	else:
		return True		# query to display friends

def getUserNameFromId(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT first_name, last_name FROM Users WHERE user_id = '{0}'".format(user_id))
	return cursor.fetchone()[0] # query to search friends

def getUsersFriends(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Friends WHERE friend_id = '{0}'".format(uid))
	return cursor.fetchall() # query to add frineds

def AddFriend(uid, friend_id):
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Friends (user_id, friend_id) VALUES ('{0}', '{1}')".format(uid, friend_id))
	conn.commit()	#add to friends table

@app.route('/friends', methods = ['GET'])
@flask_login.login_required
def friends():
	uid = getUserIdFromEmail(flask_login.current_user.id) #getting email
	cursor = conn.cursor()
	cursor.execute("SELECT friend_id FROM Friends WHERE user_id = '{0}'".format(uid)) #find friends relationship
	friends = cursor.fetchall() 
	f_name = []
	for i in friends: 
		f_name.append(getUserNameFromId(i[0])) #get names for each friend
	return render_template("friends.html", name=flask_login.current_user.id, friends=f_name)

@app.route('/search_add', methods = ['GET']) 
@flask_login.login_required
def find_friend():
	return render_template('search_add.html', name=flask_login.current_user.id)

@app.route('/search_add', methods = ['POST']) 
@flask_login.login_required
def search():
	if request.method == 'POST':
		email = request.form.get('?')
		cursor = conn.cursor()
		cursor.execute("SELECT user_id, first_name, last_name from Users WHERE email = '{0}'".format(email))
		results = cursor.fetchall()
		return render_template("search_add.html", name=flask_login.current_user.id, results = results)

@app.route('/addfriends/<uid_friend>')
@flask_login.login_required
def add_friend(uid_friend):
	uid =  getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Friends (user_id, friend_id) VALUES ('{0}', '{1}')".format(uid, uid_friend))
	conn.commit()
	friends = getUsersFriends(uid)
	fname = []
	for i in friends:
		fname.append(getUserNameFromId(i[0]))
	return render_template("friends.html", message="New friend added", friends=fname)

# TAGS #

def getTagName(tag):
	cursor = conn.cursor()
	cursor.execute("""SELECT DISTINCT t.tag
						FROM Pictures AS p, Tags AS t, Tagged_With AS w
						WHERE t.tag_id = w.tag_id 
						AND w.picture_id = p.picture_id""".format(tag))
	result = cursor.fetchall()
	return result

def getTaggedPhotos(tag):
	cursor = conn.cursor()
	cursor.execute("""SELECT DISTINCT p.imgdata, p.picture_id, t.tag_id
						FROM Pictures AS p, Tags AS t, Tagged_With AS w
						WHERE t.tag_id = w.tag_id 
						AND p.picture_id = w.picture_id""".format(tag))
	result = cursor.fetchall()
	return result
    	
def getUsersTaggedPhotos(tag):
	cursor = conn.cursor()
	cursor.execute("""SELECT DISTINCT p.imgdata, p.picture_id, t.tag_id
					FROM Tags AS t, Tagged_With AS w, Pictures AS p  
					WHERE t.tag_id = w.tag_id
					and w.picture_id = p.picture_id""".format(tag))
	return cursor.fetchall()

@app.route('/tags_and_likes', methods=['GET', 'POST'])
def taggedPhotos():
	tag = request.form.get('tag')
	myPhotos = getTaggedPhotos(tag)
	tags = getTagName(tag)
	return render_template('tags.html', photos=myPhotos, tags = tags, base64=base64)  			

@app.route('/usertags', methods=['GET', 'POST'])
@flask_login.login_required
def usersTaggedPhotos():
	tag = request.form.get('tag_id')
	photos = getUsersTaggedPhotos(tag)
	tags = getTagName(tag)
	return render_template('usertags.html', photos=photos, tags = tags, base64=base64) 

# COMMENTS #

def getComments(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT comment_id, user_id, picture_id, test, comment_date FROM Comments WHERE picture_id = '{0}'".format(photo_id))
	return cursor.fetchall() 

def getUserIdFromPhotoId(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Pictures WHERE picture_id = '{0}'".format(photo_id))
	return cursor.fetchone()[0]

@app.route('/makecomments/<album_id>/<photo_id>', methods = ['GET'])
def comment(album_id, photo_id):
	return render_template("makecomment.html", message="Create a comment here", albumid=album_id, photoid=photo_id)

@app.route('/makecomments/<album_id>/<photo_id>', methods = ['POST'])
def make_new_comment(album_id, photo_id):
	txt = request.form.get("test")
	date = request.form.get("comment_date")
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Comments(user_id, picture_id, test, comment_date) VALUES ('{0}', '{1}', '{2}', '{3}')".format(uid, photo_id, txt, date))
	conn.commit()
	comments = getComments(photo_id) 
	myComments = []
	return render_template("comments.html", message="Comment created", albumid=album_id, photoid=photo_id, comments=myComments)

@app.route('/viewcomments/<album_id>/<photo_id>', methods = ['GET'])
def see_com(album_id, photo_id):
	comments = getComments(photo_id)
	myComments = []
	uid = getUserIdFromEmail(flask_login.current_user.id)
	photo_uid = getUserIdFromPhotoId(photo_id)
	return render_template("comments.html", message="Here are the comments for this photo", albumid=album_id, photoid=photo_id, comments=myComments)
	
# LIKES #

def getPhotosLikes(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id, picture_id FROM Likes WHERE picture_id = '{0}'".format(photo_id))
	return cursor.fetchall() 

@app.route('/viewlikes/<album_id>/<photo_id>', methods = ['GET'])
@flask_login.login_required
def see_likes(album_id, photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(user_id) FROM Likes WHERE picture_id = '{0}'".format(photo_id))
	count = cursor.fetchone()[0]
	myLikes = getPhotosLikes(photo_id) 
	user = []
	for i in myLikes:
		user.append(getUserNameFromId(i[0])) 
	return render_template("likes.html", message="Here are the likes for this photo", albumid=album_id, photoid=photo_id, user_name=user, numberoflikes=count)

@app.route('/makelikes/<album_id>/<photo_id>', methods = ['POST'])
@flask_login.login_required
def make_new_like(album_id, photo_id):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if hasAlreadyLiked(photo_id, uid) == False:
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Likes(user_id, picture_id) VALUES ('{0}', '{1}')".format(uid, photo_id))
		conn.commit()
		myLikes = getPhotosLikes(photo_id)
		numberoflikes = len(myLikes) 
		user_name = []
		for i in myLikes:
			user_name.append(getUserNameFromId(i[0]))
		return render_template("likes.html", message="like created", albumid=album_id, photoid=photo_id, user_name=user_name, num_likes=numberoflikes)

	else:
		return render_template("likes.html", message="Has already like this photo", albumid=album_id, photoid=photo_id)

def hasAlreadyLiked(photo_id, user_id):
	cursor = conn.cursor()
	if cursor.execute("SELECT picture_id, user_id FROM Likes WHERE picture_id = '{0}' AND user_id = '{1}'".format(photo_id, user_id)):
		return True
	else:
		return False

# YOU MAY ALSO LIKE #
@app.route('/youmayalsolike')
@flask_login.login_required
def you_may_also_like():
	uid =  getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT DISTINCT tag_id, COUNT(picture_id) From Tagged_With NATURAL JOIN Pictures WHERE user_id = '{0}' GROUP BY tag_id ORDER BY COUNT(picture_id) DESC LIMIT 5".format(uid))
	tags = cursor.fetchall() 
	return render_template("youmayalsolike.html", message="You may also like", like = tags)

# RECOMMENDATIONS #
@app.route('/friend_recommendation')
@flask_login.login_required
def friend_recommendation():
	uid =  getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users".format(uid))
	recommended = cursor.fetchall()
	return render_template("friend_recommendation.html", recommendation = recommended)

#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare')

if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)