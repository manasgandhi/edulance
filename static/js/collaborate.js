$(document).ready(function () {
    // Initialize Select2 for skills fields
    // $('#skills, #edit-skills').select2({
    //     placeholder: "Select required skills",
    //     allowClear: true,
    //     width: '100%',
    //     dropdownParent: $('#editPostModal') // Attach dropdown to modal to fix positioning
    // });

    // Prevent modal from closing when clicking on Select2 dropdown
    $(document).on('click', '.select2-container', function (e) {
        e.stopPropagation(); // Stop click event from bubbling to modal backdrop
    });

    // Create Post Form Submission
    $('#createPostForm').on('submit', function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        const $form = $(this);
        const $submitBtn = $('#submitBtn');
        const originalBtnHtml = `<i class="fas fa-paper-plane me-2"></i>Create Post`;

        // Disable submit button
        $submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i>Creating...');

        // Prepare form data
        let deadlineValue = $form.find('#deadline').val();
        if (deadlineValue) {
            // Convert deadline to ISO 8601 format with UTC timezone (Z)
            const deadlineDate = new Date(deadlineValue);
            deadlineValue = deadlineDate.toISOString();
        }

        const formData = {
            title: $form.find('#title').val(),
            description: $form.find('#description').val(),
            activity_type: $form.find('#activity_type').val(),
            skills: $form.find('#skills').val() || [], // Ensure skills is an array, even if empty
            deadline: deadlineValue || null
        };

        $.ajax({
            url: '/collaborate/api/posts/',
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function (response) {
                showMessage('Post created successfully!', 'success');
                $form[0].reset();
                $('#skills').val(null).trigger('change'); // Reset Select2
                $('#createPostModal').modal('hide');

                // Add fadeIn class to make message visibly animate
                $('#messages-container .alert').addClass('fade show');

                refreshTab(response.activity_type);
            },
            complete: function () {
                // Re-enable button and reset original HTML
                $submitBtn.prop('disabled', false).html(originalBtnHtml);
            },
            error: function (xhr) {
                const errors = xhr.responseJSON ? xhr.responseJSON : { error: 'An error occurred' };
                showMessage(getErrorMessage(errors), 'danger');
            }
        });
    });

    // Edit Post Form Submission
    $('#edit-post-form').on('submit', function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        const $form = $(this);
        const $submitBtn = $form.find('button[type="submit"]');
        const originalBtnHtml = `<i class="fas fa-save me-2"></i>Save Changes`;

        // Disable submit button
        $submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i>Saving...');

        // Prepare form data
        let deadlineValue = $form.find('#edit-deadline').val();
        if (deadlineValue) {
            // Convert deadline to ISO 8601 format with UTC timezone (Z)
            const deadlineDate = new Date(deadlineValue);
            deadlineValue = deadlineDate.toISOString();
        }

        const formData = {
            title: $form.find('#edit-title').val(),
            description: $form.find('#edit-description').val(),
            activity_type: $form.find('#edit-activity').val(),
            skills: $form.find('#edit-skills').val() || [], // Ensure skills is an array, even if empty
            deadline: deadlineValue || null
        };

        const postId = $form.find('#post-id').val();

        $.ajax({
            url: `/collaborate/api/posts/${postId}/`,
            type: 'PATCH',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function (response) {
                showMessage('Post updated successfully!', 'success');
                $('#editPostModal').modal('hide');
                // Refresh the current page to reflect changes
                window.location.reload();
            },
            complete: function () {
                // Re-enable button and reset original HTML
                $submitBtn.prop('disabled', false).html(originalBtnHtml);
            },
            error: function (xhr) {
                const errors = xhr.responseJSON ? xhr.responseJSON : { error: 'An error occurred' };
                showMessage(getErrorMessage(errors), 'danger');
            }
        });
    });

    // Join Team Button Click
    $(document).on('click', '.join-team-btn', function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        const $btn = $(this);
        const postId = $btn.data('post-id');
        const originalHtml = $btn.html();

        $btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i>Joining...');

        $.ajax({
            url: `/collaborate/api/posts/${postId}/join/`,
            type: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function (response) {
                showMessage(response.message, 'success');

            },
            error: function (xhr) {
                const errors = xhr.responseJSON ? xhr.responseJSON : { error: 'An error occurred' };
                showMessage(getErrorMessage(errors), 'danger');
            },
            complete: function () {
                $btn.prop('disabled', false).html(originalHtml);

            }
        });
    });

    // Function to show messages
    function showMessage(message, type) {
        const messageHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        $('#messages-container').html(messageHtml).hide().fadeIn(500); // Animate appearance

        setTimeout(() => {
            $('.alert').fadeOut(500, function () {
                $(this).remove();
            });
        }, 5000);
    }

    // Function to get error message from response
    function getErrorMessage(errors) {
        if (typeof errors === 'string') return errors;
        if (errors.error) return errors.error;
        return Object.values(errors).flat().join(', ');
    }

    // Function to refresh tab content
    function refreshTab(tabId) {
        $.ajax({
            url: `/collaborate/api/posts/?activity_type=${tabId}`,
            type: 'GET',
            success: function (response) {
                const $tabContent = $(`#${tabId}`);
                if (response.results.length === 0) {
                    $tabContent.html(`
                        <div class="empty-state">
                            <i class="fas fa-${getTabIcon(tabId)}"></i>
                            <h4>${getTabTitle(tabId)}</h4>
                            <p>No ${tabId} collaboration posts available yet. Be the first to create one!</p>
                        </div>
                    `);
                } else {
                    let html = '<div class="row row-cols-1 row-cols-md-2 row-cols-xl-3 g-4">';
                    response.results.forEach(post => {
                        html += generatePostCard(post);
                    });
                    html += '</div>';
                    $tabContent.html(html);
                }
                // Update badge count
                $(`#${tabId}-tab .badge`).text(response.count);
            }
        });
    }

    // Helper function to get tab icon
    function getTabIcon(tabId) {
        const icons = {
            learning: 'book-open',
            hackathon: 'code',
            project: 'project-diagram'
        };
        return icons[tabId] || 'book-open';
    }

    // Helper function to get tab title
    function getTabTitle(tabId) {
        const titles = {
            learning: 'Learning Opportunities',
            hackathon: 'Hackathon Projects',
            project: 'Project Collaborations'
        };
        return titles[tabId] || 'Collaborations';
    }

    // Function to generate post card HTML
    function generatePostCard(post) {
        return `
            <div class="col">
                <div class="card h-100 shadow-sm border-0">
                    <div class="card-body d-flex flex-column">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="card-title text-primary fw-bold mb-0">${post.title}</h5>
                            <span class="badge bg-secondary">${post.activity_type_display}</span>
                        </div>
                        <p class="text-muted small mb-2">
                            <i class="fas fa-user me-1"></i>By ${post.user.full_name || post.user.username}
                            <span class="ms-2">
                                <i class="fas fa-clock me-1"></i>${new Date(post.created_at).toLocaleDateString()}
                            </span>
                        </p>
                        <p class="card-text text-muted mb-3 flex-grow-1">${post.description.substring(0, 100)}...</p>
                        ${post.deadline ? `
                            <div class="mb-2">
                                <small class="text-warning">
                                    <i class="fas fa-calendar-alt me-1"></i>
                                    Deadline: ${new Date(post.deadline).toLocaleString()}
                                </small>
                            </div>
                        ` : ''}
                        <div class="mt-auto">
                            ${post.required_skills.length ? `
                                <p class="mb-2"><strong class="text-dark">Required Skills:</strong></p>
                                <div class="d-flex flex-wrap gap-2 mb-3">
                                    ${post.required_skills.map(skill => `<span class="badge bg-primary rounded-pill">${skill.name}</span>`).join('')}
                                </div>
                            ` : ''}
                            <div class="d-flex gap-2">
                                <a href="/collaborate/posts/${post.id}/" class="btn btn-outline-primary btn-sm flex-fill">
                                    <i class="fas fa-eye me-1"></i>View Details
                                </a>
                                ${post.is_owner ? `
                                    <span class="btn btn-success btn-sm flex-fill disabled">
                                        <i class="fas fa-check me-1"></i>Your Post
                                    </span>
                                ` : `
                                    <button class="btn btn-primary btn-sm flex-fill join-team-btn" data-post-id="${post.id}">
                                        <i class="fas fa-users me-1"></i>Join Team
                                    </button>
                                `}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Function to get cookie
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
});