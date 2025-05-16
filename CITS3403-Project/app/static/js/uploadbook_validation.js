document.addEventListener('DOMContentLoaded', function() {
    const form              = document.querySelector('form');
    const titleField        = document.getElementById('title');
    const authorField       = document.getElementById('author');
    const pagesField        = document.getElementById('number_of_pages');
    const requiredFields    = [titleField, authorField];
  
    // Popup HTML
    function showErrors(errors) {
      const html = `
        <div id="error_popup" class="error_popup show">
          <div class="error_popup_content">
            <div class="error_popup_header">
              <span class="error_icon">&#10006;</span>
              <span class="error_title">
                Please fix the following ${errors.length > 1 ? 'errors' : 'error'}:
              </span>
              <span class="close_error_popup">&times;</span>
            </div>
            <div class="error_popup_body">
              <ul class="error_list">
                ${errors.map(e => `<li class="error_item">${e}</li>`).join('')}
              </ul>
            </div>
          </div>
        </div>`;
      
      // remove old then insert new
      let popup = document.getElementById('error_popup');
      if (popup) popup.remove();
      document.body.insertAdjacentHTML('beforeend', html);
  
      // close handlers
      document.querySelector('.close_error_popup')
        .addEventListener('click', () =>
          document.getElementById('error_popup').classList.remove('show')
        );
      document.getElementById('error_popup')
        .addEventListener('click', e => {
          if (e.target === e.currentTarget) e.currentTarget.classList.remove('show');
        });
    }
  
    // Field-level validation
    function validateField(field) {
      let valid = true;
      if (requiredFields.includes(field)) {
        valid = field.value.trim() !== '';
      } else if (field === pagesField) {
        const n = parseInt(field.value, 10);
        valid = !isNaN(n) && n > 0;
      }
      field.classList.toggle('is-invalid', !valid);
      return valid;
    }
  
    // Realtime
    [titleField, authorField, pagesField].forEach(f => {
      f.addEventListener('input', () => validateField(f));
      f.addEventListener('blur',  () => validateField(f));
    });
  
    // On submit, collect errors + show popup if any
    form.addEventListener('submit', function(event) {
      const errors = [];
  
      if (!validateField(titleField))  errors.push('Title is required');
      if (!validateField(authorField)) errors.push('Author is required');
      if (!validateField(pagesField))  errors.push('Number of pages must be a positive number');
  

      if (errors.length) {
        event.preventDefault();
        showErrors(errors);
      }
    });
  });
  