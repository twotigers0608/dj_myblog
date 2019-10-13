$.fn.grid = function for_ajax(options) {
    var $tbody = $(this).find("tbody");
    var colums = options.colums;
    var url = options.url;
    var content = [];
    var rqdata = [];
    //ajax获取数据源后存入content数据中。
    $.ajax({
        type: "post",
        url: url,
        data: {"kernel": "e.g.2018"},
        dataType: "json",
        async: false,
        success: function (data) {
            rqdata = data;
        }
    });
    content = rqdata.data
    for (var c = 0; c < content.length; c++) {
        //遍历所有列
        var cols = [];
        $.each(colums, function (key, value) {
            //遍历json数据
            $.each(content[c], function (key2, value2) {
                if (key2 == value.Index) {
                    cols.push(value2);
                }
            });
        });
        var html = "<tr" + " class=" + cols[0] + ">";
        $.each(cols, function (k, v) {
            html += "<td>" + v + "</td>"
        });
        html += "</tr>";
        $tbody.append(html)
    }
}

function f(date) {
    var t = Date.parse(date);
    if (!isNaN(t)) {
        return new Date(Date.parse(date.replace(/-/g, "/")));
    } else {
        return new Date();
    }
    ;
}

function getWeekOfYear(date) {
    //var today = (new Date(data)).getTime()
    var today = f(date);
    //alert(today);
    var y = today.getFullYear();
    var firstDay = new Date(today.getFullYear(), 0, 1);
    var dayOfWeek = firstDay.getDay();
    var spendDay = 1;
    if (dayOfWeek != 0) {
        spendDay = 7 - dayOfWeek + 1;
    }
    firstDay = new Date(today.getFullYear(), 0, 1 + spendDay);
    var d = Math.ceil((today.valueOf() - firstDay.valueOf()) / 86400000);
    var result = Math.ceil(d / 7);
    result += 1;
    var week = '' + y + '-' + '' + result
    return week;
}

function data_reduction(data) {
    var week_data = {};
    var week_list = [];
    for (var i = 0; i < data.length; i++) {
        var ww = getWeekOfYear(data[i]['released_time'])
        data[i]['week'] = ww
        week_list.push(ww)
    }
    ;
    for (var i = 0; i < week_list.length; i++) {
        var col = [];
        for (var l = 0; l < data.length; l++) {
            if (week_list[i] == data[l]['week']) {
                col.push(data[l]);
            }
            week_data[week_list[i]] = col;
        }
    }
    //console.log(week_data);
    return week_data;
}

function data_durations(data) {
    result = {};
    week = [];
    merge_list = [];
    rel_list = [];
    review_list = [];
    $.each(data, function (k, v) {
        var review_duration = 0;
        var merge_duration = 0;
        var released_duration = 0;
        week.push(k);

        for (var i = 0; i < v.length; i++) {
            for (var l = 0; l < v.length; l++) {
                review_duration += v[l]['review_duration'];
                merge_duration += Number(v[l]['merge_duration']);
                released_duration += v[l]['rel_duration'];
                console.log(v[l]['merge_duration'])
            }
        }
        review_list.push(review_duration)
        merge_list.push(merge_duration);
        rel_list.push(released_duration);
    })
    result['week'] = week;
    result['review_duration'] = review_list;
    result['merge_duration'] = merge_list;
    result['rel_durations'] = rel_list;
    console.log(result)
    return result
}