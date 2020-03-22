$(document).ready(function () {
    var patch_week = echarts.init(document.getElementById('domain'));
    // 显示标题，图例和空的坐标轴
    patch_week.setOption({
        title: {
            text: 'UPSTREAMING RACE CHART',
            x: 'center'
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
    select();
})

// window.addEvent('domready', function() {
// 	var count = 0;
// 	$('table tbody tr').each(function(el) {
// 		el.addClass(count++ % 2 == 0 ? 'odd' : 'even');
// 	});
// });

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

            // data_reduction2(result_data);
            if (result_data) {
                //var result = data_durations(data_dict);
                //rq_patch_num(data_dict, result);
                //ajax_datble(data_dict, result);
                var data_dict = data_reduction(result_data);
                rq_domain(data_dict);
                get_num(data_dict);
                get_total_num(result_data)
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
                "Core Kernel", "Image and Video", "USB", "LowPowerSubsystem",
                "Rower Perfromance", "Network", "config", "Unassrgned", "Hypervisor",
                "Security(Trustu)", "Security(CSE, MEI)", "sep-Socwatch"],
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

//构造echarts数据结构
function data_reduction(data) {
    var domain_list = ["Graphics+Display", "Camera/IPO", "Sensor", "Storage", "Audio and Codes",
        "Core Kernel", "Image and Video", "USB", "Low power subsystem",
        "Rower and Perfromance", "Network", "config", "Unassrgned", "Hypervisor",
        "Security(Trustu)", "Security(CSE, MEI,...)", "sep-Socwatch"]
    var total_list = [];
    $.each(data, function (key, value) {
            //console.log(value);
            var data_list = [];
            // $.each(value, function (key1, value1) {
            //     data_list.push(value1)
            // });
            for (var i = 0; i < domain_list.length; i++) {
                //console.log(value[domain_list[i]]);
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


function get_num(data) {
    //重写数据
    var domain_listv54 = ["Graphicsv54", "Camerav54", "Sensorv54", "Storagev54", "Audiov54",
        "Kernelv54", "Imagev54", "USBv54", "powerv54",
        "Rowerv54", "Networkv54", "configv54", "Unassrgnedv54", "Hypervisorv54",
        "Securityv54", "Trustuv54", "Socwatchv54"];
    var domain_listv55 = ["Graphicsv55", "Camerav55", "Sensorv55", "Storagev55", "Audiov55",
        "Kernelv55", "Imagev55", "USBv55", "powerv55",
        "Rowerv55", "Networkv55", "configv55", "Unassrgnedv55", "Hypervisorv55",
        "Securityv55", "Trustuv55", "Socwatchv55"];
    var domain_listv56 = ["Graphicsv56", "Camerav56", "Sensorv56", "Storagev56", "Audiov56",
        "Kernelv56", "Imagev56", "USBv56", "powerv56",
        "Rowerv56", "Networkv56", "configv56", "Unassrgnedv56", "Hypervisorv56",
        "Securityv56", "Trustuv56", "Socwatchv56"];
    var domain_list=[];
    domain_list.push(domain_listv54);
    domain_list.push(domain_listv55);
    domain_list.push(domain_listv56);
    for (var i =0; i<data.length;i++){
        $.each(data[i],function (x,y) {
            $("#" + domain_list[i][x]).text(y);
        })
    }
}

function get_total_num(data) {
    var total_list = [];
    $.each(data,function (v, value) {
        var total=0;
        $.each(value,function (k, num) {
            total += num;
        });
        total_list.push(total);
    });
    total_id = ["totalv54", "totalv55", "totalv56"];

    for (var i = 0; i < total_id.length; i++){
        $("#" + total_id[i]).text(total_list[i])
    }
}