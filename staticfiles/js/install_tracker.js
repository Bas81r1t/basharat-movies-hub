document.addEventListener("DOMContentLoaded", function () {
    const installBtn = document.getElementById("install-btn");

    function getDeviceName() {
        const ua = navigator.userAgent;

        if (/POCO/i.test(ua)) return "POCO Device";
        if (/Redmi/i.test(ua)) return "Redmi Device";
        if (/Mi/i.test(ua)) return "Xiaomi Device";
        if (/OnePlus/i.test(ua)) return "OnePlus Device";
        if (/Samsung/i.test(ua)) return "Samsung Device";
        if (/Oppo/i.test(ua)) return "Oppo Device";
        if (/Vivo/i.test(ua)) return "Vivo Device";
        if (/Realme/i.test(ua)) return "Realme Device";
        if (/iPhone/i.test(ua)) return "iPhone";
        if (/iPad/i.test(ua)) return "iPad";
        if (/Windows/i.test(ua)) return "Windows PC/Laptop";
        if (/Macintosh/i.test(ua)) return "MacBook / iMac";
        if (/Linux/i.test(ua)) return "Linux Device";
        return ua;
    }

    function getDeviceId() {
        let deviceId = localStorage.getItem("pwa_device_id");
        if (!deviceId) {
            deviceId = crypto.randomUUID();
            localStorage.setItem("pwa_device_id", deviceId);
        }
        return deviceId;
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    async function trackInstall() {
        const deviceId = getDeviceId();
        const deviceName = getDeviceName();
        const url = "/track-install/";

        if (localStorage.getItem(`installed_${deviceId}`) === "true") {
            console.log("Install already tracked for this device.");
            return;
        }

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({
                    device_id: deviceId,
                    device_name: deviceName,
                }),
            });

            const data = await response.json();
            console.log("Install tracked:", data);

            localStorage.setItem(`installed_${deviceId}`, "true");
        } catch (error) {
            console.error("Error tracking install:", error);
        }
    }

    if (installBtn) {
        let deferredPrompt;
        window.addEventListener("beforeinstallprompt", (e) => {
            e.preventDefault();
            deferredPrompt = e;
            installBtn.style.display = "inline-block";
        });

        installBtn.addEventListener("click", async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                console.log(`User response: ${outcome}`);
                if (outcome === "accepted") {
                    trackInstall();
                }
                deferredPrompt = null;
                installBtn.style.display = "none";
            }
        });
    }

    window.addEventListener("appinstalled", () => {
        console.log("PWA installed event detected.");
        trackInstall();
    });

    if (!localStorage.getItem("pwa_is_installed")) {
        console.log("First-time install detected.");
        trackInstall();
    }
});
