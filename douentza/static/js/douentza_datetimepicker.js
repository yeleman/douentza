var form_error = false;

function updateFormUI(mod, form_error) {
    console.log("updateFormUI");

    function zeroEd(value) {
        if (value < 10)
            return '0' + value;
        return value;
    }

    function getDateFormat(d) {
        var day = zeroEd(d.getUTCDate());
        var month = zeroEd(d.getUTCMonth() + 1);
        var year = d.getUTCFullYear();
        return day + '/' + month + '/' + year;
    }

    function getTimeFormat(d) {
        var hours = zeroEd(d.getHours());
        var minutes = zeroEd(d.getMinutes());
        return hours + ':' + minutes + ':00';
    }

    // datepicker
    var existing_date_picker = $("#datepicker");
    var existing_time_picker = $("#timepicker");
    var existing_date = $('#id_responded_on_0');
    var existing_time = $('#id_responded_on_1');

    if (!form_error) {
        var event_date = new Date();
        var date_fmt = getDateFormat(event_date);
        var time_fmt = getTimeFormat(event_date);

        existing_date.val(date_fmt);
        existing_time.val(time_fmt);
    }

    if (existing_date_picker.length === 0) {
        var new_date_picker = $('<div id="datepicker" class="input-group"><input id="id_responded_on_0" class="form-control" name="responded_on_0" data-format="dd/MM/yyyy" type="text" value="'+
                                existing_date.val() +
                                '"></input><span class="input-group-addon add-on glyphicon glyphicon-calendar"></span></div>');
        existing_date.replaceWith(new_date_picker);
    }
    mod.find('#datepicker').each(function () {
        $(this).datetimepicker({pickTime: false});
    });

    // timepicker

    if (!existing_time_picker.length) {
        var new_time_picker = $('<div id="timepicker" class="input-group"><input id="id_responded_on_1" name="responded_on_1" class="form-control" data-format="hh:mm:ss" type="text" value="'+
                                existing_time.val() +
                                '"></input><span class="input-group-addon add-on glyphicon glyphicon-time"></i></span></div>');
        existing_time.replaceWith(new_time_picker);
    }
    mod.find('#timepicker').datetimepicker({pickDate: false});
}
