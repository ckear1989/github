function loading_login(){
    $("body").addClass("cursor-wait");
    for (const el of document.getElementById("login_form").querySelectorAll("[required]")) {
        if (!el.reportValidity()) {
            return;
        }
    }
    $("#loading").show();
}

function loading_search(){
    $("body").addClass("cursor-wait");
    for (const el of document.getElementById("search_form").querySelectorAll("[required]")) {
        if (!el.reportValidity()) {
            return;
        }
    }
    $("#loading").show();
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
        localStorage.setItem("lightMode", true);
    } else {
        let inel = document.getElementById("lightMode");
        inel.className = "inactive";
        inel.setAttribute("class", "theme-pick")
        element.classList.remove("light-mode");
        localStorage.setItem("lightMode", false);
    }

    // deactivate dark-mode
    element.classList.remove("dark-mode");
    let outel = document.getElementById('darkMode');
    outel.className = 'inactive';
    outel.setAttribute("class", "theme-pick")

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
        localStorage.setItem("darkMode", true);
    } else {
        let inel = document.getElementById("darkMode");
        inel.className = "inactive";
        inel.setAttribute("class", "theme-pick")
        element.classList.remove("dark-mode");
        localStorage.setItem("darkMode", false);
    }

    // deactivate light-mode
    element.classList.remove("light-mode");
    let outel = document.getElementById('lightMode');
    outel.className = "inactive";
    outel.setAttribute("class", "theme-pick");

    localStorage.setItem("lightMode", false);
}
