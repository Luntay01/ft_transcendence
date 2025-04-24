// Function to handle route changes based on URL fragments
import { loadGameSettings } from './games/gamePong/js/config.js';


let currentView = '';// track the current view


async function handleCallback(code, state) {
    if (!code || !state) return false;

	const response = await fetch("/api/oauth/", {
        method: 'POST',
		headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
		body: new URLSearchParams({ code, state }),
	})
    if (!response.ok) {
        return false;
	}
	const data = await response.json();
    localStorage.setItem('access', data.access);
    localStorage.setItem('refresh', data.refresh);
    return true;
	
}

async function handleRoute()
{
   
    if (location.search.includes("state=") && 
        (location.search.includes("code=") || 
        location.search.includes("error="))) {
        const queryString = window.location.search;
    	const urlParms = new URLSearchParams(queryString);
        const code = urlParms.get('code');
        const state = urlParms.get('state');
        window.history.replaceState({}, document.title, "/#login");
        loadView('login');

        if (localStorage.getItem('auth_request_state') != state) {
            alert('Invalid state');
            return ;
        }
        const res = await handleCallback(code, state);
        if (!res) {
            // console.log("code is not found");
            alert('Login Failed');
            return ;
        }
        window.history.replaceState({}, document.title, "/");
        loadView('home');
        return ;
    }



    const newView = window.location.hash.replace('#', '') || 'welcome';
    // Prevent going back to matchmaking from the game screen
    if (currentView === 'gamePong' && newView === 'game_matchmaking' || currentView === 'game_end' && newView === 'gamePong')
    {
        navigateTo('home');
        return;
    }
    if ((currentView === 'gamePong' || currentView === 'game_matchmaking' || currentView === 'tourn_display') &&
	newView !== 'gamePong' &&
	newView !== 'tourn_display')
    {
        console.log("Exiting game, disconnecting WebSocket...");
        disconnectWebSocket();
    }
    currentView = newView;
    loadView(newView);
}

function disconnectWebSocket()
{
    const ws = WebSocketService.getInstance();
    if (ws.isConnected())
    {
        console.log("Disconnecting WebSocket...");
        ws.shouldReconnect = false; // Prevent automatic reconnection
        ws.disconnect();
    }
}

// Load the correct view when the page loads or the URL changes
window.addEventListener('load', async () => {
    await loadGameSettings();
    handleRoute();
});

//window.addEventListener('load', handleRoute);
window.addEventListener('hashchange', handleRoute);
function navigateTo(view)
{
	window.location.hash = view;  // This changes the URL hash, triggering the route handling
}
window.navigateTo = navigateTo;


async function silentRefresh()
{
    if (!localStorage.hasOwnProperty('access'))
        return false;
    const access = localStorage.getItem('access');

    const verifyAccessResponse = await fetch('/api/token/verify/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'token': access }),
    });
    if (verifyAccessResponse.ok)
        return true;

    const refresh = localStorage.getItem('refresh');
    const verifyRefreshResponse = await fetch('/api/token/verify/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'token': refresh }),
    });

    if (verifyRefreshResponse.ok) {
        const refreshResponse = await fetch('/api/token/refresh/', {
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

        document.title = `${view.charAt(0).toUpperCase()}${view.slice(1)} - Pong Games`;

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
			else if (view === 'game_matchmaking') {
				await import('./WebSocketService.js');
				const { setupMatchmaking } = await import('./matchmaking.js');
				setupMatchmaking();
			}
            else if (view === 'gamePong') {
                const { initPong } = await import('./games/gamePong/js/main.js');
                initPong();
            }
            else if (view === 'tourn_display') {
                const { setupEndMatchScreen } = await import('./tourn_display.js');
                setupEndMatchScreen();
            }
            else if (view === 'game_end') {
                const { setupEndGameScreen } = await import('./game_end.js');
                setupEndGameScreen();
            }
            else if (view === 'profile') {
                const { setupProfile } = await import('./profile.js');
                setupProfile();
            }
        }
    } catch (error) {
        console.error('Error loading view:', error);
        document.getElementById('app').innerHTML = '<p>Error loading view.</p>';
    }
}