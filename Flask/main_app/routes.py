from flask import render_template, url_for, redirect, session
from main_app import app
from authlib.integrations.flask_client import OAuth
import os
from functools import wraps

# dotenv setup
from dotenv import load_dotenv
load_dotenv()

oauth = OAuth(app)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = dict(session).get('profile', None)
        if user:
            return f(*args, **kwargs)
        return 'You aint logged in, no page for u!'
    return wrapper


@app.route('/')
def index():
    return render_template('index.html')


##############################################################################################
# Google OAuth2.0 Implementation
##############################################################################################
google = oauth.register(
    name = 'google',
    client_id = os.getenv("GOOGLE_CLIENT_ID"),
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url = 'https://accounts.google.com/o/oauth2/token',
    access_token_params = None,
    authorize_url = 'https://accounts.google.com/o/oauth2/auth',
    authorize_params = None,
    api_base_url = 'https://www.googleapis.com/oauth2/v1/certs',
    userinfo_endpoint = 'https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs = {'scope': 'openid email profile'},
)

# login route for Google
@app.route('/login/google')
def google_login():
    google = oauth.create_client('google')
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/authorize')
def google_callback():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo', token=token).json()

    session['profile'] = resp

    return redirect('/login/google/protected')

@app.route('/login/google/protected')
@login_required
def google_protected():
    return (
        "<p>Hello, {}! You're logged in! Email: {}</p>"
        "<p>Google Id: {}</p>"
        "<a href='/logout'><button>Logout</button></a>".format(
            session['profile']["name"], session['profile']["email"], session['profile']["id"]
        )
    )


##############################################################################################
# Github OAuth2.0 Implementation
##############################################################################################
github = oauth.register(
    name = 'github',
    client_id = os.getenv("GITHUB_CLIENT_ID"),
    client_secret = os.getenv("GITHUB_CLIENT_SECRET"),
    access_token_url = 'https://github.com/login/oauth/access_token',
    access_token_params = None,
    authorize_url = 'https://github.com/login/oauth/authorize',
    authorize_params = None,
    api_base_url = 'https://api.github.com/',
)

# login route for Github
@app.route('/login/github')
def github_login():
    github = oauth.create_client('github')
    redirect_uri = url_for('github_callback', _external=True)
    return github.authorize_redirect(redirect_uri)

@app.route('/login/github/authorize')
def github_callback():
    github = oauth.create_client('github')
    token = github.authorize_access_token()
    resp = github.get('user', token=token).json()

    session['profile'] = resp

    return redirect('/login/github/protected')

@app.route('/login/github/protected')
@login_required
def github_protected():
    return (
        "<p>Hello, {}! You're logged in!</p>"
        "<p>Link: {}</p>"
        "<p># of Public Repos: {}</p>"
        "<a href='/logout'><button>Logout</button></a>".format(
            session['profile']["login"], session['profile']["html_url"], session['profile']["public_repos"]
        )
    )


##############################################################################################
# Discord OAuth2.0 Implementation
##############################################################################################
discord = oauth.register(
    name = 'discord',
    client_id = os.getenv("DISCORD_CLIENT_ID"),
    client_secret = os.getenv("DISCORD_CLIENT_SECRET"),
    access_token_url = 'https://discord.com/api/oauth2/token',
    access_token_params = None,
    authorize_url = 'https://discord.com/api/oauth2/authorize',
    authorize_params = None,
    api_base_url = 'https://discord.com/api',
    client_kwargs={'scope': 'identify email guilds connections'}
)

# login route for Discord
@app.route('/login/discord')
def discord_login():
    discord = oauth.create_client('discord')
    redirect_uri = url_for('discord_callback', _external=True)
    return discord.authorize_redirect(redirect_uri)

@app.route('/login/discord/authorize')
def discord_callback():
    discord = oauth.create_client('discord')
    token = discord.authorize_access_token()
    resp = discord.get('/api/users/@me', token=token).json()

    session['profile'] = resp

    return redirect('/login/discord/protected')

@app.route('/login/discord/protected')
@login_required
def discord_protected():
    return (
        "<p>Hello, {}! You're logged in!</p>"
        "<p>Email: {}</p>"
        "<p>Verified?: {}</p>"
        "<a href='/logout'><button>Logout</button></a>".format(
            session['profile']["username"], session['profile']["email"], session['profile']["verified"]
        )
    )


# logout to allow us to logout from every login method
@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')