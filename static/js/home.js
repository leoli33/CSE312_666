function checkLoginAndRedirect(userEmail) {
    if (userEmail === 'Guest') {
        alert('Please login.');
        return false; 
    }
    return true; 
}

function sidebar_open() {
    document.getElementById("main").style.marginLeft = "150px";
    document.getElementById("sidebar").style.width = "150px";
    document.getElementById("sidebar").style.display = "block";
    document.getElementById("openNav").style.display = 'none';
}

function sidebar_close() {
    document.getElementById("main").style.marginLeft = "0%";
    document.getElementById("sidebar").style.display = "none";
    document.getElementById("openNav").style.display = "block";
}
