document.addEventListener('DOMContentLoaded', function() {
    // Cerrar alertas cuando se hace clic en el botón de cerrar
    const alertCloseButtons = document.querySelectorAll('.alert-close');
    
    alertCloseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const alertMessage = this.closest('.alert-message');
            if (alertMessage) {
                alertMessage.style.animation = 'slideOut 0.3s ease forwards';
                setTimeout(() => {
                    alertMessage.remove();
                }, 300);
            }
        });
    });

    // Enfoque en campo de contraseña para mostrar eye icon (opcional)
    const passwordInput = document.querySelector('input[type="password"]');
    if (passwordInput) {
        passwordInput.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        passwordInput.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    }

    // Validación básica del formulario
    const loginForm = document.querySelector('.login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const username = document.querySelector('input[name="username"]');
            const password = document.querySelector('input[name="password"]');
            
            let hasError = false;
            
            if (!username.value.trim()) {
                showFieldError(username, 'El usuario o email es requerido');
                hasError = true;
            }
            
            if (!password.value.trim()) {
                showFieldError(password, 'La contraseña es requerida');
                hasError = true;
            }
            
            if (hasError) {
                e.preventDefault();
            }
        });
    }

    // Función helper para mostrar errores
    function showFieldError(field, message) {
        let errorElement = field.nextElementSibling;
        if (!errorElement || !errorElement.classList.contains('error-text')) {
            errorElement = document.createElement('span');
            errorElement.className = 'error-text';
            field.parentElement.appendChild(errorElement);
        }
        errorElement.textContent = message;
        field.classList.add('error');
    }

    // Remover clase error cuando se empieza a escribir
    document.querySelectorAll('.login-form input').forEach(input => {
        input.addEventListener('input', function() {
            this.classList.remove('error');
            const errorElement = this.nextElementSibling;
            if (errorElement && errorElement.classList.contains('error-text')) {
                errorElement.textContent = '';
            }
        });
    });
});

// Animación de slide out para alertas
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(-100%);
        }
    }
    
    .login-form input.error {
        border-color: #e74c3c;
    }
    
    .login-form input.error:focus {
        box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.15);
        border-color: #e74c3c;
    }
`;
document.head.appendChild(style);
