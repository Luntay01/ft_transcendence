export function setupSignupForm() {
    const form = document.getElementById('signupForm');
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const username = form.usernameSignup.value;
        const password = form.passwordSignup.value;

        try {
            const response = await fetch('/api/signup/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
            const data = await response.json();
            if (response.ok) {
                alert('Signup successful! Please login.');
                window.location.hash = 'login';
            } else {
                alert(data.error || 'Signup failed');
            }
        } catch (error) {
            console.error('Signup error:', error);
        }
    });
}
