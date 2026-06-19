from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    issn = db.Column(db.String(20), nullable=False)
    publication_date = db.Column(db.DateTime, nullable=False)
    pages = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "issn": self.issn,
            "publication_date": self.publication_date.isoformat(),
            "pages": self.pages
        }

with app.app_context():
    db.create_all()


@app.route('/', methods=['GET'])
def get_team_members():
    """Returns the list of team members."""
    team_members = [
        {"name": "Vinicius Eduardo Taborda Costa"},
    ]
    return jsonify(team_members), 200


@app.route('/books', methods=['GET'])
def get_books():
    """Handles fetching all books from the database."""
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200


@app.route('/books', methods=['POST'])
def create_book():
    """Handles creating a new book with incoming JSON validation."""
    data = request.get_json()
    

    if not data:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400


    required_fields = ['title', 'author', 'issn', 'publication_date', 'pages']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400


    try:
        pub_date = datetime.fromisoformat(data['publication_date'])
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use ISO 8601 (YYYY-MM-DD)"}), 400

    new_book = Book(
        title=data['title'],
        author=data['author'],
        issn=data['issn'],
        publication_date=pub_date,
        pages=data['pages']
    )
    
    db.session.add(new_book)
    db.session.commit()
    
    return jsonify(new_book.to_dict()), 201


if __name__ == '__main__':
    app.run(debug=True)