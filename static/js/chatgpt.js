$.ajaxSetup({
    headers: { 'X-CSRFToken': csrf_token },
    type: 'POST',
});

$(document).ready(function(){
    $('#send').click(function() {
        const formData = {};
        const msger_input = $('#msg').val().trim();

        formData['msger_input'] = msger_input;

        $('.msger-chat').append(`<div class="question_message"> Question : ${msger_input}</div>`);

        // Add loading bar
        const loadingElement = $('<div class="loading">Loading</div>');
        $('.msger-chat').append(loadingElement);

        const loadingText = "Loading...";
        let currentIndex = 0;
        const loadingInterval = setInterval(function() {
            loadingElement.text(loadingText.substring(0, currentIndex + 1));
            currentIndex++;
            if (currentIndex === loadingText.length) {
                currentIndex = 0;
            }
        }, 500);

        // Clear interval in AJAX success callback
        $.ajax({
            url: '/HSW/mediAI/ajax_submit/', 
            method: 'POST',
            data: formData,
            success: function(response){
                clearInterval(loadingInterval); // Clear interval
                const chat_response = response['answer'];

                // Remove loader
                $('.msger-chat .loading').remove();

                // Add returned chat_response to msger-chat
                $('.msger-chat').append(`<div class="answer_message">${chat_response}</div>`);
            },
            error: function(xhr, status, error) {
                clearInterval(loadingInterval); // Clear interval
                $('.msger-chat .loading').remove();
                $('.msger-chat').append('<div class="error_message">An error occurred. Please try again.</div>');
                console.error('AJAX Error:', status, error);
            }
        });

        $('#msg').val(''); // Clear textarea content
    });

    // Trigger send button click on Enter key press
    $('#msg').keypress(function(event) {
        if (event.which === 13) { // Enter key is pressed
            event.preventDefault(); // Prevent default form submission
            $('#send').click();
        }
    });
});