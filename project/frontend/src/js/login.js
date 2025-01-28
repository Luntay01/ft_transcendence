function generateState(length) {
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

export function setupLoginForm() {
    const loginForm = document.getElementById('loginForm');
    loginForm.addEventListener('submit', async (event) => {
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
                navigateTo('home');
            } else {
                alert(data.error || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
        }
    });

    const oauthForm = document.getElementById('oauthForm');
    oauthForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const clientId = "u-s4t2ud-7eb0d578913ab9934c2b116843901211c2e920a996f3a96f058464f1d33e1f38";
        const redirectUrl = encodeURI("http://localhost:3000/callback");
        const state = generateState(20);
        const url = `https://api.intra.42.fr/oauth/authorize?` + 
            `client_id=${clientId}&` +
            `redirect_uri=${redirectUrl}&` +
            `response_type=code&` +
            `scope=public&` +
            `state=${state}`;
        window.location.href = url;
    });
}