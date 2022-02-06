from flask import Flask, render_template, request
import generator

# Configure application
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route("/")
def index():
    username = request.args.get("username")
    generate = request.args.get("generate")

    if username:
        user = generator.fetch_user(username)  # todo validate input...
        if user:
            return render_template("index.html", step="USER", user=user)
        return render_template("index.html", step="USER")

    if generate:
        generated_tweets = generator.generate(generate)
        return render_template(
            "index.html",
            step="GENERATE",
            username=generate,
            generated_tweets=generated_tweets
        )

    return render_template("index.html", step="INTRO")


@app.route("/about")
def about():
    return render_template("about.html", title="About")


if __name__ == '__main__':
    app.run()
