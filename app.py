from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- DATABASE TABLES ----------------

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Cascade delete: delete books when author is deleted
    books = db.relationship(
        'Book',
        backref='author',
        lazy=True,
        cascade="all, delete"
    )

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    status = db.Column(db.String(20), default="available")  # available / borrowed

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))

# ---------------- ROUTES ----------------

@app.route("/")
def index():
    return render_template("index.html")

# ---------------- LIST PAGES ----------------

@app.route("/books")
def books():
    all_books = Book.query.all()
    return render_template("books.html", books=all_books)

@app.route("/authors")
def authors():
    all_authors = Author.query.all()
    return render_template("authors.html", authors=all_authors)

@app.route("/members")
def members():
    all_members = Member.query.all()
    return render_template("members.html", members=all_members)

# ---------------- ADD ----------------

@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["title"]
        author_id = request.form["author_id"]

        new_book = Book(title=title, author_id=author_id)
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for("books"))

    authors = Author.query.all()
    return render_template("add_book.html", authors=authors)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        name = request.form["name"]

        new_author = Author(name=name)
        db.session.add(new_author)
        db.session.commit()

        return redirect(url_for("authors"))

    return render_template("add_author.html")


@app.route("/add_member", methods=["GET", "POST"])
def add_member():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        new_member = Member(name=name, email=email)
        db.session.add(new_member)
        db.session.commit()

        return redirect(url_for("members"))

    return render_template("add_member.html")

# ---------------- DELETE ----------------

@app.route("/delete_book/<int:id>", methods=["POST"])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for("books"))


@app.route("/delete_author/<int:id>", methods=["POST"])
def delete_author(id):
    author = Author.query.get_or_404(id)
    db.session.delete(author)
    db.session.commit()
    return redirect(url_for("authors"))


@app.route("/delete_member/<int:id>", methods=["POST"])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return redirect(url_for("members"))

# ---------------- QUERIES ----------------

@app.route("/books_by_author", methods=["GET", "POST"])
def books_by_author():
    books = []
    authors = Author.query.all()

    if request.method == "POST":
        author_id = request.form["author_id"]
        books = Book.query.filter_by(author_id=author_id).all()

    return render_template(
        "books_by_author.html",
        authors=authors,
        books=books
    )


@app.route("/available_books")
def available_books():
    books = Book.query.filter_by(status="available").all()
    return render_template("available_books.html", books=books)

# ---------------- MAIN ----------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
