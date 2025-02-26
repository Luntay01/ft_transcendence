export function setupCodeVerifyForm() {
    const form = document.getElementById('verifyForm');
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const verify_code = form.codeVerify.value;
        const email = localStorage.getItem('email');

        try {
            const response = await fetch('http://localhost:8000/api/users/codeverify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, verify_code }),
            });
            const data = await response.json();
            if (response.ok) {
                alert('Verification successful! Please login.');
                window.location.hash = 'login';
            } else {
                alert(data.error || 'Verification failed');
            }
        } catch (error) {
            console.error('Verification error:', error);
        }
    });
}