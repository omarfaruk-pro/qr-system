const API = "https://qr-system-wfs4.onrender.com";
{
    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");

    const startBtn = document.getElementById("startBtn");
    const loader = document.getElementById("loader");
    const statusText = document.getElementById("status");

    let scanning = false;

    startBtn.onclick = () => {
        startBtn.style.display = "none";
        loader.style.display = "block";
        statusText.innerText = "Camera starting...";
        startCamera();
    };

    function startCamera() {
        navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
            .then(stream => {
                video.srcObject = stream;
                video.hidden = false;
                scanning = true;
                requestAnimationFrame(scanQR);
            })
            .catch(() => {
                statusText.innerText = "Camera permission denied";
                loader.style.display = "none";
            });
    }

    function scanQR() {
        if (!scanning) return;

        if (video.readyState === video.HAVE_ENOUGH_DATA) {
            canvas.height = video.videoHeight;
            canvas.width = video.videoWidth;
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const code = jsQR(imageData.data, imageData.width, imageData.height);

            if (code) {
                scanning = false;
                loader.innerText = "QR detected. Checking...";
                sendToBackend(code.data);
                return;
            }
        }
        requestAnimationFrame(scanQR);
    }

    function sendToBackend(url) {
        console.log(url)

        fetch(`${API}/scan-qr-url`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                url: url
            })
        })
            .then(res => res.json())
            .then(data => {
                localStorage.setItem("scanResult", JSON.stringify(data));
                window.location.href = "result.html";
            });
    }

}