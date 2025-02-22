import Auth from "../auth.js";


export function load() {
    const loginForm = document.getElementById('loginForm');
    loginForm.addEventListener('submit', Auth.loginPong);

    const oauthForm = document.getElementById('oauthForm');
    oauthForm.addEventListener('submit', Auth.loginOAuth);
}