const html5QrCode = new Html5Qrcode("reader");
const config = { fps: 10, qrbox: 250 };

const qrCodeSuccessCallback = message => {
	html5QrCode.stop();
	$('#reader').css("display", "none");
	$('#fst_qr').html("Прочитан код: "+message);
}

function start_scan_invite() {

	Html5Qrcode.getCameras().then(devices => {
	  /**
	   * devices would be an array of objects of type:
	   * { id: "id", label: "label" }
	   */
	  if (devices && devices.length) {
	    var cameraId = devices[0].id;
		$('#reader').css("display", "block");
		$('#fst_qr').html("");
		html5QrCode.start(cameraId, config, qrCodeSuccessCallback);	
	    // .. use this to start scanning.
	  }
	}).catch(err => {
	  // handle err
	});

}

