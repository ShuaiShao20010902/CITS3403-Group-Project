document.addEventListener('DOMContentLoaded', function() {
    const passwordField = document.getElementById('password');
    const confirmPasswordField = document.getElementById('confirm_password');
    const popup = document.getElementById('password-requirements-popup');

    if (passwordField && popup) {
        // Show popup when password field is focused
        passwordField.addEventListener('focus', function() {
            popup.style.display = 'block';
        });

        // Hide popup when clicking outside the password field and popup
        document.addEventListener('click', function(event) {
            if (!passwordField.contains(event.target) && !popup.contains(event.target)) {
                popup.style.display = 'none';
            }
        });

        // Real-time password validation and update requirement list styles
        passwordField.addEventListener('input', function() {
            const password = this.value;

            // Update the status of each requirement
            document.getElementById('req-length').classList.toggle('valid', password.length >= 8);
            document.getElementById('req-lowercase').classList.toggle('valid', /[a-z]/.test(password));
            document.getElementById('req-uppercase').classList.toggle('valid', /[A-Z]/.test(password));
            document.getElementById('req-number').classList.toggle('valid', /[0-9]/.test(password));
            document.getElementById('req-special').classList.toggle('valid', /[@$!%*?&]/.test(password));
        });

        // Link confirm password field
        if (confirmPasswordField) {
            confirmPasswordField.addEventListener('input', function() {
                const passwordMatch = this.value === passwordField.value;
                this.classList.toggle('is-valid', passwordMatch && this.value.length > 0);
                this.classList.toggle('is-invalid', !passwordMatch && this.value.length > 0);
            });
        }
    }
});