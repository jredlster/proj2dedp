"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, flash, redirect, request, session, url_for
from werkzeug.urls import url_parse
from werkzeug.datastructures import CombinedMultiDict

from config import Config
from FlaskWebProject import app, db
from FlaskWebProject.forms import LoginForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from FlaskWebProject.models import User, Post

import msal
import uuid


# -----------------------------------------------------------------------------
# Blob base URL (works if container is PUBLIC or if you add SAS token)
# -----------------------------------------------------------------------------
imageSourceUrl = (
    "https://"
    + app.config["BLOB_ACCOUNT"]
    + ".blob.core.windows.net/"
    + app.config["BLOB_CONTAINER"]
    + "/"
)

# Optional: if you decide to store a container SAS in config, append it here
# Example: app.config["BLOB_SAS_TOKEN"] = "?sv=...."
def build_blob_url(filename: str) -> str:
    if not filename:
        return ""
    sas = app.config.get("BLOB_SAS_TOKEN", "")
    return f"{imageSourceUrl}{filename}{sas}"


# -----------------------------------------------------------------------------
# Home
# -----------------------------------------------------------------------------
@app.route("/")
@app.route("/home")
@login_required
def home():
    # Keeping your existing behavior (user fetched, though not used below)
    User.query.filter_by(username=current_user.username).first_or_404()
    posts = Post.query.all()
    return render_template(
        "index.html",
        title="Home Page",
        posts=posts,
    )


# -----------------------------------------------------------------------------
# Create Post
# -----------------------------------------------------------------------------
@app.route("/new_post", methods=["GET", "POST"])
@login_required
def new_post():
    # IMPORTANT: bind both request.form and request.files
    form = PostForm(CombinedMultiDict([request.form, request.files]))

    if request.method == "POST":
        file = request.files.get("image_path")

        # Require image ONLY on create
        if not file or file.filename == "":
            flash("Please add an image before saving.")
            return render_template(
                "post.html",
                title="Create Post",
                imageSource=imageSourceUrl,
                form=form,
                post=None,
            )

        if form.validate():
            post_obj = Post()
            post_obj.save_changes(form, file, current_user.id, new=True)
            return redirect(url_for("home"))
        else:
            flash("Please fix the errors in the form.")

    return render_template(
        "post.html",
        title="Create Post",
        imageSource=imageSourceUrl,
        form=form,
        post=None,
    )


# -----------------------------------------------------------------------------
# Edit / Delete Post
# -----------------------------------------------------------------------------
@app.route("/post/<int:id>", methods=["GET", "POST"])
@login_required
def post(id):
    post_obj = Post.query.get_or_404(int(id))

    # Delete action
    if request.args.get("action") == "delete":
        # If your model has delete_image(), use it safely
        if post_obj.image_path:
            try:
                post_obj.delete_image()
            except Exception as e:
                app.logger.warning(f"Blob delete failed: {e}")

        db.session.delete(post_obj)
        db.session.commit()
        flash(f'post "{post_obj.title}" deleted successfully')
        return redirect(url_for("home"))

    # IMPORTANT: bind both request.form and request.files, and prefill from obj=post_obj
    form = PostForm(CombinedMultiDict([request.form, request.files]), obj=post_obj)

    if request.method == "POST":
        file = request.files.get("image_path")

        # Image optional on edit: only update image if user uploaded a new one
        if form.validate():
            post_obj.save_changes(form, file, current_user.id, new=False)
            return redirect(url_for("home"))
        else:
            flash("Please fix the errors in the form.")

    return render_template(
        "post.html",
        title="Edit Post",
        imageSource=imageSourceUrl,
        form=form,
        post=post_obj,  # <-- CRITICAL: template can use post.image_path
    )


# -----------------------------------------------------------------------------
# Password Login
# -----------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.password_hash == "-":
            # OAuth2 users are not allowed to use password
            flash("Not Allowed! Sign in with your Microsoft Account")
            return redirect(url_for("login"))

        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            app.logger.warning("Invalid login attempt!")
            return redirect(url_for("login"))

        login_user(user, remember=form.remember_me.data)
        app.logger.warning(f"{user.username} logged in successfully")
        flash(f"Welcome {user.username} !")

        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("home")
        return redirect(next_page)

    # MSAL login link
    session["state"] = str(uuid.uuid4())
    auth_url = _build_auth_url(scopes=Config.SCOPE, state=session["state"])
    return render_template("login.html", title="Sign In", form=form, auth_url=auth_url)


# -----------------------------------------------------------------------------
# Microsoft Login Callback
# -----------------------------------------------------------------------------
@app.route(Config.REDIRECT_PATH)  # Must match redirect URI set in AAD
def authorized():
    if request.args.get("state") != session.get("state"):
        return redirect(url_for("home"))

    if "error" in request.args:
        return render_template("auth_error.html", result=request.args)

    if request.args.get("code"):
        cache = _load_cache()

        result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(
            code=request.args["code"],
            scopes=Config.SCOPE,
            redirect_uri=url_for("authorized", _external=True, _scheme="http"),
        )

        session["user"] = result.get("id_token_claims")

        # preferred_username is email
        username = session["user"].get("preferred_username").split("@")[0]
        user = User.query.filter_by(username=username).first()

        if not user:
            new_user = User(username=username, password_hash="-")
            db.session.add(new_user)
            db.session.commit()
            user = User.query.filter_by(username=username).first()

        login_user(user)
        flash(f"Welcome {user.username} !")
        _save_cache(cache)

    return redirect(url_for("home"))


# -----------------------------------------------------------------------------
# Logout
# -----------------------------------------------------------------------------
@app.route("/logout")
def logout():
    logout_user()

    if session.get("user"):  # Used MS Login
        session.clear()
        return redirect(
            Config.AUTHORITY
            + "/oauth2/v2.0/logout"
            + "?post_logout_redirect_uri="
            + url_for("login", _external=True, _scheme="http")
        )

    return redirect(url_for("login"))


# -----------------------------------------------------------------------------
# MSAL helpers
# -----------------------------------------------------------------------------
def _load_cache():
    cache = msal.SerializableTokenCache()
    token_cache = session.get("token_cache")
    if token_cache:
        cache.deserialize(token_cache)
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        authority=authority or Config.AUTHORITY,
        client_id=Config.CLIENT_ID,
        client_credential=Config.CLIENT_SECRET,
        token_cache=cache,
    )


def _build_auth_url(authority=None, scopes=None, state=None):
    return _build_msal_app(authority=authority).get_authorization_request_url(
        scopes=scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=url_for("authorized", _external=True, _scheme="http"),
    )
