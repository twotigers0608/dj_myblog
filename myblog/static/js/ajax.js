$.fn.grid = function forajax(options) {
    var $tbody = $(this).find("tbody");
    var colums = options.colums;
    var url = options.url;
    var content = [];
    var rqdata = []
    //ajax获取数据源后存入content数据中。
    $.ajax({
        type: "get",
        url: url,
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
        var html = "<tr>";
        $.each(cols, function (k, v) {
            html += "<td>" + v + "</td>"
        });
        html += "</tr>";
        $tbody.append(html)
    }
}

$.fn.grid = function for_ajax(options) {
    var $tbody = $(this).find("tbody");
    var colums = options.colums;
    var url = options.url;
    var content = [];
    var rqdata = []
    //ajax获取数据源后存入content数据中。
    $.ajax({
        type: "get",
        url: url,
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
$.fn.grid = (function select_classs(option) {
    //var tr_show = $.(".tr[class=" + option + "]");
    //table 标签下指定的 tr 标签
    var table_show = $("#tabledata").next(".tr[class=\" +option + \"]")
    alert("执行到此")
    table_show.show()
})
$.fn.grid = function table_data(options) {
    var $tbody = $(this).find("tbody");
    var colums = options.colums;
    var url = options.url;
    var content = [];
    var rqdata = []
    //ajax获取数据源后存入content数据中。
    $.ajax({
        type: "get",
        url: url,
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