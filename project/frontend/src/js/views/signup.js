import Auth from "../auth.js";

export function load() {
    const form = document.getElementById('signupForm');
    form.addEventListener('submit', Auth.signupPong);
}
