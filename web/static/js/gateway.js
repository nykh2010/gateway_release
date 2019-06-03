$(function(){
    $(".return_a").click(function(){
        window.history.back();
    });

    var timer = setInterval(refresh_sys_time, 1000);
    
    function refresh_sys_time() {
        var time = new Date();
        // 2019-01-21 10:47:56
        year = time.getFullYear();
        month = time.getMonth()+1;
        days = time.getDate();
        hours = time.getHours();
        minutes = time.getMinutes();
        seconds = time.getSeconds();
        month = checkTime(month);
        days = checkTime(days);
        hours = checkTime(hours);
        minutes = checkTime(minutes);
        seconds = checkTime(seconds);
        var strtime = year+"-"+month+"-"+days+"&nbsp"+hours+":"+minutes+":"+seconds;
        $("#current_time").html(strtime);
        delete time;
    }
});

