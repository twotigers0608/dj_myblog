//将时间戳转换为标准时间
function getWeekOfYear(date) {
    //var today = (new Date(data)).getTime()
    var today = new Date(date * 1000);
    //console.log(today)
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

function SecondToDate(msd) {
    var time = msd
    if (null != time && "" != time) {
        if (time > 60 && time < 60 * 60) {
            time = parseInt(time / 60.0) + "m";
        } else if (time >= 60 * 60 && time < 60 * 60 * 24) {
            time = parseInt(time / 3600.0) + "h" + parseInt((parseFloat(time / 3600.0) -
                parseInt(time / 3600.0)) * 60) + "m";
            parseInt((parseFloat((parseFloat(time / 3600.0) - parseInt(time / 3600.0)) * 60)))
        } else if (time >= 60 * 60 * 24) {
            time = parseInt(time / 3600.0 / 24) + "day" + parseInt((parseFloat(time / 3600.0 / 24) -
                parseInt(time / 3600.0 / 24)) * 24) + "h";
        }
    }
    return time;
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
        var review_num = 0;
        var merge_num = 0;
        var released_num = 0;
        week.push(k);
        for (var l = 0; l < v.length; l++) {
            review_duration += v[l]['review_duration'];
            merge_duration += v[l]['merge_duration'];
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
$.fn.grid = function (options) {
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
                    new_cols = {};
                    new_cols['week'] = cols['week'];
                    new_cols['id'] = cols['id'];
                    var verrify_time = SecondToDate(cols['verify_duration']);
                    new_cols['verify_duration'] = verrify_time;
                    var review_time = SecondToDate(cols['review_duration']);
                    new_cols['review_duration'] = review_time;
                    var merge_time = SecondToDate(cols['merge_duration']);
                    new_cols['merge_duration'] = merge_time;
                    var rel_time = SecondToDate(cols['rel_duration']);
                    new_cols['rel_duration'] = rel_time;
                    var html = "<tr" + " class=" + cols['week'] + ">";
                    $.each(new_cols, function (k, v) {
                        //console.log(v)
                        html += "<th>" + v + "</th>"
                    });
                    html += "</tr>";
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
        /*Work
                Week:                2019.20
                Nbr:                    2

                BeforeReview:        6 Day(s) 10 Hour(s)(81 %)
                Review:            0 Day(s) 10 Hour(s)(5 %)
                Maintainer:            0 Day(s) 1 Hour(s)(0 %)
                SubmitToMerge:        1 Day(s) 1 Hour(s)(13 %)
                Merge:            0 Day(s) 1 Hour(s)(1 %)*/
        tooltip: {
            trigger: 'axis',
            label: {
                show: true
            },
            formatter: function (params, ticket, callback) {
                console.log(params);
                console.log(ticket);
                console.log(callback);

                return ['week'] + params[0].name + "<br />" + "Review:    " + params[0].value + "<br />" +
                    "Merge:   " + params[1].value + "<br />" + "Released:   " + params[2].value;
            }
        },
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
        series: [
            {
                name: 'Review',
                type: 'bar',
                stack: 'total',
                itemStyle: {
                    normal: {
                        color: '#1f77b4',
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
                        position: 'insideRight',
                    }
                },
                itemStyle: {
                    normal: {
                        color: '#9467bd',
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
                        position: 'insideRight',

                    }
                },
                itemStyle: {
                    normal: {
                        color: '#ff7f0e',
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
                }
            },
            data: week_num,
        }
        ]
    });
}

/* ajax crsf */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        var csrftoken = getCookie('csrftoken');
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});