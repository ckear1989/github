function loading(){
    $("#loading").show();
    $("#content").hide();
}

function settings() {
    document.getElementById("settingsDropdown").classList.toggle("show");
}

function activateLightMode() {
    var element = document.body;
    // toggle light-mode
    element.classList.toggle("light-mode");
    // if it is now active set class for colors
    let currently_active = element.classList.contains("light-mode")
    if (currently_active) {
        let inel = document.getElementById("lightMode");
        inel.className = "active";
        inel.setAttribute("class", "theme-pick-chosen")
    } else {
        let inel = document.getElementById("lightMode");
        inel.className = "inactive";
        inel.setAttribute("class", "theme-pick")
    }

    // deactivate dark-mode
    element.classList.remove("dark-mode");
    let outel = document.getElementById('darkMode');
    outel.className = 'inactive';
    outel.setAttribute("class", "theme-pick")

    localStorage.setItem("lightMode", true);
    localStorage.setItem("darkMode", false);
}

function activateDarkMode() {
    var element = document.body;
    // toggle dark-mode
    element.classList.toggle("dark-mode");
    // if it is now active set class for colors
    let currently_active = element.classList.contains("dark-mode")
    if (currently_active) {
        let inel = document.getElementById("darkMode");
        inel.className = "active";
        inel.setAttribute("class", "theme-pick-chosen")
    } else {
        let inel = document.getElementById("darkMode");
        inel.className = "inactive";
        inel.setAttribute("class", "theme-pick")
    }

    // deactivate light-mode
    element.classList.remove("light-mode");
    let outel = document.getElementById('lightMode');
    outel.className = "inactive";
    outel.setAttribute("class", "theme-pick");

    localStorage.setItem("darkMode", true);
    localStorage.setItem("lightMode", false);
}
