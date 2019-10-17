//将时间戳转换为标准时间
function getWeekOfYear(date) {
    //var today = (new Date(data)).getTime()
    var today = new Date(date * 1000);
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

function SecondToDate(msd) {
    var time = msd
    if (null != time && "" != time) {
        //minute
        if (time > 60 && time < 60 * 60) {
            time = parseInt(time / 60.0) + "m";
        } else if (time >= 60 * 60 && time < 60 * 60 * 24) {
            //hour
            time = parseInt(time / 3600.0) + "h" + parseInt((parseFloat(time / 3600.0) -
                parseInt(time / 3600.0)) * 60) + "m";
        } else if (time >= 60 * 60 * 24) {
            //day
            time = parseInt(time / 3600.0 / 24) + "day" + parseInt((parseFloat(time / 3600.0 / 24) -
                parseInt(time / 3600.0 / 24)) * 24) + "h";
        } else {
            time = parseInt(time) + "s";
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
    //data是一个总的字典, list是字典中的相同周数据
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

function avg_duration(list, num) {
    re_list = [];
    for (var i = 0; i < list.length; i++) {
        if (num[i] == 0) num++;
        avg_time = parseFloat(list[i] / 3600 / num[i], 10).toFixed(2);
        avg_time = Number(avg_time);
        re_list.push(avg_time);
    }
    //console.log(re_list)
    return re_list
}

function data_durations(data) {
    result = {};
    week = [];
    review_list = [];
    merge_list = [];
    rel_list = [];
    review_num_list = [];
    merge_num_list = [];
    released_num_list = [];
    $.each(data, function (k, v) {
        var review_duration = 0;
        var merge_duration = 0;
        var released_duration = 0;
        var review_num = 0;
        var merge_num = 0;
        var released_num = 0;
        week.push(k);
        for (var l = 0; l < v.length; l++) {
            if (v[l]['review_duration'] != 0) review_num++;
            review_duration += v[l]['review_duration'];
            if (v[l]['merge_duration'] != 0) merge_num++;
            merge_duration += v[l]['merge_duration'];
            if (v[l]['rel_duration'] != 0) released_num++;
            released_duration += v[l]['rel_duration'];
        }
        review_list.push(review_duration);
        merge_list.push(merge_duration);
        rel_list.push(released_duration);
        review_num_list.push(review_num);
        merge_num_list.push(merge_num);
        released_num_list.push(released_num);
    });
    review_duration_list = avg_duration(review_list, review_num_list);
    merge_duration_list = avg_duration(merge_list, merge_num_list);
    released_durations_list = avg_duration(rel_list, released_num_list);
    result['week'] = week;
    result['review_duration'] = review_duration_list;
    result['merge_duration'] = merge_duration_list;
    result['rel_duration'] = released_durations_list;
    //console.log(result)
    return result
}

function getDateStr(seconds) {
    var date = new Date(seconds * 1000)
    var year = date.getFullYear();
    var month = date.getMonth() + 1;
    var day = date.getDate();
    var currentTime = year + "-" + month + "-" + day;
    return currentTime
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
                var html = "<tr" + " class=" + key1 + ">" + "<td colspan='6' style='text-align:left'>" + key1 + "</td>" + "</tr>"
                for (var c = 0; c < value1.length; c++) {
                    html += "<tr" + " class=" + key1 + ">";
                    var id = value1[c]['id'];
                    var verify_time = SecondToDate(value1[c]['verify_duration']);
                    var review_time = SecondToDate(value1[c]['review_duration']);
                    //var date_time =new Date(value1[c]['released_time']);
                    var date_time = getDateStr(value1[c]['released_time']);
                    console.log(value1[c]['review_duration'])
                    var merge_time = SecondToDate(value1[c]['merge_duration']);
                    var rel_time = SecondToDate(value1[c]['rel_duration']);
                    html += "<th>" + "<a href='#'>" + id + "</a>" + "</th>"
                        + "<th>" + date_time + "</th>" +
                        "<th>" + review_time + "</th>" +
                        "<th>" + verify_time + "</th>" +
                        "<th>" + merge_time + "</th>" +
                        "<th>" + rel_time + "</th>";
                    html += "</tr>"
                }
                ;
                $tbody.append(html)
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
        tooltip: {
            trigger: 'axis',
            label: {
                show: true
            },
            formatter: function (params, ticket, callback) {
                //console.log(params);
                //console.log(ticket);
                //console.log(callback);
                var week = params[0].name;
                var review = SecondToDate(params[0].value * 3600);
                var merge = SecondToDate(params[1].value * 3600);
                var released = SecondToDate(params[2].value * 3600);

                return ['week:  '] + week + "<br />" + "Review:    " + review + "<br />" +
                    "Merge:   " + merge + "<br />" + "Released:   " + released;
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