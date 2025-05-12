document.addEventListener('DOMContentLoaded', () => {
    const shareButton = document.getElementById('share-button');
    const shareUsername = document.getElementById('share-username');
    const message = document.getElementById('share-message');
    const bookDropdown = document.getElementById('book-dropdown');
    const bookDetails = document.getElementById('book-details');
    const bookCover = document.getElementById('book-cover');
    const bookNote = document.getElementById('book-note');
    const bookRating = document.getElementById('book-rating');

    // Handle the share button click
    shareButton.addEventListener('click', () => {
        const username = shareUsername.value.trim();
        const bookId = bookDropdown.value;

        if (!username || !bookId) {
            message.textContent = 'Please select a book and enter a username.';
            message.style.color = 'red';
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
                setTimeout(() => location.reload(), 1500); // Reload the page after success
            } else {
                message.style.color = 'red';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            message.textContent = 'An error occurred while sharing.';
            message.style.color = 'red';
        });
    });

    // Handle book selection and display details
    bookDropdown.addEventListener('change', function () {
        const selectedOption = this.options[this.selectedIndex];
        const coverUrl = selectedOption.getAttribute('data-cover');
        const note = selectedOption.getAttribute('data-note');
        const rating = selectedOption.getAttribute('data-rating');

        if (coverUrl) {
            bookCover.src = coverUrl;
        } else {
            bookCover.src = ''; // Fallback if no cover URL
        }

        if (note) {
            bookNote.textContent = note;
        } else {
            bookNote.textContent = 'No notes available.';
        }

        if (rating) {
            bookRating.textContent = `Rating: ${rating}`;
        } else {
            bookRating.textContent = 'No rating available.';
        }

        bookDetails.style.display = 'block';
    });
});
