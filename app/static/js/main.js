// Date picker initialization
document.addEventListener('DOMContentLoaded', function() {
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

    // Initialize chart if we're on the report page and have data
    if (typeof measurementData !== 'undefined' && document.getElementById('bpChart')) {
        initializeChart();
    }

    // Add measurements form handling
    const measurementsForm = document.getElementById('measurements-form');
    if (measurementsForm) {
        measurementsForm.addEventListener('submit', submitMeasurements);
    }
});

// Chart initialization
function initializeChart() {
    const ctx = document.getElementById('bpChart').getContext('2d');
    const dates = measurementData.map(m => m.date);
    const systolic = measurementData.map(m => m.systolic);
    const diastolic = measurementData.map(m => m.diastolic);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Systolic',
                    data: systolic,
                    borderColor: '#FF6384',
                    fill: false
                },
                {
                    label: 'Diastolic',
                    data: diastolic,
                    borderColor: '#36A2EB',
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    min: Math.min(...diastolic) - 10,
                    max: Math.max(...systolic) + 10
                }
            }
        }
    });
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
    let url = `/user/${userId}/report?type=${type}`;
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

// PDF generation
function generatePDFReport() {
    const form = document.getElementById('pdfForm');
    const startDate = document.getElementById('pdfStartDate');
    const endDate = document.getElementById('pdfEndDate');
    
    // Set current date range
    startDate.value = new URLSearchParams(window.location.search).get('start_date');
    endDate.value = new URLSearchParams(window.location.search).get('end_date');
    
    form.submit();
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

// Print functionality
function printReport() {
    generatePDFReport();
}