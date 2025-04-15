window.setupProfileModal = setupProfileModal;
window.setupProfile = setupProfile;
window.setupMfaModal = setupMfaModal;
window.updateProfile = updateProfile;
window.updateMfa = updateMfa;

export async function setupProfile() {
	const usernameInfo = document.getElementById('usernameInfo');
	const picture = document.getElementById('picture');
	const username = document.getElementById('username');
    const email = document.getElementById('email');
    const mfa = document.getElementById('mfa');
    const provider = document.getElementById('provider');
	const access = localStorage.getItem('access');
	try {
		const response = await fetch('/api/users/me', {
			method: 'GET',
			headers: { 'Authorization': `Bearer ${access}` }
		});
		const data = await response.json();
		if (response.ok) {
			const img = data.picture;
			const src = `${img}`;
			const width = '250px';
			const height = '250px';
			usernameInfo.textContent = `${data.username}'s Profile`;
			picture.innerHTML = 
			`
			<img src="${src}" alt="no picture found" width="${width}" height="${height}">
			`;
			username.textContent = data.username;
            email.textContent = data.email;
            provider.textContent = data.provider;
            mfa.textContent = data.mfa;
		}
	} catch (error) {
		console.error('Fail to fetch user information:', error);
	}
}

function setupProfileModal() {
    const username = document.getElementById('username');
    const email = document.getElementById('email');
    const usernameInput = document.getElementById('usernameInput');
    const emailInput = document.getElementById('emailInput');
    usernameInput.value = username.textContent;
    emailInput.value = email.textContent;
}

function setupMfaModal() {
    const mfa = document.getElementById('mfa');
    const mfaSelect = document.getElementById('mfaSelect');
    mfaSelect.value = mfa.innerText;
}

async function updateProfile() {
    const form = document.getElementById('profileForm');
    const username = form.username.value;
    const email = form.email.value;
    try { const response = await fetch('/api/profile/', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access')}`
            },
            body: JSON.stringify({username, email }),
        });
        const data = await response.json();
        if (response.ok) {
            alert('User information updated successfully!');
            localStorage.setItem('username', data.username);
            localStorage.setItem('access', data.access);
            localStorage.setItem('refresh', data.refresh);
        } else {
            alert('Fail to save user information:', response.statusText);
        }
    } catch (error) {
        alert('Fail to save user information:', error);
    }
    setupProfile();
}

async function updateMfa() {
    const form = document.getElementById('mfaForm');
    const mfa = form.mfa.value;
    try { const response = await fetch('/api/profile/', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access')}`
            },
            body: JSON.stringify({mfa}),
        });
        const data = await response.json();
        if (response.ok) {
            alert('Verify your code to switch MFA option!');
            if (data.image) {
                localStorage.setItem('qrcode', data.image);
            }
        } else {
            alert('Fail to save user information:', response.statusText);
        }
    } catch (error) {
        alert('Fail to save user information:', error);
    }
    navigateTo('codeverify', new URLSearchParams({ mfa }));
}
