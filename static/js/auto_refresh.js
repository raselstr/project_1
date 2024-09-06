// static/js/auto_refresh.js

function autoRefreshPage() {
    console.log("Halaman akan di-refresh setelah 1 menit");
    setTimeout(function() {
        window.location.reload();
    }, 60000); // 60000 milliseconds = 1 minute
}

window.onload = autoRefreshPage;
