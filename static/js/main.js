// Document Ready Function
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize date pickers
    const datePickers = document.querySelectorAll('.datepicker');
    if (datePickers.length > 0) {
        datePickers.forEach(function(picker) {
            // You can add a date picker library initialization here
            // For example, if using flatpickr:
            // flatpickr(picker, {
            //     minDate: "today",
            //     dateFormat: "Y-m-d"
            // });
        });
    }
    
    // Hall search filter toggle
    const filterToggle = document.getElementById('filter-toggle');
    if (filterToggle) {
        filterToggle.addEventListener('click', function() {
            const filterSection = document.getElementById('filter-section');
            if (filterSection.style.display === 'none') {
                filterSection.style.display = 'block';
                this.textContent = 'Hide Filters';
            } else {
                filterSection.style.display = 'none';
                this.textContent = 'Show Filters';
            }
        });
    }
    
    // Booking form validation
    const bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(event) {
            const eventDate = document.getElementById('event_date').value;
            const totalHours = document.getElementById('total_hours').value;
            
            if (!eventDate) {
                event.preventDefault();
                alert('Please select an event date');
                return false;
            }
            
            if (!totalHours || totalHours <= 0) {
                event.preventDefault();
                alert('Please enter valid number of hours');
                return false;
            }
            
            return true;
        });
    }
    
    // Dynamic price calculation for booking
    const calculatePrice = function() {
        const pricePerHour = parseFloat(document.getElementById('price_per_hour')?.value) || 0;
        const totalHours = parseFloat(document.getElementById('total_hours')?.value) || 0;
        const totalPeople = parseFloat(document.getElementById('total_people')?.value) || 0;
        
        let totalAmount = pricePerHour * totalHours;
        
        // If catering is selected
        const cateringSelect = document.getElementById('catering_service');
        if (cateringSelect && cateringSelect.value) {
            const cateringOption = cateringSelect.options[cateringSelect.selectedIndex];
            const pricePerPerson = parseFloat(cateringOption.getAttribute('data-price')) || 0;
            totalAmount += pricePerPerson * totalPeople;
        }
        
        // Display total
        const totalAmountElement = document.getElementById('total_amount');
        const displayTotalElement = document.getElementById('display_total');
        if (totalAmountElement && displayTotalElement) {
            totalAmountElement.value = totalAmount.toFixed(2);
            displayTotalElement.textContent = '₹' + totalAmount.toFixed(2);
        }
    };
    
    // Attach event listeners for price calculation
    const priceInputs = document.querySelectorAll('.price-input');
    if (priceInputs.length > 0) {
        priceInputs.forEach(function(input) {
            input.addEventListener('change', calculatePrice);
            input.addEventListener('keyup', calculatePrice);
        });
    }
});