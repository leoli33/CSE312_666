
document.getElementById('replyForm').addEventListener('submit', function(event) {
    event.preventDefault();
    var replyContent = document.getElementById('replyContent').value;

    fetch('/submit-reply', {
        method: 'POST',
        body: JSON.stringify({ 
            threadId: '{{ post._id }}', 
            content: replyContent 
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.result === 'success') {
            document.getElementById('replyContent').value = '';
            
            const replyDiv = document.createElement('div');
            replyDiv.className = 'reply';
            const currentTime = new Date().toISOString();
            replyDiv.innerHTML = `
                <p>${replyContent}</p>
                <small class="time-ago" data-timestamp="${currentTime}"></small>
            `;
            document.getElementById('replies-container').appendChild(replyDiv);
            const timeAgoElement = replyDiv.querySelector('.time-ago');
            timeAgoElement.textContent = timeSince(currentTime);
            
        } else {
            alert('Failed to submit reply.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});


function timeSince(date) {
    var seconds = Math.floor((new Date() - new Date(date)) / 1000);
    var interval = seconds / 31536000;

    if (interval > 1) {
        return Math.floor(interval) + " year" + (Math.floor(interval) > 1 ? "s" : "") + " ago";
    }
    interval = seconds / 2592000;
    if (interval > 1) {
        return Math.floor(interval) + " month" + (Math.floor(interval) > 1 ? "s" : "") + " ago";
    }
    interval = seconds / 86400;
    if (interval > 1) {
        return Math.floor(interval) + " day" + (Math.floor(interval) > 1 ? "s" : "") + " ago";
    }
    interval = seconds / 3600;
    if (interval > 1) {
        return Math.floor(interval) + " hour" + (Math.floor(interval) > 1 ? "s" : "") + " ago";
    }
    interval = seconds / 60;
    if (interval > 1) {
        return Math.floor(interval) + " minute" + (Math.floor(interval) > 1 ? "s" : "") + " ago";
    }
    return Math.floor(seconds) + " seconds ago";
}

document.addEventListener('DOMContentLoaded', (event) => {
    document.querySelectorAll('.time-ago').forEach(function(element) {
        var timestamp = element.getAttribute('data-timestamp');
        element.textContent = timeSince(timestamp);
    });
});
