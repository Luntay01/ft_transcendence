export function setupCodeVerifyForm() {
    const searchParams = new URLSearchParams(window.location.search);
    if (localStorage.getItem('qrcode') && searchParams.has('mfa') && searchParams.get('mfa') == 'Authenticator') {
        let img = document.createElement('img');
        img.src = 'data:image/png;base64,' + localStorage.getItem('qrcode');
        img.alt = 'QR Code';
        img.width = 200;
        document.getElementById('qrcode').appendChild(img);
    }
    const form = document.getElementById('verifyForm');
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const verify_code = form.codeVerify.value;
        const email = localStorage.getItem('email');

        try {
            const provider = 'Pong';
            const response = await fetch('/api/codeverify/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ email, verify_code, provider }),
            });
            const data = await response.json();
            if (response.ok) {
				if (data.id)
					localStorage.setItem('player_id', data.id);
				else
					console.log('No player ID returned by the backend.');
				if (data.username)
					localStorage.setItem('username', data.username);
				else
                    console.log('No username returned by the backend.');
                if (searchParams.has('mfa')) {
                    const mfa = searchParams.get('mfa');
                    localStorage.removeItem('qrcode');
                    try {
                        const response = await fetch('/api/users/', {
                            method: 'PATCH',
                            headers: { 
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${localStorage.getItem('access')}` 
                            },
                            body: JSON.stringify({ mfa }),
                        })
                        if (!response.ok) {
                            alert('Update failed:', response.statusText);
                            return;
                        }
                    } catch (error) {
                        alert('Update error:', error);
                    }
                    alert('MFA option updated successfully!');
                    navigateTo('profile');
                }
                else {
                    alert('Verification succeeded! Welcome to Pong!');
                    localStorage.setItem('access', data.access);
                    localStorage.setItem('refresh', data.refresh);
                    navigateTo('home');
                }
            } else {
                alert(data.error || 'Verification failed');
            }
        } catch (error) {
            console.log('Verification error:', error);
        }
    });
}