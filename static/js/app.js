(() => {
    const passwordToggle = document.querySelector('[data-password-toggle]');
    if (passwordToggle) {
        passwordToggle.addEventListener('click', () => {
            const input = document.querySelector('#id_password');
            if (!input) return;
            const show = input.type === 'password';
            input.type = show ? 'text' : 'password';
            passwordToggle.setAttribute('aria-label', show ? 'Ocultar senha' : 'Mostrar senha');
            passwordToggle.classList.toggle('is-visible', show);
        });
    }

    document.querySelectorAll('[data-dismiss-toast]').forEach((button) => {
        button.addEventListener('click', () => button.closest('[data-toast]')?.remove());
    });

    const prayerText = document.querySelector('#id_prayer_text');
    const charCount = document.querySelector('[data-char-count]');
    if (prayerText && charCount) {
        const updateCount = () => {
            const total = prayerText.value.length;
            charCount.textContent = `${total} caractere${total === 1 ? '' : 's'}`;
        };
        prayerText.addEventListener('input', updateCount);
        updateCount();
    }

    // Mantém a PWA ativa para instalação pelo próprio menu do navegador.
    // Não há botão de instalação dentro da tela de login.
    if ('serviceWorker' in navigator && window.isSecureContext) {
        navigator.serviceWorker.register('/sw.js', {scope: '/'}).catch(() => {});
    }
})();
