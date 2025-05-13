// Client-side form validation with real-time error checking
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const passwordField = document.getElementById('password');
    const confirmPasswordField = document.getElementById('confirm_password');
    
    if (form) {
        // Form submission validation
        form.addEventListener('submit', function(event) {
            const errors = [];
            
            // Password validation
            if (passwordField && passwordField.value) {
                const password = passwordField.value;
                
                // Check all password requirements
                const hasLowercase = /[a-z]/.test(password);
                const hasUppercase = /[A-Z]/.test(password);
                const hasNumber = /[0-9]/.test(password);
                const hasSpecial = /[@$!%*?&]/.test(password);
                const isLongEnough = password.length >= 8;
                
                // If password doesn't meet requirements, add error
                if (!(hasLowercase && hasUppercase && hasNumber && hasSpecial && isLongEnough)) {
                    errors.push("Password: Password must include at least one lowercase letter, one uppercase letter, one number, and one special character.");
                }
            }
            
            // Confirm password validation
            if (passwordField && confirmPasswordField && 
                passwordField.value && confirmPasswordField.value) {
                if (passwordField.value !== confirmPasswordField.value) {
                    errors.push("Password confirmation doesn't match Password");
                }
            }
            
            // If there are errors, prevent submission and show error popup
            if (errors.length > 0) {
                event.preventDefault();
                
                // Create error popup HTML and add to DOM
                const errorPopupHTML = `
                <div id="error_popup" class="error_popup show">
                    <div class="error_popup_content">
                        <div class="error_popup_header">
                            <span class="error_icon">&#10006;</span>
                            <span class="error_title">There were ${errors.length} errors with your form submission:</span>
                            <span class="close_error_popup">&times;</span>
                        </div>
                        <div class="error_popup_body">
                            <ul class="error_list">
                                ${errors.map(error => `<li class="error_item">${error}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>`;
                
                // Check if error popup already exists
                let errorPopup = document.getElementById('error_popup');
                if (errorPopup) {
                    errorPopup.remove();
                }
                
                document.body.insertAdjacentHTML('afterbegin', errorPopupHTML);
                
                // Add event listeners
                document.querySelector('.close_error_popup').addEventListener('click', function() {
                    document.getElementById('error_popup').classList.remove('show');
                });
                
                document.getElementById('error_popup').addEventListener('click', function(e) {
                    if (e.target === this) {
                        this.classList.remove('show');
                    }
                });
            }
        });
        
        // Real-time password requirements validation
        if (passwordField) {
            passwordField.addEventListener('input', function() {
                const password = this.value;
                
                // Update requirements status
                document.getElementById('req-length').classList.toggle('valid', password.length >= 8);
                document.getElementById('req-lowercase').classList.toggle('valid', /[a-z]/.test(password));
                document.getElementById('req-uppercase').classList.toggle('valid', /[A-Z]/.test(password));
                document.getElementById('req-number').classList.toggle('valid', /[0-9]/.test(password));
                document.getElementById('req-special').classList.toggle('valid', /[@$!%*?&]/.test(password));
            });
        }
        
        // Real-time confirm password validation
        if (confirmPasswordField && passwordField) {
            confirmPasswordField.addEventListener('input', function() {
                const passwordMatch = this.value === passwordField.value;
                this.classList.toggle('is-valid', passwordMatch && this.value.length > 0);
                this.classList.toggle('is-invalid', !passwordMatch && this.value.length > 0);
            });
        }
    }
});