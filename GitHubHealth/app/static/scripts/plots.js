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

function vegaEmbedPlot(plots, index, div_id, plot_index) {
    // make plot index global for left/right fill functions
    plot_index_g = plot_index;
    plots_g = plots;
    var spec = JSON.parse(plots_g[plot_index]);
    var embedOpt = {"mode": "vega-lite"};
    const el = document.getElementById(index);
    vegaEmbed(div_id, spec, embedOpt).catch(error => showError(el, error));
    prefillSelectX();
}

function fillPlotLeft() {
    var new_index = 0;
    if (plot_index_g > 0) {
        new_index = plot_index_g - 1;
    }
    vegaEmbedPlot(plots, "vis", "#vis_repo", new_index);
}

function fillPlotRight() {
    var new_index = plots.length - 1;
    if (plot_index_g < (plots.length - 1)) {
        new_index = plot_index_g + 1;
    }
    vegaEmbedPlot(plots, "vis", "#vis_repo", new_index);
}

function prefillSelectY() {
    let dropdown = $("#select-y");
    dropdown.empty();
    dropdown.append('<option disabled>Choose Y Variable</option>');
    dropdown.prop('selectedIndex', 0);
    $.each(plots_g, function (plot) {
        plot_parsed = JSON.parse(plots[plot]);
        dropdown.append($('<option></option>').attr('value', plot_parsed.encoding.y.field).text(plot_parsed.encoding.y.field));
    })
}

function prefillSelectX(checked=null) {
    let dropdown = $("#select-x");
    let selected_plot = JSON.parse(plots_g[plot_index_g]);
    dropdown.empty();
    this_x = selected_plot.encoding.x.field;
    dataset = selected_plot.data.name;
    $.each(selected_plot.datasets[dataset], function (this_dataset) {
        this_x_val = selected_plot.datasets[dataset][this_dataset][this_x];
        if (checked == null) {
            var $group_cb = $('<input type="checkbox" checked onclick="filterX(this.id)"></input>').attr("id", this_x_val).attr("value", this_x_val);
        } else {
            if (checked.includes(this_x_val)) {
                var $group_cb = $('<input type="checkbox" checked onclick="filterX(this.id)"></input>').attr("id", this_x_val).attr("value", this_x_val);
            } else {
                var $group_cb = $('<input type="checkbox" onclick="filterX(this.id)"></input>').attr("id", this_x_val).attr("value", this_x_val);
            }
        }
        var $group_label = $('<label></label>').attr("for", this_x_val).text(this_x_val);
        var $form_group = $("<div class='form-group' style='display: flex; flex-direction: row; justify-content: left'></div>");
        $group_cb.appendTo($form_group);
        $group_label.appendTo($form_group);
        dropdown.append($form_group);
    });
}

function filterX(check_id) {
    let this_check = $('#select-x input[type="checkbox"]').find('#' + check_id);
    if (this_check.checked == 'true') {
        this_check.checked = 'false';
    } else if (this_check.checked == 'false') {
        this_check.checked = 'true';
    }
    let selected_plot = JSON.parse(plots_g[plot_index_g]);
    let select_x = [];
    $('#select-x input[type="checkbox"]:checked').each(function(index, elem) {
        select_x.push($(elem).val());
    });
    let this_x = selected_plot.encoding.x.field;
    let dataset = selected_plot.data.name;
    let this_dataset = selected_plot.datasets[dataset];
    filtered_plot = selected_plot;
    filtered_dataset = this_dataset.filter(function(x) {
        if (select_x.includes(x[this_x])) {
            return true;
        }
        return false;
    });
    filtered_plot.datasets[dataset] = filtered_dataset;
    var embedOpt = {"mode": "vega-lite"};
    const el = document.getElementById("vis_error");
    vegaEmbed("#vis_repo", filtered_plot, embedOpt).catch(error => showError(el, error));
    prefillSelectX(select_x);
}

function selectY(aval) {
    var new_index = 0;
    $.each(plots_g, function (plot) {
        plot_parsed = JSON.parse(plots_g[plot]);
        if (aval == plot_parsed.encoding.y.field) {
            vegaEmbedPlot(plots, "vis", "#vis_repo", new_index);
            prefillSelectY();
        }
        new_index += 1;
    });
}

function selectX(aval) {
    var new_index = 0;
    $.each(plots_g, function (plot) {
        plot_parsed = JSON.parse(plots_g[plot]);
        if (aval == plot_parsed.encoding.y.field) {
            vegaEmbedPlot(plots, "vis", "#vis_repo", new_index);
        }
        new_index += 1;
    });
}

var expanded = false;
function showCheckboxes() {
  var checkboxes = document.getElementById("select-x");
  if (!expanded) {
    checkboxes.style.display = "flex";
    checkboxes.style.flexDirection = "column";
    expanded = true;
  } else {
    checkboxes.style.display = "none";
    expanded = false;
  }
}
