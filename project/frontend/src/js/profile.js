export async function setupProfile() {
	const userinfo = document.getElementById('userinfo');
	const nameinfo = document.getElementById('userinfo');
	const access = localStorage.getItem('access');
	try {
		const response = await fetch('http://localhost:8000/api/users/me', {
			method: 'GET',
			headers: { 'Authorization': `Bearer ${access}` }
		});
		const data = await response.json();
		if (response.ok) {
			let username = data.username;
			let email = data.email;
			let provider = data.provider;
			let img = data.picture;
			let src = `http://localhost:8000/${img}`;
			let width = '250px';
			let height = '250px';
			userinfo.innerHTML = 
			`
			<div class="wrapper">
			<div class="custom-border">
			<div class="img-wrapper">
				<img src="${src}" alt="picture is not found" width=${width} height=${height}>
			</div>
			</div>
			<button class="btn btn-secondary btn-custom2" onclick="navigateTo('')">Change Picture</button>
			<h2> Username:  ${username} </h2>
			<h2> Email: ${email} </h2>
			<h2> Provider: ${provider} </h2>
			</div>
			`
		}
	} catch (error) {
		console.error('Fail to fetch user information:', error);
	}
}
