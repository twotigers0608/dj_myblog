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

function getWeek(date) {
    //var today = (new Date(data)).getTime()
    var today = new Date(date * 1000);
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
    return result;
}

function getyear(date) {
    var today = new Date(date * 1000);
    var y = today.getFullYear();
    return y
}

function data_reduction(data) {
    var week_data = {};
    var new_week_data = {};
    var week_list = [];
    var year_week = {};
    for (var i = 0; i < data.length; i++) {
        var ww = getWeekOfYear(data[i]['release_time']);
        var y = getyear(data[i]['release_time']);
        var w = getWeek(data[i]['release_time']);
        data[i]['week'] = ww;
        data[i]['year'] = y;
        data[i]['week_num'] = w;
        year_week[y] = [];
    }
    //构造一个 year:week 将max 和 min 中的week 填充起来
    for (var key in year_week) {
        col = [];
        for (var c = 0; c < data.length; c++) {
            if (key == data[c]["year"]) {
                col.push(data[c]["week_num"])
            }
        }
        year_week[key] = col;
    }
    for (var key in year_week) {
        var max = Math.max.apply(null, year_week[key]);
        var min = Math.min.apply(null, year_week[key]);
        var diff = max - min + 1;
        $.unique(year_week[key]);
        if (diff != year_week[key].length) {
            var new_week = []
            for (var c = 0; c < diff; c++) {
                var num = min + c;
                new_week.push(num)
            }
            year_week[key] = new_week
        }
    }
    console.log(year_week);
    // week_data = {week:data}
    $.each(year_week, function (key, value) {
        for (var i = 0; i < value.length; i++) {
            var str = '' + key + '-' + value[i];
            week_data[str] = [];
        }
    });

    var year_week_data = {};
    $.each(week_data, function (key, value) {
        for (var i = 0; i < data.length; i++) {
            if (key == data[i]["week"]) {
                value.push(data[i])
            }
        }
    })
    console.log(week_data)
    return week_data;
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

function getDateStr(seconds) {
    var date = new Date(seconds * 1000)
    var year = date.getFullYear();
    var month = date.getMonth() + 1;
    var day = date.getDate();
    var currentTime = year + "-" + month + "-" + day;
    return currentTime
}

function rq_mychart(data_dict, result) {
    //var data_dict = data_reduction(result_data);
    //var result = data_durations(data_dict);
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
                return ['Week:  '] + week + "<br />" + params[0].marker + "Review:    " + review + "<br />" + params[1].marker +
                    "Merge:   " + merge + "<br />" + params[2].marker + "Released:   " + released;
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

function rq_mychart1(data_dict, result) {
    //var data_dict = data_reduction(result_data);
    //console.log('data_dict')
    //console.log(data_dict)
    //var result = data_durations(data_dict)
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
        tooltip: {
            trigger: 'axis',
            label: {
                show: true
            },
            formatter: function (params, ticket, callback) {
                //console.log(params)
                return '' + params[0].value;
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

//返回表格数据
function ajax_datble(data_dict, result) {
    $("#tabledata").html("");
    var str = "<table width=\"90%\" class=\"table\" id=\"tabledata\">\n" +
        "    <tbody>\n" +
        "    <tr class=\"title\">\n" +
        "        <td>ID</td>\n" +
        "        <td>Date</td>\n" +
        "        <td>Review Time</td>\n" +
        "        <td>Verify Time</td>\n" +
        "        <td>Merage Time</td>\n" +
        "        <td>Release Time</td>\n" +
        "    </tr>\n" +
        "    </tbody>\n" +
        "</table>"
    $("#tabledata ").append(str)
    var table_tbody = $("#tabledata").find("tbody");
    //var data_dict = data_reduction(result_data);
    $.each(data_dict, function (key1, value1) {
        var html = "<tr" + " class=" + key1 + ">" + "<th colspan='6' style='text-align:left'>" + "WW" + key1 + "</th>" + "</tr>"
        for (var c = 0; c < value1.length; c++) {
            html += "<tr" + " class=" + key1 + ">";
            var id = value1[c]['id'];
            var verify_time = SecondToDate(value1[c]['verify_duration']);
            var review_time = SecondToDate(value1[c]['review_duration']);
            var date_time = getDateStr(value1[c]['release_time']);
            var merge_time = SecondToDate(value1[c]['merge_duration']);
            var rel_time = SecondToDate(value1[c]['rel_duration']);

            html += "<td>" + "<a href='https://git-amr-4.devtools.intel.com/gerrit/#/c/" + id + "' >" + id + "</a>" + "</td>"
                + "<td>" + date_time + "</td>" +
                "<td>" + review_time + "</td>" +
                "<td>" + verify_time + "</td>" +
                "<td>" + merge_time + "</td>" +
                "<td>" + rel_time + "</td>";
            html += "</tr>"
        }
        table_tbody.append(html)
    });
}
