$(document).ready(function() {

    $('#checkAvailabilityBtn').click(function() {
        $.get('/check_availability', function(data) {
            if (data.status === 'success') {
                $('#availabilityStatus').text(`Available Slot: ${data.slot_id}`);
            } else {
                $('#availabilityStatus').text(data.message);
            }
        });
    });

    $('#ticketForm').submit(function(event) {
        event.preventDefault();
        const vehicleNumber = $('#vehicle_number').val();
        
        $.post('/create_ticket', { vehicle_number: vehicleNumber }, function(data) {
            if (data.status === 'success') {
                $('#ticketResult').html(`
                    <p>Ticket ID: ${data.ticket_id}</p>
                    <p>Expiry Time: ${data.expiry_time}</p>
                    <img src="${data.qr_code}" alt="QR Code">
                `);
            } else {
                $('#ticketResult').text(data.message);
            }
        });
    });
});
