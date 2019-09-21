$.fn.grid = function (options) {
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
    alert(rqdata.data)
    for (var c = 0; c < content.length; c++) {
        //遍历所有列
        var cols = [];
        alert(cols)
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
    alert($tbody)
}