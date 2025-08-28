document.addEventListener("DOMContentLoaded", function() {
    const installBtn = document.getElementById('install-btn');

    if(!installBtn){
        console.warn("Install button not found!");
        return;
    }

    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        installBtn.style.display = 'inline-block';
    });

    installBtn.addEventListener('click', async () => {
        if(!deferredPrompt) return;
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log(`User response to install: ${outcome}`);
        deferredPrompt = null;
        installBtn.style.display = 'none';
    });
});
