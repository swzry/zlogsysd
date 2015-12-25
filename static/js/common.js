function CopyTitle(){
	//document.title=$('#pagetitle').html();
	$("#pagetitlebar_pcc").html(document.title);
	$("#pagetitlebar_mbc").html(document.title);
}
function mobi_navmenutoggle() {
	if($("#mobi_navmenu").attr("disp")=="1"){
		$("#mobi_navmenu").attr("disp","0");
		$("#mobi_navmenu").css("display","none");
		$("#mobi_navmenu_icon").attr("class","glyphicon glyphicon-chevron-up");
	}else{
		$("#mobi_navmenu").attr("disp","1");
		$("#mobi_navmenu").css("display","block");
		$("#mobi_navmenu_icon").attr("class","glyphicon glyphicon-chevron-down");
	}
}

function uuidGenerate() {
	var s = [];
	var hexDigits = "0123456789abcdef";
	for (var i = 0; i < 36; i++) {
		s[i] = hexDigits.substr(Math.floor(Math.random() * 0x10), 1);
	}
	s[14] = "4"; // bits 12-15 of the time_hi_and_version field to 0010
	s[19] = hexDigits.substr((s[19] & 0x3) | 0x8, 1); // bits 6-7 of the clock_seq_hi_and_reserved to 01
	s[8] = s[13] = s[18] = s[23] = "-";

	var uuid = s.join("");
	return uuid;
} 