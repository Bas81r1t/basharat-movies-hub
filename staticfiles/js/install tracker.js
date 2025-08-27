// ✅ Unique user/device ID
function getUserUUID() {
    let uuid = localStorage.getItem("user_uuid");
    if (!uuid) {
        uuid = self.crypto.randomUUID();
        localStorage.setItem("user_uuid", uuid);
    }
    return uuid;
}

// ✅ CSRF Token
function getCSRFToken() {
    let cookieValue = null;
    let name = "csrftoken";
    if (document.cookie && document.cookie !== "") {
        let cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ✅ API call function
function sendInstall() {
    fetch("/track-install/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({
            device_id: getUserUUID(),
            device_info: navigator.userAgent,
        }),
    })
    .then(res => res.json())
    .then(data => console.log("Install tracked:", data))
    .catch(err => console.error("Tracker error:", err));
}

// Optional: automatic install tracking on page load
window.addEventListener("DOMContentLoaded", () => {
    sendInstall();
});
