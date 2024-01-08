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

