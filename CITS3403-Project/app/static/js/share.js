document.addEventListener('DOMContentLoaded', () => {
    const shareButton = document.getElementById('share-button');
    const shareUsername = document.getElementById('share-username');
    const message = document.getElementById('share-message');

    shareButton.addEventListener('click', () => {
        const username = shareUsername.value.trim();
        const bookId = document.getElementById('book-dropdown').value;

        if (!username || !bookId) {
            message.textContent = 'Please select a book and enter a username.';
            return;
        }

        fetch('/share', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, book_id: bookId })
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
        })
        .catch(error => {
            console.error('Error:', error);
            message.textContent = 'An error occurred while sharing.';
        });
    });

    // Handle book selection and display details
    document.getElementById('book-dropdown').addEventListener('change', function () {
        const selectedOption = this.options[this.selectedIndex];
        const coverUrl = selectedOption.getAttribute('data-cover');
        const note = selectedOption.getAttribute('data-note');
        const rating = selectedOption.getAttribute('data-rating');

        if (coverUrl && note && rating) {
            document.getElementById('book-cover').src = coverUrl;
            document.getElementById('book-note').textContent = note;
            document.getElementById('book-rating').textContent = rating;
            document.getElementById('book-details').style.display = 'block';
        } else {
            document.getElementById('book-details').style.display = 'none';
        }
    });
});
