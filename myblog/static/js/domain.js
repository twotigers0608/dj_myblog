$(document).ready(function () {
    var patch_week = echarts.init(document.getElementById('domain'));
    // 显示标题，图例和空的坐标轴
    patch_week.setOption({
        title: {
            text: 'UPSTREAMING RACE CHART',
            x: 'center',
        },
        tooltip: {},
        legend: {
            data: ['左上角标题']
        },
        xAxis: {
            type: 'category',
            // name: "domain",
            data: []
        },
        yAxis: {
            // name: "Num",
        },
        series: [{
            name: 'time',
            type: 'bar',
            data: []
        }]
    });
    select()
})


// 异步加载数据
function select() {
    var domain = echarts.getInstanceByDom(document.getElementById('domain'));
    $.ajax({
        type: "post",
        async: true,
        url: "/ajax/get_domain/",
        data: {},
        dataType: "json",
        beforeSend: function () {
            domain.showLoading();
        },
        success: function (result) {
            domain.hideLoading();
            result_data = result;
            if (result_data) {
                //var result = data_durations(data_dict);
                //rq_patch_num(data_dict, result);
                //ajax_datble(data_dict, result);
                var data_dict = data_reduction(result_data);
                rq_domain(data_dict);
                console.log(result_data)
            }
        },
        error: function (errorMsg) {
            //请求失败时执行该函数
            alert("Chart request data failed!");
        }
    });

}

//返回图形数据
function rq_domain(data_dict) {
    var domain = echarts.getInstanceByDom(document.getElementById('domain'));
    var a = echarts.g;
    var v54 = data_dict[0];
    var v55 = data_dict[1];
    var v56 = data_dict[2];
    //console.log(week)
    domain.hideLoading();    //隐藏加载动画
    domain.setOption({
        // 顶部选择
        legend: {
            show: true,
            top: "6%",
            data: ['v5.4', 'v5.5', 'v5.6-rc5']
        },
        backgroundColor: "#fbffff",
        // 自动调节位置
        tooltip: {
            trigger: 'axis',
            label: {
                show: true
            },
            /*
            格式化显示柱状图详细资料
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
            */
        },
        // domain
        xAxis: {
            data: ["Graphics+Display", "Camera/IPO", "Sensor", "Storage", "Audio and Codes",
                "Core Kernel", "Image and Video", "USB", "Low power subsystem",
                "Rower and Perfromance", "Network", "config", "Unassrgned", "Hypervisor",
                "Security(Trustu)", "Security(CSE, MEI,...)", "sep-Socwatch"],
            axisLabel: {
                interval: 0,
                rotate: 30,
                grid: {
                    top: '80%',
                    left: '25%',
                    bottom: '60'
                }
            },
        },
        // 每个版本的数量
        yAxis: {
            type: 'value',
            splitArea: {show: true},
        },
        series: [
            {
                name: 'v5.4',
                type: 'bar',
                stack: 'total0',
                itemStyle: {
                    normal: {
                        color: '#1f77b4',
                    }
                },
                data: v54,
            },
            {
                name: 'v5.5',
                type: 'bar',
                stack: 'total1',
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
                data: v55,
            },
            {
                name: 'v5.6-rc5',
                type: 'bar',
                stack: 'total2',
                label: {
                    normal: {
                        position: 'insideRight',

                    }
                },
                itemStyle: {
                    normal: {
                        color: '#9192a4',
                    }
                },
                data: v56,
            }]
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

//构造数据结构
function data_reduction(data) {

    var domain_list = ["Graphics+Display", "Camera/IPO", "Sensor", "Storage", "Audio and Codes",
        "Core Kernel", "Image and Video", "USB", "Low power subsystem",
        "Rower and Perfromance", "Network", "config", "Unassrgned", "Hypervisor",
        "Security(Trustu)", "Security(CSE, MEI,...)", "sep-Socwatch"]
    var total_list = [];
    $.each(data, function (key, value) {
            console.log(value);
            var data_list = [];
            // $.each(value, function (key1, value1) {
            //     data_list.push(value1)
            // });
            for (var i = 0; i < domain_list.length; i++) {
                console.log(value[domain_list[i]]);
                if (value[domain_list[i]]) {
                    var num = parseInt(value[domain_list[i]])
                    data_list.push(num)
                } else {
                    data_list.push(0)
                }
            }
            total_list.push(data_list);
        }
    )
    console.log(total_list)
    return total_list;
}

//返回表格数据
function ajax_datble(data_dict, result) {
    $("#tabledata").html("");
    var str = "<table width=\"90%\" class=\"table\" id=\"tabledata\">\
            <tbody>\
            <tr class=\"title\">\
                <td>ID</td>\
                <td>Date</td>\
                <td>Review Time</td>\
                <td>Verify Time</td>\
                <td>Merage Time</td>\
                <td>Release Time</td>\
            </tr>\
            </tbody>\
        </table>"
    $("#tabledata ").append(str)
    var $tbody = $("#tabledata").find("tbody");
    var sorted_ww = Object.keys(data_dict).sort().reverse();
    $.each(sorted_ww, function (i, ww) {
        //console.log(result_data)
        ww_data = data_dict[ww];
        var html = "<tr" + " class=" + ww + ">" + "<th colspan='6' style='text-align:left'>" + "WW" + ww + "</th>" + "</tr>"
        for (var c = 0; c < ww_data.length; c++) {
            html += "<tr" + " class=" + ww + ">";
            var id = ww_data[c]['id'];
            var verify_time = SecondToDate(ww_data[c]['verify_duration']);
            var review_time = SecondToDate(ww_data[c]['review_duration']);
            var date_time = getDateStr(ww_data[c]['release_time']);
            var merge_time = SecondToDate(ww_data[c]['merge_duration']);
            var rel_time = SecondToDate(ww_data[c]['rel_duration']);

            // html += "<td>" + "<a target='_blank' href='https://git-amr-4.devtools.intel.com/gerrit/#/c/" + id + "' >" + id + "</a>" + "</td>"
            //     + "<td>" + date_time + "</td>" +
            //     "<td>" + review_time + "</td>" +
            //     "<td>" + verify_time + "</td>" +
            //     "<td>" + merge_time + "</td>" +
            //     "<td>" + rel_time + "</td>";
            // html += "</tr>"
            html += "<td>" + "<a target='_blank' href='https://git-amr-4.devtools.intel.com/gerrit/#/c/" + id + "' >" + id + "</a>" + "</td>"
                + "<td>" + date_time + "</td>" +
                "<td>" + review_time + "</td>" +
                "<td>" + verify_time + "</td>" +
                "<td>" + merge_time + "</td>" +
                "<td>" + rel_time + "</td>";
            html += "</tr>"
        }
        ;
        $tbody.append(html)
        //console.log(html)
    });
}
