// Stok Takip Sistemi - Ana JavaScript dosyası

document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltip'lerini etkinleştir
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Alert'leri otomatik kapat
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// Yardımcı fonksiyonlar
function formatNumber(num) {
    return new Intl.NumberFormat('tr-TR').format(num);
}

function formatCurrency(num) {
    return new Intl.NumberFormat('tr-TR', {
        style: 'currency',
        currency: 'TRY'
    }).format(num);
}

// Loading spinner göster/gizle
function showLoading(element) {
    element.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Yükleniyor...';
    element.disabled = true;
}

function hideLoading(element, originalText) {
    element.innerHTML = originalText;
    element.disabled = false;
}