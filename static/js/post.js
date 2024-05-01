
function navigateToPost(postId) {
    window.location.href = '/posts/' + postId;
}

document.addEventListener('DOMContentLoaded', (event) => {
    document.querySelectorAll('.time-ago').forEach(function(element) {
        var timestamp = element.getAttribute('data-timestamp');
        var postingTime = element.closest('.post-summary').getAttribute('data-posting-time');
        if (timestamp) {
            element.textContent = timeSince(new Date(timestamp)) + ' ago';
        } else if (postingTime) {
            element.textContent = timeSince(new Date(postingTime)) + ' ago';
        } else {
            element.textContent = 'some time ago';
        }
    });


    document.querySelectorAll('.post-summary').forEach(post => {
        const postingTime = new Date(post.getAttribute('data-posting-time'));
        const now = new Date();
        const timeDifference = now - postingTime;
        console.log(timeDifference);
        if (timeDifference < 60000) { // 60000 ms = 1 minute
            const recallBtn = post.querySelector('.recall-btn');
            recallBtn.style.display = 'block';
    
            setTimeout(() => {
                recallBtn.style.display = 'none';
            }, 60000 - timeDifference);
        }
    });

    const postsContainer = document.getElementById('posts-container');

    postsContainer.addEventListener('click', function(event) {
        if (event.target.classList.contains('recall-btn')) {
            event.stopPropagation(); 
            const postId = event.target.getAttribute('data-post-id');
    
            fetch(`/delete-post/${postId}`, {
                method: 'DELETE', 
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Post recalled successfully.');
                    event.target.closest('.post-summary').remove();
                } else {
                    alert('Failed to recall the post: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Network error, failed to recall the post.');
            });
        }
    });
});


document.getElementById("newThreadForm").addEventListener("submit", function(event) {
    event.preventDefault();
    var title = document.getElementById("newThreadTitle").value;
    var content = document.getElementById("newThreadContent").value;

    content = content.replace(/&/g,"&amp;");
    content = content.replace(/</g,"&lt;");
    content = content.replace(/>/g,"&gt;");

    title = title.replace(/&/g,"&amp;");
    title = title.replace(/</g,"&lt;");
    title = title.replace(/>/g,"&gt;");

    fetch('/submit-post', {
        method: 'POST',
        body: JSON.stringify({ title: title, content: content }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if(data.result === 'success') {
            var newPostSummary = document.createElement("div");
            var authorEmail = data.author_email || 'Unknown';
            const now = new Date();
            newPostSummary.className = "post-summary";
            newPostSummary.setAttribute('data-posting-time', new Date().toISOString());
            var contentPreview = content.slice(0, 10);

            newPostSummary.innerHTML = `
                <div>
                    <h3 onclick="navigateToPost('${data.post_id}')" style="cursor:pointer;">${title}</h3>
                    <p>${contentPreview}... - Posted by: ${authorEmail}</p>
                    <button class="recall-btn" data-post-id="${data.post_id}" style="display: none;">Recall</button>
                </div>
                <div class="post-last-reply-time">
                    <small>Last reply: <span class="time-ago">just now</span></small>
                </div>
            `;
            document.getElementById("posts-container").appendChild(newPostSummary);
            const recallBtn = newPostSummary.querySelector('.recall-btn');
            recallBtn.style.display = 'block';
            setTimeout(() => {
                recallBtn.style.display = 'none';
            }, 60000);

            document.getElementById("newThreadTitle").value = '';
            document.getElementById("newThreadContent").value = '';
            closeNewThreadSidebar();
        } else {
            console.error('Failed to create the post.');
        }
    })
    .catch(error => {
        console.error('Network error:', error);
    });
});

function timeSince(date) {
    const seconds = Math.floor((new Date() - new Date(date)) / 1000);
    let interval = seconds / 31536000;

    if (interval > 1) return Math.floor(interval) + " years";
    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + " months";
    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + " days";
    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + " hours";
    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + " minutes";
    return Math.floor(seconds) + " seconds";
}

document.querySelectorAll('.time-ago').forEach(function(element) {
    const timestamp = element.getAttribute('data-timestamp');
    if (timestamp) {
        element.textContent = timeSince(timestamp) + ' ago';
    } else {
        element.textContent = '0 minutes ago';
    }
});

//////////////////DEBUG CLEAR POST////////////////////
function clearPosts() {
    if(confirm('Are you sure you want to clear all threads? This cannot be undone.')) {
        fetch('/clear-posts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if(data.result === 'success') {
                // Remove all post-summary elements
                const summaries = document.querySelectorAll('.post-summary');
                summaries.forEach(summary => summary.remove());
                alert('All threads have been cleared.');
                window.location.reload(); // Refresh the page
            } else {
                console.error('Failed to clear the threads.');
            }
        })
        .catch(error => {
            console.error('Network error:', error);
        });
    }
}
///////////////////Profile Sidebar ////////////////////
function toggleProfileSidebar() {
    var ProfileSidebar = document.getElementById("mySidebar");
    var chatIcon = document.getElementById("ProfileIcon"); 
    if (ProfileSidebar.style.width === "25%") {
        ProfileSidebar.style.width = "0";
        ProfileSidebar.style.height = "0";
    } else {
        ProfileSidebar.style.width = "25%";
        ProfileSidebar.style.height = "25%"; 
        ProfileSidebar.style.display = "block";
    }
}
function closeSidebar() {
    document.getElementById("mySidebar").style.width = "0"; 
    document.getElementById("mySidebar").style.height = "0";

}
///////////////////Chat Sidebar ////////////////////
function toggleChatSidebar() {
    var chatSidebar = document.getElementById("myChatSidebar");
    var chatIcon = document.getElementById("chatIcon"); 
    if (chatSidebar.style.width === "15%") {
        chatSidebar.style.width = "0";
    } else {
        chatSidebar.style.width = "15%";
        chatSidebar.style.display = "block";
    }
}
function closeChatSidebar() {
    document.getElementById("myChatSidebar").style.width = "0"; 
}
///////////////////Thread Sidebar ////////////////////
function toggleNewThreadSidebar() {
    var newThreadSidebar = document.getElementById("myNewThreadSidebar");
    if (newThreadSidebar.style.height === "35%") {
        newThreadSidebar.style.height = "0"; 
        newThreadSidebar.style.paddingTop = "0";
        newThreadSidebar.style.boxShadow = "none"; 
    } else {
        newThreadSidebar.style.height = "35%"; 
        newThreadSidebar.style.display = "block";
        newThreadSidebar.style.paddingTop = "10px";
        newThreadSidebar.style.boxShadow = "0 -2px 5px rgba(0,0,0,0.5)"; 
    }
}
function closeNewThreadSidebar() {
    var newThreadSidebar = document.getElementById("myNewThreadSidebar");
    newThreadSidebar.style.height = "0"; 
    newThreadSidebar.style.paddingTop = "0"; 
    newThreadSidebar.style.boxShadow = "none"; 
}
