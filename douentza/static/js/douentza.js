function formatDate(date, format) {
    function pad(value) {
        return (value.toString().length < 2) ? '0' + value : value;
    }
    return format.replace(/%([a-zA-Z])/g, function (_, formatCode) {
        switch (formatCode) {
        case 'Y':
            return date.getUTCFullYear();
        case 'M':
            return pad(date.getUTCMonth() + 1);
        case 'd':
            return pad(date.getUTCDate());
        case 'H':
            return pad(date.getUTCHours());
        case 'm':
            return pad(date.getUTCMinutes());
        case 's':
            return pad(date.getUTCSeconds());
        default:
            throw new Error("ce format n'est pas supporté: " + formatCode);
        }
    });
}

function update_event_tables(data_url) {
    $.getJSON(data_url, function(data) {
        var today_events_table = $('.today_events_table tbody');
        var yesterday_events_table = $('.yesterday_events_table tbody');
        var ancient_events_table = $('.ancient_events_table tbody');
        var time = "%H:%m:%s";
        var date_tine = "%d %M %Y %H:%m:%s"

        today_events_table.empty();
        yesterday_events_table.empty();
        ancient_events_table.empty();

        function get_empty_row() {
            return $('<tr><td colspan="4">Aucun événnement</td></tr>');
        }

        function get_row_for(anevent, formatCode) {
            function get_td(cls, text, icon) {
                var td = $('<td><button type="button" class="btn btn-xs">' +
                           '<span class="glyphicon"></span> </button></td>');
                var btn = td.find("button");
                btn.addClass(cls);
                btn.append(text);
                if (icon !== null)
                    td.find("span").addClass(icon);
                return td;
            }
            var row = $('<tr></tr>');
            var entry_button = get_td('btn-success', "Saisir le rappel", 'glyphicon-pencil');
            var callback_button = get_td('btn-default', "Occupé");
            var dontanswer_button = get_td('btn-danger', "Ne répond pas");

            var td_infos = $('<td />');
            td_infos.append($('<span class="glyphicon glyphicon-earphone"></span>'));
            var infos = '<strong>(' + anevent.identity + ')</strong> '
                                    + formatDate(new Date(anevent.received_on), formatCode)
                                    + ' ' + anevent.status + ' '
                                    +anevent.event_type
            td_infos.append(infos);
            row.append(td_infos);
            row.append(entry_button);
            row.append(callback_button);
            row.append(dontanswer_button);

            return row;
        }

        if (data.ancient_event.length === 0) {
            ancient_events_table.append(get_empty_row());
        } else{
            $.each(data.ancient_event, function(num, anevent) {
                ancient_events_table.append(get_row_for(anevent, date_tine));
            });
        }

        if (data.yesterday_event.length === 0) {
            yesterday_events_table.append(get_empty_row());
        } else{
            $.each(data.yesterday_event, function(num, anevent) {
                yesterday_events_table.append(get_row_for(anevent, time));
            });
        }

        if (data.today_event.length === 0) {
            today_events_table.append(get_empty_row());
        } else{
            $.each(data.today_event, function(num, anevent) {
                today_events_table.append(get_row_for(anevent, time));
            });
        }
    });
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
};