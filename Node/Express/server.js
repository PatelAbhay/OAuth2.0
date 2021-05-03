import express from 'express'
import fetch from 'node-fetch'
require('dotenv').config();

const app = express();

/* Client ID and Client Secret obtained from the github app */
const client_id = process.env.GITHUB_CLIENT_ID;
const client_secret = process.env.GITHUB_CLIENT_SECRET;

/* General landing page routing */
app.get("/", (req, res) => {
    res.redirect(`http://localhost:` + PORT + `/login/github`);
})

/* Exchange code for the access token from github */
async function getAccessToken ( code, client_id, client_secret) {
    const res = await fetch("https://github.com/login/oauth/access_token", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            client_id,
            client_secret,
            code
        })
    });
    const data = await res.text();
    const params = new URLSearchParams(data);
    return params.get("access_token");
}

/* Uses github api to get the user data */
async function getGithubUser (token) {
    const request = await fetch("https://api.github.com/user", {
        method: "GET",
        headers: {
            Authorization: "token " + token
        }
    });
    const data = await request.text()
    return data;
}

/* Routing to the github login */
app.get("/login/github", (req, res) => {
    res.redirect(
        `https://github.com/login/oauth/authorize?client_id=${client_id}`
    );
})

/* Routing to callback url that github will redirect user to once login complete */
app.get("/login/github/callback", async (req, res) => {
    const code = req.query.code
    const access_token = await getAccessToken(code, client_id, client_secret)
    const user = await getGithubUser(access_token)
    if (user) {
        res.send(user)
    }
    else {
        res.redirect("/failed-login");
    }
});

app.get("/failed-login", (req, res) => {
    res.send("Failed to login, please try again");
})

/* Routing to logout */
app.get("/logout", (req, res) => {
    req.logout();
    //delete req.session;
    req.session = null;
    res.redirect("/");
});


const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log("Listening on http://localhost:" + PORT));
