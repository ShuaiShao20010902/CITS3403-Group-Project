document.addEventListener('DOMContentLoaded', () => {
    const shareButton = document.getElementById('share-button');
    const shareUsername = document.getElementById('share-username');
    const message = document.getElementById('share-message');
    const bookDropdown = document.getElementById('book-dropdown');
    const bookDetails = document.getElementById('book-details');
    const bookCover = document.getElementById('book-cover');
    const bookNote = document.getElementById('book-note');
    const bookRating = document.getElementById('book-rating');
    const suggestionsBox = document.createElement('div');
    suggestionsBox.id = 'suggestions-box';
    suggestionsBox.style.position = 'absolute';
    suggestionsBox.style.border = '1px solid #ccc';
    suggestionsBox.style.backgroundColor = '#fff';
    suggestionsBox.style.zIndex = '1000';
    suggestionsBox.style.display = 'none';
    document.body.appendChild(suggestionsBox);

    // Get the current user's username (optional: pass it from the backend)
    const currentUser = "{{ session.get('username') }}";

    // Handle the share button click
    shareButton.addEventListener('click', () => {
        const username = shareUsername.value.trim();

        if (username === currentUser) {
            message.textContent = 'You cannot share to yourself.';
            message.style.color = 'red';
            return;
        }

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

    // Handle username input and display suggestions
    shareUsername.addEventListener('input', function () {
        const query = this.value.trim();

        if (query.length < 2) {
            suggestionsBox.style.display = 'none';
            return;
        }

        fetch(`/search_users?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(users => {
                if (users.length === 0) {
                    suggestionsBox.style.display = 'none';
                    return;
                }

                // Populate the suggestions box
                suggestionsBox.innerHTML = '';
                users.forEach(user => {
                    if (user === currentUser) return; // Skip the current user

                    const suggestion = document.createElement('div');
                    suggestion.textContent = user;
                    suggestion.style.padding = '5px';
                    suggestion.style.cursor = 'pointer';

                    // Handle click on a suggestion
                    suggestion.addEventListener('click', () => {
                        shareUsername.value = user;
                        suggestionsBox.style.display = 'none';
                    });

                    suggestionsBox.appendChild(suggestion);
                });

                // Position the suggestions box below the input field
                const rect = shareUsername.getBoundingClientRect();
                suggestionsBox.style.left = `${rect.left + window.scrollX}px`;
                suggestionsBox.style.top = `${rect.bottom + window.scrollY}px`;
                suggestionsBox.style.width = `${rect.width}px`;
                suggestionsBox.style.display = 'block';
            })
            .catch(error => {
                console.error('Error fetching user suggestions:', error);
                suggestionsBox.style.display = 'none';
            });
    });

    // Hide suggestions box when clicking outside
    document.addEventListener('click', (event) => {
        if (!shareUsername.contains(event.target) && !suggestionsBox.contains(event.target)) {
            suggestionsBox.style.display = 'none';
        }
    });
});
