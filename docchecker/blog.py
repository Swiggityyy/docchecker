from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort
import openai
import keys
import pandas as pd

from docchecker.auth import login_required
from docchecker.db import get_db

openai.organization = keys.organizationid
openai.api_key = keys.apikey
openai.Model.list()


bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    db = get_db()
    posts = db.execute(
        "SELECT p.id, prompt, essay, chatGPT, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template("blog/index.html", posts=posts)

def spacey():
    db = get_db()
    posts = db.execute(
    "SELECT p.id, prompt, essay, chatGPT, created, author_id, username"
    ).fetchall()
    with open (db, "r") as f:
        text = f.read()
        chapters = text.split("\n\n")[1:]

    chapter1 = chapters[0]

    nlp = spacy.load("en_core_web_lg")

    doc = nlp(chapter1)
    sentences = list(doc.sents)
    print (sentences[1])
    
def get_post(id, check_author=True):
    """Get a post and its author by id.
    Checks that the id exists and optionally that the current user is
    the author.
    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = (
        get_db()
        .execute(
            "SELECT p.id, prompt, essay, created, chatGPT, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        prompt = request.form["prompt"]
        essay = request.form["essay"]
        error = None
        
        if not prompt:
            error = "Prompt is required."

        if error is not None:
            flash(error)
        else:
            essay = request.form.get("essay")
            completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
            {"role": "system", "content": prompt}
            ]
            )
            chatGPT = completion.choices[0].message.content
            db = get_db()
            db.execute(
                "INSERT INTO post (prompt, essay, chatGPT, author_id) VALUES (?, ?, ?, ?)",
                (prompt, essay, chatGPT, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        prompt = request.form["prompt"]
        essay = request.form["essay"]
        error = None

        if not prompt:
            error = "prompt is required."

        if error is not None:
            flash(error)
        else:
            completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
            {"role": "system", "content": prompt}
            ]
            )
            chatGPT = completion.choices[0].message.content
            db = get_db()
            db.execute(
                "UPDATE post SET chatGPT = ?, prompt = ?, essay = ? WHERE id = ?", (chatGPT, prompt, essay, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.
    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))