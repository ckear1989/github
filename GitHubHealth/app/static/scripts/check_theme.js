document.ready= function() {
    // localStorage.getItem somehow returns a string and so
    // must be checked against string "true" and "false"
    // I wasted an hour on this crap.
    var element = document.body;
    if (localStorage.getItem("lightMode") == "true") {
        element.classList.add("light-mode");
        element.classList.remove("dark-mode");
        let inel = document.getElementById("lightMode");
        inel.className = "active";
        inel.setAttribute("class", "theme-pick-chosen")
        let outel = document.getElementById("darkMode");
        outel.className = "inactive";
        outel.setAttribute("class", "theme-pick");
    }
    else if (localStorage.getItem("darkMode") == "true") {
        element.classList.add("dark-mode");
        element.classList.remove("light-mode");
        let inel = document.getElementById("darkMode");
        inel.className = "active";
        inel.setAttribute("class", "theme-pick-chosen")
        let outel = document.getElementById("lightMode");
        outel.className = "inactive";
        outel.setAttribute("class", "theme-pick");
    }
}
