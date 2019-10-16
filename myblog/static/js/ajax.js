//将时间戳转换为标准时间
function f(date) {
    var date = new Date(date);
    // 格式化日期
    dateTime = date.toLocaleString();
    var t = Date.parse(dateTime);
     console.log(t)
    if (!isNaN(t)) {
        return new Date(Date.parse(dateTime.replace(/-/g, "/")));
    } else {
        return new Date();
    }
    ;
};
function getWeekOfYear(date) {
    //var today = (new Date(data)).getTime()
    var today = f(date);
    console.log(today)
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
    var week = '' + y + '-' + '' + result;
    return week;
}

function data_reduction(data) {
    var week_data = {};
    var week_list = [];
    for (var i = 0; i < data.length; i++) {
        var ww = getWeekOfYear(data[i]['released_time']);
        data[i]['week'] = ww;
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

function fmt(s) {
    var h = parseInt(s / 3600, 10);
    var n = parseInt((s - h * 3600) / 60, 10);
    //var s = s % 60;
    r = '';
    r = h == 0 ? r : h + "h"
    r = (n == 0 && s == 0) ? r : r + n + "m"
    //r = s = 0 ? r : r + s + "秒"
    return r;
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
        for (var l = 0; l < v.length; l++) {
            review_duration += v[l]['review_duration'];
            merge_duration += Number(v[l]['merge_duration']);
            released_duration += v[l]['rel_duration'];
        }
        ;
        review_duration = parseFloat(released_duration / 3600, 10).toFixed(2);
        merge_duration = parseFloat(merge_duration / 3600, 10).toFixed(2);
        released_duration = parseFloat(released_duration / 3600, 10).toFixed(2);
        review_list.push(review_duration);
        merge_list.push(merge_duration);
        rel_list.push(released_duration);
    });
    result['week'] = week;
    result['review_duration'] = review_list;
    result['merge_duration'] = merge_list;
    result['rel_duration'] = rel_list;
    //console.log(result)
    return result
}

//返回表格数据
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
            result_data = data.data;
            var data_dict = data_reduction(result_data);
            var result = data_durations(data_dict);
            // console.log(data_dict);
            //console.log(colums)
            $.each(data_dict, function (key1, value1) {
                //console.log(value1);
                //遍历标签名 返回需要的key
                for (var c = 0; c < value1.length; c++) {
                    var cols = {};
                    $.each(value1[c], function (key2, value2) {
                        //console.log(value);
                        //遍历字典获取
                        $.each(colums, function (key, value) {
                            if (key2 == value.Index) {
                                cols[key2] = value2;
                                //console.log(value2)
                            }
                        });

                    });
                    console.log(cols['review_duration'])
                    //console.log(cols)
                    new_cols = {};
                    new_cols['week'] = cols['week'];
                    new_cols['id'] = cols['id'];
                    var verrify_time = fmt(cols['verify_duration']);
                    new_cols['verify_duration'] = verrify_time;
                    var review_time = fmt(cols['review_duration']);
                    new_cols['review_duration'] = review_time;
                    var merge_time = fmt(cols['merge_duration']);
                    new_cols['merge_duration'] = merge_time;
                    var rel_time = fmt(cols['rel_duration']);
                    new_cols['rel_duration'] = rel_time;
                    var html = "<tr" + " class=" + cols['week'] + ">";
                    $.each(new_cols, function (k, v) {
                        //console.log(v)
                        html += "<th>" + v + "</th>"
                    });
                    // for (var i = 0; i < cols.length; i ++){
                    //     html += "<td>" + cols[i] + "</td>"
                    // };
                    html += "</tr>";
                    //console.log(html)
                    $tbody.append(html)
                }
                content = rqdata.data
            })
        }
    });
}

function rq_mychart(result_data) {
    var data_dict = data_reduction(result_data);
    var result = data_durations(data_dict)
    //挨个取出类别并填入类别数组
    var week = result['week'];
    //var verify_nums = result['released_durations'];
    var review_nums = result['review_duration'];
    var merge_nums = result['merge_duration'];
    var released_nums = result['rel_duration'];
    //console.log(week)
    myChart.hideLoading();    //隐藏加载动画
    myChart.setOption({
        // 顶部选择
        legend: {
            data: ['Review', 'Merge', 'Released']
        },
        // 自动调节位置
        toolbox: {
            show: true,
            orient: 'vertical',
            x: 'right',
            y: 'center',
            feature: {
                mark: true,
                dataView: {readOnly: false},
                magicType: ['line', 'bar'],
                restore: true,
                saveAsImage: true
            }
        },
        calculable: true,
        // 显示每周
        xAxis: {
            data: week,
            axisLabel: {
                interval: 0,
                rotate: 40
            },
        },
        // 每周每个任务的时间
        yAxis: {
            type: 'value',
            splitArea: {show: true},
        },
        series: [{
            name: 'Review',
            type: 'bar',
            stack: 'total',
            label: {
                normal: {
                    show: true,
                    position: 'insideRight'
                }
            }, itemStyle: {
                normal: {
                    color: '#1f77b4',
                    //barBorderRadius: [20, 20, 20, 20],
                }
            },
            data: review_nums,
        },
            {
                name: 'Merge',
                type: 'bar',
                stack: 'total',
                label: {
                    normal: {
                        show: true,
                        position: 'insideRight'
                    }
                }, itemStyle: {
                    normal: {
                        color: '#9467bd',
                        //barBorderRadius: [20, 20, 20, 20],
                    }
                },
                data: merge_nums,
            },
            {
                name: 'Released',
                type: 'bar',
                stack: 'total',
                label: {
                    normal: {
                        show: true,
                        position: 'insideRight',

                    }
                },
                itemStyle: {
                    normal: {
                        color: '#ff7f0e',
                        //barBorderRadius: [20, 20, 20, 20],
                    }
                },
                data: released_nums,
            }]
    });
}

function rq_mychart1(result_data) {
    var data_dict = data_reduction(result_data);
    //console.log('data_dict')
    //console.log(data_dict)
    var result = data_durations(data_dict)
    //挨个取出类别并填入类别数组
    var week = result['week'];
    var week_num = []
    $.each(data_dict, function (k, v) {
        var num_leg = v.length;
        week_num.push(num_leg)
    })
    //console.log(week_num)
    myChart1.hideLoading();
    //resule = JSON.parse(resule);//把string字符串转换为json数组
    myChart1.setOption({
        // 自动调节位置
        toolbox: {
            show: true,
            orient: 'vertical',
            x: 'right',
            y: 'center',
            feature: {
                mark: true,
                dataView: {readOnly: false},
                magicType: ['line', 'bar'],
                restore: true,
                saveAsImage: true
            }
        },
        xAxis: {
            data: week,
            axisLabel: {
                interval: 0,
                rotate: 40
            },
        },
        yAxis: {},
        series: [{
            name: 'name:number',
            type: 'bar',
            itemStyle: {
                normal: {
                    color: '#1f77b4',
                    //barBorderRadius: [20, 20, 20, 20],
                }
            },
            data: week_num,
        }
        ]
    });
}