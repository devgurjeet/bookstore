from flask import Flask
from flask_restplus import Api, Resource, fields

app = Flask(__name__)
api = api(app, version='1.0.0', title='Books api', description="A simple books api.")


ns = api.namespace('books', description="Books Operations")

book = 	api.model('Book', {
			'id': fields.Integer(readonly=True, description='Book ID'),
			'title': fields.String(required=True, description='Book title'),
			'isbn': fields.Integer( required=True, description='Book ISBN'),
			'pages': fields.Integer( required=True, description='Number of pages'),
			'price': fields.Integer( required=True, description='Price of book'),
		})


class BookDAO(object):
	"""docstring for BookDAO"""
	def __init__(self):
		self.counter = 0
		self.books   = []	
	
	def get(self, id):
		for book in self.books:
			if book['id'] == id:
				return book
		api.abort(404, "Book {} doesn't exist.".format(id))

	def create(self, data): 
		book = data
		book['id']	=  self.counter = self.counter + 1
		self.books.append(book)
		return todo

	def update(self, id, data):
		book = self.get(id)
		book.update(data)
		return book

	def delete(self, id):
		