from __future__ import with_statement
from contextlib import closing

# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
	abort, render_template, flash

#configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

#create our little application
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
	db = sqlite3.connect(app.config['DATABASE'])
	db.row_factory = sqlite3.Row
	return db

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql') as f:
			db.cursor().executescript(f.read())
		db.commit()

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def get_db():
	db = getattr(g, '_db', None)
	if db == None:
		db = g._db = connect_db()
	return db

def query_db(query, args=(), one=False):
	db = get_db()
	cur = db.execute(query, args)
	rv = cur.fetchall()
	db.commit()
	cur.close()
	return (rv[0] if rv else None) if one else rv

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, '_db', None)
	if db != None:
		db.close()

@app.route('/')
def show_entries():
	entries = query_db('select id, title, text, writer from entries order by id desc')
	return render_template('show_entries.html', entries=entries)

@app.route('/add', methods = ['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	query_db('insert into entries (title, text, writer) values (?, ?, ?)', [request.form['title'], request.form['text'], request.form['writer']])
	flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))

# modify function
@app.route('/modify_success', methods = ['POST'])
def modify_success():
	if not session.get('logged_in'):
		abort(401)
	query_db('UPDATE entries SET title=? WHERE id=?', [request.form['title'], request.form['id']])
	query_db('UPDATE entries SET text=? WHERE id=?', [request.form['text'], request.form['id']])

	flash('This Entry was successfully modified')
	flash(request.form['id'])
	return redirect(url_for('show_entries'))

@app.route('/modify_entry/<int:entry_id>')
def modify_entry(entry_id):
	if not session.get('logged_in'):
		abort(401)
	entry = query_db('select id, title, text from entries where id = ?', [entry_id], one=True)
	return render_template('modify.html', entry=entry)


@app.route('/delete_entry/<int:entry_id>')
def delete_entry(entry_id):
	if not session.get('logged_in'):
		abort(401)
	query_db('DELETE FROM entries WHERE id=?', [entry_id])

	flash('This Entry was successfully deleted')
	return redirect(url_for('show_entries'))


@app.route('/signup', methods = ['GET', 'POST'])
def signup_member():
	error = None
	if request.method == 'POST':
		if request.form['password'] != request.form['password_check']:
			error = 'Two passwords are Different'
		else:
			query_db('insert into members (userid, password, nickname) values (?, ?, ?)',
					[request.form['userid'], request.form['password'], request.form['nickname']])

			flash('WELCOME')
			return redirect(url_for('show_entries'))

	return render_template('signup.html', error=error)


@app.route('/login', methods = ['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		print request.form['userid']
		member = query_db('SELECT userid, password, nickname FROM members WHERE userid=?', [request.form['userid']], one=True)
		if member == None:
			error = 'Invalid ID'
		else:
			if request.form['password'] != member['password']:
				error = 'Invalid password'
			else:
				session['logged_in'] = True
				session['logged_id'] = member['userid']
				flash('You were logged in')
				return redirect(url_for('show_entries'))

	return render_template('login.html', error=error)


@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))

if __name__ == '__main__':
	app.run()