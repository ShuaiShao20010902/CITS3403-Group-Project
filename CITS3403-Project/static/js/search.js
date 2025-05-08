const titleInput = document.querySelector('.search-input');
const resultsContainer = document.getElementById('book-results');
const noMatches = document.getElementById('no-matches');
const importBox = document.getElementById('import-box');

let latestquery = '';

titleInput.addEventListener('input', () => {
  const query = titleInput.value.trim();
  latestquery = query;

  if (query.length < 3) {
    resultsContainer.innerHTML = '';
    return;
  }

  const fetchquery = query;

  fetch(`https://openlibrary.org/search.json?q=${encodeURIComponent(query)}&limit=10`) //change limit for more than 10 results (not sure how much)
    .then(res => res.json())
    .then(data => {
      if (latestquery !== fetchquery) return;

      resultsContainer.innerHTML = '';

      if (!data.docs || data.docs.length === 0) {
        resultsContainer.innerHTML = '';
        noMatches.style.display = 'block';
        importBox.style.display = 'block';
        return;
      } else {
        noMatches.style.display = 'none';
        importBox.style.display = 'none';
      }      

      const books = data.docs.slice(0, 10);

      books.forEach(doc => {
        const title = doc.title || 'Untitled';
        const author = doc.author_name ? doc.author_name.join(', ') : 'Unknown';
        const year = doc.first_publish_year || 'Unknown Year';
        const coverId = doc.cover_i;
        const coverUrl = coverId
          ? `https://covers.openlibrary.org/b/id/${coverId}-M.jpg`
          : 'https://via.placeholder.com/120x180?text=No+Cover';

        const card = document.createElement('div');
        card.className = 'book-card';
        card.innerHTML = `
            <img src="${coverUrl}" alt="Cover" class="book-cover">
            <div class="book-info">
                <h3>${title}</h3>
                <p><strong>Author:</strong> ${author}</p>
                <p><strong>Year:</strong> ${year}</p>
            </div>
            <div class="book-actions">
                <select>
                <option>To Read</option>
                <option>Reading</option>
                <option>Completed</option>
                </select>
                <button>Add to Dashboard</button>
            </div>
        `;
        resultsContainer.appendChild(card);
      });
    })
    .catch(err => {
      console.error('Failed to fetch books:', err);
    });
});
