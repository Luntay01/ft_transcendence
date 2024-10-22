// Function to handle route changes based on URL fragments
function handleRoute() {
    const hash = window.location.hash.replace('#', '');
    loadView(hash || 'welcome'); // Default to 'welcome' if no hash is provided
}

// Load the correct view when the page loads or the URL changes
window.addEventListener('load', handleRoute);
window.addEventListener('hashchange', handleRoute);

function navigateTo(view)
{
    window.location.hash = view;  // This changes the URL hash, triggering the route handling
}

async function loadView(view)
{
    try {
        const response = await fetch(`/views/${view}.html`);
        if (!response.ok) throw new Error('View not found');
        const html = await response.text();
        document.getElementById('app').innerHTML = html;

        // After loading the view, set up the appropriate form handlers
        if (view === 'login') {
            const { setupLoginForm } = await import('./login.js');
            setupLoginForm();
        } else if (view === 'signup') {
            const { setupSignupForm } = await import('./signup.js');
            setupSignupForm();
        } else if (view === 'gamePong') {
            const { initPong } = await import('./gamePong/gamePong.js');
            initPong();
        }

    } catch (error) {
        console.error('Error loading view:', error);
        document.getElementById('app').innerHTML = '<p>Error loading view.</p>';
    }
}


