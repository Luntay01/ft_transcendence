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

async function silentRefresh()
{
    if (!localStorage.hasOwnProperty('access'))
        return false;
    const access = localStorage.getItem('access');

    const verifyAccessResponse = await fetch('http://localhost:8000/api/token/verify/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'token': access }),
    });
    if (verifyAccessResponse.ok)
        return true;

    const refresh = localStorage.getItem('refresh');
    const verifyRefreshResponse = await fetch('http://localhost:8000/api/token/verify/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'token': refresh }),
    });

    if (verifyRefreshResponse.ok) {
        const refreshResponse = await fetch('http://localhost:8000/api/token/refresh/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 'refresh': refresh }),
        });
        const data = await refreshResponse.json();
        localStorage.setItem('access', data.access);
        return true;
    }
    return false;
}


async function loadView(view)
{
    try {
        const response = await fetch(`/views/${view}.html`);
        if (!response.ok) {
            console.log('Page not found. Back to top page.'); //TODO: display message to notify page not found
            navigateTo('');
            return;
        }
        const html = await response.text();
        document.getElementById('app').innerHTML = html;

        // After loading the view, set up the appropriate form handlers
        if (view == 'welcome') {
            return ;
        } else if (view === 'login') {
            const { setupLoginForm } = await import('./login.js');
            setupLoginForm();
        } else if (view === 'signup') {
            const { setupSignupForm } = await import('./signup.js');
            setupSignupForm();
        } else {
            const isTokenValid = await silentRefresh();
            if (!isTokenValid) {
                console.log("Token is invalid or expired. Please login again."); //TODO: display message to notify token invalid
                navigateTo('login');
                return;
            }
            if (view == 'home') {
                const { setupHome } = await import('./home.js');
                setupHome();
            }
            else if (view === 'gamePong') {
                const { initPong } = await import('./gamePong/gamePong.js');
                initPong();
            }
        }
    } catch (error) {
        console.error('Error loading view:', error);
        document.getElementById('app').innerHTML = '<p>Error loading view.</p>';
    }
}
