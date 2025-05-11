// Password Visibility Toggle Functionality
document.addEventListener('DOMContentLoaded', function() {
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    const toggleButtons = document.querySelectorAll('.toggle-password');

    toggleButtons.forEach((button, index) => {
        button.addEventListener('click', function() {
            const passwordInput = passwordInputs[index];
            
            if (passwordInput.type === 'password') {
                // Change to text
                passwordInput.type = 'text';
                button.classList.add('active');
                button.setAttribute('aria-label', 'Hide password');
            } else {
                // Change back to password
                passwordInput.type = 'password';
                button.classList.remove('active');
                button.setAttribute('aria-label', 'Show password');
            }
        });
    });
});