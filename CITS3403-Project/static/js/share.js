document.addEventListener('DOMContentLoaded', () => {
    const shareButton = document.getElementById('share-button');
    const shareUsername = document.getElementById('share-username');
    const message = document.getElementById('share-message');

    shareButton.addEventListener('click', () => {
        const username = shareUsername.value.trim();
        if (!username) {
            message.textContent = "Please enter a username.";
            return;
        }

        fetch('/share', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username })
        })
        .then(response => response.json())
        .then(data => {
            message.textContent = data.message;
            if (data.status === 'success') {
                message.style.color = 'green';
                setTimeout(() => location.reload(), 1500);
            } else {
                message.style.color = 'red';
            }
        });
    });
});
