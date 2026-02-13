const API = "https://qr-system-wfs4.onrender.com";

// Signup
function signup() {
    const name = document.getElementById("signupName").value;
    const email = document.getElementById("signupEmail").value;
    const password = document.getElementById("signupPass").value;
    fetch(`${API}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password })
    })
        .then(res => res.json())
        .then(data => alert(data.message))
}

// Login
function login() {
    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPass").value;
    fetch(`${API}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                localStorage.setItem("userEmail", email);
                window.location.href = "menu.html";
            } else {
                alert(data.message);
            }
        })
}

// Generate QR
function generateQR() {
    const url = document.getElementById("urlInput").value;
    const email = localStorage.getItem("userEmail");
    fetch(`${API}/generate-qr`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, email })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                document.getElementById("qrResult").innerHTML = `<img src="data:image/png;base64,${data.qr_base64}">`;
            }
        })
}

// Scan QR
function scanQR() {
    const file = document.getElementById("qrFile").files[0];
    const formData = new FormData();
    formData.append("file", file);
    fetch(`${API}/scan-qr`, { method: "POST", body: formData })
        .then(res => res.json())
        .then(data => {
            console.log(data);
            localStorage.setItem("scanResult", JSON.stringify(data));
            window.location.href = "result.html";
            // if (data.success) {
            //     const status = data.registered ? "Registered" : "Not Registered";
            //     document.getElementById("scanResult").innerHTML = `<p>URL: ${data.url}</p><p>Status: ${status}</p>`;
            // } else {
            //     alert(data.message);
            // }
        })


}
{
    const scanResult = document.getElementById("scanResult");

    if (scanResult) {
        const data = JSON.parse(localStorage.getItem("scanResult"));
        if (data) {
            if (data.success) {
                const status = data.registered ? "Registered" : "Not Registered";
                scanResult.innerHTML = `<p>URL: ${data.url}</p><p>Status: ${status}</p>`;
            } else {
                scanResult.innerHTML = `<p>Your image could not have any QR code</p>`;

            }
        } else {
            scanResult.innerHTML = `<p>You have not scanned any QR code</p>`;
        }
    }
}