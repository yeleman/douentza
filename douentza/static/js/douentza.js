
Array.prototype.diff = function(a) {
    return this.filter(function(i) {
            return !(a.indexOf(i) > -1);
    });
};

if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) {
      return typeof args[number] != 'undefined'
        ? args[number]
        : match
      ;
    });
  };
}

String.prototype.toSlug = function () {
  return this.replace(/^\s+|\s+$/g, '').replace(/\s+/g, '-').toLowerCase();
};


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

// Tag Manager
var tagManagers = {};

function getTagManager(options) {

    function TagManager(options) {
        this.request_id = options.request_id || null;
        this.readonly = options.readonly || false;
        this.max_items = options.max_items || 10;
        this.local_items = [];
        this.all_items = [];
        this.remaining_items = [];
        this.update_url = '/api/tags/{0}/update'.format(this.request_id);
        this.all_tags_url = '/api/all_tags';
        this.tags_for_url = '/api/tags/{0}'.format(this.request_id);
        this.container = null;
        this.manager_id = this._random_id();
        this.autocomple_options = {
            serviceUrl: null,
            minChars:1,
            deferRequestBy: 0,
            tabDisabled: true,
            noCache: true,
            lookup: []};

        this.create_basic_container();
        this.update_all_from_database();
        this.update_local_from_database();
        this.build();
    }

    TagManager.prototype._random_id = function () {
        var d = new Date().getTime();
        var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = (d + Math.random()*16)%16 | 0;
            d = Math.floor(d/16);
            return (c=='x' ? r : (r&0x7|0x8)).toString(16);
        });
        return uuid;
    };

    TagManager.prototype._parse_json_url = function(url) {
        return JSON.parse($.ajax({
            type: "GET",
            url: url,
            cache: false,
            async: false,
            dataType: "json",
        }).responseText);
    };

    TagManager.prototype.push_to_database = function() {
        // update databse for request
        $.post(this.update_url, JSON.stringify(this.local_items));
    };

    TagManager.prototype.update_all_from_database = function () {
        this.all_items = this._parse_json_url(this.all_tags_url);
    };

    TagManager.prototype.update_local_from_database = function() {
        this.local_items = this._parse_json_url(this.tags_for_url);
        this.update_remaining_tags();
    };

    TagManager.prototype.update_local_from_ui = function() {
        var local_items = [];
        this.container.find('.tag_name').each(function () {
            local_items.push($(this).html());
        });
        this.local_items = local_items;
    };

    TagManager.prototype.update_items_lists = function() {
        this.update_local_from_ui();
        this.update_remaining_tags();
    };

    TagManager.prototype.update_remaining_tags = function () {
        this.remaining_items = this.all_items.diff(this.local_items);
    };

    TagManager.prototype.update_database_from_ui = function() {
        // update DB from actual items in UI
        this.update_local_from_ui();
        this.push_to_database();
    };

    TagManager.prototype._create_tag_element = function(text) {
        var tagButton = $('<button class="btn btn-info btn-xs tag_elem"/>');
        var tagNameSpan = $('<span class="tag_name" />');
        tagNameSpan.html(text);
        tagButton.append(tagNameSpan);

        if (!this.readonly) {
            var tagSpan = $('<span class="glyphicon glyphicon-remove" />');
            tagButton.append(" ");
            tagButton.append(tagSpan);

            // click action (remove from parent list)
            tagButton.click(function (e) {
                var parent = $(this).parent();
                $(this).remove();
                // update from manager
                var manager_id = parent.attr('manager_id');
                var manager = getTagManager({manager_id: manager_id});
                manager.update_database_from_ui();
            });
        }
        return tagButton;
    };

    TagManager.prototype.add_tag_element = function(text) {
        if (this.local_items.indexOf(text.toSlug()) == -1) {
            this.container.append(this._create_tag_element(text.toSlug()));
        }
    };

    TagManager.prototype.update_autocomplete_for = function(element) {
        return element.autocomplete('setOptions', {
            lookup: this.remaining_items});
    };

    TagManager.prototype._create_addtag_element = function() {
        var elem = $('<input class="form-control add_tag_input"/>');
        elem.attr('placeholder', "Taggez ici.");

        elem.autocomplete(this.autocomple_options);
        elem.autocomplete('setOptions', {lookup: this.remaining_items});

        // TODO: change behavior
        elem.on('focus', function (e) {
            var manager = getTagManager({manager_id: $(this).parent().attr('manager_id')});
            manager.update_autocomplete_for($(this));
        });

        elem.on('keypress', function (e) {
            var code = (e.keyCode ? e.keyCode : e.which);
            if (code != 13) // Enter Key
                return e;
            var content = $(this).val();
            $(this).val('');

            // update from manager
            var manager = getTagManager({manager_id: $(this).parent().attr('manager_id')});
            manager.add_tag_element(content);
            manager.update_database_from_ui();
            manager.update_autocomplete_for($(this));
        });

        return elem;
    };

    TagManager.prototype.create_basic_container = function() {
        this.container = $('<p class="tags_container" />');
        this.container.attr('request_id', this.request_id);
        this.container.attr('readonly', this.readonly);
        this.container.attr('manager_id', this.manager_id);
    };


    TagManager.prototype._grouped_items_element = function() {
        var elem = $('<button class="btn btn-info btn-xs tag_elem"/>');
        elem.append(this.local_items.length + " tags");
        elem.append("&nbsp;");
        elem.append($('<span class="glyphicon glyphicon-tag" />'));

        elem.popover({
            html: true,
            placement: 'top',
            trigger: 'hover',
            content: getTagManager({request_id: this.request_id, readonly: true}).container.html()
        }).popover('show');

        return elem;
    };

    TagManager.prototype.build = function() {

        if (this.readonly && this.max_items <= this.local_items.length) {
            this.container.append(this._grouped_items_element());
            return;
        }

        if (!this.readonly)
            this.container.append(this._create_addtag_element());

        for (var idx=0; idx < this.local_items.length; idx++) {
            this.container.append(this._create_tag_element(this.local_items[idx]));
        }

        if (!this.readonly) {
            this.update_remaining_tags();
            this.update_autocomplete_for($('.add_tag_input'));
        }

        return this.container;
    };

    var manager_id = options.manager_id || null;
    if (manager_id !== null)
        return tagManagers[manager_id];

    var manager = new TagManager(options);
    tagManagers[manager.manager_id] = manager;
    return manager;
}
