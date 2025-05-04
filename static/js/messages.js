// Global tracking for form submissions
let replyFormSubmissions = {};

// Document ready handler
$(document).ready(function() {
    console.log('Messages JS initialized from AdminStatic/js/messages.js');
    
    // Initialize Bootstrap tabs
    if (typeof $('#messageTab a').tab === 'function') {
        $('#messageTab a').click(function(e) {
            e.preventDefault();
            $(this).tab('show');
        });
        
        // Activate first tab by default
        $('#messageTab a:first').tab('show');
    } else {
        console.warn('Bootstrap tabs not available');
    }
    
    // Enable tooltips if available
    if (typeof $('[data-toggle="tooltip"]').tooltip === 'function') {
        $('[data-toggle="tooltip"]').tooltip();
    }
    
    // Log messages counts for debugging
    console.log('Checking messages:');
    console.log('Inbox messages: ' + ($('#inbox .message-card').length || 0));
    console.log('All messages: ' + ($('#all .message-card').length || 0));
    
    // Make message cards clickable to expand/collapse on mobile
    $('.message-card').on('click', function(e) {
        if ($(window).width() < 768 && !$(e.target).closest('a, button').length) {
            $(this).find('.message-content').slideToggle();
        }
    });
    
    // Add pulse animation for buttons
    $('.message-actions .btn').on('mouseenter', function() {
        $(this).addClass('pulse-animation');
    }).on('mouseleave', function() {
        $(this).removeClass('pulse-animation');
    });
    
    // Add CSS animation for buttons
    const style = $('<style>').text(`
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        .pulse-animation {
            animation: pulse 0.5s ease-in-out;
        }
    `);
    $('head').append(style);
    
    // Improved confirmation for mark as read button
    $('.btn-mark-read').on('click', function(e) {
        e.preventDefault();
        
        const btn = $(this);
        const url = btn.attr('href');
        if (!url) {
            console.error('No URL found for mark as read button');
            return;
        }
        
        const messageId = url.split('/').slice(-2)[0];
        const senderName = btn.closest('.message-card').find('.sender-info h6').text() || 'this sender';
        
        // Create confirmation dialog
        const confirmDialog = $(`
            <div class="modal fade confirm-modal" id="confirmMarkRead${messageId}" tabindex="-1" role="dialog">
                <div class="modal-dialog modal-dialog-centered" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Confirm Action</h5>
                            <button type="button" class="close text-white" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <p>Mark this message from <strong>${senderName}</strong> as read?</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary confirm-action">Mark as Read</button>
                        </div>
                    </div>
                </div>
            </div>
        `);
        
        $('body').append(confirmDialog);
        confirmDialog.modal('show');
        
        confirmDialog.find('.confirm-action').on('click', function() {
            // Proceed with marking as read
            window.location.href = url;
        });
        
        confirmDialog.on('hidden.bs.modal', function() {
            confirmDialog.remove();
        });
    });
    
    // Enhanced reply form functionality with AJAX
    $('.reply-form').each(function() {
        const form = $(this);
        const formId = form.attr('id') || 'replyForm_' + Math.random().toString(36).substring(2);
        
        // If form doesn't have an ID, set one
        if (!form.attr('id')) {
            form.attr('id', formId);
        }
        
        form.on('submit', function(e) {
            e.preventDefault();
            
            // Prevent duplicate submissions
            if (replyFormSubmissions[formId]) {
                console.log('Form already submitted, preventing duplicate submission');
                return false;
            }
            
            const submitBtn = form.find('.send-reply-btn');
            const spinner = submitBtn.find('.spinner-border');
            const successAlert = form.find('.reply-success');
            const errorAlert = form.find('.reply-error');
            const textarea = form.find('textarea');
            
            // For debugging - log form data
            console.log('Submitting reply form:', formId);
            
            // Hide any existing alerts
            successAlert.hide();
            errorAlert.hide();
            
            // Validate form
            if (!textarea.val().trim()) {
                textarea.addClass('is-invalid');
                return false;
            } else {
                textarea.removeClass('is-invalid');
            }
            
            // Mark form as being submitted
            replyFormSubmissions[formId] = true;
            
            // Disable button and show spinner
            submitBtn.prop('disabled', true);
            if (spinner.length) {
                spinner.show();
            } else {
                console.warn('Spinner element not found in form', formId);
            }
            
            // Get form data
            const formData = new FormData(form[0]);
            
            // For debugging - log form data entries
            console.log('Form data:');
            for (let pair of formData.entries()) {
                console.log(pair[0] + ': ' + pair[1]);
            }
            
            // Check if we should use fallback mode
            if (form.data('fallback') === true) {
                useDirectSubmission();
                return false;
            }
            
            // Set a timeout to prevent infinite waiting
            const ajaxTimeout = setTimeout(function() {
                console.error('AJAX request timed out after 10 seconds');
                ajaxError(null, 'timeout', 'Request timed out');
            }, 10000);
            
            // Function to handle ajax errors
            function ajaxError(xhr, status, error) {
                clearTimeout(ajaxTimeout);
                
                console.error('Reply error:', status, error);
                if (xhr) {
                    console.error('Response:', xhr.responseText);
                }
                
                // Reset submission tracking
                replyFormSubmissions[formId] = false;
                
                // Mark form as failed for backup handler
                form.data('ajax-failed', true);
                
                // Show error message
                let errorMsg = 'Could not send message. Please try again.';
                
                if (xhr && xhr.status === 403) {
                    errorMsg = 'Session expired. Please log in again.';
                } else if (xhr && xhr.status === 500) {
                    errorMsg = 'Server error. Please try again or contact support.';
                    // Set fallback mode for next attempt
                    form.data('fallback', true);
                    errorMsg += '<br><small>Next attempt will use traditional form submission.</small>';
                } else if (status === 'timeout') {
                    errorMsg = 'Request timed out. Please try again.';
                    form.data('fallback', true);
                } else if (xhr) {
                    try {
                        const responseData = JSON.parse(xhr.responseText);
                        if (responseData && responseData.error) {
                            errorMsg = responseData.error;
                        }
                    } catch (e) {
                        console.error('Error parsing response:', e);
                    }
                }
                
                errorAlert.html(`<i class="fas fa-exclamation-circle mr-2"></i> Error: ${errorMsg}`);
                errorAlert.slideDown();
                
                // Re-enable button and hide spinner
                submitBtn.prop('disabled', false);
                if (spinner.length) {
                    spinner.hide();
                }
            }
            
            // Function to use direct form submission
            function useDirectSubmission() {
                console.log('Using direct form submission');
                // Reset submission tracking
                replyFormSubmissions[formId] = false;
                
                // Set form to open in new tab to prevent infinite loops
                form.attr('target', '_blank');
                
                // Remember current action
                const originalAction = form.attr('action');
                
                // Make sure we have all data
                if (!formData.has('csrfmiddlewaretoken')) {
                    console.warn('CSRF token missing, trying to add it manually');
                    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                    if (csrftoken) {
                        formData.append('csrfmiddlewaretoken', csrftoken);
                    }
                }
                
                // Submit the form
                console.log('Submitting form directly to', originalAction);
                form[0].submit();
                
                // Reset form
                setTimeout(function() {
                    form.attr('target', '');
                    submitBtn.prop('disabled', false);
                    if (spinner.length) {
                        spinner.hide();
                    }
                    
                    // Show success message after a short delay
                    setTimeout(function() {
                        successAlert.slideDown();
                        // Clear the textarea
                        textarea.val('');
                    }, 500);
                }, 1000);
                
                return true;
            }
            
            // Send AJAX request
            $.ajax({
                url: form.attr('action'),
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                timeout: 10000, // 10 second timeout
                success: function(response) {
                    clearTimeout(ajaxTimeout);
                    console.log('Reply success:', response);
                    
                    // Show success message
                    successAlert.slideDown();
                    
                    // Clear the textarea
                    textarea.val('');
                    
                    // Automatically close modal after delay
                    setTimeout(function() {
                        // Close the modal
                        form.closest('.modal').modal('hide');
                        
                        // Reset submission tracking after modal is hidden
                        setTimeout(function() {
                            replyFormSubmissions[formId] = false;
                        }, 500);
                        
                        // Show notification instead of reloading to prevent loop
                        const notification = $(`
                            <div class="alert alert-success alert-dismissible fade show" role="alert" style="position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 350px;">
                                <i class="fas fa-check-circle mr-2"></i> Your message has been sent successfully!
                                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                                    <span aria-hidden="true">&times;</span>
                                </button>
                            </div>
                        `);
                        $('body').append(notification);
                        
                        // Remove notification after 5 seconds
                        setTimeout(function() {
                            notification.alert('close');
                        }, 5000);
                    }, 1500);
                },
                error: ajaxError,
                complete: function() {
                    // This function will be called regardless of success or error
                    // We already handle re-enabling the button in the success and error callbacks
                }
            });
        });
    });
    
    // Add CSS for form validation
    const formStyle = $('<style>').text(`
        .reply-form textarea.is-invalid {
            border-color: var(--danger-color, #f44336);
            box-shadow: 0 0 0 0.2rem rgba(244, 67, 54, 0.25);
        }
        .reply-success, .reply-error {
            margin-bottom: 15px;
            border-radius: 8px;
        }
        .send-reply-btn:disabled {
            cursor: not-allowed;
            opacity: 0.7;
        }
    `);
    $('head').append(formStyle);
    
    // Add ripple effect to buttons
    $('.btn').on('click', function(e) {
        const btn = $(this);
        
        // Create ripple element
        const ripple = $('<span class="ripple-effect"></span>');
        btn.append(ripple);
        
        // Get position
        const btnOffset = btn.offset();
        if (!btnOffset) return;
        
        const xPos = e.pageX - btnOffset.left;
        const yPos = e.pageY - btnOffset.top;
        
        // Add ripple style
        ripple.css({
            top: yPos + 'px',
            left: xPos + 'px'
        }).addClass('animate');
        
        // Remove ripple after animation
        setTimeout(function() {
            ripple.remove();
        }, 600);
    });
    
    // Add CSS for ripple effect
    const rippleStyle = $('<style>').text(`
        .btn {
            position: relative;
            overflow: hidden;
        }
        .ripple-effect {
            position: absolute;
            border-radius: 50%;
            background-color: rgba(255, 255, 255, 0.4);
            width: 100px;
            height: 100px;
            margin-top: -50px;
            margin-left: -50px;
            transform: scale(0);
            opacity: 1;
            pointer-events: none;
        }
        .ripple-effect.animate {
            animation: ripple 0.6s linear;
        }
        @keyframes ripple {
            100% {
                transform: scale(2.5);
                opacity: 0;
            }
        }
    `);
    $('head').append(rippleStyle);
});
