window.setupProfileModal = setupProfileModal;
window.setupProfile = setupProfile;
window.setupMfaModal = setupMfaModal;
window.updateProfile = updateProfile;
window.updateMfa = updateMfa;
window.previewImage = previewImage;
window.updatePicture = updatePicture;
window.logout = logout;

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
			usernameInfo.innerHTML = 
			`
			<h1>${data.username}'s Profile</h1>
			`;
			picture.innerHTML = 
			`
			<img src="${src}" alt="no picture found" width="${width}" height="${height}">
			`;
			username.innerHTML =
			`
            <h2 id="currentUsername">${data.username}</h2>
			`;
            email.innerHTML =
            `
            <h2 id="currentEmail">${data.email}</h2>
            `;
            provider.innerHTML =
            `
            <h2 id="currentProvider">${data.provider}</h2>
            `;
            mfa.innerHTML =
            `
            <h2 id="currentMfa">${data.mfa}</h2>
            `;
		}
	} catch (error) {
		console.error('Fail to fetch user information:', error);
	}
}

function setupProfileModal() {
    const username = document.getElementById('currentUsername');
    const email = document.getElementById('currentEmail');
    const usernameInput = document.getElementById('usernameInput');
    const emailInput = document.getElementById('emailInput');
    usernameInput.value = username.innerText;
    emailInput.value = email.innerText;
}

function setupMfaModal() {
    const mfa = document.getElementById('currentMfa');
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

function previewImage() {
    const fileInput = document.getElementById('fileInput');
    const preview = document.getElementById('preview');
    const file = fileInput.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        }
        reader.readAsDataURL(file);
    }
}

async function updatePicture() {
    const fileInput = document.getElementById('fileInput')
    const form = new FormData();
    form.append('picture', fileInput.files[0]);
    try { const response = await fetch('/api/profile/', {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access')}`
            },
            body: form
        });
        if (response.ok) {
            alert('PIcute has been uploaded!');
        } else {
            alert('Fail to upload picture:', response.statusText);
        }
    } catch (error) {
        alert('Fail to upload picture:', error);
    }
    setupProfile();
}

function logout() {
    localStorage.clear();
    navigateTo('');
}