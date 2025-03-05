export function setupCodeVerifyForm() {
    const form = document.getElementById('verifyForm');
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const verify_code = form.codeVerify.value;
        const email = localStorage.getItem('email');

        try {
            const provider = 'Pong';
            const response = await fetch('http://localhost:8000/api/users/codeverify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ email, verify_code, provider }),
            });
            const data = await response.json();
            if (response.ok) {
                alert('Verification succeeded! Welcome to Pong!');
                localStorage.setItem('access', data.access);
                localStorage.setItem('refresh', data.refresh);
                navigateTo('home');
            } else {
                alert(data.error || 'Verification failed');
            }
        } catch (error) {
            console.error('Verification error:', error);
        }
    });
}