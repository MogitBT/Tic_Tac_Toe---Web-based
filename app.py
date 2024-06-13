from flask import Flask, jsonify, request

app = Flask(__name__)

book_list = [
    {
        "book_id": 1,
        "author_name": "J.K. Rowling",
        "year": 1997,
        "title": "Harry Potter and the Philosopher's Stone"
    },
    {
        "book_id": 2,
        "author_name": "George Orwell",
        "year": 1949,
        "title": "1984"
    },
    {
        "book_id": 3,
        "author_name": "J.R.R. Tolkien",
        "year": 1954,
        "title": "The Lord of the Rings: The Fellowship of the Ring"
    },
    {
        "book_id": 4,
        "author_name": "Harper Lee",
        "year": 1960,
        "title": "To Kill a Mockingbird"
    },
    {
        "book_id": 5,
        "author_name": "F. Scott Fitzgerald",
        "year": 1925,
        "title": "The Great Gatsby"
    },
    {
        "book_id": 6,
        "author_name": "Gabriel Garcia Marquez",
        "year": 1967,
        "title": "One Hundred Years of Solitude"
    },
    {
        "book_id": 7,
        "author_name": "Jane Austen",
        "year": 1813,
        "title": "Pride and Prejudice"
    },
    {
        "book_id": 8,
        "author_name": "Mark Twain",
        "year": 1884,
        "title": "Adventures of Huckleberry Finn"
    },
    {
        "book_id": 9,
        "author_name": "Herman Melville",
        "year": 1851,
        "title": "Moby-Dick"
    }
]

@app.route("/books", methods = ['GET', 'POST'])
def books():
    if request.method == "GET":
        if len(book_list) > 0:
            return jsonify(book_list)
        else:
            return 'Nothing Found',404
        
    elif request.method == "POST":
        new_author = request.form['author_name']
        new_year = request.form['year']
        new_title = request.form['title']
        new_id = book_list[-1]['book_id']+1

        new_obj = {
            'book_id' : new_id,
            'author_name' : new_author,
            'year' : new_year,
            'title' : new_title
        }

        book_list.append(new_obj)
        return jsonify(book_list)
    
@app.route('/book/<int:book_id>', methods = ['GET'])
def single_book(book_id):
    for book in book_list:
        if book['book_id'] == book_id:
            return jsonify(book)


app.run()