document.addEventListener('DOMContentLoaded', function() {
  // Notes editing logic
  const notesDisplay = document.getElementById('notes-display');
  const notesEditor  = document.getElementById('notes-editor');
  const notesActions = document.getElementById('notes-actions');
  const saveBtn      = document.getElementById('save-notes');
  const discardBtn   = document.getElementById('discard-notes');
  const notesMsg     = document.getElementById('notes-message');

  let originalNotes = notesDisplay.textContent.trim() === 'No notes yet. Click here to start typing.' ? '' : notesDisplay.textContent.trim();

  notesDisplay.addEventListener('click', () => {
    notesEditor.value  = originalNotes;
    notesDisplay.style.display = 'none';
    notesEditor.style.display  = 'block';
    notesActions.style.display = 'flex'; 
    notesEditor.focus();
  });


  notesEditor.addEventListener('input', () => {
    const current = notesEditor.value.trim();
    if (current !== originalNotes) {
      notesActions.style.display = 'block';
    } else {
      notesActions.style.display = 'none';
    }
  });

  saveBtn.addEventListener('click', () => {
    const newNotes = notesEditor.value;
    $.ajax({
      url: window.UPDATE_BOOK_URL,
      type: "POST",
      data: { notes: newNotes },
      success() {
        originalNotes = newNotes;
        notesDisplay.textContent = newNotes || 'No notes yet.';
        notesMsg.textContent = 'Notes saved!';
        notesMsg.style.color = 'green';
        setTimeout(() => {
          notesEditor.style.display = 'none';
          notesActions.style.display = 'none';
          notesDisplay.style.display = 'block';
          notesMsg.textContent = '';
        }, 1000);
      },
      error() {
        notesMsg.textContent = 'Error saving.';
        notesMsg.style.color = 'red';
      }
    });
  });

  discardBtn.addEventListener('click', () => {
    notesEditor.value = originalNotes;
    notesActions.style.display = 'none';
    notesEditor.style.display = 'none';
    notesDisplay.style.display = 'block';
    notesMsg.textContent = '';
  });

  
  // Below is for the rating systep 
  const fullStarSVG = `
    <svg viewBox="0 0 24 24" fill="gold" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 17.27L18.18 21l-1.64-7.03
                L22 9.24l-7.19-.61L12 2 9.19 8.63
                2 9.24l5.46 4.73L5.82 21z"/>
    </svg>`;
  const halfStarSVG = `
    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="halfGrad"><stop offset="50%" stop-color="gold"/><stop offset="50%" stop-color="lightgray"/></linearGradient>
      </defs>
      <path d="M12 17.27L18.18 21l-1.64-7.03
                L22 9.24l-7.19-.61L12 2 9.19 8.63
                2 9.24l5.46 4.73L5.82 21z"
            fill="url(#halfGrad)"/>
    </svg>`;
  const emptyStarSVG = `
    <svg viewBox="0 0 24 24" fill="lightgray" xmlns="http://www.w3.org/2000/svg">
      <path d="M22 9.24l-7.19-.62L12 2 9.19 8.63
                2 9.24l5.46 4.73L5.82 21 12 17.27
                18.18 21l-1.64-7.03L22 9.24z"/>
    </svg>`;

  const stars = document.querySelectorAll('#star-rating .star');
  let selectedRating = 0;

  function paintStars(rating) {
    stars.forEach((star, idx) => {
      const diff = rating - idx;
      if (diff >= 1) star.innerHTML = fullStarSVG;
      else if (diff >= 0.5) star.innerHTML = halfStarSVG;
      else star.innerHTML = emptyStarSVG;
    });
  }

  // Initial paint
  paintStars(0);

  stars.forEach(star => {
    star.addEventListener('mousemove', e => {
      const idx = +star.dataset.index;
      const { left, width } = star.getBoundingClientRect();
      const isHalf = (e.clientX - left) < width/2;
      paintStars(idx + (isHalf ? 0.5 : 1));
    });
    star.addEventListener('click', e => {
      const idx = +star.dataset.index;
      const { left, width } = star.getBoundingClientRect();
      const isHalf = (e.clientX - left) < width/2;
      selectedRating = idx + (isHalf ? 0.5 : 1);
      paintStars(selectedRating);
    });
  });

  document.getElementById('star-rating').addEventListener('mouseleave', () => {
    paintStars(selectedRating);
  });

  // Rate button AJAX
  $('#rate-button').on('click', () => {
    if (selectedRating <= 0) return;
    $.ajax({
      url: window.UPDATE_BOOK_URL,
      type: "POST",
      data: { rating: selectedRating },
      success() {
        $('#rating-message')
          .text('Book rating has been rated!')
          .css('color','green')
          .fadeIn()
          .delay(1500)
          .fadeOut();
      },
      error() {
        $('#rating-message')
          .text('Error saving rating.')
          .css('color','red')
          .fadeIn()
          .delay(1500)
          .fadeOut();
      }
    });
  });


  /* globals UPDATE_BOOK_URL, readingLogs */

  const $modal  = $('#logModal');
  const $msg    = $('#log-message');
  const $total  = $('#pages-read-total');
  const $view   = $('#single-entry');
  const $edit   = $('#edit-pages');
  const $editBtn = $('#edit-button');
  const $actions = $('#entry-actions');
  const $editInp = $('#edit-pages');

  let idx = 0;                                     
  readingLogs.sort((a, b) => b.date.localeCompare(a.date));

  /* ------------ helpers ------------ */
  const todayISO = () => new Date().toISOString().slice(0, 10);

  function recalcTotal() {
    const sum = readingLogs.reduce((t, l) => t + l.pages_read, 0);
    $total.text(sum);
  }

  function showEntry () {
    if (!readingLogs.length) {
      $view.text('No entries yet');
      $('#prev-entry, #next-entry, #edit-button').prop('disabled', true);
      $actions.attr('hidden', true);
      return;
    }

    const e = readingLogs[idx];
    $view.text(`${e.date}: ${e.pages_read} pages`);

    $('#prev-entry').prop('disabled', idx === readingLogs.length - 1);
    $('#next-entry').prop('disabled', idx === 0);
    $editBtn.prop('disabled', false).show();
    $actions.attr('hidden', true);
  }

  window.openForm  = () => { showEntry(); $modal.removeAttr('hidden'); };
  window.closeForm = () => { $modal.attr('hidden', true); $msg.text(''); };;

  /* ------------ navigation ------------ */
  $('#prev-entry').on('click', () => { if (idx < readingLogs.length - 1) { idx++; showEntry(); }});
  $('#next-entry').on('click', () => { if (idx > 0)                    { idx--; showEntry(); }});

  /* -------- enter edit-mode -------- */
  $editBtn.on('click', () => {
    const e = readingLogs[idx];
    $editInp.val(e.pages_read);
    $editBtn.hide();
    $actions.removeAttr('hidden');
  });
  
  /* ------------ save existing entry ------------ */
  $('#save-entry').on('click', () => {
  const pages = parseInt($editInp.val(), 10) || 0;
  if (pages <= 0) { $msg.text('Enter pages > 0'); return; }

  const entry = readingLogs[idx];
  $.post(UPDATE_BOOK_URL, { edit_date: entry.date, page_read: pages })
    .done(() => {
      entry.pages_read = pages;
      recalcTotal();  showEntry();
      $msg.text('Entry updated');
    })
    .fail(() => $msg.text('Error updating entry'));
  });
  /* ------------ delete existing entry ------------ */
  $('#delete-entry').on('click', () => {
  const entry = readingLogs[idx];
  $.post(UPDATE_BOOK_URL, { delete_date: entry.date })
    .done(() => {
      readingLogs.splice(idx, 1);
      if (idx > 0) idx--;
      recalcTotal();  showEntry();
      $msg.text('Entry deleted');
    })
    .fail(() => $msg.text('Error deleting entry'));
  });

  /* ------------ add new entry ------------ */
  $('#log-date').val(todayISO());               // autofill today
  $('#add-entry').on('click', () => {
    const date = $('#log-date').val() || todayISO();
    const pages = parseInt($('#log-pages').val(), 10) || 0;
    if (pages <= 0) { $msg.text('Enter pages > 0'); return; }

    $.post(UPDATE_BOOK_URL, { date, page_read: pages })
      .done(() => {
        const existing = readingLogs.find(l => l.date === date);
        if (existing) existing.pages_read += pages;
        else readingLogs.unshift({ date, pages_read: pages });
        idx = 0;
        recalcTotal();
        showEntry();
        $msg.text('Entry added');
        $('#log-pages').val('');
      })
      .fail(() => $msg.text('Error adding entry'));
  });

});