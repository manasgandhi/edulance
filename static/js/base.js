// Placeholder for shared JavaScript/jQuery code
// Add any common scripts here if needed
window.setTimeout(function () {
    $('.toast').fadeOut('slow');
}, 5000);

// Enable Bootstrap tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
});

// CSRF token for AJAX requests
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Setup AJAX with CSRF token
$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

// Show notification function
function showNotification(message, type = 'info') {
    const toast = `
                <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="toast-header">
                        <strong class="me-auto">
                            ${type === 'error' ? '<i class="fas fa-exclamation-circle text-danger me-2"></i>Error' : ''}
                            ${type === 'success' ? '<i class="fas fa-check-circle text-success me-2"></i>Success' : ''}
                            ${type === 'warning' ? '<i class="fas fa-exclamation-triangle text-warning me-2"></i>Warning' : ''}
                            ${type === 'info' ? '<i class="fas fa-info-circle text-info me-2"></i>Info' : ''}
                        </strong>
                        <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                    <div class="toast-body">
                        ${message}
                    </div>
                </div>
            `;

    $('.toast-container').append(toast);

    // Remove toast after 5 seconds
    setTimeout(function () {
        $('.toast-container .toast').first().remove();
    }, 5000);
}

// Navbar scroll effect
$(window).scroll(function () {
    if ($(window).scrollTop() > 50) {
        $('.navbar').addClass('scrolled');
    } else {
        $('.navbar').removeClass('scrolled');
    }
}); 