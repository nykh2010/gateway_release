// server_setup.js

function server_config() {
	var xsrf_tmp = $("#wan_dhcp_form").children("input[name='_xsrf']").val();
	var obj = {};
	obj._xsrf = xsrf_tmp;
	obj.sip = $("#sip").val();
	obj.sport = $("#sport").val();
	obj.skey = $("#skey").val();
	obj.gid = $("#gid").val();
	obj.mac = $("#mac").val();
	obj.ethernet = $("#ethernet_enable").hasClass("radio_on");

	$.post("/setup/server", obj, function(data){
		var ret = dataDeal(data);
        if (ret == "SUCCESS") {
            show_message("success");
        }
        else {
            show_message("error", igd.make_err_msg(data));
        }
	});
}