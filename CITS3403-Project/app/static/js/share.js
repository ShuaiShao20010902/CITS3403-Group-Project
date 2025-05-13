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

    // Parse the shared stats data from the HTML data block
    const statsDataScript = document.getElementById('shared-stats-data');
    window.sharedStatsData = statsDataScript ? JSON.parse(statsDataScript.textContent) : {};

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
        const selectedValue = this.value;
        bookDetails.style.display = 'block';

        // Remove any previous chart preview
        const existingChart = document.getElementById('shareStatsChart');
        if (existingChart) existingChart.remove();

        if (selectedValue === 'stats') {
            // Hide book-specific fields
            bookCover.style.display = 'none';
            bookNote.parentElement.style.display = 'none';
            bookRating.parentElement.style.display = 'none';

            // Remove previous chart if present
            const existingChart = document.getElementById('shareStatsChart');
            if (existingChart) existingChart.remove();

            // Add chart preview
            const chartCanvas = document.createElement('canvas');
            chartCanvas.id = 'shareStatsChart';
            chartCanvas.width = 220;   // Match card chart width
            chartCanvas.height = 180;  // Match card chart height
            bookDetails.appendChild(chartCanvas);

            // Render the chart using the preview data
            const chartData = window.sharedStatsData['preview'] || [];
            const ctx = chartCanvas.getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: chartData.map(item => item.date),
                    datasets: [{
                        label: 'Pages Read',
                        data: chartData.map(item => item.pages_read),
                        fill: true,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.2,
                        pointRadius: 3
                    }]
                },
                options: {
                    responsive: false,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            title: { display: true, text: 'Date' },
                            ticks: { font: { size: 12 } }
                        },
                        y: {
                            title: { display: true, text: 'Pages' },
                            beginAtZero: true,
                            ticks: { font: { size: 12 } }
                        }
                    }
                }
            });
        } else {
            // Show book-specific fields
            bookCover.style.display = '';
            bookNote.parentElement.style.display = '';
            bookRating.parentElement.style.display = '';

            // Remove chart if present
            const chartCanvas = document.getElementById('shareStatsChart');
            if (chartCanvas) chartCanvas.remove();

            // Existing logic for book preview...
            const selectedOption = bookDropdown.options[bookDropdown.selectedIndex];
            bookCover.src = selectedOption.getAttribute('data-cover');
            bookNote.textContent = selectedOption.getAttribute('data-note');
            bookRating.textContent = selectedOption.getAttribute('data-rating');
        }
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

    // Loop through all stats cards and render the chart
    document.querySelectorAll('canvas[id^="sharedChart-"]').forEach(canvas => {
        const itemId = canvas.id.split('-')[1];
        // You need to make sure stats data is available for each item, e.g.:
        // window.sharedStatsData = { "123": [...], "124": [...] }
        const chartData = window.sharedStatsData[itemId];
        if (!chartData) return;
        new Chart(canvas.getContext('2d'), {
            type: 'line',
            data: {
                labels: chartData.map(item => item.date),
                datasets: [{
                    label: 'Pages Read',
                    data: chartData.map(item => item.pages_read),
                    fill: true,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.2,
                    pointRadius: 3
                }]
            },
            options: { responsive: false, maintainAspectRatio: false }
        });
    });
});
