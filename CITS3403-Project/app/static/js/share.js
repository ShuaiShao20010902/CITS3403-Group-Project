document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
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
    Object.assign(suggestionsBox.style, {
        position: 'absolute',
        border: '1px solid #ccc',
        backgroundColor: '#fff',
        zIndex: '1000',
        display: 'none'
    });
    document.body.appendChild(suggestionsBox);

    // --- Shared Stats Data ---
    const statsDataScript = document.getElementById('shared-stats-data');
    window.sharedStatsData = statsDataScript ? JSON.parse(statsDataScript.textContent) : {};

    // --- Current User (from backend) ---
    const currentUser = "{{ session.get('username') }}";

    // --- Share Button Handler ---
    shareButton.addEventListener('click', () => {
        const username = shareUsername.value.trim();
        const bookId = bookDropdown.value;

        if (username === currentUser) {
            message.textContent = 'You cannot share to yourself.';
            message.style.color = 'red';
            return;
        }
        if (!username || !bookId) {
            message.textContent = 'Please select a book and enter a username.';
            message.style.color = 'red';
            return;
        }

        fetch('/share', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, book_id: bookId })
        })
        .then(response => response.json())
        .then(data => {
            message.textContent = data.message;
            message.style.color = data.status === 'success' ? 'green' : 'red';
            if (data.status === 'success') setTimeout(() => location.reload(), 1500);
        })
        .catch(() => {
            message.textContent = 'An error occurred while sharing.';
            message.style.color = 'red';
        });
    });

    // --- Book Selection Handler ---
    bookDropdown.addEventListener('change', function () {
        shareButton.disabled = false;
        message.textContent = '';
        bookDetails.style.display = 'block';

        // Remove previous chart preview
        const existingChart = document.getElementById('shareStatsChart');
        if (existingChart) existingChart.remove();

        // Reset book details
        bookCover.src = '';
        bookNote.textContent = '';
        bookRating.textContent = '';
        bookCover.style.display = '';
        bookNote.parentElement.style.display = '';
        bookRating.parentElement.style.display = '';

        const selectedValue = this.value;

        if (selectedValue === 'stats') {
            bookCover.style.display = 'none';
            bookNote.parentElement.style.display = 'none';
            bookRating.parentElement.style.display = 'none';

            // Add chart preview
            const chartCanvas = document.createElement('canvas');
            chartCanvas.id = 'shareStatsChart';
            chartCanvas.width = 220;
            chartCanvas.height = 180;
            bookDetails.appendChild(chartCanvas);

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
            bookCover.style.display = '';
            bookNote.parentElement.style.display = '';
            bookRating.parentElement.style.display = '';
            const selectedOption = bookDropdown.options[bookDropdown.selectedIndex];
            bookCover.src = selectedOption.getAttribute('data-cover');
            bookNote.textContent = selectedOption.getAttribute('data-note');
            bookRating.textContent = selectedOption.getAttribute('data-rating');
        }
    });

    // --- Username Suggestions ---
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
                suggestionsBox.innerHTML = '';
                users.forEach(user => {
                    if (user === currentUser) return;
                    const suggestion = document.createElement('div');
                    suggestion.textContent = user;
                    suggestion.style.padding = '5px';
                    suggestion.style.cursor = 'pointer';
                    suggestion.addEventListener('click', () => {
                        shareUsername.value = user;
                        suggestionsBox.style.display = 'none';
                    });
                    suggestionsBox.appendChild(suggestion);
                });
                const rect = shareUsername.getBoundingClientRect();
                suggestionsBox.style.left = `${rect.left + window.scrollX}px`;
                suggestionsBox.style.top = `${rect.bottom + window.scrollY}px`;
                suggestionsBox.style.width = `${rect.width}px`;
                suggestionsBox.style.display = 'block';
            })
            .catch(() => {
                suggestionsBox.style.display = 'none';
            });
    });

    // Hide suggestions box when clicking outside
    document.addEventListener('click', event => {
        if (!shareUsername.contains(event.target) && !suggestionsBox.contains(event.target)) {
            suggestionsBox.style.display = 'none';
        }
    });

    // --- Render Shared Stats Charts ---
    document.querySelectorAll('canvas[id^="sharedChart-"]').forEach(canvas => {
        const itemId = canvas.id.split('-')[1];
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
            options: {
                responsive: false,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Pages' },
                        ticks: { font: { size: 12 } }
                    },
                    x: {
                        title: { display: true, text: 'Date' },
                        ticks: { font: { size: 12 } }
                    }
                }
            }
        });
    });

    // --- Copy to Clipboard Button ---
    const clipboardIcon = `<svg viewBox="0 0 20 20"><path d="M6 2a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H6zm0 2h8v12H6V4zm2 2v2h4V6H8z"/></svg> Copy Title to Clipboard`;
    document.querySelectorAll('.copy-title-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const title = btn.getAttribute('data-title');
            navigator.clipboard.writeText(title).then(() => {
                btn.textContent = 'Copied!';
                btn.classList.add('copied');
                setTimeout(() => {
                    btn.innerHTML = clipboardIcon;
                    btn.classList.remove('copied');
                }, 1500);
            }, () => {
                alert('Failed to copy!');
            });
        });
    });

    // --- Tabs ---
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
        });
    });

    // --- Carousel Arrows ---
    document.querySelectorAll('.carousel-container').forEach(container => {
        const track = container.querySelector('.carousel-track');
        container.querySelector('.carousel-arrow.left').onclick = () => {
            track.scrollBy({ left: -300, behavior: 'smooth' });
        };
        container.querySelector('.carousel-arrow.right').onclick = () => {
            track.scrollBy({ left: 300, behavior: 'smooth' });
        };
    });
});

