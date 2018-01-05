from api import db, BookDAO
db.create_all()


book = {
			'title': 'BloodLine',
			'isbn': 1324564897,
			'pages': '100',
			'price': '12',
		}
DAO = BookDAO()
DAO.create(book)
# DAO.create({'task': '?????'})
# DAO.create({'task': 'profit!'})