export function setupLoginForm() {
    const form = document.getElementById('loginForm');
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const username = form.username.value;
        const password = form.password.value;

        try {
            const response = await fetch('http://localhost:8000/api/users/login/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                url: `http://localhost:8000`,
                body: JSON.stringify({ username, password }),
            });
            const data = await response.json();
            if (response.ok) {
                alert('Login successful!');
                window.location.hash = 'home';
            } else {
                alert(data.error || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
        }
    });
}