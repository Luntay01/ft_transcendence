//TODO: should it be SPA?
//TODO: handle access without passing code
async function handleRoute() {
	const queryString = window.location.search;
	const urlParms = new URLSearchParams(queryString);
	const code = urlParms.get('code');
	const res = await handler(code);
    if (!res) console.log("code is not found");
}

window.addEventListener('load', handleRoute);

async function handler(code) {
	if (!code) return false;

	const response = await fetch("http://localhost:8000/api/users/oauth/", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
	})

	if (response.ok) window.location.href = 'http://localhost:3000/#login';
	return true;
}