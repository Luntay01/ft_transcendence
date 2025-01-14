export async function setupHome() {
	const userinfo = document.getElementById('userinfo');
	const access = localStorage.getItem('access');
	try {
		const response = await fetch('http://localhost:8000/api/users/me', {
			method: 'GET',
			headers: { 'Authorization': `Bearer ${access}` }
		});
		const data = await response.json();
		if (response.ok) {
			let nickname = data.username;
			let email = data.email;
			let provider = data.provider;
			let img = data.picture;
			let src = `http://localhost:8000/${img}`;
			let width = '200px';
			let height = '200px';
			userinfo.innerHTML = 
			`
			<h4> Nickname:  ${nickname} </h4>
			<h4> Email: ${email} </h4>
			<h4> Provider: ${provider} </h4>
			<h4> Picture: </h4><img src="${src}" alt="picture is not found" width=${width} height=${height}>
			`
		}
	} catch (error) {
		console.error('Fail to fetch user information:', error);
	}
}