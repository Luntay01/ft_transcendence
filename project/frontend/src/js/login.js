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

function setupLoginFormEx(form)
{
	form.addEventListener('submit', async (event) => {
		event.preventDefault();
		const email = form.email.value;
		const password = form.password.value;
		const provider = 'Pong';

		try {
			const response = await fetch('/api/login/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
				body: new URLSearchParams({ email, password, provider }),
			});
			const data = await response.json();
			if (response.ok) {
                localStorage.setItem('email', email)
                // DEBUG: skip MFA
                if (data.access) {
                    localStorage.setItem('access', data.access);
                    localStorage.setItem('refresh', data.refresh);
                    localStorage.setItem('player_id', data.id);
                    localStorage.setItem('username', data.username);
                    navigateTo('home');
                    return ;
                }
                // <-- MFA skip
                alert('MFA is enabled. Please verify code to login.');
                navigateTo('codeverify');
			} else {
				alert(data.error || 'Login failed');
			}
		} catch (error) {
			console.error('Login error:', error);
		}
	});
}

export function setupLoginForm() {

	// multiple login forms for user / and debug testing users quickshortcuts
	const loginForms = document.querySelectorAll("#loginForm");
	loginForms.forEach(loginForm => {
		setupLoginFormEx(loginForm);
	});

    const oauthForm = document.getElementById('oauthForm');
    oauthForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const clientId = "u-s4t2ud-7eb0d578913ab9934c2b116843901211c2e920a996f3a96f058464f1d33e1f38";
        const redirectUrl = encodeURIComponent(window.location.protocol + "//" + window.location.host);
        const state = generateState(20);
        localStorage.setItem('auth_request_state', state);
        const url = `https://api.intra.42.fr/oauth/authorize?` + 
            `client_id=${clientId}&` +
            `redirect_uri=${redirectUrl}&` +
            `response_type=code&` +
            `scope=public&` +
            `state=${state}`;
        window.location.href = url;
    });
}