// static/js/auto_refresh.js

function autoRefreshPage() {
    setTimeout(function() {
        window.location.reload();
    }, 60000); // 60000 milliseconds = 1 minute
}

window.onload = autoRefreshPage;
