export function setupSignupForm() {
    const form = document.getElementById('signupForm');
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const username = form.usernameSignup.value;
        const password = form.passwordSignup.value;
        const email = form.emailSignup.value;
        const provider = 'Pong';

        try {
            const response = await fetch('/api/signup/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password, email, provider }),
            });
            const data = await response.json();
            if (response.ok) {
                localStorage.setItem('email', email);
                alert('Verification code is sent to your email! Please verify your email.');
                navigateTo('codeverify');
            } else {
                alert(data.error || 'Signup failed');
            }
        } catch (error) {
            console.error('Signup error:', error);
        }
    });
}
