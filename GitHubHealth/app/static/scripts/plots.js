function showError(el, error){
    el.innerHTML = ('<div class="error" style="color:red;">'
                    + '<p>JavaScript Error: ' + error.message + '</p>'
                    + "<p>This usually means there's a typo in your chart specification. "
                    + "See the javascript console for the full traceback.</p>"
                    + '</div>');
    throw error;
}

function vegaEmbedPlot(spec, index, div_id) {
    var embedOpt = {"mode": "vega-lite"};
    const el = document.getElementById(index);
    vegaEmbed(div_id, spec, embedOpt)
    .catch(error => showError(el, error));
}
