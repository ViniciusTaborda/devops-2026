import pytest
from datetime import datetime
from main import app as flask_app, db, Book

@pytest.fixture
def app():
    """Configures the app for testing and sets up an in-memory database."""
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app 
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Provides a test client for making HTTP requests."""
    return app.test_client()


def test_get_team_members_success(client):
    """Test 1 (Team Members): Garante que o endpoint retorna status 200 e o formato de lista."""
    response = client.get('/')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_team_members_content(client):
    """Test 2 (Team Members): Valida se o nome do integrante esperado está correto na resposta."""
    response = client.get('/')
    data = response.get_json()
    
    assert len(data) == 1
    assert data[0]['name'] == "Vinicius Eduardo Taborda Costa"


def test_get_team_members_method_not_allowed(client):
    """Test 3 (Team Members): Garante que o endpoint bloqueia requisições do tipo POST com erro 405."""
    response = client.post('/', json={"name": "Novo Integrante"})
    assert response.status_code == 405

def test_get_books_empty(client):
    """Test 1 (GET): Returns an empty list when no books exist."""
    response = client.get('/books')
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_books_success(client, app):
    """Test 2 (GET): Successfully retrieves a collection of existing books."""
    with app.app_context():
        book = Book(
            title="The Hobbit", 
            author="J.R.R. Tolkien", 
            issn="12345", 
            publication_date=datetime.fromisoformat("1937-09-21"), 
            pages=310
        )
        db.session.add(book)
        db.session.commit()

    response = client.get('/books')
    data = response.get_json()
    
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['title'] == "The Hobbit"


def test_get_books_structure_verification(client, app):
    """Test 3 (GET): Verifies that JSON structures match model schema formatting rules."""
    with app.app_context():
        book = Book(
            title="1984", 
            author="George Orwell", 
            issn="67890", 
            publication_date=datetime.fromisoformat("1949-06-08"), 
            pages=328
        )
        db.session.add(book)
        db.session.commit()

    response = client.get('/books')
    book_entry = response.get_json()[0]
    
    assert 'id' in book_entry
    assert book_entry['author'] == "George Orwell"
    assert book_entry['publication_date'] == "1949-06-08T00:00:00"



def test_post_book_success(client):
    """Test 1 (POST): Returns 201 code and serialized object data upon valid creation payload."""
    payload = {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "issn": "978-0132350884",
        "publication_date": "2008-08-01",
        "pages": 464
    }
    response = client.post('/books', json=payload)
    data = response.get_json()
    
    assert response.status_code == 201
    assert data['title'] == "Clean Code"
    assert 'id' in data


def test_post_book_missing_fields(client):
    """Test 2 (POST): Returns 400 Bad Request error if essential fields are absent."""
    payload = {
        "title": "Incomplete Payload Book",
        "author": "Mystery Author"
        # Missing fields: issn, publication_date, pages
    }
    response = client.post('/books', json=payload)
    data = response.get_json()
    
    assert response.status_code == 400
    assert "Missing required fields" in data['error']


def test_post_book_invalid_date_format(client):
    """Test 3 (POST): Returns 400 Bad Request if the publication date string breaks ISO 8601 expectations."""
    payload = {
        "title": "The Title",
        "author": "An Author",
        "issn": "111-222-333",
        "publication_date": "08/01/2008",  # Invalid format (should be YYYY-MM-DD)
        "pages": 200
    }
    response = client.post('/books', json=payload)
    data = response.get_json()
    
    assert response.status_code == 400
    assert "Invalid date format" in data['error']