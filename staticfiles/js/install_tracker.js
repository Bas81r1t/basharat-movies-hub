(function() {
    // -----------------------------
    // Get CSRF token (standard Django)
    // -----------------------------
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // -----------------------------
    // Send install info to Django
    // -----------------------------
    function trackInstall() {
        const device = navigator.userAgent || 'Unknown device';
        fetch('/track-install/', {   // ✅ match URL with Django urls.py
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ device: device })
        })
        .then(response => response.json())
        .then(data => console.log('PWA Install tracked:', data))
        .catch(err => console.error('Error tracking PWA install:', err));
    }

    // -----------------------------
    // Listen for PWA installation
    // -----------------------------
    window.addEventListener('appinstalled', (evt) => {
        console.log('PWA successfully installed!');
        trackInstall();
    });

    // -----------------------------
    // Optional: beforeinstallprompt fallback
    // -----------------------------
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        console.log('beforeinstallprompt fired, user may install PWA');

        // Optional: show custom install button
        // button.addEventListener('click', () => {
        //     deferredPrompt.prompt();
        //     deferredPrompt.userChoice.then(choiceResult => {
        //         console.log(choiceResult.outcome);
        //     });
        // });
    });

})();
