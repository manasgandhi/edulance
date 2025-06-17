$(document).ready(function () {
    $('.skills-select').select2({
        tags: true,
        tokenSeparators: [',', ' '],
        placeholder: "Select or type skills",
        allowClear: true
    });

    function showToast(message, type) {
        const toastHtml = `
            <div class="toast toast-container ${type === 'success' ? 'toast-success' : 'toast-error'}" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header mb-0">
                    <strong class="me-auto">${type === 'success' ? 'Success' : 'Error'}</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>`;
        $('body').append(toastHtml);
        $('.toast').toast({ delay: 1800000 }).toast('show');
        // setTimeout(() => $('.toast').remove(), 5500);
    }

    $('#profile_picture').change(function (e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                $('.profile-picture-preview').attr('src', e.target.result);
            }
            reader.readAsDataURL(file);
        }
    });

    $('#profile-form').submit(function (e) {
        e.preventDefault();
        const formData = new FormData(this);
        var updateProfileUrl = $('#updateProfileButton').data('url');


        $.ajax({
            url: updateProfileUrl,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.success) {
                    showToast(response.success, 'success');
                } else {
                    showToast(response.error, 'error');
                }
            },
            error: function () {
                showToast('An error occurred while updating profile', 'error');
            }
        });
    });

    $('#skills-form').submit(function (e) {
        e.preventDefault();
        const selectedSkills = $('.skills-select').select2('data').map(item => ({
            id: item.id,
            name: item.text,
            isNew: item.id.includes('select2-')
        }));
        var updateSkillsUrl = $('#updateSkillsButton').data('url');

    
        $.ajax({
            url: updateSkillsUrl,
            type: 'POST',
            data: {
                skills: JSON.stringify(selectedSkills),
                // csrfmiddlewaretoken: '{{ csrf_token }}'
            },
            success: function (response) {
                if (response.success) {
                    showToast(response.success, 'success');
                    location.reload();
                } else {
                    showToast(response.error, 'error');
                }
            },
            error: function () {
                showToast('An error occurred while updating skills', 'error');
            }
        });
    });

    $('#resume').change(function (e) {
        const file = e.target.files[0];
        const fileDisplay = $('#fileDisplay');
        const fileText = $('#fileText');
        const fileInfo = $('#fileInfo');
        const uploadButton = $('#uploadButton');

        if (file) {
            if (file.type !== 'application/pdf') {
                showToast('Please select a PDF file only.', 'error');
                this.value = '';
                return;
            }

            fileDisplay.addClass('file-selected');
            fileText.html('<i class="fas fa-check me-2"></i>File Selected');
            fileInfo.text(file.name).show();
            uploadButton.prop('disabled', false);
        } else {
            fileDisplay.removeClass('file-selected');
            fileText.html('<i class="fas fa-file-pdf me-2"></i>Choose PDF file');
            fileInfo.hide();
            uploadButton.prop('disabled', true);
        }
    });
});