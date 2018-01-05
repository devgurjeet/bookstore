from flask import Flask
from flask_restplus import Resource, Api, fields
from werkzeug.contrib.fixers import ProxyFix

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:testteam@localhost/bookstore'
app.wsgi_app = ProxyFix(app.wsgi_app)

db = SQLAlchemy(app)

api = Api(app, version='1.0.0', title='Books api', description="A simple books api.")

ns = api.namespace('books', description="Books Operations")

# Db definition.
class BookModel(db.Model):
	id    = db.Column( db.Integer, primary_key=True )
	title = db.Column( db.String(100))
	isbn  = db.Column( db.String(50))
	pages = db.Column( db.Integer)
	price = db.Column( db.Float)

	def __init__(self, title, isbn, pages, price):
		self.title = title
		self.isbn  = isbn 
		self.pages = pages
		self.price = price

	def __repr__(self):
		return '<Book %r>' % self.title

book = 	api.model('Book', {
			'id': fields.Integer(readonly=True, description='Book ID'),
			'title': fields.String(required=True, description='Book title'),
			'isbn': fields.Integer( required=True, description='Book ISBN'),
			'pages': fields.Integer( required=True, description='Number of pages'),
			'price': fields.Integer( required=True, description='Price of book'),
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
		book = BookModel(data['title'], data['isbn'], data['pages'], data['price'])
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


@ns.route('/')
class BookList(Resource):
	'''Shows a list of all books, and lets you POST to add new Books'''
	@ns.doc('list_books')
	@ns.marshal_list_with(book)
	def get(self):
	    '''List all books'''
	    return DAO.books

	@ns.doc('create_book')
	@ns.expect(book)
	@ns.marshal_with(book, code=201)
	def post(self):
	    '''Create a new task'''
	    return DAO.create(api.payload), 201


@ns.route('/<int:id>')
@ns.response(404, 'Book not found')
@ns.param('id', 'The Book identifier')
class Book(Resource):
	'''Show a single Book item and lets you delete them'''
	@ns.doc('get_book')
	@ns.marshal_with(book)
	def get(self, id):
		'''Fetch a given resource'''
		return DAO.get(id)

	@ns.doc('delete_book')
	@ns.response(204, 'Book deleted')
	def delete(self, id):
		'''Delete a task given its identifier'''
		DAO.delete(id)
		return '', 204

	@ns.expect(book)
	@ns.marshal_with(book)
	def put(self, id):
		'''Update a task given its identifier'''
		return DAO.update(id, api.payload)

if __name__ == '__main__':
	app.run(debug=True)
