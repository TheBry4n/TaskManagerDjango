// ===== MAIN JAVASCRIPT =====

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(function(card) {
        card.classList.add('fade-in');
    });

    // Form validation feedback
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// Utility function for showing messages
function showMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}

// Auto-update task status every 30 seconds
function autoUpdateTaskStatus() {
    setInterval(function() {
        fetch('/tasks/api/status/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            // Update the statistics cards
            const totalElement = document.querySelector('.card.bg-primary h3');
            const activeElement = document.querySelector('.card.bg-success h3');
            const completedElement = document.querySelector('.card.bg-info h3');
            const failedElement = document.querySelector('.card.bg-danger h3');
            
            if (totalElement) {
                const total = data.active_count + data.completed_count + data.failed_count;
                totalElement.textContent = total;
            }
            if (activeElement) {
                activeElement.textContent = data.active_count;
            }
            if (completedElement) {
                completedElement.textContent = data.completed_count;
            }
            if (failedElement) {
                failedElement.textContent = data.failed_count;
            }
            
            // If any tasks were updated, reload the page to show the changes
            if (data.updated_count > 0) {
                console.log(`${data.updated_count} tasks were automatically updated to failed status`);
                // Reload the page to show the updated task lists
                window.location.reload();
            }
        })
        .catch(error => {
            console.error('Error updating task status:', error);
        });
    }, 30000); // Check every 30 seconds
}





// Initialize auto-update on task list page
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the task list page
    if (window.location.pathname.includes('/tasks/') && !window.location.pathname.includes('/create') && !window.location.pathname.includes('/update')) {
        autoUpdateTaskStatus();
    }
});
