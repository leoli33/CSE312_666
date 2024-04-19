function checkLoginAndRedirect(userEmail) {
    if (userEmail === 'Guest') {
        alert('Please login.');
        return false; 
    }
    return true; 
}

function sidebar_open() {
    document.getElementById("main").style.marginLeft = "160px";
    document.getElementById("sidebar").style.width = "150px";
    document.getElementById("sidebar").style.display = "block";
}

function sidebar_close() {
    document.getElementById("main").style.marginLeft = "0%";
    document.getElementById("sidebar").style.display = "none";
}
