document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle initialization
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.body.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);
        
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.body.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    // Disclaimer modal handling
    const disclaimerTrigger = document.getElementById('disclaimer-trigger');
    const disclaimerModal = document.getElementById('disclaimer-modal');
    if (disclaimerTrigger && disclaimerModal) {
        disclaimerTrigger.addEventListener('click', function() {
            disclaimerModal.style.display = 'block';
        });

        const closeButtons = disclaimerModal.getElementsByClassName('close-modal');
        Array.from(closeButtons).forEach(button => {
            button.addEventListener('click', function() {
                disclaimerModal.style.display = 'none';
            });
        });
    }

    // Registration form handling
    const registrationForm = document.getElementById('registrationForm');
    if (registrationForm) {
        registrationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            fetch('/register', {
                method: 'POST',
                body: new FormData(registrationForm)
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    alert('User registered successfully');
                    window.location.href = '/';
                }
            })
            .catch(error => {
                alert('Error registering user');
            });
        });
    }

    // Initialize Flatpickr for date inputs
    const dateConfig = {
        dateFormat: "d/m/Y",
        altFormat: "d/m/Y",
        allowInput: true,
        maxDate: "today"
    };
    
    if (document.getElementById('startDate')) {
        flatpickr("#startDate", dateConfig);
    }
    if (document.getElementById('endDate')) {
        flatpickr("#endDate", dateConfig);
    }
    if (document.getElementById('date_of_birth')) {
        flatpickr("#date_of_birth", dateConfig);
    }

    // Add measurements form handling
    const measurementsForm = document.getElementById('measurements-form');
    if (measurementsForm) {
        measurementsForm.addEventListener('submit', submitMeasurements);
    }

    // Add CSV upload handler
    const csvUpload = document.getElementById('csv-upload');
    if (csvUpload) {
        csvUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            const userId = window.location.pathname.split('/')[2];
            uploadCSV(userId, file);
        });
    }

    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        const modals = document.getElementsByClassName('modal');
        Array.from(modals).forEach(modal => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
});

// Theme icon update function
function updateThemeIcon(theme) {
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
        themeIcon.src = theme === 'light' 
            ? '/static/icons/mode_dark.svg'
            : '/static/icons/mode_light.svg';
        themeIcon.alt = theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode';
    }
}

// Measurements form handling
function submitMeasurements(event) {
    event.preventDefault();
    const form = event.target;
    const userId = window.location.pathname.split('/')[2];
    
    fetch(`/user/${userId}/add_measurements`, {
        method: 'POST',
        body: new FormData(form)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            window.location.href = `/user/${userId}`;
        }
    })
    .catch(error => {
        alert('An error occurred while saving measurements');
    });
}

function confirmCancel() {
    document.getElementById('cancel-modal').style.display = 'block';
}

function closeCancelModal() {
    document.getElementById('cancel-modal').style.display = 'none';
}

// Report loading functions
function loadReport(type) {
    const userId = window.location.pathname.split('/')[2];
    const url = `/user/${userId}/report?type=${type}`;
    window.location.href = url;
}

function showDateRangeModal() {
    document.getElementById('dateRangeModal').style.display = 'block';
}

function closeDateRangeModal() {
    document.getElementById('dateRangeModal').style.display = 'none';
}

function closeNoDataModal() {
    document.getElementById('noDataModal').style.display = 'none';
}

function applyDateRange() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    if (!startDate || !endDate) {
        alert('Please select both start and end dates');
        return;
    }

    const userId = window.location.pathname.split('/')[2];
    const url = `/user/${userId}/report?type=custom&start_date=${startDate}&end_date=${endDate}`;
    window.location.href = url;
}

// CSV upload function
function uploadCSV(userId, file) {
    if (!file) return;
    
    if (!file.name.endsWith('.csv')) {
        document.getElementById('csv-error-message').textContent = 'Please select a CSV file';
        document.getElementById('csv-error-modal').style.display = 'block';
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch(`/user/${userId}/import_csv`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('csv-error-message').textContent = data.error;
            document.getElementById('csv-error-modal').style.display = 'block';
        } else {
            document.getElementById('csv-success-message').textContent = data.message;
            document.getElementById('csv-success-modal').style.display = 'block';
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        }
    })
    .catch(error => {
        document.getElementById('csv-error-message').textContent = 'An error occurred while uploading the file';
        document.getElementById('csv-error-modal').style.display = 'block';
    });
}

// PDF generation
function printReport() {
    const form = document.getElementById('pdfForm');
    const startDate = document.getElementById('pdfStartDate');
    const endDate = document.getElementById('pdfEndDate');
    
    // Get dates from the report header
    const reportHeader = document.querySelector('.report-container h2').textContent;
    const dates = reportHeader.match(/(\d{2}\/\d{2}\/\d{4})/g);
    
    if (dates && dates.length >= 2) {
        startDate.value = dates[0];
        endDate.value = dates[1];
        form.submit();
    } else {
        alert('Error: Could not determine report dates');
    }
}

// User deletion confirmation
function confirmDelete(userId) {
    document.getElementById('delete-modal').style.display = 'block';
}

function closeDeleteModal() {
    document.getElementById('delete-modal').style.display = 'none';
}

function closeDeleteConfirmationModal() {
    document.getElementById('delete-confirmation-modal').style.display = 'none';
}

function proceedWithDelete() {
    document.getElementById('delete-modal').style.display = 'none';
    document.getElementById('delete-confirmation-modal').style.display = 'block';
}

function finalizeDelete(userId) {
    const confirmationInput = document.getElementById('delete-confirmation-input');
    if (confirmationInput.value !== 'DELETE') {
        alert('Please type DELETE exactly as shown to confirm');
        return;
    }

    fetch(`/user/${userId}/delete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `confirmation=DELETE`
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            window.location.href = '/';
        }
    })
    .catch(error => {
        alert('An error occurred while deleting the user');
    });
}