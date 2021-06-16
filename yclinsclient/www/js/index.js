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


var db;

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
			var storeT = db.createObjectStore('transactions', { keyPath: 'id' });

			storeV.createIndex('qrCode', 'qr', { unique: true });
		};
	});
}


function initView() {

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


function hide_modal() {
	$('#infomessages').hide();
	$('.prj').hide();
}


function getVolunteers() {
	$('#infomessages').show();
	$('#infomessages').css('opacity', '100');
	$('.prj').show();

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
	        result.forEach((i) => {
	        	ost.add(i);
	        });
	        tr.commit();
	        console.log("DB updated");
	    }
	});
}