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

function show_vol_info(o) {
	$('.feed_name').html(o.name + " " + o.surname + " (" + o.callsign + ")");
}

function show_error(o, msg) {
	$('.feed_decision').css('display', 'block');
	$('.feed').css('background-color', 'red');
	$('.feed_left').html("");
	show_vol_info(o);
	if(msg != "") {
		$('.feed_whynot').html(msg);
	}
}

function show_green(o) {
	$('.feed_decision').css('display', 'none');
	$('.feed_ok').css('display', 'flex');
	$('.feed_50p').css('display', 'none');
	$('.feed_whynot').css('display', 'none');
	$('.feed').css('background-color', 'green');
	show_vol_info(o);
	$('.feed_left').html("Осталось " + (o.balance - 1) + " доступных приемов пищи");
	$('.feed_ok').css('display', 'flex');
}

function show_red(o) {
	$('.feed_decision').css('display', 'flex');
	$('.feed_ok').css('display', 'none');
	$('.feed_50p').css('display', 'none');
	$('.feed_whynot').css('display', 'none');
	$('.feed').css('background-color', 'red');
	$('.feed_left').html("Перерасход приемов пищи:" + ((o.balance - 1) * -1));
	show_vol_info(o);
}

function show_50p(o) {
	$('.feed_decision').css('display', 'none');
	$('.feed_ok').css('display', 'none');
	$('.feed_whynot').css('display', 'none');
	$('.feed_50p').css('display', 'flex');
	$('.feed').css('background-color', 'orange');
	show_vol_info(o);
}

function show_100p(o) {
	$('.feed_decision').css('display', 'none');
	$('.feed_ok').css('display', 'none');
	$('.feed_whynot').css('display', 'none');
	$('.feed_50p').css('display', 'flex');
	$('.feed').css('background-color', 'blue');
	show_vol_info(o);
}


function feed_volunteer(qrcode) {
	$('.trobber').css('display', 'block');

	var ost = db.transaction(["volunteers"], 'readwrite').objectStore('volunteers');
	var ind = ost.index("qrCode");

	ost.onerror = (ev) => {
		$('.trobber').css('display', 'none');
	}

	ind.get(qrcode).onsuccess = (e) => {
		$('.trobber').css('display', 'none');
		$('.feed').css('display', 'flex');

		let o = e.target.result;

		if(o == undefined) {
			o = {
				"name": "Бейдж не найден в списке",
				"surname": "",
				"callsign": "",
				"balance": 0,
				"is_valid": 0,
				"is_active": 0,
				"qr": qrcode
			};			
		}

		$('.feed').attr('qr', o.qr);

		// FT1 - eat while work
		// FT2 - fixed balance
		// FT3 - child
		// FT4 - 50%
		// FT5 - 100%

		if(o.is_valid != 1 || o.is_active != 1) {
			let _msg = "";
			if(o.is_valid != 1) {
				_msg += "Бейдж заблокирован<br>";
			}
			if(o.is_active != 1) {
				_msg += "Бейдж не активирован в штабе";
			}
			show_error(o, _msg);
			return;
		}

		if(o.feed_type == "FT1" || o.feed_type == "FT2" || o.feed_type == "FT3") {
			if(o.balance > 0) {
				show_green(o);
			} else {
				show_red(o);
			}
			return;
		}

		if(o.feed_type == "FT4") {
			show_50p(o);
			return;
		}

		if(o.feed_type == "FT5") {
			show_100p(o);
			return;
		}
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

function feed_dialog_close() {
	$('.feed').css('display', 'none');
	$('.feed_decision').hide();
}



function addVolToDb(o) {
	var tr = db.transaction(["volunteers"], "readwrite");
	tr.objectStore('volunteers').put(o);
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
					tr.objectStore('volunteers').clear();
					tr.oncomplete = (ev) => {
		        result.forEach((i) => {
		        	addVolToDb(i);
		        });
						console.log("DB updated");
	       		show_modal();
					};
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