import Router from "./router.js";

class Auth {
    constructor() {

    }

    static async silentRefresh()
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

    static async loginPong(event) {
        event.preventDefault();
        const email = loginForm.email.value;
        const password = loginForm.password.value;
        const provider = 'Pong';

        try {
            const response = await fetch('http://localhost:8000/api/token/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ email, password, provider }),
            });
            const data = await response.json();
            if (response.ok) {
                alert('Login successful!');
                localStorage.setItem('access', data.access);
                localStorage.setItem('refresh', data.refresh);
				if (data.id)
					localStorage.setItem('player_id', data.id);
				else
					console.warn('No player ID returned by the backend.');
				if (data.username)
					localStorage.setItem('username', data.username);
				else
					console.warn('No username returned by the backend.');
                Router.navigateTo('home');
            } else {
                alert(data.error || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
        }
    }

    static async loginOAuth(event) {
        event.preventDefault();
        const email = loginForm.email.value;
        const password = loginForm.password.value;
        const provider = 'Pong';

        try {
            const response = await fetch('http://localhost:8000/api/token/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ email, password, provider }),
            });
            const data = await response.json();
            if (response.ok) {
                alert('Login successful!');
                localStorage.setItem('access', data.access);
                localStorage.setItem('refresh', data.refresh);
				if (data.id) {
                    localStorage.setItem('player_id', data.id);
                } else {
                    console.warn('No player ID returned by the backend.');
                }
					
				if (data.username) {
                    localStorage.setItem('username', data.username);
                } else {
                    console.warn('No username returned by the backend.');
                }
					
                Router.navigateTo('home');
            } else {
                alert(data.error || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
        }
    }

    static generateState(length) {
        let result = '';
        const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        const charactersLength = characters.length;
        let counter = 0;
        while (counter < length) {
          result += characters.charAt(Math.floor(Math.random() * charactersLength));
          counter += 1;
        }
        return result;
    };
    
}

export default Auth