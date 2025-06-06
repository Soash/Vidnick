
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.send-request').forEach((button) => {
        button.addEventListener('click', function () {
            const teacherId = this.getAttribute('data-teacher-id');
            
            fetch('/matchmaking/send_request/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
                body: JSON.stringify({ teacher_id: teacherId }),
            })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    alert('Request sent successfully!');
                } else {
                    alert('Failed to send request.');
                }
            });
        });
    });
});

