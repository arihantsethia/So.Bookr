#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import datetime
from google.appengine.ext import db
from google.appengine.api import users

class Bookmark(db.Model):
	title = db.StringProperty(required=True)
	link = db.StringProperty(required=True)
	owner = db.StringProperty(required=True)
	repo = db.StringProperty(required=True)
	
class User(db.Model):
	name = db.StringProperty(required=True)
	userid = db.StringProperty()
	
class Repo(db.Model):
	name = db.StringProperty(required=True)
	owner=db.StringProperty()
	


class MainHandler(webapp2.RequestHandler):
	def get(self):
		
		#q = Bookmark.all()
		#q.filter("owner =", "Derp")
		#self.response.out.write('aa')
		#results = q.fetch(100)
		#for p in results:
		#	self.response.out.write(p.title + ' ' + p.link + ' ' + p.owner + '<br>')
		#self.response.out.write('asdf')
		
		self.response.out.write('<h3>Repositories</h3>')
		results = Repo.all().fetch(100)
		for p in results:
			self.response.out.write('<a href="repolist?repo=' + p.name + '">' + p.name + '</a>' + '<br>')
		
		self.response.out.write('<br><br>')
		
		self.response.out.write('<h3>Users</h3>')
		results = User.all().fetch(100)
		for p in results:
			if (p.userid):
				uid=p.userid
			else:
				uid=''
			self.response.out.write('<a href="userrepos?user=' + p.name + '" >' + p.name + '</a>' + ' (<a href="https://plus.google.com/u/0/' + uid + '/">Profile</a>)<br>')
		self.response.out.write('<br/><br/><a href="new"> Add Link </a> | <a href="reposearch">Search</a>')
		self.response.out.write('<br><br><a href="graph/bm.html">Visualize</a>')

class NewLink(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			u = User.all()
			u.filter("name =", user.nickname())
			
			if (u.count() == 0):
				usr = User(name=user.nickname(), userid=user.user_id())
				usr.put()
			
			r = Repo.all()
			r.filter("name =", self.request.get('repo'))
			
			if (r.count() == 0):
				rep = Repo(name=self.request.get('repo'), owner=user.nickname())
				rep.put()
			
			e = Bookmark(title=self.request.get('title'), link=self.request.get('link'), owner=user.nickname(),repo=self.request.get('repo'))
			e.put()
			
		self.redirect('/')

		
class SubmitLink(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			greeting = ("Welcome, %s! <form method='get' action='newlink'>Title: <input type='text' name='title' /><br> Link: <input type='text' name='link' /><br> Repo: <input type='text' name='repo' /><br><input type='submit' value='Submit'></form>(<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/")))
		else:
			greeting = ("<a href=\"%s\">sign in or register</a>." % users.create_login_url("/new"))
		self.response.out.write("<html><body>%s</body></html>" % greeting)

class UserRepos(webapp2.RequestHandler):
	def get(self):
		r = Repo.all()
		r.filter("owner =", self.request.get('user'))
		results = r.fetch(100)
		
		for p in results:
			self.response.out.write('<a href="repolist?repo=' + p.name + '">' + p.name + "</a><br>")
		
class RepoSearch(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			greeting = ("Welcome, %s! <form method='get' action='repolist'>Repo Search: <input type='text' name='repo' /><br> User Search : <input type='text' name='user' /><br><input type='submit' value='Submit'></form>(<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/")))
		else:
			greeting = ("<a href=\"%s\">sign in or register</a>." % users.create_login_url("/new"))
		self.response.out.write("<html><body>%s</body></html>" % greeting)

class RepoList(webapp2.RequestHandler):
	def get(self):
		str = "function bm(){if (window.sidebar){"
		user = users.get_current_user()
		if user:
			q= Bookmark.all()
			if(self.request.get('repo')!=''):
				q.filter("repo =" , self.request.get('repo'))
			if(self.request.get('user')!=''):
				q.filter("owner =" , self.request.get('user'))
			resultRepo = q.fetch(100)
			self.response.out.write('<table border="1"><tr><th>' + 'Title         ' + '</th> <th>' + 'Link         ' + '</th> <th>' + 'Owner         ' + '</th> <th>' + 'Repo         ' + '</th> </tr>')
			for p in resultRepo:
				str = str + "window.sidebar.addPanel(" + p.title + ", " + p.link + ", '');"
				self.response.out.write('<tr><td>'+p.title + '</td><td>' + '<a href="' + p.link + '">' + p.link + '</a>' +'</td><td>' + p.owner + '</td><td>' + p.repo + '</td></tr>')
			self.response.out.write('</table>')
			str = str + "}"
			
			self.response.out.write('<script>' + str + '</script> <br><a href="#" onClick="bm()">Sync</a>')
			
			
		
app = webapp2.WSGIApplication([('/', MainHandler), ('/new', SubmitLink), ('/newlink', NewLink), ('/reposearch', RepoSearch), ('/repolist', RepoList), ('/userrepos', UserRepos)],
                              debug=True)
