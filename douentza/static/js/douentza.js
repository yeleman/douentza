
var DEFAULT_FORMAT_TIMEONLY = "HH#mm";
var DEFAULT_FORMAT_DATETIME = "dd MMMM yyyy à HH#mm";


function formatFromTimestamp(ts, format) {
    if (format === null || format === undefined) {
        format = DEFAULT_FORMAT_DATETIME;
    }

    return formatDate(new Date(ts), format);
}


function formatDate(adate, format) {

    return adate.toString(format).replace('#', 'h');
}


function graph_event_response_counts(data_url) {
    $.getJSON(data_url, function(data) {
        $('#container').highcharts({
            chart: { type: 'spline',
            },
            title: { text: "Nombre d'appels par jour",
                x: -20 //center
            },
            xAxis: { type: 'datetime',
            },
            yAxis: {
                title: { text: "APPELS"
                },
            },
            tooltip: { valueSuffix: null,
            },
            legend: {},
            series: [{name: "Appels à la hotline",
                      data: data.events},
                     {name: "Rappels par la hotline",
                      data: data.responses,}]
        });
    });
}


function styleFormElements() {
    // bootstrap3 requires form elements to have the `form-control` CSS class
    $("form * select, form * input, form * textarea").addClass("form-control");
}
