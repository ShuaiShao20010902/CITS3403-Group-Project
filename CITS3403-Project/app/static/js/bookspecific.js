/* globals UPDATE_BOOK_URL, readingLogs */
document.addEventListener('DOMContentLoaded', () => {
  /* --------------------------------------------------
   *  helpers: success / error messages
   * -------------------------------------------------- */
  const $logMsg    = $('#log-message');
  const $ratingMsg = $('#rating-message');
  function ok($el, txt)   { $el.removeClass('msg-error').addClass('msg-success').text(txt); }
  function err($el, txt)  { $el.removeClass('msg-success').addClass('msg-error').text(txt); }

  /* ---------- BOOK CHART helpers ---------- */
  let bookChart = null;                     // Chart.js instance

  function buildOrUpdateChart() {
    const logsSorted = [...window.readingLogs]
        .sort((a,b)=> a.date.localeCompare(b.date));

    if (logsSorted.length < 2) {            // not enough data
      $('#book-chart-wrap').attr('hidden', true);
      $('#book-chart-msg').show();
      if (bookChart) { bookChart.destroy(); bookChart = null; }
      return;
    }

    // cumulative pages
    let running = 0;
    const labels = [];
    const data   = [];
    logsSorted.forEach(l=>{
      running += l.pages_read;
      labels.push(l.date);
      data.push(running);
    });

    $('#book-chart-msg').hide();
    $('#book-chart-wrap').removeAttr('hidden');

    if (!bookChart) {
      const ctx = document.getElementById('bookReadingChart').getContext('2d');
      bookChart = new Chart(ctx, {
        type:'line',
        data:{ labels, datasets:[{
          label:'Cumulative Pages',
          data,
          fill:true,
          borderColor:'#4bc0c0',
          backgroundColor:'rgba(75,192,192,.2)',
          tension:.2, pointRadius:3
        }]},
        options:{
          responsive:true,
          maintainAspectRatio:false,
          scales:{
            x:{ title:{ display:true, text:'Date' }},
            y:{ title:{ display:true, text:'Pages' },
             beginAtZero:true,
             max: window.BOOK_PAGES || undefined }  
          }
        }
      });
    } else {
      bookChart.data.labels = labels;
      bookChart.data.datasets[0].data = data;
      bookChart.options.scales.y.max  = window.BOOK_PAGES || undefined;
      bookChart.update();
    }
  }

  /* --------------------------------------------------
   *  Notes inline–editor 
   * -------------------------------------------------- */
  const $notesDisplay = $('#notes-display');
  const $notesEditor  = $('#notes-editor');
  const $notesActions = $('#notes-actions');
  const $saveNotes    = $('#save-notes');
  const $discardNotes = $('#discard-notes');
  const $notesMsg     = $('#notes-message');

  let originalNotes = $notesDisplay.text().trim() === 'No notes yet. Click here to start typing.' ? '' : $notesDisplay.text().trim();
  let notesChanged  = false;

  $notesDisplay.on('click', () => {
    $notesEditor.val(originalNotes).show().focus();
    $notesDisplay.hide();
  });

  $notesEditor.on('input', () => {
    notesChanged = $notesEditor.val().trim() !== originalNotes;
    $notesActions.toggle(notesChanged);
  });

  $saveNotes.on('click', () => {
    const txt = $notesEditor.val();
    $.ajax({
      url: UPDATE_BOOK_URL,
      type: 'POST',
      data: { notes: txt },
      success() {
        originalNotes = txt;
        $notesDisplay.text(txt || 'No notes yet. Click here to start typing.').show();
        $notesEditor.hide(); $notesActions.hide();
        ok($notesMsg, 'Notes saved!');
        setTimeout(() => $notesMsg.text(''), 1500);
      },
      error() { err($notesMsg, 'Error saving.'); }
    });
  });

  $discardNotes.on('click', () => {
    $notesEditor.hide();  $notesActions.hide();
    $notesDisplay.show(); $notesMsg.text('');
    $notesEditor.val(originalNotes);
  });

  /* --------------------------------------------------
   *  Star-rating widget
   * -------------------------------------------------- */
  const fullStar = /* svg */ `<svg viewBox="0 0 24 24" fill="gold" xmlns="http://www.w3.org/2000/svg"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>`;
  const halfStar = /* svg */ `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="halfGrad"><stop offset="50%" stop-color="gold"/><stop offset="50%" stop-color="lightgray"/></linearGradient></defs><path fill="url(#halfGrad)" d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>`;
  const emptyStar = /* svg */ `<svg viewBox="0 0 24 24" fill="lightgray" xmlns="http://www.w3.org/2000/svg"><path d="M22 9.24l-7.19-.62L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21 12 17.27 18.18 21l-1.64-7.03L22 9.24z"/></svg>`;

  const stars          = document.querySelectorAll('#star-rating .star');
  const paint = r => stars.forEach((s,i)=>{
    s.innerHTML = (r-i>=1)?fullStar:(r-i>=0.5)?halfStar:emptyStar;
  });
  let selectedRating = window.initialRating || 0;
  paint(selectedRating); 

  stars.forEach(star=>{
    star.addEventListener('mousemove', e=>{
      const idx = +star.dataset.index;
      const {left,width}=star.getBoundingClientRect();
      const half = (e.clientX-left)<width/2;
      paint(idx+(half?0.5:1));
    });
    star.addEventListener('click', e=>{
      const idx = +star.dataset.index;
      const {left,width}=star.getBoundingClientRect();
      const half = (e.clientX-left)<width/2;
      selectedRating = idx+(half?0.5:1);
      paint(selectedRating);
    });
  });
  document.getElementById('star-rating')
    .addEventListener('mouseleave',()=>paint(selectedRating));

  $('#rate-button').on('click',()=>{
    if(!selectedRating) return;
    $.ajax({
      url: UPDATE_BOOK_URL,
      type:'POST',
      data:{ rating:selectedRating },
      success() {
        ok($ratingMsg, 'Rated!');
        $('#rating-status').text(
            `You rated this book ${selectedRating}/5`
        );
      },
      error  (){ err($ratingMsg,'Error');  }
    });
  });

  /* --------------------------------------------------
   *  Reading-log modal
   * -------------------------------------------------- */
  const $modal        = $('#logModal');
  const $singleEntry  = $('#single-entry');
  const $editPagesInp = $('#edit-pages');
  const $editBtn      = $('#edit-button');
  const $actions      = $('#entry-actions');
  
  let idx = 0;
  readingLogs.sort((a,b)=>b.date.localeCompare(a.date));

  function recalcTotal(){
    const sum = readingLogs.reduce((t,l)=>t+l.pages_read,0);
    $('#pages-read-total').text(sum);  // modal
    $('#current-total').text(sum);     // main card
    const statusText = (window.BOOK_PAGES && sum >= window.BOOK_PAGES)
                     ? 'Completed' : 'Reading';
    $('#status-text').text(statusText);
  }

  function showEntry(){
    if(!readingLogs.length){
      $singleEntry.text('No entries yet');
      $('#prev-entry,#next-entry,#edit-button').prop('disabled',true);
      $actions.prop('hidden',true);
      return;
    }
    const e = readingLogs[idx];
    $singleEntry.text(`${e.date}: ${e.pages_read} pages`);
    $('#prev-entry').prop('disabled', idx === readingLogs.length-1);
    $('#next-entry').prop('disabled', idx === 0);
    $editBtn.prop('disabled',false).show();
    $actions.prop('hidden',true);
  }

  window.openForm  = () => { showEntry(); $modal.removeAttr('hidden'); };
  window.closeForm = () => { $modal.attr('hidden',true); $logMsg.text(''); };

  /* navigation */
  $('#prev-entry').on('click',()=>{ if(idx<readingLogs.length-1){ idx++; showEntry(); }});
  $('#next-entry').on('click',()=>{ if(idx>0){ idx--; showEntry(); }});

  /* edit existing */
  $editBtn.on('click',()=>{
    const e = readingLogs[idx];
    $editPagesInp.val(e.pages_read);
    $editBtn.hide(); $actions.prop('hidden',false);
  });

  $('#save-entry').on('click',()=>{
    const pages = +$editPagesInp.val()||0;
    if(pages<=0){ err($logMsg,'Enter pages > 0'); return; }
    const entry = readingLogs[idx];
    $.ajax({
      url: UPDATE_BOOK_URL,
      type:'POST',
      data:{ edit_date:entry.date, page_read:pages },
      success(){
        entry.pages_read = pages;
        recalcTotal(); showEntry(); buildOrUpdateChart();
        ok($logMsg,'Entry updated');
      },
      error(xhr){
        err($logMsg, xhr.responseJSON?.message || 'Error updating entry');
      }
    });
  });

  $('#delete-entry').on('click',()=>{
    const entry = readingLogs[idx];
    $.ajax({
      url: UPDATE_BOOK_URL,
      type:'POST',
      data:{ delete_date:entry.date },
      success(){
        readingLogs.splice(idx,1);
        if(idx>0) idx--;
        idx=0;recalcTotal(); showEntry(); buildOrUpdateChart();
        ok($logMsg,'Entry deleted');
      },
      error(){ err($logMsg,'Error deleting entry'); }
    });
  });

  /* add new */
  const todayISO = () => new Date().toISOString().slice(0,10);
  $('#log-date').val(todayISO());

  $('#add-entry').on('click',()=>{
    const date = $('#log-date').val() || todayISO();
    const pages= +$('#log-pages').val()||0;
    if(pages<=0){ err($logMsg,'Enter pages > 0'); return; }

    $.ajax({
      url: UPDATE_BOOK_URL,
      type:'POST',
      data:{ date, page_read:pages },
      success(resp){
        readingLogs.unshift(resp.new_log);
        idx=0; recalcTotal(); showEntry(); buildOrUpdateChart();
        ok($logMsg,'Entry added');
        $('#log-pages').val('');
      },
      error(xhr){
        err($logMsg, xhr.responseJSON?.message || 'Error adding entry');
      }
    });
  });


  const $pagesModal = $('#pagesModal');
  const $pagesInp   = $('#pages-input');
  const $pagesMsg   = $('#pages-msg');

  window.openPagesModal = () => {
    $pagesInp.val(window.BOOK_PAGES || 0);
    $pagesMsg.text('');
    $pagesModal.removeAttr('hidden');
  };
  window.closePagesModal = () => $pagesModal.attr('hidden', true);

  $('#pages-save').on('click', () => {
    const val = +$pagesInp.val() || 0;
    if (val <= 0) { $pagesMsg.text('Enter a positive number'); return; }

    $.ajax({
      url : UPDATE_BOOK_URL,
      type: 'POST',
      data: { pages_total: val },
      success(resp){
        // backend returns {"new_pages": val}
        window.BOOK_PAGES = resp.new_pages;
        $('#book-pages-total').text(val);
        recalcTotal();                // may flip Completed flag
        buildOrUpdateChart();         // y-axis max changes
        closePagesModal();
      },
      error(xhr){
        $pagesMsg.text(xhr.responseJSON?.message || 'Error updating');
      }
    });
  });

  // initial load
  recalcTotal();
  buildOrUpdateChart();
  
});
