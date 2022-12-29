from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/book-details")
def book_details():
    return render_template("book-details.html")

if __name__ == "__main__":
    app.run(debug=True)