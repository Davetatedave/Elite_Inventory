var date_filter_button=document.getElementById('date_filter_button');
var date_error=document.getElementById('date_error');
var start_date=document.getElementById('start_date');
var end_date=document.getElementById('end_date');

function valiDate() {
    if (start_date.value > end_date.value) {
        console.log('start date is greater than end date');
        date_error.innerHTML='Start date cannot be greater than end date';
        date_error.style.display='block';
        date_filter_button.disabled=true;
    }
    else {
        console.log('start date is less than end date');
        date_filter_button.disabled=false;
        date_error.style.display='none';
    }
    }
    $(document).ready( function () {
        $('#myTable').DataTable({
            ajax: {
                url: '/inventoryAjax/',  // Replace with your Django view URL
                dataSrc: 'data',     // Data property name in the JSON response
            },
            columns: [
                { data: 'imei' },
                { data: 'model' },
                { data: 'capacity' },
                { data: 'color' },
                { data: 'grade' },
            ],
            lengthMenu: [10, 25, 50],  // Define the dropdown menu options for record per page
            pageLength: 10,
            processing: true,
            serverSide: true           // Define the default length per page
        });
    } );

    
    document.addEventListener('DOMContentLoaded', function() {
        const clearButtons = document.querySelectorAll('.clear-button');
    
        clearButtons.forEach(function(clearButton) {
            clearButton.addEventListener('click', function() {
                const dropdownId = this.getAttribute('data-dropdown');
                const checkboxes = document.querySelectorAll(`input[name="models"]`);
    
                checkboxes.forEach(function(checkbox) {
                    checkbox.checked = false;
                });
            });
        });
    });