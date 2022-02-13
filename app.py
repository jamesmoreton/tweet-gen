import generator
import re
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/gen")
def gen():
    query_username = request.args.get("username")
    generate_username = request.args.get("generate")

    if query_username:
        if not valid(query_username):
            return render_template("gen.html", step="START", username=query_username, invalid=True), 400

        user = generator.fetch_user(query_username)
        if user:
            return render_template("gen.html", step="USER", user=user)
        return render_template("gen.html", step="START", username=query_username)

    if generate_username:
        if not valid(generate_username):
            return render_template("gen.html", step="START", username=generate_username, invalid=True), 400

        generated_tweets = generator.generate(generate_username)
        return render_template(
            "gen.html",
            step="GENERATE",
            response=generated_tweets
        )

    return render_template("gen.html", step="START")

@app.route("/about")
def about():
    return render_template("about.html", title="About")

@app.errorhandler(Exception)
def handle_exception(e):
    print(e)
    return render_template("error.html", reason="GENERIC", e=e), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", reason="NOT_FOUND", e=e), 404

def valid(username):
    return re.match(r"^[a-zA-Z0-9_]{1,15}$", username)

if __name__ == '__main__':
    app.run(debug=True)
