const html5QrCode = new Html5Qrcode("reader");
const config = { fps: 20 };

const link_vol = message => {
	html5QrCode.stop();
	$('#reader').css("display", "none");

	var data2 = {
		"vol_id": vol_id,
		"qr": message
	};

	$.ajax({
		type: 'POST',
		url: '/link_vol_to_badge',
		crossDomain: true,
		data: JSON.stringify(data2),
		contentType: "application/json; charset=utf-8",
		success: (ev) => {
			$('#res').html("Прочитан код: "+message + " vol:" + vol_id);
		},
		failure: (ev) => {
        	$('#res').html("Ошибка: "+ev);
    	}
	});
}

const activate_vol = message => {
	html5QrCode.stop();
	$('#reader').css("display", "none");

	var data2 = {
		"qr": message
	};

	$.ajax({
		type: 'POST',
		url: '/activate_vol',
		crossDomain: true,
		data: JSON.stringify(data2),
		dataType: "json",
		contentType: "application/json; charset=utf-8",
		success: (ev) => {
			console.log(ev.res);
			if(ev.res == "ok"){
				$('#fst_qr').html("Прочитан код: "+message+"<br>Бейдж для "+ev.name+" активирован.");
			} else {
				$('#fst_qr').html("Прочитан код: "+message+"<br>Произошла ошибка, бейдж не активирован!!!");
			}
			
		},
		failure: (ev) => {
        	$('#fst_qr').html("Ошибка: "+ev);
    	}
	});
}

function start_scan_invite(mode) {

	Html5Qrcode.getCameras().then(devices => {
	  /**
	   * devices would be an array of objects of type:
	   * { id: "id", label: "label" }
	   */
	  if (devices && devices.length) {
	    var cameraId = devices[0].id;
		$('#reader').css("display", "block");
		$('#fst_qr').html("");
		if(mode == "link") {
			var cbf = link_vol;
		} else {
			var cbf = activate_vol;
		}
		html5QrCode.start(cameraId, config, cbf);
	  }
	}).catch(err => {
	  console.log(err);
	});
}

