// ──────────────────────────────────────────────────────────────
// Elements
// ──────────────────────────────────────────────────────────────

const titleInput = document.querySelector('.search-input');
const resultsContainer = document.getElementById('book-results');
const noMatches = document.getElementById('no-matches');
const importBox = document.getElementById('import-box');

//Modal
const modal = document.getElementById('modals');
const pageInput = document.getElementById('pageInput');
const confirmBtn = document.getElementById('confirmAddButton');
const cancelBtn = document.getElementById('cancelAddButton');

let latestquery = '';
let selectedBook = null;
let selectedAddBtn = null;

//Sorting
const sortSelect = document.getElementById('sort-select');
let currentSort = 'relevance';

sortSelect.addEventListener('change', () => {
  currentSort = sortSelect.value;
  titleInput.dispatchEvent(new Event('input')); // re-trigger search
});

const sortMap = {
  'relevance': '', // default
  'new': 'new',
  'old': 'old'
};

// ──────────────────────────────────────────────────────────────
// Live Search
// ──────────────────────────────────────────────────────────────
titleInput.addEventListener('input', () => {
  const query = titleInput.value.trim();
  latestquery = query;

  if (query.length < 0) { //how much words to be typed into search bar before search results show up
    resultsContainer.innerHTML = '';
    return;
  }

  const fetchquery = query;

  const sortParam = sortMap[currentSort];
  let url = `https://openlibrary.org/search.json?q=${encodeURIComponent(query)}&limit=10`; //change limit for more than 10 results
  if (sortParam) {
    url += `&sort=${encodeURIComponent(sortParam)}`;
  }

  fetch(url) 
    .then(res => res.json())
    .then(data => {
      // Check if latest query matches the fetch query
      if (latestquery !== fetchquery) return;

      resultsContainer.innerHTML = '';

      // No matches, show fallback message
      if (!data.docs || data.docs.length === 0) {
        resultsContainer.innerHTML = '';
        noMatches.innerHTML = `No matches for: <strong>"${query}"</strong>`;
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
        const author = doc.author_name ? doc.author_name.join(', ') : 'Unknown Author';
        const year = doc.first_publish_year || 'Unknown Year';
        const coverId = doc.cover_i;
        const coverUrl = coverId
          ? `https://covers.openlibrary.org/b/id/${coverId}-M.jpg`
          : 'https://via.placeholder.com/120x180?text=No+Cover';

        // Create a card for each book
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
                <button>Add to Dashboard</button>
            </div>
        `;
        resultsContainer.appendChild(card);

        // Add to dashboard button
        const addBtn = card.querySelector('button');

        addBtn.addEventListener('click', () => {
          selectedBook = doc;
          selectedAddBtn = addBtn;
          modal.style.display = 'flex';
          pageInput.value = '';
          pageInput.focus();
        });
      });
    })
    .catch(err => {
      console.error('Can not fetch books:', err);
      noMatches.style.display = 'none';
      importBox.style.display = 'none';
  });
});

// ──────────────────────────────────────────────────────────────
// Add Pages Modal
// ──────────────────────────────────────────────────────────────
confirmBtn.addEventListener('click', () => {
  const pagesStr = pageInput.value.trim();
  const pages = parseInt(pagesStr, 10);

  if (isNaN(pages) || pages <= 0) {
    alert("Enter a valid positive number of pages.");
    return;
  }

  confirmBtn.disabled = true;
  confirmBtn.textContent = 'Adding...';

  fetch('/add_book', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
      work_key: selectedBook.key,
      number_of_pages: pages, 
      })
  })
  .then(r => r.json())
  .then(res => {
      if (res.status === 'success') {
      selectedAddBtn.textContent = 'Added ✔';
      selectedAddBtn.disabled = true;
      modal.style.display = 'none';
      } else {
      alert('Failed: ' + (res.message || 'unknown error'));
      }
  })
  .catch(() => alert('Network error, please try again'))
  .finally(() => {
    confirmBtn.disabled = false;
    confirmBtn.textContent = 'Confirm';
  });
});

cancelBtn.addEventListener('click', () => {
  modal.style.display = 'none';
});