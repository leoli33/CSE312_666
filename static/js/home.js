function checkLoginAndRedirect(userEmail) {
    if (userEmail === 'Guest') {
        alert('Please login.');
        return false; 
    }
    return true; 
}

function sidebar_open() {
    document.getElementById("main").style.marginLeft = "25%";
    document.getElementById("sidebar").style.width = "25%";
    document.getElementById("sidebar").style.display = "block";
    document.getElementById("openNav").style.display = 'none';
}

function sidebar_close() {
    document.getElementById("main").style.marginLeft = "0%";
    document.getElementById("sidebar").style.display = "none";
    document.getElementById("openNav").style.display = "block";
}
