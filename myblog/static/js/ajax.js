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
    var today = f(date)
    //var today = new Date();
    //alert(today)
    var firstDay = new Date(today.getFullYear(), 0, 1);
    var dayOfWeek = firstDay.getDay();
    var spendDay = 1;
    if (dayOfWeek != 0) {
        spendDay = 7 - dayOfWeek + 1;
    }
    firstDay = new Date(today.getFullYear(), 0, 1 + spendDay);
    var d = Math.ceil((today.valueOf() - firstDay.valueOf()) / 86400000);
    var result = Math.ceil(d / 7);
    return result + 1;
};
