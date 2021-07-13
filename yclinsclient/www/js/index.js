/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

// Wait for the deviceready event before using any of Cordova's device APIs.
// See https://cordova.apache.org/docs/en/latest/cordova/events/events.html#deviceready
document.addEventListener('deviceready', onDeviceReady, false);

function onDeviceReady() {
    // Cordova is now initialized. Have fun!
    console.log('Running cordova-' + cordova.platformId + '@' + cordova.version);
    init();
}


function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}


var db;
var qr_scanner;


function initDB() {
	var dbName = 'yclins';
	var dbVer = 2;

	var openRequest = window.indexedDB.open(dbName, dbVer);

	console.log('init DB...');

	return new Promise((resolve, reject) => {
		openRequest.onerror = function (event) {
			reject({'res': 0, 'code': openRequest.errorCode});
		};

		openRequest.onsuccess = function (event) {
			db = openRequest.result;
			resolve({'res': 1})
		};

		openRequest.onupgradeneeded = function (event) {
			var db = event.target.result;
			db.onerror = function () {
				reject({'res': 0, 'code': db.errorCode});
			};

			var storeV = db.createObjectStore('volunteers', { keyPath: 'id' });
			var storeT = db.createObjectStore('transactions', { keyPath: 'id', autoIncrement:true });

			storeV.createIndex('qrCode', 'qr', { unique: true });
		};
	});
}


function initView() {
	qr_scanner = window.QRScanner;
}


function init() {
	initDB().then((v) => {
		initView();
	}).catch((e) => {
		console.log(e);
	});
	
}


function sendTransactions() {

}


function show_modal() {
	$('#infomessages').show();
	$('#infomessages').css('opacity', '100');
	$('.prj').show();	
}


function hide_modal() {
	$('#infomessages').hide();
	$('.prj').hide();
}


function scan_qr() {
	$(".app").hide();
	qr_scanner.scan( (err, cont) => {
			console.log(cont);
			qr_scanner.hide();
			$(".app").show();
			$("body").css('background-color', 'white');
			feed_volunteer(cont);
	} );
	qr_scanner.show( (sts) => {
		console.log(sts);
	});
}


function add_feed_transaction(qrcode) {
	var tr = db.transaction(["volunteers", "transactions"], 'readwrite');
	var ostv = tr.objectStore('volunteers');
	var ostt = tr.objectStore('transactions');
	var ind = ostv.index("qrCode");
	ind.get(qrcode).onsuccess = (e) => {
		let o = e.target.result;
		if(o !== undefined) {
			t = {
				"vol_id": o.id,
				"dtime": Date.now(),
				"amount": 1,
				"trhash": uuidv4()
			};
			ostt.add(t);
		}
	}
}


function feed_volunteer(qrcode) {
	var ost = db.transaction(["volunteers"], 'readwrite').objectStore('volunteers');
	var ind = ost.index("qrCode");
	ind.get(qrcode).onsuccess = (e) => {
		let showGreen = false;
		let o = e.target.result;
		if(o !== undefined) {
			if(o.balance > 0) {
				showGreen = true;
			};
			$('.feed').attr('qr', o.qr);
		} else {
			o = {
				"name": "Anonymous",
				"surname": "",
				"callsign": "",
				"balance": 0,
				"qr": qrcode
			};
			$('.feed').attr('qr','-1');
		}
		$('.feed').css('display', 'flex');
		if(showGreen) {
			$('.feed').css('background-color', 'green');
			o.balance -= 1;
			ost.put(o);
			add_feed_transaction(qrcode);
			setTimeout(() => {
				$('.feed').css('display', 'none');
			}, 4000);
		} else {
			$('.feed').css('background-color', 'red');
			let _msg = "";
			if(o.is_valid != 1) {
				msg += "Бейдж помечен невалидным";
			}
			if(o.is_valid != 1) {
				msg += "Бейдж не активирован в штабе";
			}
			if(msg != "") {
				$('.feed_whynot').html(msg);
			}
			$('.feed_decision').show();
		}
		$('.feed_name').html(o.name + " " + o.surname + " (" + o.callsign + ")");
		$('.feed_left').html("Осталось питания: " + (o.balance));
	}
}

function force_feed() {
	$('.feed').css('display', 'none');
	$('.feed_decision').hide();
	let qr = $('.feed').attr('qr');
	if(qr == undefined) {
		return;
	}
	var ost = db.transaction(["volunteers"], 'readwrite').objectStore('volunteers');
	var ind = ost.index("qrCode");
	ind.get(qr).onsuccess = (e) => {
		let o = e.target.result;
		if(o !== undefined) { 
			o.balance -= 1;
			ost.put(o);
			add_feed_transaction(qr);
		}
	}	
}

function force_nofeed() {
	$('.feed').css('display', 'none');
	$('.feed_decision').hide();	
}


function getOnlyVols() {
	var apiUrl = 'https://yclins.hamsterspb.xyz/get_vol_list';
	$.ajax({
	    type: "GET",
	    url: apiUrl,
	    crossDomain: true,
	    cache: false,
	    success: function(result) {
	        var result = $.parseJSON(result);
	        var tr = db.transaction(["volunteers"], "readwrite");
	        var ost = tr.objectStore('volunteers');
	        ost.clear();
	        result.forEach((i) => {
	        	ost.add(i);
	        });
	        console.log("DB updated");
	        show_modal();
	    }
	});	
}


function getVolunteers() {

	var tr = db.transaction(["transactions"], 'readwrite');
	var ostt = tr.objectStore('transactions');

	var req = ostt.getAll();
	req.onsuccess = (e) => {
		var data2 = [];
		var trs = e.target.result;
		trs.forEach((o) => {
			let _t = {
				'vol_id': o.vol_id,
				'amount': o.amount,
				'timestamp': o.dtime,
				'trhash': o.trhash
			};
			data2.push(_t);
		});
		var sendUrl = 'https://yclins.hamsterspb.xyz/load_transactions';
		$.ajax({
			type: 'POST',
			url: sendUrl,
			crossDomain: true,
			data: JSON.stringify(data2),
			contentType: "application/json; charset=utf-8",
			success: (ev) => {
				var tr = db.transaction(["transactions"], 'readwrite');
				var ostt = tr.objectStore('transactions');
				ostt.clear();
				getOnlyVols();
			},
			failure: (ev) => {
            	console.log(ev);
        	}
		});
	}
}