export async function setupHome() {
	const userinfo = document.getElementById('userinfo');
	const access = localStorage.getItem('access');
	try {
		const response = await fetch('/api/users/me', {
			method: 'GET',
			headers: { 'Authorization': `Bearer ${access}` }
		});
		const data = await response.json();
		if (response.ok) {
			let username = data.username;
			let email = data.email;
			let provider = data.provider;
			let img = data.picture;
			let src = `/${img}`;
			let width = '50px';
			let height = '50px';
			userinfo.innerHTML = 
			`
			<div class ="top-right">
			<img src="${src}" alt="picture is not found" width=${width} height=${height}>
			</div>
			<div class="center-container">
			<p> Welcome back, ${username}!</p>
			</div>
			<div class="bottom-container">
			<p> Service Provider: ${provider} </p>
			</div>
			`
		}
	} catch (error) {
		console.error('Fail to fetch user information:', error);
	}
}