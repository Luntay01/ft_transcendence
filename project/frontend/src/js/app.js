// Function to handle route changes based on URL fragments
function handleRoute() {
    const hash = window.location.hash.replace('#', '');
    loadView(hash || 'welcome'); // Default to 'welcome' if no hash is provided
}

// Load the correct view when the page loads or the URL changes
window.addEventListener('load', handleRoute);
window.addEventListener('hashchange', handleRoute);

function navigateTo(view) {
    window.location.hash = view;  // This changes the URL hash, triggering the route handling
}

async function loadView(view) {
    try {
        const response = await fetch(`/views/${view}.html`);
        if (!response.ok) throw new Error('View not found');
        const html = await response.text();
        document.getElementById('app').innerHTML = html;

        // After loading the view, set up the appropriate form handlers
        if (view === 'login') {
            setupLoginForm();
        }
        if (view === 'signup') {
            setupSignupForm();
        }
    } catch (error) {
        console.error('Error loading view:', error);
        document.getElementById('app').innerHTML = '<p>Error loading view.</p>';
    }
}

// Setup function for the login form
function setupLoginForm() {
    const form = document.getElementById('loginForm');
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const username = form.username.value;
        const password = form.password.value;

        try {
            const response = await fetch('/api/login/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
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

// Setup function for the signup form
function setupSignupForm() {
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
