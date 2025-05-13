// Error popup functionality
document.addEventListener('DOMContentLoaded', function() {
    // Show error popup
    function showErrorPopup() {
        const errorPopup = document.getElementById('error_popup');
        if (errorPopup) {
            errorPopup.classList.add('show');
        }
    }

    // Close error popup
    function closeErrorPopup() {
        const errorPopup = document.getElementById('error_popup');
        if (errorPopup) {
            errorPopup.classList.remove('show');
        }
    }

    // Add close button event
    const closeButton = document.querySelector('.close_error_popup');
    if (closeButton) {
        closeButton.addEventListener('click', closeErrorPopup);
    }

    // Click outside to close popup
    const errorPopup = document.getElementById('error_popup');
    if (errorPopup) {
        errorPopup.addEventListener('click', function(event) {

            if (event.target === errorPopup) {
                closeErrorPopup();
            }
        });
    }

    // Automatically show error popup if it exists and has errors
    const errorItems = document.querySelectorAll('.error_item');
    if (errorItems.length > 0) {
        showErrorPopup();
    }

    // Support ESC key to close popup
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeErrorPopup();
        }
    });
});