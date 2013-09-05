
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

function changeSelectContent(selectElement, content) {
    selectElement.empty();
    $.each(content, function (idx, entity) {
        selectElement.append($("<option value='"+entity.slug +"'>" + entity.name + "</option>"));
    });
}

function changeRegion(regionElem, cercle_id, commune_id, village_id) {
    var region_id = regionElem.val();
    var cercle = $('#id_cercle');
    $.getJSON('/entities/' + region_id).done(function (response) {
        changeSelectContent(cercle, response);
        if (cercle_id !== undefined && cercle_id !== null) {
            cercle.val(cercle_id);
        }
        changeCercle(cercle, commune_id, village_id);
    });
}

function changeCercle(cercleElem, commune_id, village_id) {
    var cercle_id = cercleElem.val();
    var commune = $('#id_commune');
    $.getJSON('/entities/' + cercle_id).done(function (response) {
        changeSelectContent(commune, response);
        if (commune_id !== undefined && commune_id !== null) {
            commune.val(commune_id);
        }
        changeCommune(commune, village_id);
    });
}

function changeCommune(communeElem, village_id) {
    var commune_id = communeElem.val();
    var village = $('#id_village');
    $.getJSON('/entities/' + commune_id).done(function (response) {
        changeSelectContent(village, response);
        if (village_id !== undefined && village_id !== null) {
            village.val(village_id);
        }
    });
}

function fill_from_previous() {
    var cercle_id = $('#previous_cercle').val();
    var commune_id = $('#previous_commune').val();
    var village_id = $('#previous_village').val();
    if (cercle_id !== undefined && cercle_id !== null) {
        changeRegion($('#id_region'), cercle_id, commune_id, village_id);
    }
}

$('#id_region').change(function () {
    var region_id = $(this).val();
    var cercle = $('#id_cercle');
    console.log("Changed region: " + region_id);
    $.getJSON('/entities/' + region_id).done(function (response) {
        changeSelectContent(cercle, response);
        changeCercle($("#id_cercle"));
    });
});

$('#id_cercle').change(function () {
    changeCercle($(this));
});

$('#id_commune').change(function () {
    changeCommune($(this));
});