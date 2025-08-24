// static/js/install_tracker.js
(function () {
  // -----------------------------
  // Helper: Unique device ID (persisted)
  // -----------------------------
  function getDeviceId() {
    let deviceId = localStorage.getItem("device_id");
    if (!deviceId) {
      if (window.crypto && crypto.randomUUID) {
        deviceId = crypto.randomUUID();
      } else {
        // Fallback UUID v4
        deviceId = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
          const r = (Math.random() * 16) | 0;
          const v = c === "x" ? r : (r & 0x3) | 0x8;
          return v.toString(16);
        });
      }
      localStorage.setItem("device_id", deviceId);
    }
    return deviceId;
  }

  // -----------------------------
  // Helper: CSRF token
  // -----------------------------
  function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(";") : [];
    for (let c of cookies) {
      c = c.trim();
      if (c.startsWith(name + "=")) {
        return decodeURIComponent(c.substring(name.length + 1));
      }
    }
    return null;
  }
  function csrfHeader() {
    const token = getCookie("csrftoken");
    return token ? { "X-CSRFToken": token } : {};
  }

  // -----------------------------
  // Helper: POST to server
  // -----------------------------
  function sendData(url, payload) {
    return fetch(url, {
      method: "POST",
      headers: Object.assign(
        { "Content-Type": "application/json" },
        csrfHeader()
      ),
      body: JSON.stringify(payload),
      credentials: "same-origin",
    })
      .then((r) => r.json())
      .catch((e) => {
        console.error("Tracker error:", e);
        return { status: "error", message: e?.message || "network" };
      });
  }

  // -----------------------------
  // Install event (PWA added to home screen)
  // -----------------------------
  window.addEventListener("appinstalled", function () {
    const payload = {
      device_id: getDeviceId(),
      device_info: navigator.userAgent || "",
    };
    sendData("/track-install/", payload).then((res) =>
      console.log("Install track:", res)
    );
    // Reset uninstall flag because app is installed now
    localStorage.removeItem("uninstalledFlag");
  });

  // -----------------------------
  // Uninstall detection (best-effort)
  // If user opens site in browser (not standalone), and we haven't sent uninstall yet.
  // -----------------------------
  function checkAppStatus() {
    const isStandalone =
      window.matchMedia("(display-mode: standalone)").matches ||
      window.navigator.standalone;

    const deviceId = getDeviceId();

    if (!isStandalone) {
      const flag = localStorage.getItem("uninstalledFlag");
      if (flag !== "true") {
        const payload = {
          device_id: deviceId,
          device_info: navigator.userAgent || "",
        };
        sendData("/track-uninstall/", payload).then((res) =>
          console.log("Uninstall track:", res)
        );
        localStorage.setItem("uninstalledFlag", "true");
      }
    } else {
      // If running as app, clear uninstall flag
      localStorage.removeItem("uninstalledFlag");
    }
  }

  window.addEventListener("load", checkAppStatus);
})();
