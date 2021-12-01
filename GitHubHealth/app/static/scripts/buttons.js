function showPlotLeft() {
    var x = document.getElementsByClassName("plot");
    l = x.length;
    // from right to left disable display until we find already displayed
    for (i = l-1; i > 0; i--) {
        if (x[i].style.display == "block") {
            x[i].style.display = "none";
            x[i-1].style.display = "block";
            break;
        }
    }
}

function showPlotRight() {
    var x = document.getElementsByClassName("plot");
    l = x.length;
    // from left to right disable display until we find already displayed
    for (i = 0; i < l-1; i++) {
        if (x[i].style.display == "block") {
            x[i].style.display = "none";
            x[i+1].style.display = "block";
            break;
        }
    }
}
