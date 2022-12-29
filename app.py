from flask import Flask, render_template,jsonify
from flaskext.mysql import MySQL
from pymysql import cursors
from flask_mail import Mail, Message

app = Flask(__name__)

# SQL DATABASE CONNECTION
mysql = MySQL()
app.secret_key = "novel123"
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = ''
# app.config["MYSQL_DATABASE_PASSWORD"] = 'LAwrence1234**'
app.config["MYSQL_DATABASE_DB"] = "novel"
app.config["MYSQL_DATABASE_HOST"] = "127.0.0.1"
app.config["MYSQL_DATABASE_PORT"] = 3308
mysql.init_app(app)

# Mail server config.

app.config['MAIL_DEBUG'] = True
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'business.elysian21@gmail.com'
app.config['MAIL_PASSWORD'] = 'protected911'
app.config['MAIL_DEFAULT_SENDER'] = ('business.elysian21@gmail.com')

mail = Mail(app)

@app.route("/")
def index():
    conn = mysql.connect()
    cursor = conn.cursor(cursors.DictCursor)
    cursor.execute('''SELECT book_id from editors_pick;''')
    editors_pick_book_ids = cursor.fetchall()
    
    editors_pick_books = []
    for i in editors_pick_book_ids:
        cursor.execute('''SELECT book_id,name,book_genre.genre_name as genre,complete,mature,copyrights,tags,description,
                            books.image,ratings,points,user_id,books.timestamp,book_inactive,publish_status
                            FROM books
                            INNER JOIN book_genre ON book_genre.genre_id = books.genre
                            WHERE book_inactive = "active" and publish_status = "published" and book_id=%s ''',[i['book_id']])
        book = cursor.fetchone()
        editors_pick_books.append(book)

    cursor.execute('''SELECT book_id,name,book_genre.genre_name as genre,complete,mature,copyrights,tags,description,
                        books.image,ratings,points,user_id,books.timestamp,book_inactive,publish_status
                        FROM books
                        INNER JOIN book_genre ON book_genre.genre_id = books.genre
                        WHERE book_inactive = "active" and publish_status = "published" and genre=11 ''',)

    romance = cursor.fetchall()

    cursor.execute('''SELECT book_id,name,book_genre.genre_name as genre,complete,mature,copyrights,tags,description,
                        books.image,ratings,points,user_id,books.timestamp,book_inactive,publish_status
                        FROM books
                        INNER JOIN book_genre ON book_genre.genre_id = books.genre
                        WHERE book_inactive = "active" and publish_status = "published" ORDER BY book_id DESC LIMIT 10;''',)

    new_release = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()
    # return jsonify({"editors_pick":editors_pick})
    return render_template("index.html",editors_pick=editors_pick_books,romance=romance,new_release=new_release)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/book-details/<string:bookid>")
def book_details(bookid):    
    book_id = bookid
    conn = mysql.connect()
    cursor = conn.cursor(cursors.DictCursor)
    cursor.execute('''SELECT books.book_id,users.name as author, books.name as book_title,book_genre.genre_name as genre,complete,mature,copyrights,tags,
    books.description,books.image,users.user_id,book_inactive,publish_status 
    FROM books
    INNER JOIN users ON books.user_id = users.user_id
    INNER JOIN book_genre ON books.genre = book_genre.genre_id
    WHERE book_id = %s;''', [book_id])
    book_data = cursor.fetchall()

    cursor.execute('''SELECT chapter_id,title,publish_status
                    FROM chapter
                    WHERE book_id = %s;''', [book_id])
    chapters_list = cursor.fetchall()

    cursor.execute('''SELECT COUNT(*) as total_chapters
                    FROM chapter
                    WHERE book_id = %s;''', [book_id])
    total_chapters = cursor.fetchall()

    cursor.execute('''SELECT comment_id, comment,comments.timestamp,users.user_id,users.image as userimage,users.name as username
                FROM comments
                INNER JOIN users ON users.user_id = comments.commentator_id
                WHERE comments.book_id=%s;''', [book_id])
    comments_data = cursor.fetchall()

    cursor.execute('''SELECT AVG(rating)
                        FROM ratings
                        WHERE book_id = %s;''', [book_id])
    rating_data1 = cursor.fetchall()
    rating_data1 = rating_data1[0]["AVG(rating)"]
    if rating_data1:
        rating_data = round(rating_data1, 1)
    else:
        rating_data = rating_data1

    cursor.execute('''SELECT COUNT(book_id) as votes
                        FROM chapter_vote
                        WHERE book_id = %s;''', [book_id])
    total_votes = cursor.fetchall()
    cursor.execute('''SELECT COUNT(book_id) as views
                            FROM chapter_views
                            WHERE book_id = %s;''', [book_id])
    total_views = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'success': True, "book_data": book_data, "total_chapters": total_chapters,
                    "total_views": total_views,
                    "total_votes": total_votes,
                    "chapters_list": chapters_list, "comments": comments_data,
                    "rating_data": str(rating_data)})
    return render_template("book-details.html",book_data=book_data, total_chapters=total_chapters,
                    total_views=total_views,
                    total_votes= total_votes,
                    chapters_list= chapters_list, comments= comments_data,
                    rating_data= str(rating_data))

if __name__ == "__main__":
    app.run(debug=True)