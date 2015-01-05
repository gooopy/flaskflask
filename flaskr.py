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
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	g.db.close()

@app.route('/')
def show_entries():
	cur = g.db.execute('select id, title, text from entries order by id desc')
	entries = [dict(id=row[0], title=row[1], text=row[2]) for row in cur.fetchall()]
	return render_template('show_entries.html', entries=entries)

@app.route('/add', methods = ['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	g.db.execute('insert into entries (title, text) values (?, ?)',
					[request.form['title'], request.form['text']])
	g.db.commit()
	flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))

# modify function
@app.route('/modify_success', methods = ['POST'])
def modify_success():
	if not session.get('logged_in'):
		abort(401)
	g.db.execute('UPDATE entries SET title=? WHERE id=?', [request.form['title'], request.form['id']])
	g.db.execute('UPDATE entries SET text=? WHERE id=?', [request.form['text'], request.form['id']])
	g.db.commit()
	flash('This Entry was successfully modified')
	flash(request.form['id'])
	return redirect(url_for('show_entries'))

@app.route('/modify_entry', methods = ['POST'])
def modify_entry():
	if not session.get('logged_in'):
		abort(401)
	return render_template('modify.html', title=request.form['title'], text=request.form['text'], id=request.form['id'])


@app.route('/delete_entry', methods = ['POST'])
def delete_entry():
	if not session.get('logged_in'):
		abort(401)
	g.db.execute('DELETE FROM entries WHERE id=?', [request.form['id']])
	g.db.commit()
	flash('This Entry was successfully deleted')
	return redirect(url_for('show_entries'))


@app.route('/login', methods = ['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_entries'))
	return render_template('login.html', error=error)



@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))


#@app.route('')
if __name__ == '__main__':
	app.run()