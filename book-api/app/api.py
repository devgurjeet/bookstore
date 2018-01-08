from datetime import datetime
from flask import Flask
from flask_restplus import Resource, Api, fields
from werkzeug.contrib.fixers import ProxyFix

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:testteam@localhost/bookstore'
app.wsgi_app = ProxyFix(app.wsgi_app)

db = SQLAlchemy(app)

api = Api(app, version='1.0.0', title='Books api', description="A simple books api.")

book_ns = api.namespace('books', description="Books Operations")
author_ns = api.namespace('authors', description="Author Operations")

# Db definition.
class BookModel(db.Model):
	__tablename__ = "books"
	id    		= db.Column(db.Integer, primary_key  = True)
	title 		= db.Column(db.String(100), nullable = False)
	isbn		= db.Column(db.String(100), nullable = False)
	pages 		= db.Column( db.Integer, nullable = False)
	price 		= db.Column( db.Float, nullable = False)
	publishedOn = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())	
	authorId 	= db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
	authors 	= db.relationship('AuthorModel', backref=db.backref('authors', lazy=True))


	def __init__(self, title, isbn, pages, price, authorId = ''):
		self.title    = title
		self.isbn     = isbn
		self.pages    = pages
		self.price    = price
		self.authorId = authorId

	def __repr__(self):
		return '<Book %r>' % self.title

class AuthorModel(db.Model):
	__tablename__ = 'authors'
	id   = db.Column(db.Integer, primary_key  = True)
	name = db.Column(db.String(100), nullable = False)

	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return '<Author %r>' % self.name

book = 	api.model('Book', {
			'id': fields.Integer(readonly=True, description='Book ID'),
			'title': fields.String(required=True, description='Book title'),
			'isbn': fields.Integer( required=True, description='Book ISBN'),
			'pages': fields.Integer( required=True, description='Number of pages'),
			'price': fields.Integer( required=True, description='Price of book'),
			'authorId': fields.Integer( required=True, description='Author Id'),
		})

author = 	api.model('Author', {
			'id': fields.Integer(readonly=True, description='Author ID'),
			'name': fields.String(required=True, description='Author Name')			
		})



class BookDAO(object):
	
	@property
	def books(self):
		return BookModel.query.all()

	def get(self, id):
		book = BookModel.query.filter_by(id=id).first()
		if book:
			return {"id": book.id, "Book": book.title}
		api.abort(404, "book {} doesn't exist".format(id))

	def create(self, data):
		book = BookModel(data['title'], data['isbn'], data['pages'], data['price'], data['authorId'])
		db.session.add(book)
		db.session.commit()
		return book

	def update(self, id, data):
		book = BookModel.query.filter_by(id=id).first()
		book.title = data['title']
		book.isbn  = data['isbn']
		book.pages = data['pages']
		book.price = data['price']

		db.session.commit()
		return book

	def delete(self, id):
		book = BookModel.query.filter_by(id=id).first()
		if book:
			db.session.delete(book)
			db.session.commit()
			
		api.abort(404, "book {} doesn't exist".format(id))


DAO = BookDAO()


class AuthorDAO(object):
	
	@property
	def authors(self):
		return AuthorModel.query.all()

	def get(self, id):
		author = AuthorModel.query.filter_by(id=id).first()
		if author:
			return {"id": author.id, "author": author.name}
		api.abort(404, "Author {} doesn't exist".format(id))

	def create(self, data):
		author = AuthorModel(data['name'])
		db.session.add(author)
		db.session.commit()
		return author

	def update(self, id, data):
		author = AuthorModel.query.filter_by(id=id).first()
		author.name = data['name']		

		db.session.commit()
		return author

	def delete(self, id):
		author = AuthorModel.query.filter_by(id=id).first()
		if author:
			db.session.delete(author)
			db.session.commit()
			
		api.abort(404, "Author {} doesn't exist".format(id))


ADAO = AuthorDAO()

@book_ns.route('/')
class BookList(Resource):
	'''Shows a list of all books, and lets you POST to add new Books'''
	@book_ns.doc('list_books')
	@book_ns.marshal_list_with(book)
	def get(self):
	    '''List all books'''
	    return DAO.books

	@book_ns.doc('create_book')
	@book_ns.expect(book)
	@book_ns.marshal_with(book, code=201)
	def post(self):
	    '''Create a new task'''
	    return DAO.create(api.payload), 201


@book_ns.route('/<int:id>')
@book_ns.response(404, 'Book not found')
@book_ns.param('id', 'The Book identifier')
class Book(Resource):
	'''Show a single Book item and lets you delete them'''
	@book_ns.doc('get_book')
	@book_ns.marshal_with(book)
	def get(self, id):
		'''Fetch a given resource'''
		return DAO.get(id)

	@book_ns.doc('delete_book')
	@book_ns.response(204, 'Book deleted')
	def delete(self, id):
		'''Delete a task given its identifier'''
		DAO.delete(id)
		return '', 204

	@book_ns.expect(book)
	@book_ns.marshal_with(book)
	def put(self, id):
		'''Update a task given its identifier'''
		return DAO.update(id, api.payload)



@author_ns.route('/')
class AuthorList(Resource):
	'''Shows a list of all Authors, and lets you POST to add new Auhtors'''
	@author_ns.doc('list_Auhtors')
	@author_ns.marshal_list_with(author)
	def get(self):
	    '''List all authors'''
	    return ADAO.authors

	@author_ns.doc('create_authors')
	@author_ns.expect(author)
	@author_ns.marshal_with(author, code=201)
	def post(self):
	    '''Create a new authors'''
	    return ADAO.create(api.payload), 201


@author_ns.route('/<int:id>')
@author_ns.response(404, 'authors not found')
@author_ns.param('id', 'The authors identifier')
class Auhtor(Resource):
	'''Show a single authors and lets you delete them'''
	@author_ns.doc('get_author')
	@author_ns.marshal_with(book)
	def get(self, id):
		'''Fetch a given resource'''
		return ADAO.get(id)

	@author_ns.doc('delete_author')
	@author_ns.response(204, 'author deleted')
	def delete(self, id):
		'''Delete a author given its identifier'''
		ADAO.delete(id)
		return '', 204

	@author_ns.expect(author)
	@author_ns.marshal_with(author)
	def put(self, id):
		'''Update a author given its identifier'''
		return ADAO.update(id, api.payload)



if __name__ == '__main__':
	app.run(debug=True)
