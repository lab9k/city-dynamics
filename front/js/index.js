// map & layers
var map;
var gauge;
var theme_layer;
var circles = [];
var circles_d3 = [];
var circles_layer;
var markers = [];
// var geojson;
var traffic_layer;
var districts_d3 = [];
var hotspots_d3 = [];
var hotspots_layer;
var districts_layer;
var districtsIndexJson;
var districtsJson;
var hotspotsIndexJson;
var hotspotsJson;
var realtimeJson;

// global arrays
var control_array = ['search','logo','dlogo','m_more','m_menu','beta','controls','themas','mapswitch','info','leftbox']
var control_array = ['info']
var districts_array = [];
var hotspots_array = [];
var realtime_array = [];

// states
var debug = false;
var vollcode;
var mobile = false;
var active_layer = 'hotspots';
var ams_realtime = 0;
var ams_expected = 0;

// global vars
var marker; // used by search
var lastClickedLayer;
var total_index;
var areaGraph;

// interval
var popup_interval;

// links
var geomap1 = 'https://t1.data.amsterdam.nl/topo_wm/{z}/{x}/{y}.png';
var geomap2 = 'https://t1.data.amsterdam.nl/topo_wm_zw/{z}/{x}/{y}.png';
var geomap3 = 'https://t1.data.amsterdam.nl/topo_wm_light/{z}/{x}/{y}.png';

// Initially assume we have the API running locally.
// var origin = 'http://127.0.0.1:8117/api';
var origin = 'https://acc.drukteradar.amsterdam.nl/api';


if(window.location.href.indexOf('drukteradar.amsterdam.nl') > -1)
{
	var origin = 'https://drukteradar.amsterdam.nl/api';
}

// However, when using the acceptation server, get the API from there.
if(window.location.href.indexOf('acc.drukteradar.amsterdam.nl') > -1)
{
	var origin = 'https://acc.drukteradar.amsterdam.nl/api';
}


var base_api = origin + '/';
var hotspotsJsonUrl = base_api + 'hotspots/?format=json';
var hotspotsIndexJsonUrl = base_api + 'hotspots_drukteindex/?format=json';
var districtJsonUrl = base_api + 'buurtcombinatie/?format=json';
var districtIndexJsonUrl = base_api + 'buurtcombinatie_drukteindex/?format=json';
var realtimeUrl = base_api + 'realtime/?format=json';


// theme api
var trafficJsonUrl = origin + '/apiproxy?api=traveltime&format=json';
var parkJsonUrl = origin + '/apiproxy?api=parking_garages&format=json';
var fietsJsonUrl = origin + '/apiproxy?api=ovfiets&format=json';
var eventsJsonUrl = origin + '/apiproxy?api=events&format=json';
var weatherJsonUrl = 'https://weerlive.nl/api/json-data-10min.php?key=demo&locatie=Amsterdam';

// temp local api
// hotspotsJsonUrl = 'data/hotspots.json';
// hotspotsIndexJsonUrl = 'data/hotspots_drukteindex.json';
// districtJsonUrl = 'data/buurtcombinaties.json';
// districtIndexJsonUrl = 'data/buurtcombinaties_drukteindex.json';
// realtimeUrl = 'data/realtime.json';
//
// trafficJsonUrl = 'data/reistijdenAmsterdam.geojson';
// parkJsonUrl = 'data/parkjson.json';
// fietsJsonUrl = 'data/ovfiets.json';
// eventsJsonUrl = 'data/events.js';

// specific
var def = '+proj=sterea +lat_0=52.15616055555555 +lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel +towgs84=565.4171,50.3319,465.5524,1.9342,-1.6677,9.1019,4.0725 +units=m +no_defs ';
var proj4RD = proj4('WGS84', def);
var amsterdam = {
	coordinates: [52.368, 4.897],
	druktecijfers: [{h:0,d:0,i:0},{h:1,d:0,i:0},{h:2,d:0,i:0},{h:3,d:0,i:0},{h:4,d:0,i:0},{h:5,d:0,i:0},{h:6,d:0,i:0},{h:7,d:0,i:0},{h:8,d:0,i:0},{h:9,d:0,i:0},{h:10,d:0,i:0},{h:11,d:0,i:0},{h:12,d:0,i:0},{h:13,d:0,i:0},{h:14,d:0,i:0},{h:15,d:0,i:0},{h:16,d:0,i:0},{h:17,d:0,i:0},{h:18,d:0,i:0},{h:19,d:0,i:0},{h:20,d:0,i:0},{h:21,d:0,i:0},{h:22,d:0,i:0},{h:23,d:0,i:0},{h:24,d:0,i:0}],
	hotspot: "Amsterdam",
	index: -1
}

// ######### onload init sequence ###############
$(document).ready(function(){

	// set page tag
	setTag('main');

	// check device resolution
	mobile = ($( document ).width()<=750);

	$.each(control_array, function (key, value) {
		var controlDiv = L.DomUtil.get(value);
		L.DomEvent.disableClickPropagation(controlDiv);
	});


	initMap();

	if(debug) {
		console.log('Do mandatory api calls:');
		console.log(districtIndexJsonUrl);
		console.log(districtJsonUrl);
		console.log(hotspotsIndexJsonUrl);
		console.log(hotspotsJsonUrl);
		console.log(realtimeUrl);
	}

	// first promise chain
	$.when($.getJSON(districtIndexJsonUrl),$.getJSON(districtJsonUrl),$.getJSON(hotspotsJsonUrl), $.getJSON(hotspotsIndexJsonUrl),$.getJSON(realtimeUrl)).done(
		function(districtsIndexJson_t,districtsJson_t,hotspotsJson_t,hotspotsIndexJson_t,realtimeJson_t){

		districtsIndexJson = districtsIndexJson_t[0];
		districtsJson = districtsJson_t[0];
		hotspotsIndexJson = hotspotsIndexJson_t[0];
		hotspotsJson = hotspotsJson_t[0];
		realtimeJson = realtimeJson_t[0];

		if(debug) {
			console.log('Districts index json:');
			console.log(districtsIndexJson);
			console.log('Districts geo json:');
			console.log(districtsJson);
			console.log('Hotspots index json:');
			console.log(hotspotsIndexJson);
			console.log('Hotspots geo json:');
			console.log(hotspotsJson);
			console.log('Realtime json:');
			console.log(realtimeJson);
		}

		getDistrictIndex();

		getDistricts();

		getHotspotsIndex();

		getHotspots();

		calcAmsAverage();

		getRealtime();

		initGauge();

		initLineGraph();

		initAutoComplete();

		initWeerWidget();

		initEventMapping();

		// start with traffic
		hideActiveLayer();
		resetTheme();
		// showInfo('Verkeersdrukte in en rondom de stad.', 0);
		addTrafficLayer();
		$('.traffic_b').addClass('active');
		setTag('traffic');

		// custom
		$('.event_today').html(getDay());

	}).fail(function(districtsIndexJson_t,districtsJson_t,hotspotsJson_t,hotspotsIndexJson_t,realtimeJson_t){
		console.error('One or more apis failed.');
		if(dindexJson[1]!='success')
		{
			console.error('One or more apis failed.');
		}
	});

	// chrome control button style
	if (navigator.appVersion.indexOf("Chrome/") != -1) {
		$('.controls').addClass('chrome');
	}

	// $('.index0').css('color',getColorChroma(0));
	// $('.index10').css('color',getColorChroma(0.1));
	// $('.index20').css('color',getColorChroma(0.2));
	// $('.index30').css('color',getColorChroma(0.3));
	// $('.index40').css('color',getColorChroma(0.4));
	// $('.index50').css('color',getColorChroma(0.5));
	// $('.index60').css('color',getColorChroma(0.6));
	// $('.index70').css('color',getColorChroma(0.7));
	// $('.index80').css('color',getColorChroma(0.8));
	// $('.index90').css('color',getColorChroma(0.9));
	// $('.index100').css('color',getColorChroma(1));

});

// ######### general init and get functions ###############
function initMap()
{
	if(mobile) {
		var map_center = [52.368, 4.897];
		var zoom = 13.5;
	}
	else {
		var map_center = [52.368, 4.897];
		var zoom = 13.5;

		// var map_center = [52.36, 4.95];
		// var zoom = 12;
	}

	$('.graphbar_title span').html(getCurrentDateOnly());

	// wgs map
	map = L.map('mapid', {zoomControl: false}).setView(map_center, zoom);

	L.tileLayer(geomap2, {
		minZoom: 10,
		maxZoom: 18
	}).addTo(map);

	L.control.zoom({
		position:'topright'
	}).addTo(map);
}

function getDistrictIndexOld() {

		$.each(districtsIndexJson.results, function (key, value) {

			var buurtcode = this.vollcode;

			var dataset = {};

			dataset.index = this.druktecijfers_bc;
			if(dataset.index.length>0)
			{
				dataset.index.push({h:24,d:dataset.index[0].d});
			}

			districts_array[buurtcode] = dataset;
		});

		if(debug) { console.log('getDistrictIndex: Done') }
}

function getDistrictIndex() {

	$.each(districtsIndexJson.results, function (key, value) {

		var buurtcode = this.vollcode;

		var dataset = {};

		var day_array = [];

		this.druktecijfers_bc.sort(function (a, b) {
			return a.d - b.d;
		});

		var days = [];
		$.each(this.druktecijfers_bc, function (key, value) {
			if($.inArray(this.d, days)==-1)
			{
				days.push(this.d);
				day = this.d;
			}
			if(days.length==1)
			{
				if(this.h>=5 && this.d == day)
				{
					day_array.push(this);
				}
			}
			if(days.length==2)
			{
				if(this.h<=5 && this.d == day)
				{
					day_array.push(this);
				}
			}
		});

		day_array.sort(function (a, b) {
			return a.d - b.d;
		});

		dataset.index = day_array;

		//if(dataset.index.length==25)
		//{
			districts_array[buurtcode] = dataset;
		//}

	});

	if(debug) { console.log('getDistrictIndex: Done') }

}

function getDistricts()
{
	districts_layer = L.geoJSON(districtsJson.results, {style: styleDistrict, onEachFeature: onEachFeatureDistrict}).addTo(map);

	districts_layer.eachLayer(function (layer) {

		layer._path.id = 'feature-' + layer.feature.properties.vollcode;
		districts_d3[layer.feature.properties.vollcode] = d3.select('#feature-' + layer.feature.properties.vollcode);
	});

	// hide map by default
	map.removeLayer(districts_layer);

	if(debug) { console.log('getDistricts: Done') }


	if(debug) {
		console.log('districts_array:');
		console.log(districts_array);
	}

}

function addDistrictLayer()
{
	districts_layer.addTo(map);

	districts_layer.eachLayer(function (layer) {
		layer._path.id = 'feature-' + layer.feature.properties.vollcode;
		districts_d3[layer.feature.properties.vollcode] = d3.select('#feature-' + layer.feature.properties.vollcode);

		var elapsed_time = $('.line-group').attr('time');
		var hour = convertHour(Math.ceil(elapsed_time));

		if(districts_array[layer.feature.properties.vollcode].index.length)
		{
			districts_d3[layer.feature.properties.vollcode].attr('fill', getColor(districts_array[layer.feature.properties.vollcode].index[hour].i));
		}
	});
}

function styleDistrict(feature) {

	if(districts_array[feature.properties.vollcode].index.length)
	{
		var dindex = districts_array[feature.properties.vollcode].index[0].d * 10;
		if(dindex>1) { dindex=1;}
	}
	else
	{
		var dindex = 0;
	}


	return {
		fillColor: getColor(dindex),
		weight: 1,
		opacity: 0.6,
		color: '#fff',
		fillOpacity: 0.7
	};
}

function onEachFeatureDistrict(feature, layer) {

	districts_array[feature.properties.vollcode].layer = layer;
	districts_array[feature.properties.vollcode].buurt = feature.properties.naam;

	layer.on({
		mouseover: highlightFeature,
		mouseout: resetHighlight,
		click: zoomToFeature
	});
	layer.bindPopup('<div class="popup_district"><i class="material-icons">fiber_manual_record</i><h3>' + layer.feature.properties.naam + '</h3></div>', {autoClose: false});

	layer.on('mouseover', function (e) {
		this.openPopup();
	});
	layer.on('mouseout', function (e) {
		this.closePopup();
	});
}

function getHotspotsIndex() {

	$.each(hotspotsIndexJson.results, function (key, value) {

		var hotspotcode = this.index;

		var dataset = {};

		dataset.hotspot = this.hotspot;

		var day_array = [];

		this.druktecijfers.sort(function (a, b) {
			return a.d - b.d;
		});

		var days = [];
		$.each(this.druktecijfers, function (key, value) {
			if($.inArray(this.d, days)==-1)
			{
				days.push(this.d);
				day = this.d;
			}
			if(days.length==1)
			{
				if(this.h>=5 && this.d == day)
				{
					day_array.push(this);
				}
			}
			if(days.length==2)
			{
				if(this.h<=5 && this.d == day)
				{
					day_array.push(this);
				}
			}
		});

		day_array.sort(function (a, b) {
			return a.d - b.d || a.h - b.h;
		});


		dataset.druktecijfers = day_array;

		if(dataset.druktecijfers.length==25)
		{
			hotspots_array[hotspotcode] = dataset;
		}

	});

	if(debug) { console.log('getHotspotsIndex: Done') }

}

function calcAmsAverage()
{
	var hotspot_count = 0;
	$.each(hotspots_array, function (key, value) {

		// used for ams average todo: calc average in backend
		$.each(this.druktecijfers, function (key, value) {
			amsterdam.druktecijfers[this.h].i += this.i
			amsterdam.druktecijfers[this.h].d = this.d
		});

		hotspot_count++;
	});

	// used for ams average todo: calc average in backend
	$.each(amsterdam.druktecijfers, function (key, value) {
		amsterdam.druktecijfers[this.h].i = amsterdam.druktecijfers[this.h].i / hotspot_count;
	});

	amsterdam.druktecijfers.sort(function (a, b) {
		return a.d - b.d || a.h - b.h;
	});

	if(debug) {
		console.log('AMS average:');
		console.log(amsterdam.druktecijfers);
	}

}


function getHotspots()
{
	$.each(hotspotsJson.results.features, function (key, value) {

		hotspots_array[this.id].coordinates = this.geometry.coordinates;
	});

	circles_layer = L.layerGroup();
	$.each(hotspots_array, function (key, value) {

		var hh = getHourDigit();
		var dindex = this.druktecijfers[hh].i;

		circles[key] = L.circleMarker(this.coordinates.reverse(), {
			color      : getColor(dindex),
			fillColor  : getColor(dindex),
			fillOpacity: 1,
			radius     : (12),
			name       : this.hotspot
		});
		circles[key].addTo(map);
		$(circles[key]._path).attr('stroke-opacity', 0.6);
		$(circles[key]._path).attr('stroke', '#666666');
		$(circles[key]._path).attr('hotspot', key);
		$(circles[key]._path).addClass('hotspot_' + key);
		circles[key].bindPopup('<div class="popup_hotspot"><i class="material-icons">fiber_manual_record</i><h3>' + this.hotspot + '</h3></div>', {autoClose: false});
		circles[key].on("click", function (e) {
			var clickedCircle = e.target;

			var hotspot_id = $(clickedCircle._path).attr('hotspot');

			updateLineGraph(hotspot_id,'hotspot');

			updateGauge(hotspot_id,'hotspot');

			clearInterval(popup_interval);

			popup_interval = setInterval(function () {
				var current_fill = $('[hotspot=' + hotspot_id + ']').css('fill');
				$('.popup_hotspot .material-icons').css('color', current_fill);
			}, 100);

			// do something, like:
			$('.graphbar_title h2').text(clickedCircle.options.name);
		});
		circles[key].addTo(circles_layer);

		circles_d3[key] = d3.select('path.hotspot_' + key);

	});

	if(debug) { console.log('getHotspots: Done') }


	if(debug) {
		console.log('hotspots_array:');
		console.log(hotspots_array);
		console.log('circles_array:');
		console.log(circles_d3);
	}

}

function getHotspotsNeW()
{
	hotspots_layer = L.geoJSON(hotspotsJson.results, {style: styleHotspots, onEachFeature: onEachFeatureHotspots}).addTo(map);

	hotspots_layer.eachLayer(function (layer) {

		layer._path.id = 'feature-' + layer.feature.properties.index;
		hotspots_d3[layer.feature.properties.index] = d3.select('#feature-' + layer.feature.properties.index);
	});

	//hide map by default
	map.removeLayer(hotspots_layer);

	if(debug) { console.log('getHotspots: Done') }


	if(debug) {
		console.log('hotspots_array:');
		console.log(hotspots_array);
	}

}

function addHotspotsLayer()
{
	hotspots_layer.addTo(map);

	hotspots_layer.eachLayer(function (layer) {
		layer._path.id = 'feature-' + layer.feature.id;
		hotspots_d3[layer.feature.id] = d3.select('#feature-' + layer.feature.id);
	});
}

function styleHotspots(feature) {

	console.log(feature);
	if(hotspots_array[feature.id].index.length)
	{
		var dindex = hotspots_array[feature.id].index[0].d * 10;
		if(dindex>1) { dindex=1;}
	}
	else
	{
		var dindex = 0;
	}


	return {
		fillColor: getColor(dindex),
		weight: 1,
		opacity: 0.6,
		color: '#fff',
		fillOpacity: 0.7
	};
}

function onEachFeatureHotspots(feature, layer) {

	hotspots_array[feature.id].layer = layer;
	hotspots_array[feature.id].hotspot = feature.properties.hotspot;

	layer.on({
		mouseover: highlightFeature,
		mouseout: resetHighlight,
		click: zoomToFeature
	});
	layer.bindPopup('<div class="popup_district"><i class="material-icons">fiber_manual_record</i><h3>' + layer.feature.properties.hotspot + '</h3></div>', {autoClose: false});

	layer.on('mouseover', function (e) {
		this.openPopup();
	});
	layer.on('mouseout', function (e) {
		this.closePopup();
	});
}

function getHotspotsOld(hotspotsJson) {

	var hotspot_count = 0;
	$.each(hotspotsJson.results, function (key, value) {

		this.druktecijfers.sort(function (a, b) {
			return a.h - b.h;
		});

		var time24 = {h:24,d:this.druktecijfers[0].d};
		this.druktecijfers.push(time24);

		// used for ams average todo: calc average in backend
		$.each(this.druktecijfers, function (key, value) {

			// console.log(this.d);
			amsterdam.druktecijfers[this.h].d += this.d

			// console.log('cum: '+amsterdam.druktecijfers[this.h].d);
		});

		var dataset = this;
		if (this.druktecijfers.length < 1) {
			this.druktecijfers = '[{h:0,d:0},{h:1,d:0},{h:2,d:0},{h:3,d:0},{h:4,d:0},{h:5,d:0},{h:6,d:0},{h:7,d:0},{h:8,d:0},{h:9,d:0},{h:10,d:0},{h:11,d:0},{h:12,d:0},{h:13,d:0},{h:14,d:0},{h:15,d:0},{h:16,d:0},{h:17,d:0},{h:18,d:0},{h:19,d:0},{h:20,d:0},{h:21,d:0},{h:22,d:0},{h:23,d:0}];'
		}

		hotspot_count++;
		hotspot_array.push(dataset);

	});

	hotspot_array.sort(function (a, b) {
		return a.index - b.index;
	});

	// used for ams average todo: calc average in backend
	$.each(amsterdam.druktecijfers, function (key, value) {
		amsterdam.druktecijfers[this.h].d = amsterdam.druktecijfers[this.h].d / hotspot_count;
	});

	circles_layer = L.layerGroup();
	$.each(hotspot_array, function (key, value) {

		var hh = getHourDigit();
		var dindex = this.druktecijfers[hh].d;

		circles[key] = L.circleMarker(this.coordinates, {
			color      : getColorBucket(dindex),
			fillColor  : getColorBucket(dindex),
			fillOpacity: 1,
			radius     : (12),
			name       : this.hotspot
		});
		circles[key].addTo(map);
		$(circles[key]._path).attr('stroke-opacity', 0.6);
		$(circles[key]._path).attr('stroke', '#666666');
		$(circles[key]._path).attr('hotspot', this.index);
		$(circles[key]._path).addClass('hotspot_' + this.index);
		circles[key].bindPopup('<div class="popup_hotspot"><i class="material-icons">fiber_manual_record</i><h3>' + this.hotspot + '</h3></div>', {autoClose: false});
		circles[key].on("click", function (e) {
			var clickedCircle = e.target;

			var hotspot_id = $(clickedCircle._path).attr('hotspot');

			updateLineGraph(hotspot_id,'hotspot');

			clearInterval(popup_interval);

			popup_interval = setInterval(function () {
				var current_fill = $('[hotspot=' + hotspot_id + ']').css('fill');
				$('.popup_hotspot .material-icons').css('color', current_fill);
			}, 100);

			// do something, like:
			$('.graphbar_title h2').text(clickedCircle.options.name);
		});
		circles[key].addTo(circles_layer);


		circles_d3[key] = d3.select('path.hotspot_' + this.index);

	});

	if(debug) { console.log('getHotspots: Done') }

}


function getRealtime()
{

	$.getJSON('data/hotspot_realtime_mapping.json').done(function(realtimeMapping){
		$.each(realtimeMapping, function (key, place_id_array) {
			var place_id_count = place_id_array.length;
			var hotspot_cum = 0;
			$.each(place_id_array, function (key, place_id) {
				$.each(realtimeJson.results, function (key, value) {
					if(this.place_id == place_id)
					{
						// console.log(place_id + ' - ' + this.data['Real-time']);
						hotspot_cum += this.data['Real-time'];
					}
				});
			});
			realtime_array[key] = hotspot_cum / place_id_count;
		});
	});

	if(debug) { console.log('getRealtime: Done') }

	if(debug) {
		console.log('realtime arrray:')
		console.log(realtime_array)
	}
}

function initAutoComplete()
{
	$('#loc_i').keypress(function(e) {
		if(e.which == 13) {
			var term = $('#loc_i').val();

			term_array = term.split(' ');
			term_count = term_array.length;
			if(term_count>1 && !isNaN(term_array[term_count-1])) {
				var loc_obj = $.getJSON("https://api.data.amsterdam.nl/atlas/typeahead/bag/?q=" + term).done(function (data) {
					var label = data[0].content[0]._display;
					var value = data[0].content[0].uri;
					setLocationMarker(value, label);
				});
			}
			else {
				alert('Geef een huisnummer op voor de exacte locatie.');
			}

		}
	});

	// init auto complete
	$('#loc_i').autocomplete({
		source: function (request, response) {
			//console.log(request.term);
			$.getJSON("https://api.data.amsterdam.nl/atlas/typeahead/bag/?q=" + request.term).done( function (data) {
				//console.log(data[0].content);
				response($.map(data[0].content, function (value, key) {
					//console.log(value);
					return {
						label: value._display,
						value: value.uri
					};
				}));
			});
		},
		minLength: 3,
		delay: 100,
		select: function(event, ui) {

			event.preventDefault();

			// console.log(ui.item);
			setLocationMarker(ui.item.value,ui.item.label)

			$('#loc_i').val(ui.item.label);

		}
	});
}


function setLocationMarker(address,label)
{
	$.getJSON("https://api.data.amsterdam.nl/" + address).done( function (data) {

		if (marker) {
			map.removeLayer(marker);
		}

		// set marker
		if(data.geometrie.type == 'Point')
		{
			var point = [];
			point.x = data.geometrie.coordinates[0];
			point.y =  data.geometrie.coordinates[1];


			var latLang = getLatLang(point);
			//console.log(latLang);

			var blackIcon = L.icon({
				iconUrl: 'images/loc.svg',

				iconSize:     [60, 60],
				iconAnchor:   [30, 52],
				popupAnchor:  [0, -50]
			});

			marker = L.marker(latLang, {icon: blackIcon}).addTo(map);
			marker.bindPopup('<div class="popup_location"><i class="material-icons">fiber_manual_record</i><h3>' + label + '</h3></div>', {autoClose: false});

			map.setView(latLang);
		}
		else
		{
			alert('Geef een huisnummer op voor de exacte locatie.');
		}

		var active_layer = districts_array[data._buurtcombinatie.vollcode].layer;
		setLayerActive(active_layer);

		$('.detail h2').html(districts_array[data._buurtcombinatie.vollcode].buurt);
		$('.detail').show();
		$('.details_graph').show();

	});
}

function initEventMapping()
{

	$('.detail_top i').on('click',function () {
		closeDetails();
	});

	$( document).on('click', ".search a",function () {
		if($(this).parent().hasClass('open'))
		{
			closeSearch();
		}
		else
		{
			openSearch();
		}
	});

	$( document).on('click', ".feedback",function () {
		// alert('feedback');
		window.usabilla_live('trigger', 'techfeedback');
	});

	$( document).on('click', ".m_more a",function () {
		if($(this).parent().hasClass('open'))
		{
			closeMobileMenu();
		}
		else
		{
			openMobileMenu()
		}
	});

	$( document).on('click', ".dlogo,.infolink1,.topbar_left h2",function () {
		showInfo('	<h2>De DrukteRadar</h2><p>De Drukteradar is een interactieve kaart van Amsterdam die per locatie laat zien wat de verwachte drukte van vandaag is. De drukte score vergelijkt de drukte in een bepaald gebied  met de gemiddelde drukte.</p><p>Deze drukte-score is samengesteld uit verschillende databronnen die allemaal iets zeggen over drukte in de stad. Momenteel bevat de drukte-score data over wegverkeer, openbaar vervoer, OV fietsen, parkeren, en bezoeken aan openbare plekken. Waar mogelijk worden actuele databronnen gebruikt. In andere gevallen zijn historische gemiddelden beschikbaar.</p>')
	});

	$( document).on('click', ".beta,.infolink2, .topbar_left span",function () {
		showInfo('<h2 style="color:red;">Beta</h2><p>De Drukteradar is in de ‘beta fase’. Dit houdt in dat we aan het testen zijn en er continue verbeteringen gemaakt worden. Heb je feedback dan horen we graag van je. Hierbij worden geen persoonsgegevens verzameld.</p>')
	});

	$( document).on('click', ".searchclose",function () {
		$(this).parent().removeClass('open');
	});

	$( document).on('click', ".close",function () {
		$(this).parent().fadeOut();
	});
	4
	$( document).on('click', ".graphbar_title .reset_icon",function () {
		resetMap();
	});

	$(document).on('click', ".graphbar_title .info_icon", function () {
		showInfo('<h2>Verklaring legenda / grafiek</h2><p>De grafiek toont de verwachte drukte van vandaag. Rood wil zeggen dat het op een locatie drukker is dan normaal gesproken op dit tijdstip, groen betekent dat het rustiger is dan normaal.</p><p>De animatie op de kaart is gekoppeld aan de grafiek: als je een locatie of buurt op de kaart selecteert zal de grafiek de drukte van die locatie tonen. Je kunt de animatie pauzeren met de ‘play/pause’ knop. De witte stippellijn geeft het huidige tijdstip aan. Je kunt de grafiek ook weer terugzetten met de ververs-knop: deze toont dan de verwachte drukte voor de hele stad.</p>');
	});

	$( document).on('click', ".mapswitch a",function () {

		if($(this).hasClass('active'))
		{
			// reset map
			resetMap();
			// hide hotspots
			$('path[hotspot]').hide();
			// show district
			addDistrictLayer();
			// set latlong & zoom
			if(mobile)
			{
				map.setView([52.368, 4.897], 11);
			}
			else
			{
				map.setView([52.36, 4.95], 12);
			}

			active_layer = 'buurten';


			$('.mapswitch a span').html('Hotspots');

			$(this).removeClass('active');
			setTag('map_districts');
		}
		else
		{
			// reset map
			resetMap();
			// hide district
			map.removeLayer(districts_layer);
			// show hotspots
			$('path[hotspot]').show();
			// set latlong & zoom
			map.setView([52.368, 4.897], 13.5);

			active_layer = 'hotspots';

			$('.mapswitch a span').html('Buurten');

			$(this).addClass('active');

			setTag('main');
		}
	});

	$( document).on('click', ".fiets_b",function () {
		if($(this).hasClass('active'))
		{
			showActiveLayer();
			hideMarkers();
			hideInfo();
			$(this).removeClass('active');
			setTag('main');
		}
		else
		{
			hideActiveLayer();
			resetTheme();
			showInfo('De beschikbaarheid van de OV-fietsen op de verschillende locaties.', 0);
			showOvFiets();
			$(this).addClass('active');
			setTag('ovfiets');
		}
	});

	$( document).on('click', ".cam_b",function () {
		if($(this).hasClass('active'))
		{
			showActiveLayer();
			hideMarkers();
			hideInfo();
			$(this).removeClass('active');
			setTag('main');
		}
		else
		{
			hideActiveLayer();
			resetTheme();
			showInfo('Verschillende webcams in en rond de stad.', 0);
			showFeeds();
			$(this).addClass('active');
			setTag('cam');
		}
	});

	$( document).on('click', ".events_b",function () {
		if($(this).hasClass('active'))
		{
			showActiveLayer();
			hideMarkers();
			hideInfo();
			$(this).removeClass('active');
			setTag('main');
		}
		else
		{
			hideActiveLayer();
			resetTheme();
			showInfo('Geplande evenementen van vandaag en het aantal bezoekers aanmeldingen op Facebook.', 0);
			showEvents();
			$(this).addClass('active');
			setTag('events');
		}
	});

	$( document).on('click', ".option_museum",function () {
		if($(this).hasClass('active'))
		{
			hideMarkers();
			hideInfo();
			$(this).removeClass('active');
		}
		else
		{
			resetThemeDetail();
			showMuseum();
			$(this).addClass('active');
		}
	});

	$( document).on('click', ".option_parc",function () {
		if($(this).hasClass('active'))
		{
			hideMarkers();
			hideInfo();
			$(this).removeClass('active');
		}
		else
		{
			resetThemeDetail();
			addParcLayer();
			$(this).addClass('active');
		}
	});

	$( document).on('click', ".option_market",function () {
		if($(this).hasClass('active'))
		{
			hideMarkers();
			hideInfo();
			$(this).removeClass('active');
		}
		else
		{
			resetThemeDetail();
			addMarketLayer();
			$(this).addClass('active');
		}
	});

	$( document).on('click', ".traffic_b",function () {
		if($(this).hasClass('active'))
		{
			showActiveLayer();
			hideMarkers();
			hideInfo();
			$(this).removeClass('active');
			setTag('main');
		}
		else
		{
			hideActiveLayer();
			resetTheme();
			showInfo('Verkeersdrukte in en rondom de stad.', 0);
			addTrafficLayer();
			$(this).addClass('active');
			setTag('traffic');
		}
	});

	$( document).on('click', ".hotspots_b",function () {
		if($(this).hasClass('active'))
		{

			closeThemaDetails();
			hideInfo();
			$(this).removeClass('active');
		}
		else
		{
			resetTheme();
			openThemaDetails('hotspots_content');
			$(this).addClass('active');
		}
	});

	$( document).on('click', ".google_b",function () {
		if($(this).hasClass('active'))
		{

			hideMarkers();
			hideInfo();
			$(this).removeClass('active');
		}
		else
		{
			resetTheme();
			showGoogle();
			$(this).addClass('active');
		}
	});

	$( document).on('click', ".park_b",function () {
		if($(this).hasClass('active'))
		{
			showActiveLayer();
			hideMarkers();
			hideInfo();
			$(this).removeClass('active');
			setTag('main');
		}
		else
		{
			hideActiveLayer();
			resetTheme();
			showInfo('Het aantal beschikbare plekken in parkeergarages en park & ride locaties.', 0);
			addParkLayer();
			$(this).addClass('active');
			setTag('parking');
		}
	});

	$( document).on('click', ".water_b",function () {
		if($(this).hasClass('active'))
		{
			closeThemaDetails();
			hideMarkers();
			hideInfo();
			$(this).removeClass('active');
			setTag('main');
		}
		else
		{
			resetTheme();
			showWater();
			showInfo('De waterdrukte binnen de stad.', 0);
			$(this).addClass('active');
			setTag('water');
		}
	});

	$('.controls').on('click',function(){
		map.setView([52.36, 4.95], 12);
	});

	$( document).on('click', ".water_b",function () {
	});

}

// ######### widget functions ###############
function initWeerWidget()
{
	$.getJSON(weatherJsonUrl).done(function(weatherJson)
	{
		var weather_img_url = 'images/'+weatherJson.liveweer[0].image+'.svg';
		$('.weather img').attr('src',weather_img_url);
		$('.weather img').attr('title',weatherJson.liveweer[0].verw);
		$('.weather span').html(weatherJson.liveweer[0].temp + ' &#8451');
	});
}

// ######### google functions ###############
function setTag(tag) {
	var url_array = window.location.href.split('#');

	if (url_array.length > 1) {
		var group = url_array[1]
		// google
		ga('set', 'page', '/'+tag+'_'+group+'.html');
	}
	else
	{
		// google
		ga('set', 'page', '/'+tag+'.html');
	}

	// google
	ga('send', 'pageview');
}


// ######### map / animation functions ###############
function getColorChroma(dindex) {

	if(dindex<0.5)
	{
		var a = '#50E6DB'; //50E6DB 63c6e6
		var b = '#F5A623';
		dindex = dindex * 2;
	}
	else {
		var a = '#F5A623';
		var b = '#DB322A';
		dindex = (dindex-0.5) * 2;
	}


	var color = chroma.mix(a,b,dindex).hex();
	console.log(color);

	return color;
}


function getColor(dindex)
{
	if(dindex<0.5)
	{
		var a = '#50E6DB'; //50E6DB 63c6e6
		var b = '#F5A623';
		dindex = dindex * 2;
	}
	else {
		var a = '#F5A623';
		var b = '#DB322A';
		dindex = (dindex-0.5) * 2;
	}

	// var a = '#50E6DB'; //50E6DB 63c6e6
	// var b = '#DB322A';

	var ah = parseInt(a.replace(/#/g, ''), 16),
		ar = ah >> 16, ag = ah >> 8 & 0xff, ab = ah & 0xff,
		bh = parseInt(b.replace(/#/g, ''), 16),
		br = bh >> 16, bg = bh >> 8 & 0xff, bb = bh & 0xff,
		rr = ar + dindex * (br - ar),
		rg = ag + dindex * (bg - ag),
		rb = ab + dindex * (bb - ab);

	var color = '#' + ((1 << 24) + (rr << 16) + (rg << 8) + rb | 0).toString(16).slice(1);

	return color;
}

function getColorBucket(dindex)
{
	if(dindex<0.40)
	{
		return '#50E6DB'; //50E6DB 63c6e6

	}
	else if(dindex<0.70){
		return  '#F5A623';
	}
	else
	{
		return '#DB322A';
	}

}

function resetMap() {
	map.closePopup();
	$('.graphbar_title h2').text(amsterdam.hotspot);
	updateLineGraph('ams','ams');
	updateGauge('ams','ams');
}

function stopAnimation()
{
	clearInterval(interval);

	$.each(hotspots_array, function (key, value) {

		circles_d3[key]
			.transition()
			.duration(0);
	});
}

function startAnimation()
{
	var elapsed_time = $('.line-group').attr('time');

	if(elapsed_time<1)
	{
		// hotspots
		// $.each(hotspot_array, function (key, value) {
		// 	circles_d3[key]
		// 		.attr('stroke-opacity', 0.6)
		// 		.attr('stroke-width', 3)
		// 		// .transition()
		// 		// .duration(1000)
		// 		.attr('fill', getColorBucket(this.druktecijfers[0].d))
		// 		.attr('stroke', '#666666');
		// });

		// buurtcombinaties
		// $.each(districts_array, function (key, value) {
		//
		// 	var start_index = this['index'][0].d * 10;
		//
		// 	districts_d3[key].transition()
		// 		.duration(1000)
		// 		.attr('fill', getColor(start_index))
		//
		// });
	}

	var counter = 0;
	interval = setInterval(function() {
		elapsed_time = $('.line-group').attr('time');
		//console.log(elapsed_time+ '' + counter);
		if(elapsed_time > counter)
		{
			var hour = convertHour(Math.ceil(elapsed_time));

			// hotspots
			$.each(hotspots_array, function (key, value) {
				if(key==0)
				{
					// console.log(this.druktecijfers);
					// console.log(key + ' ' +hour + ' ' + this.druktecijfers[hour].i);
				}
				circles_d3[key]
					.attr('stroke-opacity', 0.6)
					.attr('stroke-width', 3)
					// .transition()
					// .duration(1000)
					.attr('fill', getColor(this.druktecijfers[hour].i))
					.attr('stroke', '#666666');
			});

			// hotspots
			// for (i in hotspots_array) {
			// 	buurt_obj = hotspots_array[i];
			// 	console.log(i);
			// 	console.log(buurt_obj);
			//
			// 	var dindex = 0;
			// 	if(buurt_obj.druktecijfers==25) {
			// 		dindex = buurt_obj.druktecijfers[hour].i;
			// 	}
			//
			// 	if(dindex>1){dindex=1;}
			//
			// 	hotspots_d3[i]
			// 		.transition()
			// 		.duration(1000)
			// 		.attr('fill', getColor(dindex));
			//
			// 	// $('#feature-'+ i).attr('fill', getColorBucket(dindex));
			// 	// $('#feature-'+ i).remove();
			//
			//
			// 	// console.log(hotspots_d3[i]);
			// };

			// districts
			for (i in districts_array) {
				buurt_obj = districts_array[i];


				var dindex = 0;
				if(buurt_obj.index.length==25) {
					dindex = buurt_obj.index[hour].i;
				}

				if(dindex>1){dindex=1;}

				districts_d3[i]
					.transition()
					.duration(1000)
					.attr('fill', getColor(dindex));

				// $('#feature-'+ i).attr('fill', getColorBucket(dindex));
				// $('#feature-'+ i).remove();


				 // console.log(districts_d3[i]);
			};

			// console.log(hour);

			counter++;
		}
		if(elapsed_time>23)
		{
			clearInterval(interval);
		}

	},500);
}

function dragAnimation() {
	elapsed_time = $('.line-group').attr('time');
	var hour = convertHour(Math.ceil(elapsed_time));

	$.each(hotspots_array, function (key, value) {
		circles_d3[key]
			.attr('stroke-opacity', 0.6)
			.attr('stroke-width', 3)
			.attr('fill', getColor(this.druktecijfers[hour].i))
			.attr('stroke', '#666666');
	});

	// buurtcombinaties
	for (i in districts_array) {
		buurt_obj = districts_array[i];

		var dindex = 0;
		if(buurt_obj.index.length) {
			dindex = buurt_obj.index[hour].i;
		}

		if(dindex>1){dindex=1;}

		districts_d3[i].attr('fill', getColor(dindex));

	};
}
function setToCurrentTime()
{

	var hour = getHourDigit();

	$.each(hotspots_array, function (key, value) {
		circles_d3[key]
			.attr('stroke-opacity', 0.6)
			.attr('stroke-width', 3)
			.attr('fill', getColor(this.druktecijfers[hour].i))
			.attr('stroke', '#666666');
	});

	// buurtcombinaties
	for (i in districts_array) {
		buurt_obj = districts_array[i];

		var dindex = 0;
		if(buurt_obj.index.length) {
			dindex = buurt_obj.index[hour].i;
		}

		if(dindex>1){dindex=1;}

		districts_d3[i].attr('fill', getColor(dindex));

	};

	areaGraph[0].setToTime();
}

function getLatLangArray(point) {
	return lnglat = proj4RD.inverse([point.x, point.y]);
}

function getLatLang(point) {
	var lnglat = proj4RD.inverse([point.x, point.y]);
	return L.latLng(lnglat[1]-0.0006, lnglat[0]-0.002);
}

function highlightFeature(e) {
	var layer = e.target;

	var dindex = districts_array[layer.feature.properties.vollcode].index;
	var buurt = districts_array[layer.feature.properties.vollcode].buurt;
}

function resetHighlight(e) {
	// geojson.resetStyle(e.target);
}

function zoomToFeature(e) {
	var layer = e.target;

	layer.closePopup();

	// set layer active
	setLayerActive(layer);
}

function setLayerActive(layer)
{
	if(lastClickedLayer){
		districts_layer.resetStyle(lastClickedLayer);
		$(lastClickedLayer.getElement()).removeClass("active_path");
	}

	vollcode = layer.feature.properties.vollcode;

	var buurt = districts_array[vollcode].buurt;
	var dindex = districts_array[vollcode].index;

	updateLineGraph(vollcode,'district');

	// set name
	$('.graphbar_title h2').html(buurt);

	$(layer.getElement()).addClass("active_path");

	layer.setStyle({
		weight: 2,
		color: '#cccccc',
		opacity: 0.8,
		fillOpacity: 0.6,
		className: 'path_active'
	});

	if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
		layer.bringToFront();
	}

	lastClickedLayer = layer;
}

// ######### graph functions ###############
function initLineGraph()
{
	var data = [];

	$.each(amsterdam.druktecijfers, function (key, value) {

		var dataset = {};
		dataset.y = Math.round(this.i * 100);
		dataset.x = parseInt(key);

		data.push(dataset);
	});

	// console.log(data);

	areaGraph = $('.graphbar_graph').areaGraph(data,ams_realtime);

	areaGraph[0].startCount();

}

function updateLineGraph(key,type)
{
	// get proper data from json array
	var data = [];

	//console.log(key);

	var realtime = 0;

	if(type=='ams')
	{
		var point_array = amsterdam.druktecijfers;
	}
	else if(type == 'hotspot')
	{
		var point_array = hotspots_array[key].druktecijfers;
		realtime = realtime_array[key];
	}
	else
	{
		var point_array =  districts_array[key].index;
	}

	// console.log(hotspots_array[key]);
	// console.log(point_array);

	$.each(point_array, function (key, value) {
		// console.log(key);
		// console.log(this);
		var dataset = {};
		dataset.y = Math.round(this.i * 100);
		dataset.x = parseInt(key);

		// console.log(dataset);

		data.push(dataset);
	});

	// console.log(data);



	areaGraph[0].update(data,realtime);
}

// ######### gauge functions ###############
function initGauge()
{
	var counter = 0;
	$.each(realtimeJson.results, function (key, value) {

		if(this.data['Real-time']>0)
		{
			// console.log('real: ' + this.data['Real-time']);
			// console.log('expected: ' + this.data['Expected']);
			ams_realtime = ams_realtime + this.data['Real-time'];
			ams_expected = ams_expected + this.data['Expected'];
			counter++;
		}
	});

	ams_realtime = ams_realtime  / counter;
	ams_expected = ams_expected  / counter;

	// todo check expected in real time feed.
	var hour = getHourDigit();
	ams_expected = amsterdam.druktecijfers[hour].i;

	// console.log('real: ' + ams_realtime);
	// console.log('expected: ' + ams_expected);

	gauge = $('.gauge').arcGauge({
		// value     :  Math.round(ams_realtime*100),
		value     : Math.round(ams_expected*100),
		value2     : Math.round(ams_expected*100),
		// colors    : getColor(ams_realtime),
		colors    : getColor(ams_expected),
		colors2    : getColor(ams_expected),
		transition: 500,
		thickness : 12,
		onchange  : function (value) {
			$('.gauge-text .value').text(value[0]);
			$('.gauge-text .value2').text(value[1]);
		}
	});
	$('.graphbar_right .time').text(getHours());
	$('.graphbar_right .value').text(Math.round(ams_expected*100)).css('color',getColor(ams_expected));
	// $('.graphbar_right .value').text(Math.round(ams_realtime*100)).css('color',getColor(ams_realtime));
	$('.graphbar_right .value2').text(Math.round(ams_expected*100)).css('color',getColor(ams_expected));


}

function updateGauge(key,type)
{
	var hour = convertHour(getHourDigit());

	if(type=='ams')
	{
		// gauge[0].set([Math.round(ams_realtime*100),Math.round(ams_expected*100)]);
		gauge[0].set([Math.round(ams_expected*100),0]);
		$('.graphbar_right .value').text(Math.round(ams_expected*100)).css('color',getColor(ams_expected));
	}
	else if(type == 'hotspot')
	{
		var point_array = hotspots_array[key].druktecijfers;
		var realtime = realtime_array[key];
		var expected =  point_array[hour].i;

		gauge[0].set([Math.round(expected*100),0]);
		$('.graphbar_right .gauge_top_text').text('Normale drukte');
		$('.graphbar_right .value').text(Math.round(expected*100)).css('color',getColor(expected));


		// if(realtime > 0 )
		// {
		// 	gauge[0].set([Math.round(realtime*100),Math.round(expected*100)]);
		// 	$('.graphbar_right .gauge_top_text').text('Live drukte');
		// 	$('.graphbar_right .value').text(Math.round(realtime*100)).css('color',getColor(realtime));
		// 	$('.graphbar_right .value2').text(Math.round(expected*100)).css('color',getColor(expected));
		// }
		// else
		// {
		// 	gauge[0].set([0,Math.round(expected*100)]);
		// 	$('.graphbar_right .gauge_top_text').text('Geen live data');
		// 	$('.graphbar_right .value').text('').css('color','#fff');
		// 	$('.graphbar_right .value2').text(Math.round(expected*100)).css('color',getColor(expected));
		// }

	}
	else
	{
		gauge[0].set([0,0]);
	}


}


// ######### date functions ###############
function setView()
{
	// if(mobile)
	// {
	// 	map.setView([52.368, 4.897], 11);
	// }
	// else
	// {
	// 	map.setView([52.36, 4.95], 12);
	// }
}

function hideActiveLayer()
{
	// stop time and set to time
	setToCurrentTime();

	//
	// switch(active_layer)
	// {
	// 	case 'hotspots':
	// 		$('path[hotspot]').hide();
	// 		break;
	// 	case 'buurten':
	// 		map.removeLayer(geojson);
	// 		break;
	// }
}
function showActiveLayer()
{
	areaGraph[0].stopResumeCount();

	// switch(active_layer)
	// {
	// 	case 'hotspots':
	// 		$('path[hotspot]').show();
	// 		break;
	// 	case 'buurten':
	// 		addDistrictLayer();
	// 		break;
	// }
}

// ######### date functions ###############
function getDate()
{
	var today = new Date();
	var dd = today.getDate();
	var mm = today.getMonth()+1; //January is 0!

	var yyyy = today.getFullYear();
	if(dd<10){
		dd='0'+dd;
	}
	if(mm<10){
		mm='0'+mm;
	}
	var today = dd+'/'+mm+'/'+yyyy;

	return today;
}

function getDay()
{
	var today = new Date();
	var dd = today.getDate();

	return dd;
}

function getHours()
{
	var today = new Date();
	var hh = today.getHours();

	if(hh<10)
	{
		hh = '0'+hh;
	}

	return hh + ':00';
}

function getHourDigit()
{
	var today = new Date();
	var hh = today.getHours();

	return hh;
}

function getTimeInt()
{
	var today = new Date();
	var hh = today.getHours();
	var mm =today.getMinutes();

	mm =  Math.round(mm / 60 * 100);

	return hh+'.'+mm;
}

function convertHour(hour)
{
	if(hour > 5 && hour < 24)
	{
		hour = hour -5;
	}
	else {
		hour = hour + 19;
	}

	return hour;
}

function getNowDate()
{
	// get date
	var date = getDate();
	//var date = $( ".date_i" ).datepicker({ dateFormat: 'yy-mm-dd' }).val();

	// get time
	var time = getHours();

	var now_date = date.replace('/','-').replace('/','-')+'-'+time.replace(':','-')+'-00';

	return now_date;
}

function getCurrentDateOnly()
{
	// get date
	var date = getDate();

	return date.replace('/','-').replace('/','-');
}

// ######### window / visualisation handling ###############
function showInfo(content,duration)
{
	$('.info_content').html(content);

	$('.info').show();

	closeMobileMenu();

	if(duration>0)
	{
		setTimeout(function(){$('.info').fadeOut()},duration);
	}
}

function hideInfo()
{
	$('.info').fadeOut();
}

function openMobileMenu()
{
	closeSearch();
	hideInfo();

	// hide mobile menu
	$('.m_menu').show();
	$('.m_more').addClass('open');
}

function closeMobileMenu()
{
	// hide mobile menu
	$('.m_menu').hide();
	$('.m_more').removeClass('open');
}

function openSearch()
{
	closeMobileMenu();
	hideInfo();

	$('.search').addClass('open');
}

function closeSearch()
{
	$('.search').removeClass('open');
}


function openThemaDetails(show)
{
	// open detail
	$('.themas').addClass('open');

	$('.'+show).fadeIn();
}

function closeThemaDetails()
{
	// close detail
	$('.themas').removeClass('open');

	// remove content
	$('.themas .themas_content div').hide();
}

function openDetails()
{
	$('.detail').addClass('open');
	$('.cta').addClass('open');
	$('.details_graph').show();
}

function closeDetails()
{
	$('.detail').removeClass('open');
	$('.cta').removeClass('open');
	$('.details_graph').hide();
}

function showLeftBox(content,header)
{
	$( ".leftbox .content" ).html('');
	$( ".leftbox h2" ).html('');

	$( ".leftbox" ).fadeIn( "slow" );

	$( ".leftbox h2" ).append(header);
	$( ".leftbox .content" ).append(content);
}

function hideLeftBox()
{
	$( ".leftbox" ).fadeOut( "slow" );

	$( ".leftbox .content" ).html('');
	$( ".leftbox h2" ).html('');
}

// ######### theme layer handling ###############

function resetTheme()
{
	// remove buttons acitve state
	$('.themas_buttons_top li').removeClass('active');

	// close the theme if its open
	closeThemaDetails();

	// remove all markers
	hideMarkers();

	// remove custom layers
	if(theme_layer)
	{
		removeThemeLayer();
	}
}

function resetThemeDetail()
{
	// remove buttons acitve state
	$('.hotspots_content li').removeClass('active');

	// remove all markers
	hideMarkers();

	// remove custom layers
	if(theme_layer)
	{
		removeThemeLayer();
	}
}

function hideMarkers()
{
	$.each(markers, function(key,value) {
		map.removeLayer(this);
	});
}

function removeThemeLayer()
{
	map.removeLayer(theme_layer);
}

// ######### theme layers ###############

function showFeeds()
{
	setView();

	var feeds = new Array();

	feeds[0] = {name:"Dam",url:"https://www.youtube.com/embed/6Pc-59pPXpY?rel=0&amp;controls=0&amp;showinfo=0&amp;autoplay=1", lat:"52.3732104", lon:"4.8914401"};
	feeds[1] = {name:"Knooppunt Watergraafsmeer",url:"https://vid.nl/EmbedStream/cam/61?w=100p", lat:"52.351620", lon:"4.962818"};
	feeds[2] = {name:"Knooppunt Amstel",url:"https://vid.nl/EmbedStream/cam/5?w=100p", lat:"52.329157", lon:"4.913159"};
	feeds[3] = {name:"A10 Afslag S107",url:"https://vid.nl/EmbedStream/cam/14?w=100p", lat:"52.340781", lon:"4.841226"};
	feeds[4] = {name:"Knooppunt Holendrecht",url:"https://vid.nl/EmbedStream/cam/36?w=100p", lat:"52.286287", lon:"4.948061"};
	feeds[5] = {name:"A4 Amsterdam-Sloten",url:"https://vid.nl/EmbedStream/cam/18?w=100p", lat:"52.338195", lon:"4.813557"};
	feeds[6] = {name:"Knooppunt Westpoort",url:"https://vid.nl/EmbedStream/cam/41?w=100p", lat:"52.396049", lon:"4.844490"};
	//feeds[x] = {name:"Oudezijds Voorburgwal",url:"https://www.youtube.com/embed/_uj8ELeiYKs?rel=0&amp;controls=0&amp;showinfo=0&amp;autoplay=1", lat:"52.3747178", lon:"4.8991389"};
	// feeds[1] = {name:"Centraal Station (zicht op het IJ)",url:"https://www.portofamsterdam.com/nl/havenbedrijf/webcam	", lat:"52.380149", lon:"4.900437"};

	var camIcon = L.icon({
		iconUrl: 'images/cam_marker.svg',

		iconSize:     [35, 50],
		iconAnchor:   [17.5, 50],
		popupAnchor:  [0, -50]
	});

	$.each(feeds, function(key,value) {
		var cam_marker = L.marker([this.lat,this.lon], {icon: camIcon,title:this.name,alt:this.url}).addTo(map).on('click', function(){showFeed(this.options.title,this.options.alt);});
		cam_marker.bindPopup("<h3>" + this.name + "</h3>", {autoClose: false});
		markers.push(cam_marker);
	});

	return feeds;
}

function showFeed(title, url)
{

	var content = '<iframe width="100%" height="100%" src="'+url+'" frameborder="0"></iframe>';

	showLeftBox(content,'Webcam '+title);
}

function addParkLayer()
{
	setView();

	if(debug) {
		console.log('Park api:');
		console.log(parkJsonUrl);
	}

	$.getJSON(parkJsonUrl).done(function(parkJson){
		if(debug) {
			console.log('Park json:');
			console.log(parkJson);
		}
		theme_layer = L.geoJSON(parkJson,{style: stylePark, onEachFeature: onEachFeaturePark, pointToLayer: pointToLayerPark}).addTo(map);
	});

}

function pointToLayerPark(feature, latlng) {

	var prefix = 'park';
	if(feature.properties.Name.includes("P+R"))
	{
		var prefix = 'parkride';
	}



	var suffix = 'none';

	if(feature.properties.FreeSpaceShort<10 && feature.properties.FreeSpaceShort>0)
	{
		suffix = 'some';
	}
	else if(feature.properties.FreeSpaceShort>10)
	{
		suffix = 'plenty';
	}

	var parkIcon = L.icon({
		iconUrl: 'images/'+prefix+'_marker_'+suffix+'.svg',

		iconSize:     [35, 50],
		iconAnchor:   [17.5, 50],
		popupAnchor:  [0, -50]
	});

	var marker = L.marker(latlng, {icon: parkIcon});
	var long ='';
	var short ='';

	if(feature.properties.ShortCapacity>0)
	{
		short = "<p>Parkeren kort: " + feature.properties.FreeSpaceShort + " / " + feature.properties.ShortCapacity + '</p>';
	}
	if(feature.properties.LongCapacity>0)
	{
		long = "<p>Parkeren lang: " + feature.properties.FreeSpaceLong + " / " + feature.properties.LongCapacity + '</p>';
	}
	marker.bindPopup('<div class="popup_'+ suffix +'"><i class="material-icons">fiber_manual_record</i><h3>' + feature.properties.Name + '</h3><div class="pop_inner_content"><h4>Plekken beschikbaar: ' + feature.properties.FreeSpaceShort +'</h4><span class="ammount">' +  feature.properties.FreeSpaceShort + '</span></div></div>', {autoClose: false});

	markers.push(marker);

	return marker;
}

function stylePark(feature) {

	return {
		fillColor: '#fff',
		weight: 1,
		opacity: 0.6,
		color: '#fff',
		fillOpacity: 0.7
	};
}

function onEachFeaturePark(feature, layer) {

}

function showOvFiets()
{
	setView();

	if(debug) { console.log(fietsJsonUrl) }
	$.getJSON(fietsJsonUrl).done(function(fietsJson){
		if(debug) { console.log(fietsJson) }

		var ams_locaties = ['ASB','RAI','ASA','ASDM','ASDZ','ASD','ASDL','ASS'];

		$.each(fietsJson.locaties, function(key,value) {
			if(ams_locaties.indexOf(this.stationCode)>=0)
			{
				//console.log(this.stationCode);
				if(this.lat>0 && this.lng>0)
				{
					var suffix = 'none';
					if(this.extra.rentalBikes>0)
					{
						suffix = 'some';
					}
					if(this.extra.rentalBikes>10)
					{
						suffix = 'plenty';
					}

					var fietsIcon = L.icon({
						iconUrl: 'images/fiets_marker_'+suffix+'.svg',

						iconSize:     [50, 58],
						iconAnchor:   [25, 58],
						popupAnchor:  [0, -50]
					});

					var marker_info = {};
					marker_info.name = this.name;
					marker_info.free = this.extra.rentalBikes;
					var fiets_marker = L.marker([this.lat,this.lng], {icon: fietsIcon,title:this.description,alt:this.url}).addTo(map);
					fiets_marker.bindPopup('<div class="popup_'+ suffix +'"><i class="material-icons">fiber_manual_record</i><h3>' + this.name + '</h3><div class="pop_inner_content"><h4>Fietsen beschikbaar : '+ this.extra.rentalBikes + '</h4><span class="ammount">' + this.extra.rentalBikes + '</span></div></div>', {autoClose: false});
					markers.push(fiets_marker);

				}
			}
		});

	});
}

function showEvents()
{
	setView();

	if(debug) { console.log(eventsJsonUrl) }
	$.getJSON(eventsJsonUrl).done(function(eventsJson){
		if(debug) { console.log(eventsJson) }

		$.each(eventsJson, function(key,value) {

			if(this.attending<100)
			{
				suffix = 'plenty';
			}
			else if(this.attending<500)
			{
				suffix = 'some';
			}
			else if(this.attending>500)
			{
				var suffix = 'none';
			}

			var eventIcon = L.icon({
				iconUrl: 'images/events_marker_'+suffix+'.svg',

				iconSize:     [35, 50],
				iconAnchor:   [17.5, 50],
				popupAnchor:  [0, -50]
			});



			// console.log(this);
			markers[key] = L.marker([this.lat,this.long], {
				icon: eventIcon,
				name: this.location
			});
			markers[key].addTo(map);
			markers[key].bindPopup('<div class="popup_'+ suffix +'"><i class="material-icons">fiber_manual_record</i><h3>' + this.location +'</h3><img src="'+this.img+'"><div class="pop_inner_content"><p>'+ this.date+'</p><h4>'+this.title+'</h4><br><p>Aanmeldingen: '+this.attending+'</p><span class="ammount">' +  this.attending + '</span></div></div>', {autoClose: false});
			markers[key].on("click", function(e){
				var clickedCircle = e.target;

			});


		});

	});
}

function showMuseum()
{
	var eventsJsonUrl = 'data/MuseaGalleries.json';
	if(debug) { console.log(eventsJsonUrl) }
	$.getJSON(eventsJsonUrl).done(function(eventsJson){
		if(debug) { console.log(eventsJson) }

		var camIcon = L.icon({
			iconUrl: 'images/musea_marker.svg',

			iconSize:     [35, 40],
			iconAnchor:   [17.5, 40],
			popupAnchor:  [0, -50]
		});

		$.each(eventsJson, function(key,value) {
			var latitude = this.location.latitude.replace(',','.');
			var longitude = this.location.longitude.replace(',','.');
			var event_marker = L.marker([latitude,longitude], {icon: camIcon,title:this.details.nl.title}).addTo(map);
			event_marker.bindPopup("<h3>" + this.title + "</h3><br>" + this.details.nl.shortdescription + '<br><a target="blank" href="' +  this.urls[0] + '">Website >></a>' , {autoClose: false});
			markers.push(event_marker);
		});

	});
}

function addParcLayer()
{
	//var parkJsonUrl = "http://opd.it-t.nl/data/amsterdam/ParkingLocation.json";
	var parcJsonUrl = 'data/AGROEN_7_STADSPARK.json';

	if(debug) { console.log(parcJsonUrl) }
	$.getJSON(parcJsonUrl).done(function(parcJson){
		if(debug) { console.log(parcJson) }
		theme_layer = L.geoJSON(parcJson,{style: styleParc, onEachFeature: onEachFeatureParc, pointToLayer: pointToLayerParc}).addTo(map);
	});

}

function pointToLayerParc(feature, latlng) {
	var parkIcon = L.icon({
		iconUrl: 'images/parc_marker.svg',

		iconSize:     [35, 40],
		iconAnchor:   [17.5, 40],
		popupAnchor:  [0, -50]
	});
	var marker = L.marker(latlng, {icon: parkIcon});
	marker.bindPopup("<h3>" + feature.properties.Naam + "</h3>", {autoClose: false});
	return marker;
}

function styleParc(feature) {

	return {
		fillColor: '#fff',
		weight: 1,
		opacity: 0.6,
		color: '#fff',
		fillOpacity: 0.7
	};
}

function onEachFeatureParc(feature, layer) {

}

function addMarketLayer()
{
	var marketJsonUrl = 'data/MARKTEN.json';

	if(debug) { console.log(marketJsonUrl) }
	$.getJSON(marketJsonUrl).done(function(marketJson){
		if(debug) { console.log(marketJson) }
		theme_layer = L.geoJSON(marketJson,{style: styleMarket, onEachFeature: onEachFeatureMarket, pointToLayer: pointToLayerMarket}).addTo(map);
	});

}

function pointToLayerMarket(feature, latlng) {
	var marketIcon = L.icon({
		iconUrl: 'images/market_marker.svg',

		iconSize:     [35, 40],
		iconAnchor:   [17.5, 40],
		popupAnchor:  [0, -50]
	});
	var marker =  L.marker(latlng, {icon: marketIcon});
	var website = '';
	if(feature.properties.Website)
	{
		website = "<br>" + feature.properties.Website;
	}
	marker.bindPopup("<h3>" + feature.properties.Locatie + "</h3>" + feature.properties.Artikelen + '<br /><br /><a target="blank" href="' + website + '">Website >></a>', {autoClose: false});
	return marker;
}

function styleMarket(feature) {

	return {
		fillColor: '#fff',
		weight: 1,
		opacity: 0.6,
		color: '#fff',
		fillOpacity: 0.7
	};
}

function onEachFeatureMarket(feature, layer) {

}

function addTrafficLayer()
{
	if(debug) {
		console.log('Traffic api url:');
		console.log(trafficJsonUrl);
	}
	$.getJSON(trafficJsonUrl).done(function(trafficJson){
		if(debug) {
			console.log('Traffic Json');
			console.log(trafficJson);
		}

		$.each(trafficJson.features, function(key,value) {

			var coordinates = [];
			$.each(this.geometry.coordinates, function(key,value) {
				coordinates.push([this[1],this[0]]);
			});
			var traffic_line = L.polyline(coordinates, {color: speedToColor(this.properties.Type, this.properties.Velocity)}).addTo(map);
			traffic_line.bringToBack();
			markers.push(traffic_line);
		});

	});

}

function speedToColor(type, speed){
	if(type == "H"){
		//Snelweg
		var speedColors = {0: getColor(1), 1: getColor(0.9), 30: getColor(0.75), 50: getColor(0.6), 70: getColor(0.4), 90: getColor(0.2),120: getColor(0)};
	} else {
		//Overige wegen
		var speedColors = {0: getColor(1), 1: getColor(0.9), 10: getColor(0.75), 20: getColor(0.6), 30: getColor(0.4), 40: getColor(0.2), 70: getColor(0)};
	}
	var currentColor = "#D0D0D0";
	for(var i in speedColors){
		if(speed >= i) currentColor = speedColors[i];
	}
	return currentColor;
}

function speedToColorOrg(type, speed){
	if(type == "H"){
		//Snelweg
		var speedColors = {0: "#D0D0D0", 1: "#BE0000", 30: "#FF0000", 50: "#FF9E00", 70: "#FFFF00", 90: "#AAFF00",120: "#00B22D"};
	} else {
		//Overige wegen
		var speedColors = {0: "#D0D0D0", 1: "#BE0000", 10: "#FF0000", 20: "#FF9E00", 30: "#FFFF00", 40: "#AAFF00", 70: "#00B22D"};
	}
	var currentColor = "#D0D0D0";
	for(var i in speedColors){
		if(speed >= i) currentColor = speedColors[i];
	}
	return currentColor;
}

function showGoogle()
{
	// var googleJsonUrl = 'http://apis.quantillion.io:3001/gemeenteamsterdam/locations/realtime/current';
	var googleJsonUrl =  realtimeUrl;

	if(debug) { console.log(googleJsonUrl) }
	$.getJSON(googleJsonUrl).done(function(googleJson){
		if(debug) { console.log(googleJson) }

		$.each(googleJson.results, function(key,value) {


			var ratio =  this.data['Real-time'] / this.data['Expected'] * 100;

			var marker_icon = 'images/google_marker_2.svg';

			if(ratio<70)
			{
				marker_icon = 'images/google_marker_0.svg'
			}
			if(ratio<90)
			{
				marker_icon = 'images/google_marker_1.svg'
			}
			if(ratio>110)
			{
				marker_icon = 'images/google_marker_4.svg'
			}
			if(ratio>130)
			{
				marker_icon = 'images/google_marker_5.svg'
			}

			var googleIcon = L.icon({
				iconUrl: marker_icon,

				iconSize:     [35, 40],
				iconAnchor:   [17.5, 40],
				popupAnchor:  [0, -50]
			});

			var header = this.name;
			var content = '<p>Expected' + this.data['Expected'] +  '</p>'  + '<p>Realtime' + this.data['Real-time'] +  '</p>'  + '<p>' + this.data.formatted_address +  '</p>' + '<br /><a target="blank" href="' + this.data.url +  '">Website</a>';

			var latitude = this.data.location.coordinates[0];
			var longitude =  this.data.location.coordinates[1];
			var event_marker = L.marker([latitude,longitude], {icon: googleIcon,title: this.data.name, alt: this.data['Real-time']}).addTo(map).on('click', function(){
				closeDetails();

				$('.detail h2').html(this.options.title);

			});

			event_marker.bindPopup("<h3>" + this.name + "</h3>" + content, {autoClose: false});
			markers.push(event_marker);
		});

	});
}

function showWater()
{
	var waterIcon = L.icon({
		iconUrl: 'images/water_marker.svg',

		iconSize:     [35, 50],
		iconAnchor:   [17.5, 50],
		popupAnchor:  [0, -50]
	});

	var title = 'Watermeetpunt Prinsengracht';
	var latitude = '52.375389';
	var longitude = '4.883740';
	var event_marker = L.marker([latitude,longitude], {icon: waterIcon,title:title}).addTo(map);
	event_marker.bindPopup("<h3>"+title+"</h3>", {autoClose: false});
	markers.push(event_marker);

	openThemaDetails('water_content');

}





























