
document.getElementById('replyForm').addEventListener('submit', function(event) {
    event.preventDefault();
    var replyContent = document.getElementById('replyContent').value;
    var postContainer = document.getElementById('thread-content');
    var postId = postContainer.dataset.postId; 

    fetch('/submit-reply', {
        method: 'POST',
        body: JSON.stringify({ 
            threadId: postId, 
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
            replyDiv.innerHTML = `
                <p class="reply-content">${replyContent}</p>
                <div class="reply-details">
                    <span class="posted-by">Posted by: ${data.author_email}</span>
                    <small class="time-ago" data-timestamp="${new Date().toISOString()}">just now</small>
                </div>
            `;
    
            document.getElementById('replies-container').appendChild(replyDiv);
            const timeAgoElement = replyDiv.querySelector('.time-ago');
            timeAgoElement.textContent = timeSince(new Date(timeAgoElement.getAttribute('data-timestamp')));
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
    var replySection = document.getElementById('reply-section');
    var toggleBtn = document.getElementById('toggleReplySectionBtn');
    document.querySelectorAll('.time-ago').forEach(function(element) {
        var timestamp = element.getAttribute('data-timestamp');
        element.textContent = timeSince(timestamp);
    });
    toggleBtn.addEventListener('click', function() {
        if (replySection.style.display === 'none') {
            replySection.style.display = 'block';

        } else {
            replySection.style.display = 'none'; 

        }
    });
});

