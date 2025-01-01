//TODO: should it be SPA?
//TODO: handle access without passing code
async function handleRoute() {
	const queryString = window.location.search;
	const urlParms = new URLSearchParams(queryString);
	const code = urlParms.get('code');
	const state = urlParms.get('state');
	const res = await handler(code, state);
    if (!res) console.log("code is not found");
}

window.addEventListener('load', handleRoute);

async function handler(code, state) {
	if (!code || !state) return false;

	const response = await fetch("http://localhost:8000/api/users/oauth/", {
        method: 'POST',
		headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
		body: new URLSearchParams({ code, state }),
	})

	const data = await response.json();
	if (response.ok) {
		localStorage.setItem('access', data.access);
		localStorage.setItem('refresh', data.refresh);
		window.location.href = 'http://localhost:3000/#home';
	}
	return true;
}