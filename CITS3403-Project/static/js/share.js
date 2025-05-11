document.addEventListener('DOMContentLoaded', () => {
    const shareUsername = document.getElementById('share-username');
    const message = document.getElementById('share-message');

    document.getElementById('share-button').addEventListener('click', function () {
        const username = document.getElementById('share-username').value;
        const bookId = document.getElementById('book-dropdown').value;

        if (!username || !bookId) {
            document.getElementById('share-message').textContent = 'Please select a book and enter a username.';
            return;
        }

        fetch('/share', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username, book_id: bookId })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('share-message').textContent = data.message;
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('share-message').textContent = 'An error occurred while sharing.';
        });
    });

    // Handle book selection and display details
    document.getElementById('book-dropdown').addEventListener('change', function () {
        const selectedOption = this.options[this.selectedIndex];
        const coverUrl = selectedOption.getAttribute('data-cover');
        const note = selectedOption.getAttribute('data-note');
        const rating = selectedOption.getAttribute('data-rating');

        if (coverUrl) {
            document.getElementById('book-cover').src = coverUrl;
        } else {
            document.getElementById('book-cover').src = ''; // Fallback if no cover URL
        }

        if (note) {
            document.getElementById('book-note').textContent = note;
        } else {
            document.getElementById('book-note').textContent = 'No notes available.';
        }

        if (rating) {
            document.getElementById('book-rating').textContent = `Rating: ${rating}`;
        } else {
            document.getElementById('book-rating').textContent = 'No rating available.';
        }

        document.getElementById('book-details').style.display = 'block';
    });
});
