from flask import Flask, render_template, request
import generator

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/gen")
def gen():
    username = request.args.get("username")
    generate = request.args.get("generate")

    if username:
        user = generator.fetch_user(username)  # todo validate input...
        if user:
            return render_template("gen.html", step="USER", user=user)
        return render_template("gen.html", step="USER", username=username)

    if generate:
        generated_tweets = generator.generate(generate)
        return render_template(
            "gen.html",
            step="GENERATE",
            username=generate,
            generated_tweets=generated_tweets
        )

    return render_template("gen.html", step="START")

@app.route("/about")
def about():
    return render_template("about.html", title="About")

@app.errorhandler(Exception)
def handle_exception(e):
    return render_template("gen.html", step="ERROR", e=e), 500

if __name__ == '__main__':
    app.run()
