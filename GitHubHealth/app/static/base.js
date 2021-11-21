function loading(){
    $("#loading").show();
    $("#content").hide();
}

function settings() {
    document.getElementById("settingsDropdown").classList.toggle("show");
}

function toggleMode() {
    var element = document.body;
    element.classList.toggle("light-mode");
    document.getElementById("settingsDropdown").classList.toggle("hide");
}
