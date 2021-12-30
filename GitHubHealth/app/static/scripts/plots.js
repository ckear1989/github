function showError(el, error){
    el.innerHTML = (
        '<div class="error" style="color:red;">'
        + '<p>JavaScript Error: ' + error.message + '</p>'
        + "<p>This usually means there's a typo in your chart specification. "
        + "See the javascript console for the full traceback.</p>"
        + '</div>'
    );
    throw error;
}

function vegaEmbedPlot(spec, index, div_id) {
    var embedOpt = {"mode": "vega-lite"};
    const el = document.getElementById(index);
    vegaEmbed(div_id, spec, embedOpt).catch(error => showError(el, error));
}

function vegaEmbedPlotNew(plots, index, div_id, plot_index) {
    // make plot index global for left/right fill functions
    plot_index_g = plot_index;
    plots_g = plots;
    var spec = JSON.parse(plots_g[plot_index]);
    var embedOpt = {"mode": "vega-lite"};
    const el = document.getElementById(index);
    vegaEmbed(div_id, spec, embedOpt).catch(error => showError(el, error));
}

function fillPlotLeft() {
    var new_index = 0;
    if (plot_index_g > 0) {
        new_index = plot_index_g - 1;
    }
    vegaEmbedPlotNew(plots, "vis", "#vis_repo", new_index);
}

function fillPlotRight() {
    var new_index = plots.length - 1;
    if (plot_index_g < (plots.length - 1)) {
        new_index = plot_index_g + 1;
    }
    vegaEmbedPlotNew(plots, "vis", "#vis_repo", new_index);
}

function prefillDropdown(plots) {
    let dropdown = $("#select-var");
    dropdown.empty();
    dropdown.append('<option disabled>Choose Variable</option>');
    dropdown.prop('selectedIndex', 0);
    $.each(plots, function (plot) {
        plot_parsed = JSON.parse(plots[plot]);
        dropdown.append($('<option></option>').attr('value', plot_parsed.encoding.y.field).text(plot_parsed.encoding.y.field));
    })
}

function selectVar(aval) {
    var new_index = 0;
    $.each(plots_g, function (plot) {
        plot_parsed = JSON.parse(plots_g[plot]);
        if (aval == plot_parsed.encoding.y.field) {
            vegaEmbedPlotNew(plots, "vis", "#vis_repo", new_index);
        }
        new_index += 1;
    });
}
