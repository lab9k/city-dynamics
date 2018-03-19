// map & layers
var map;
var theme_layer;
var circles = [];
var circles_d3 = [];
var circles_layer;
var markers = [];
var geojson;
var traffic_layer;
var districts_d3 = [];

// global arrays
var buurtcode_prop_array = [];
var hotspot_array = [];
var realtime_array = [];

// states
var debug = true;
var vollcode;
var mobile = false;
var active_layer = 'hotspots';

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
var origin = 'http://127.0.0.1:8117';
var origin = 'https://acc.citydynamics.amsterdam.nl/api';

// When using the production server, get the API from there.
// TODO: Update this when the website name becomes "drukteradar.nl" or something alike.
if(window.location.href.indexOf('prod.citydynamics.amsterdam') > -1)
{
	var origin = 'https://prod.citydynamics.amsterdam.nl/api';
}

// However, when using the acceptation server, get the API from there.
if(window.location.href.indexOf('acc.citydynamics.amsterdam.nl') > -1)
{
	var origin = 'https://acc.citydynamics.amsterdam.nl/api';
}

var base_api = origin + '/';
var dindex_api = base_api + 'drukteindex/?format=json&op=';
var dindex_hotspots_api = base_api + 'hotspots/?format=json';
var realtimeUrl = base_api + 'realtime/?format=json';
var geoJsonUrl = base_api + 'buurtcombinatie/?format=json';
var dindex_uurtcombinaties_api = base_api + 'buurtcombinaties_drukteindex/?format=json';

// temp local api
dindex_hotspots_api = 'data/hotspots_drukteindex.json';
// dindex_hotspots_api = 'data/hotspots_fallback.json';
geoJsonUrl = 'data/buurtcombinaties.json';
dindex_uurtcombinaties_api = 'data/buurtcombinaties_drukteindex.json';

// specific
var def = '+proj=sterea +lat_0=52.15616055555555 +lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel +towgs84=565.4171,50.3319,465.5524,1.9342,-1.6677,9.1019,4.0725 +units=m +no_defs ';
var proj4RD = proj4('WGS84', def);
var amsterdam = {
	coordinates: [52.368, 4.897],
	druktecijfers: [{h:0,d:0},{h:1,d:0},{h:2,d:0},{h:3,d:0},{h:4,d:0},{h:5,d:0},{h:6,d:0},{h:7,d:0},{h:8,d:0},{h:9,d:0},{h:10,d:0},{h:11,d:0},{h:12,d:0},{h:13,d:0},{h:14,d:0},{h:15,d:0},{h:16,d:0},{h:17,d:0},{h:18,d:0},{h:19,d:0},{h:20,d:0},{h:21,d:0},{h:22,d:0},{h:23,d:0}],
	hotspot: "Amsterdam",
	index: -1
}

// ######### onload init sequence ###############
$(document).ready(function(){

	// check device resolution
	mobile = ($( document ).width()<=360);

	initMap();

	var sequence_array = [];

	sequence_array.push(getDistrictIndex());
	sequence_array.push(getHotspots());
	sequence_array.push(getRealtime());

	// first promise chain
	$.when(sequence_array).done(
		function(){
			// second promise chain
			$.when(getDistricts()).done(
				function() {
					initLineGraph();

					initAutoComplete();

					initEventMapping();
				}
			)

		}
	).fail(function(){console.error('One or more connections failed.')});



	// chrome control button style
	if (navigator.appVersion.indexOf("Chrome/") != -1) {
		$('.controls').addClass('chrome');
	}

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

	L.tileLayer(geomap3, {
		minZoom: 10,
		maxZoom: 18
	}).addTo(map);

	L.control.zoom({
		position:'topright'
	}).addTo(map);
}

function getDistrictIndex() {

	var dindexJsonUrl = dindex_uurtcombinaties_api;
	if(debug) {
		console.log('Start: getDistrictIndex');
		console.log(dindexJsonUrl);
	}

	var promise = $.getJSON(dindexJsonUrl).done(function (dindexJson) {
		if(debug) { console.log(dindexJson) }

		$.each(dindexJson.results, function (key, value) {

			var buurtcode = this.vollcode;

			var dataset = {};

			dataset.index = this.druktecijfers_bc;

			buurtcode_prop_array[buurtcode] = dataset;
		});

		if(debug) { console.log('getDistrictIndex: OK') }

	});

	return promise;
}

function getDistricts()
{
	var promise = $.getJSON(geoJsonUrl).done(function (geoJson) {
		if(debug) {
			console.log('Start: getDistricts');
			console.log(geoJsonUrl);
		}
		geojson = L.geoJSON(geoJson.results, {style: style, onEachFeature: onEachFeature}).addTo(map);

		geojson.eachLayer(function (layer) {
			layer._path.id = 'feature-' + layer.feature.properties.vollcode;
			districts_d3[layer.feature.properties.vollcode] = d3.select('#feature-' + layer.feature.properties.vollcode);
		});

		// hide map by default
		map.removeLayer(geojson);

		if(debug) { console.log('getDistricts: OK') }
	});

	return promise;
}

function addDistrictLayer()
{
	geojson.addTo(map);

	geojson.eachLayer(function (layer) {
		layer._path.id = 'feature-' + layer.feature.properties.vollcode;
		districts_d3[layer.feature.properties.vollcode] = d3.select('#feature-' + layer.feature.properties.vollcode);
	});
}

function style(feature) {

	if(buurtcode_prop_array[feature.properties.vollcode].index.length)
	{
		var dindex = buurtcode_prop_array[feature.properties.vollcode].index[0].d * 10;
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

function onEachFeature(feature, layer) {

	buurtcode_prop_array[feature.properties.vollcode].layer = layer;
	buurtcode_prop_array[feature.properties.vollcode].buurt = feature.properties.naam;

	layer.on({
		mouseover: highlightFeature,
		mouseout: resetHighlight,
		click: zoomToFeature
	});

	layer.bindPopup('<div><h3>' + layer.feature.properties.naam + '</h3></div>');
	layer.on('mouseover', function (e) {
		this.openPopup();
	});
	layer.on('mouseout', function (e) {
		this.closePopup();
	});
}

function getHotspots() {
	// hotspots map init
	var hotspotsJsonUrl = dindex_hotspots_api + '&timestamp=' + getNowDate();
	var hotspotsJsonUrl = dindex_hotspots_api;
	if (debug) {
		console.log('Start: getHotspots');
		console.log(hotspotsJsonUrl);
	}

	var promise = $.getJSON(hotspotsJsonUrl).done(function (hotspotsJson) {
		if (debug) {
			console.log(hotspotsJson)
		}

		var hotspot_count = 0;
		$.each(hotspotsJson.results, function (key, value) {

			this.druktecijfers.sort(function (a, b) {
				return a.h - b.h;
			});

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
			$(circles[key]._path).attr('stroke', '#4a4a4a');
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

		if(debug) { console.log('getHotspots: OK') }
	});

	return promise;
}


function getRealtime()
{
	// realtime check
	if(debug) { console.log('Start: getRealtime'); console.log(realtimeUrl); }
	var promise = $.getJSON(realtimeUrl).done(function (realtimeJson) {

		var hotspots_match_array = [];
		hotspots_match_array[18] = 'ARTIS';
		hotspots_match_array[34] = 'Museumplein';
		hotspots_match_array[0] = 'Amsterdam Centraal';
		hotspots_match_array[3] = 'Madame Tussauds Amsterdam'; //dam
		hotspots_match_array[33] = 'Dappermarkt';
		hotspots_match_array[15] = 'Tolhuistuin'; // overhoeksplein
		hotspots_match_array[5] = 'Mata Hari'; // Oudezijds Achterburgwal
		hotspots_match_array[13] = 'de Bijenkorf'; // Nieuwerzijdse voorburgwal

		if(debug) { console.log(hotspots_match_array) }

		$.each(realtimeJson.results, function (key, value) {

			var name = this.name;
			var exists = $.inArray(name, hotspots_match_array );
			if(exists > -1)
			{
				// console.log(name + ' - ' + this.data.place_id + ' - ' + this.data['Real-time']);
				realtime_array[exists] = this.data['Real-time'];
			}

		});

		if(debug) { console.log(realtime_array) }

		if(debug) { console.log('getRealtime: OK') }

	});

	return promise;
}

function initAutoComplete()
{
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

			$('#loc_i').val(ui.item.label);

			$.getJSON("https://api.data.amsterdam.nl/" + ui.item.value).done( function (data) {

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
					map.setView(latLang);
				}
				else
				{
					//alert('Vul een adres in plus huisnummer voor het bepalen van de locatie.'); #todo better selection add default nr..
				}

				var active_layer = buurtcode_prop_array[data._buurtcombinatie.vollcode].layer;
				setLayerActive(active_layer);

				$('.detail h2').html(buurtcode_prop_array[data._buurtcombinatie.vollcode].buurt);
				$('.detail').show();
				$('.details_graph').show();

			});

		}
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

	$( document).on('click', ".dlogo",function () {
		showInfo('	<h2>De Amsterdam DrukteRadar</h2> <p>De Amsterdam Drukte Radar toont drukte in de openbare ruimte van Amsterdam over tijd met een drukte-score. De drukte-score geeft de relatieve drukte in een bepaald gebied weer ten opzichte van historische ‘normaalwaarden’ van dit gebied.</p> <p>De drukte-score is een gewogen waarde samengesteld uit verschillende databronnen en met de Verblijvers Dichtheid Index als basis. Momenteel bevat de drukte-score data van wegverkeer, openbaar vervoer, parkeren, en bezoeken aan openbare plekken.  Sommigen van deze bronnen geven de data ‘realtime’ weer, terwijl anderen gemiddelden over een bepaalde periode weergeven.</p>')
	});

	$( document).on('click', ".beta",function () {
		showInfo('<h2 style="color:red;">Beta</h2><p>De Drukte Radar is in de beta fase, wat inhoudt dat er continue verbeteringen aan gemaakt worden en dat we feedback aan het verzamelen zijn. <br><a href="mailto:@">Heb je feedback dan horen we graag van je.</a></p>')
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

	$( document).on('click', ".graphbar_title .info_icon",function () {
		showInfo('<h2>Verklaring legenda / grafiek</h2><p>De lijn van de grafiek toont de verwachte drukte in een gebied ten op zichte van de normale drukte op dat tijdstip. De balk op het actuele tijdstip toont de actuele drukte voor het gebied.</p>');
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
		}
		else
		{
			// reset map
			resetMap();
			// hide district
			map.removeLayer(geojson);
			// show hotspots
			$('path[hotspot]').show();
			// set latlong & zoom
			map.setView([52.368, 4.897], 13.5);

			active_layer = 'hotspots';

			$('.mapswitch a span').html('Buurten');

			$(this).addClass('active');
		}
	});

	$( document).on('click', ".fiets_b",function () {
		if($(this).hasClass('active'))
		{
			showActiveLayer();
			hideMarkers();
			hideInfo();
			$(this).removeClass('active');
		}
		else
		{
			hideActiveLayer();
			resetTheme();
			showInfo('De beschikbaarheid van de OV fietsen over de verschillende locaties.', 0);
			showOvFiets();
			$(this).addClass('active');
		}
	});

	$( document).on('click', ".cam_b",function () {
		if($(this).hasClass('active'))
		{
			showActiveLayer();
			hideMarkers();
			hideInfo();
			$(this).removeClass('active');
		}
		else
		{
			hideActiveLayer();
			resetTheme();
			showInfo('Verschillende webcams in en rond de stad.', 0);
			showFeeds();
			$(this).addClass('active');
		}
	});

	$( document).on('click', ".events_b",function () {
		if($(this).hasClass('active'))
		{
			showActiveLayer();
			hideMarkers();
			hideInfo();
			$(this).removeClass('active');
		}
		else
		{
			hideActiveLayer();
			resetTheme();
			showInfo('Geplande evenementen van vandaag.', 0);
			showEvents();
			$(this).addClass('active');
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
		}
		else
		{
			hideActiveLayer();
			resetTheme();
			showInfo('Verkeersdrukte in en rond de stad.', 0);
			addTrafficLayer();
			$(this).addClass('active');
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
		}
		else
		{
			hideActiveLayer();
			resetTheme();
			showInfo('De capaciteit en het aantal beschikbare plekken in de parkeergarages.', 0);
			addParkLayer();
			$(this).addClass('active');
		}
	});

	$( document).on('click', ".water_b",function () {
		if($(this).hasClass('active'))
		{
			closeThemaDetails();
			hideMarkers();
			hideInfo();
			$(this).removeClass('active');
		}
		else
		{
			resetTheme();
			showWater();
			showInfo('De waterdrukte binnen de stad.', 0);
			$(this).addClass('active');
		}
	});

	$('.controls').on('click',function(){
		map.setView([52.36, 4.95], 12);
	});
}


// ######### map / animation functions ###############
function getColor(dindex)
{
	if(dindex<0.5)
	{
		var a = '#50E6DB'; //50E6DB 63c6e6
		var b = '#F5A623';
	}
	else {
		var a = '#F5A623';
		var b = '#DB322A';
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

	return '#' + ((1 << 24) + (rr << 16) + (rg << 8) + rb | 0).toString(16).slice(1);
}

function getColorBucket(dindex)
{
	if(dindex<0.40)
	{
		return '#50E6DB'; //50E6DB 63c6e6

	}
	else if(dindex<0.60){
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
}

function stopAnimation()
{
	clearInterval(interval);

	$.each(hotspot_array, function (key, value) {

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
		// 		.attr('stroke', '#4a4a4a');
		// });

		// buurtcombinaties
		// $.each(buurtcode_prop_array, function (key, value) {
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
		if(elapsed_time > counter)
		{
			var hour = Math.ceil(elapsed_time);

			// hotspots
			$.each(hotspot_array, function (key, value) {

				// if(key==10)
				// {
				// 	console.log(key + ' - ' + hour + ' - ' + this.druktecijfers[hour].d );
				// }

				circles_d3[key]
					.attr('stroke-opacity', 0.6)
					.attr('stroke-width', 3)
					// .transition()
					// .duration(1000)
					.attr('fill', getColorBucket(this.druktecijfers[hour].d))
					.attr('stroke', '#4a4a4a');
			});

			// buurtcombinaties
			for (i in buurtcode_prop_array) {
				buurt_obj = buurtcode_prop_array[i];

				var dindex = 0;
				if(buurt_obj.index.length) {
					dindex = buurt_obj.index[hour].d;
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

			console.log(hour);

			counter++;
		}
		if(elapsed_time>23)
		{
			clearInterval(interval);
		}

	},500);
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

	var dindex = buurtcode_prop_array[layer.feature.properties.vollcode].index;
	var buurt = buurtcode_prop_array[layer.feature.properties.vollcode].buurt;
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
		geojson.resetStyle(lastClickedLayer);
		$(lastClickedLayer.getElement()).removeClass("active_path");
	}

	vollcode = layer.feature.properties.vollcode;

	var buurt = buurtcode_prop_array[vollcode].buurt;
	var dindex = buurtcode_prop_array[vollcode].index;

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
		dataset.y = Math.round(this.d * 100);
		dataset.x = parseInt(this.h);

		data.push(dataset);
	});

	areaGraph = $('.graphbar_graph').areaGraph(data);

	setTimeout(areaGraph[0].startCount(),3000); //todo: replace timeout for proper load flow

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
		var point_array = hotspot_array[key].druktecijfers;
		realtime = realtime_array[key];
	}
	else
	{
		var point_array =  buurtcode_prop_array[key].index;
	}


	$.each(point_array, function (key, value) {

		var dataset = {};
		dataset.y = Math.round(this.d * 100);
		dataset.x = parseInt(this.h);

		data.push(dataset);
	});

	// console.log(data);



	areaGraph[0].update(data,realtime);
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
	areaGraph[0].stop();
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
	$('.themas_buttons li').removeClass('active');

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

		iconSize:     [35, 58],
		iconAnchor:   [17.5, 58],
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
	// var parkJsonUrl = "http://opd.it-t.nl/data/amsterdam/ParkingLocation.json";
	var parkJsonUrl = 'data/parkjson.json';

	$.getJSON(parkJsonUrl).done(function(parkJson){
		//console.log(parkJson);
		theme_layer = L.geoJSON(parkJson,{style: stylePark, onEachFeature: onEachFeaturePark, pointToLayer: pointToLayerPark}).addTo(map);
	});

}

function pointToLayerPark(feature, latlng) {

	// if(feature.properties.Name.includes("P+R"))
	// {
	// 	var parkIcon = L.icon({
	// 		iconUrl: 'images/park_marker_green.svg',
	//
	// 		iconSize:     [35, 40],
	// 		iconAnchor:   [17.5, 40],
	// 		popupAnchor:  [0, -50]
	// 	});
	// }
	// else
	// {
	// 	var parkIcon = L.icon({
	// 		iconUrl: 'images/park_marker.svg',
	//
	// 		iconSize:     [35, 40],
	// 		iconAnchor:   [17.5, 40],
	// 		popupAnchor:  [0, -50]
	// 	});
	// }

	var suffix = 'none';
	var height = 64;
	if(feature.properties.FreeSpaceShort<10)
	{
		suffix = 'some';
		height = 72;
	}
	if(feature.properties.FreeSpaceShort>10)
	{
		suffix = 'plenty';
		height = 80;
	}

	var parkIcon = L.icon({
		iconUrl: 'images/park_marker_'+suffix+'.svg',

		iconSize:     [35, 58],
		iconAnchor:   [17.5, 58],
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
	marker.bindPopup('<div class="popup_'+ suffix +'"><i class="material-icons">fiber_manual_record</i><h3>' + feature.properties.Name + '</h3><div class="pop_inner_content">'+ short + long +'<span class="ammount">' +  feature.properties.FreeSpaceShort + '</span></div></div>', {autoClose: false});

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

	var fietsJsonUrl = 'http://fiets.openov.nl/locaties.json';
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
	// var eventsJsonUrl = 'http://api.simfuny.com/app/api/2_0/events?callback=__ng_jsonp__.__req1.finished&offset=0&limit=25&sort=popular&search=&types[]=unlabeled&dates[]=today';
	var eventsJsonUrl = 'data/events.js';

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

				iconSize:     [35, 58],
				iconAnchor:   [17.5, 58],
				popupAnchor:  [0, -50]
			});



			// console.log(this);
			markers[key] = L.marker([this.lat,this.long], {
				icon: eventIcon,
				name: this.location
			});
			markers[key].addTo(map);
			markers[key].bindPopup('<div class="popup_'+ suffix +'"><i class="material-icons">fiber_manual_record</i><h3>' + this.location +'</h3><img src="'+this.img+'"><div class="pop_inner_content"><p>'+ this.date+'</p><h4>'+this.title+'</h4><p>Aanmeldingen: '+this.attending+'</p><span class="ammount">' +  this.attending + '</span></div></div>', {autoClose: false});
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
	// var trafficJsonUrl = 'http://web.redant.net/~amsterdam/ndw/data/reistijdenAmsterdam.geojson';
	var trafficJsonUrl = 'data/reistijdenAmsterdam.geojson';

	if(debug) { console.log(trafficJsonUrl) }
	$.getJSON(trafficJsonUrl).done(function(trafficJson){
		if(debug) { console.log(trafficJson) }

		$.each(trafficJson.features, function(key,value) {

			var coordinates = [];
			$.each(this.geometry.coordinates, function(key,value) {
				coordinates.push([this[1],this[0]]);
			});

			var event_marker = L.polyline(coordinates, {color: speedToColor(this.properties.Type, this.properties.Velocity)}).addTo(map);
			markers.push(event_marker);
		});

	});

}

function speedToColor(type, speed){
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

		iconSize:     [35, 58],
		iconAnchor:   [17.5, 58],
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





























