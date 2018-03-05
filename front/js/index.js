// map & layers
var map;
var theme_layer;
var circles = [];
var circles_d3 = [];
var circles_layer;
var markers = [];
var geojson;

// global arrays
var buurtcode_prop_array = [];
var hotspot_array = [];
var realtime_array = [];

// states
var vollcode;
var mobile = false;
var active_layer = 'hotspots';

// global vars
var marker; // used by search
var lastClickedLayer;
var total_index;
var areaGraph;

// links
var geomap1 = 'https://t1.data.amsterdam.nl/topo_wm/{z}/{x}/{y}.png';
var geomap2 = 'https://t1.data.amsterdam.nl/topo_wm_zw/{z}/{x}/{y}.png';
var geomap3 = 'https://t1.data.amsterdam.nl/topo_wm_light/{z}/{x}/{y}.png';

var origin = 'https://acc.api.data.amsterdam.nl';
if(window.location.href.indexOf('localhost') !== -1 )
{
	var origin = 'http://127.0.0.1:8117';
}

var base_api = origin + '/citydynamics/';
var dindex_api = base_api + 'drukteindex/?format=json&op=';
var dindex_hotspots_api = base_api + 'hotspots/?format=json';
var realtimeUrl = base_api + 'realtime/?format=json';
var geoJsonUrl = base_api + 'buurtcombinatie/?format=json';

// specific
var def = '+proj=sterea +lat_0=52.15616055555555 +lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel +towgs84=565.4171,50.3319,465.5524,1.9342,-1.6677,9.1019,4.0725 +units=m +no_defs ';
var proj4RD = proj4('WGS84', def);
var amsterdam = {
	coordinates: [52.368, 4.897],
	druktecijfers: [{h:0,d:0},{h:1,d:0},{h:2,d:0},{h:3,d:0},{h:4,d:0},{h:5,d:0},{h:6,d:0},{h:7,d:0},{h:8,d:0},{h:9,d:0},{h:10,d:0},{h:11,d:0},{h:12,d:0},{h:13,d:0},{h:14,d:0},{h:15,d:0},{h:16,d:0},{h:17,d:0},{h:18,d:0},{h:19,d:0},{h:20,d:0},{h:21,d:0},{h:22,d:0},{h:23,d:0}],
	hotspot: "Amsterdam",
	index: -1
}

$(document).ready(function(){

	// check device resolution
	mobile = ($( document ).width()<=360);

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

	var dindexJsonUrl = dindex_api + getNowDate();
	//console.log(dindexJsonUrl);

	// district map init
	$.getJSON(dindexJsonUrl).done(function (dindexJson) {
		//console.log(dindexJson);

		var calc_index = 0;
		var count_index = 0;

		$.each(dindexJson.results, function (key, value) {
			var buurtcode = this.vollcode;
			var $dataset = [];

			if(this.drukte_index>0)
			{
				dindex = this.drukte_index,buurtcode;
				$dataset["index"] = dindex;
			}
			else
			{
				$dataset["index"] = 0;
			}

			calc_index += Math.round($dataset["index"] * 100);
			count_index++;

			buurtcode_prop_array[buurtcode] = $dataset;
		});


		total_index = Math.round(calc_index / count_index);

		$.getJSON(geoJsonUrl).done(function (geoJson) {
			geojson = L.geoJSON(geoJson.results, {style: style, onEachFeature: onEachFeature}).addTo(map);

			geojson.eachLayer(function (layer) {
				layer._path.id = 'feature-' + layer.feature.properties.vollcode;
				buurtcode_prop_array[layer.feature.properties.vollcode]['layer'] = layer;
				buurtcode_prop_array[layer.feature.properties.vollcode]['buurt'] = layer.feature.properties.naam;
			});

			// hide map by default
			map.removeLayer(geojson);

		});
	});

	// hotspots map init
	var hotspotsJsonUrl = dindex_hotspots_api+'&timestamp='+ getNowDate();
	console.log(hotspotsJsonUrl);

	$.getJSON(hotspotsJsonUrl).done(function(hotspotsJson) {
		//console.log(hotspotsJson);

		var hotspot_count = 0;
		$.each(hotspotsJson.results, function (key, value) {

			this.druktecijfers.sort(function (a, b) {
				return a.h - b.h;
			});

			hotspot_count++;

			// used for ams average todo: calc average in backend
			$.each(this.druktecijfers, function (key, value) {

				// console.log(this.d);
				amsterdam.druktecijfers[this.h].d += this.d

				// console.log('cum: '+amsterdam.druktecijfers[this.h].d);
			});

			var dataset = this;

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
				color: getColor(dindex),
				fillColor: getColor(dindex),
				fillOpacity: 1,
				radius: (12),
				name: this.hotspot
			});
			circles[key].addTo(map);
			$(circles[key]._path).attr('stroke-opacity' , 0.6);
			$(circles[key]._path).attr('stroke' , '#4a4a4a');
			$(circles[key]._path).attr('hotspot' , this.index);
			$(circles[key]._path).addClass('hotspot_'+ this.index);
			circles[key].bindPopup("<h3>" + this.hotspot + "</h3>", {autoClose: false});
			circles[key].on("click", function(e){
				var clickedCircle = e.target;

				updateLineGraph($(clickedCircle._path).attr('hotspot'));

				// do something, like:
				$('.graphbar_title h2').text(clickedCircle.options.name);
			});
			circles[key].addTo(circles_layer);


			circles_d3[key] = d3.select('path.hotspot_'+ this.index);

		});

		initLineGraph();

	});

	// init auto complete
	$('#loc_i').autocomplete({
		source: function (request, response) {
			console.log(request.term);
			$.getJSON("https://api.data.amsterdam.nl/atlas/typeahead/bag/?q=" + request.term).done( function (data) {
				//console.log(data[0].content);
				response($.map(data[0].content, function (value, key) {
					console.log(value);
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

			console.log(ui.item);

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

	// realtime check
	$.getJSON(realtimeUrl).done(function (realtimeJson) {

		var hotspots_match_array = [];
		hotspots_match_array[18] = 'ARTIS';
		hotspots_match_array[36] = 'Museumplein';
		hotspots_match_array[0] = 'Amsterdam Centraal';
		hotspots_match_array[3] = 'Madame Tussauds Amsterdam'; //dam
		hotspots_match_array[33] = 'Dappermarkt';
		hotspots_match_array[15] = 'Tolhuistuin'; // overhoeksplein
		hotspots_match_array[5] = 'Mata Hari'; // Oudezijds Achterburgwal

		$.each(realtimeJson.results, function (key, value) {

			var name = this.name;
			var exists = $.inArray(name, hotspots_match_array );
			if(exists > -1)
			{
				// console.log(name + ' - ' + this.data.place_id + ' - ' + this.data['Real-time']);
				realtime_array[exists] = this.data['Real-time'];
			}

		});

	});


	$('.detail_top i').on('click',function () {
		closeDetails();
	});

	$( document).on('click', ".search a",function () {
		if($(this).parent().hasClass('open'))
		{
			$(this).parent().removeClass('open');
		}
		else
		{
			$(this).parent().addClass('open');
		}
	});

	$( document).on('click', ".m_more a",function () {
		if($(this).parent().hasClass('open'))
		{
			$(this).parent().removeClass('open');
			$('.m_menu').hide();
		}
		else
		{
			$(this).parent().addClass('open');
			$('.m_menu').show();
		}
	});

	$( document).on('click', ".searchclose",function () {
		$(this).parent().removeClass('open');
	});

	$( document).on('click', ".close",function () {
		$(this).parent().fadeOut();
	});
4
	$( document).on('click', ".graphbar_title i",function () {
		resetMap();
	});

	$( document).on('click', ".mapswitch a",function () {

		if($(this).hasClass('active'))
		{
			// reset map
			resetMap();
			// hide hotspots
			$('path[hotspot]').hide();
			// show district
			geojson.addTo(map);
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
			$(this).removeClass('active');
		}
		else
		{
			hideActiveLayer();
			resetTheme();
			showInfo('Toont de beschikbaarheid van de OV fietsen over de verschillende locaties.', 6000);
			showOvFiets();
			$(this).addClass('active');
		}
	});

	$( document).on('click', ".cam_b",function () {
		if($(this).hasClass('active'))
		{
			showActiveLayer();
			hideMarkers();
			$(this).removeClass('active');
		}
		else
		{
			hideActiveLayer();
			resetTheme();
			showInfo('Toont de verschillende webcams in en rond de stad.', 6000);
			showFeeds();
			$(this).addClass('active');
		}
	});

	$( document).on('click', ".events_b",function () {
		if($(this).hasClass('active'))
		{
			showActiveLayer();
			hideMarkers();
			$(this).removeClass('active');
		}
		else
		{
			hideActiveLayer();
			resetTheme();
			showInfo('Toont de geplande evenementen van vandaag..', 6000);
			showEvents();
			$(this).addClass('active');
		}
	});

	$( document).on('click', ".option_museum",function () {
		if($(this).hasClass('active'))
		{
			hideMarkers();
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
			$(this).removeClass('active');
		}
		else
		{
			resetThemeDetail();
			addMarketLayer();
			$(this).addClass('active');
		}
	});

	$( document).on('click', ".hotspots_b",function () {
		if($(this).hasClass('active'))
		{

			closeThemaDetails();
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
			$(this).removeClass('active');
		}
		else
		{
			hideActiveLayer();
			resetTheme();
			showInfo('Toont de capaciteit en het aantal beschikbare plekken in de parkeergarages.', 6000);
			addParkLayer();
			$(this).addClass('active');
		}
	});

	$( document).on('click', ".water_b",function () {
		if($(this).hasClass('active'))
		{
			closeThemaDetails();
			hideMarkers();
			$(this).removeClass('active');
		}
		else
		{
			resetTheme();
			showWater();
			$(this).addClass('active');
		}
	});

	$('.controls').on('click',function(){
		map.setView([52.36, 4.95], 12);
	});

	// chrome control button style
	if (navigator.appVersion.indexOf("Chrome/") != -1) {
		$('.controls').addClass('chrome');
	}

});

function resetMap() {
	map.closePopup();
	$('.graphbar_title h2').text(amsterdam.hotspot);
	updateLineGraph('ams');
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
		$.each(hotspot_array, function (key, value) {
			circles_d3[key]
				.attr('stroke-opacity', 0.6)
				.attr('stroke-width', 3)
				.transition()
				.duration(1000)
				.attr('fill', getColor(this.druktecijfers[0].d))
				.attr('stroke', '#4a4a4a');
		});
	}

	var counter = 0;
	interval = setInterval(function() {
		elapsed_time = $('.line-group').attr('time');
		if(elapsed_time > counter)
		{
			var hour = Math.ceil(elapsed_time);



			$.each(hotspot_array, function (key, value) {

				if(key==10)
				{
					//console.log(key + ' - ' + hour + ' - ' + this.druktecijfers[hour].d );
				}

				circles_d3[key]
					.attr('stroke-opacity', 0.6)
					.attr('stroke-width', 3)
					.transition()
					.duration(1000)
					.attr('fill', getColor(this.druktecijfers[hour].d))
					.attr('stroke', '#4a4a4a');
			});


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
	return L.latLng(lnglat[1], lnglat[0]);
}

function getColor(dindex)
{
	var a = '#50E6DB'; //50E6DB 63c6e6
	var b = '#DB322A';

	var ah = parseInt(a.replace(/#/g, ''), 16),
		ar = ah >> 16, ag = ah >> 8 & 0xff, ab = ah & 0xff,
		bh = parseInt(b.replace(/#/g, ''), 16),
		br = bh >> 16, bg = bh >> 8 & 0xff, bb = bh & 0xff,
		rr = ar + dindex * (br - ar),
		rg = ag + dindex * (bg - ag),
		rb = ab + dindex * (bb - ab);

	return '#' + ((1 << 24) + (rr << 16) + (rg << 8) + rb | 0).toString(16).slice(1);
}

function style(feature) {

	var dindex = buurtcode_prop_array[feature.properties.vollcode].index

	return {
		fillColor: getColor(dindex),
		weight: 1,
		opacity: 0.6,
		color: '#fff',
		fillOpacity: 0.7
	};
}

function onEachFeature(feature, layer) {
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

	// set name
	$('.graphbar_title').html(buurt);

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

function updateLineGraph(hotspot)
{
	// get proper data from json array
	var data = [];


	if(hotspot=='ams')
	{
		var point_array = amsterdam.druktecijfers;
	}
	else
	{
		var point_array = hotspot_array[hotspot].druktecijfers;
	}


	$.each(point_array, function (key, value) {

		var dataset = {};
		dataset.y = Math.round(this.d * 100);
		dataset.x = parseInt(this.h);

		data.push(dataset);
	});

	// console.log(data);

	var realtime = realtime_array[hotspot];

	areaGraph[0].update(data,realtime);
}

function setView()
{
	if(mobile)
	{
		map.setView([52.368, 4.897], 11);
	}
	else
	{
		map.setView([52.36, 4.95], 12);
	}
}


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
	var today = "07/12/2017";

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

function showInfo(content,duration)
{
	$('.info').html(content);

	$('.info').show();

	setTimeout(function(){$('.info').fadeOut()},duration)
}

function hideActiveLayer()
{
	areaGraph[0].stop();

	switch(active_layer)
	{
		case 'hotspots':
			$('path[hotspot]').hide();
			break;
		case 'buurten':
			map.removeLayer(geojson);
			break;
	}
}
function showActiveLayer()
{
	areaGraph[0].stopResumeCount();

	switch(active_layer)
	{
		case 'hotspots':
			$('path[hotspot]').show();
			break;
		case 'buurten':
			geojson.addTo(map);
			break;
	}
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

		iconSize:     [35, 72],
		iconAnchor:   [17.5, 72],
		popupAnchor:  [0, -50]
	});

	$.each(feeds, function(key,value) {
		var cam_marker = L.marker([this.lat,this.lon], {icon: camIcon,title:this.name,alt:this.url}).addTo(map).on('click', function(){showFeed(this.options.title,this.options.alt);});
		cam_marker.bindPopup("<h3>" + this.name + "</h3>", {autoClose: false});
		markers.push(cam_marker);
	});

	return feeds;
}

function showLeftBox(content,header)
{
	$( ".leftbox .content" ).html('');
	$( ".leftbox h2" ).html('');

	$( ".legend" ).fadeOut( "slow" );
	$( ".leftbox" ).fadeIn( "slow" );

	$( ".leftbox h2" ).append(header);
	$( ".leftbox .content" ).append(content);
}

function hideLeftBox()
{
	$( ".leftbox" ).fadeOut( "slow" );
	$( ".legend" ).fadeIn( "slow" );

	$( ".leftbox .content" ).html('');
	$( ".leftbox h2" ).html('');
}

function showFeed(title, url)
{

	var content = '<iframe width="100%" height="100%" src="'+url+'" frameborder="0"></iframe>';

	showLeftBox(content,'Webcam '+title);
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

function addParkLayer()
{
	setView();
	//var parkJsonUrl = "http://opd.it-t.nl/data/amsterdam/ParkingLocation.json";
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

		iconSize:     [35, height],
		iconAnchor:   [17.5, 40],
		popupAnchor:  [0, -50]
	});

	var marker = L.marker(latlng, {icon: parkIcon});
	var long ='';
	var short ='';

	if(feature.properties.ShortCapacity>0)
	{
		short = "<br>Parkeren kort: " + feature.properties.FreeSpaceShort + " / " + feature.properties.ShortCapacity;
	}
	if(feature.properties.LongCapacity>0)
	{
		long = "<br>Parkeren lang: " + feature.properties.FreeSpaceLong + " / " + feature.properties.LongCapacity;
	}
	marker.bindPopup("<h3>" + feature.properties.Name + "</h3>"+ short + long , {autoClose: false});

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

	$.getJSON(fietsJsonUrl).done(function(fietsJson){
		//console.log(fietsJson);

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
						iconUrl: 'images/fiets_marker_'+suffix+'.svg?available=' + this.extra.rentalBikes,

						iconSize:     [35, 72],
						iconAnchor:   [17.5, 72],
						popupAnchor:  [0, -50]
					});

					var marker_info = {};
					marker_info.name = this.name;
					marker_info.free = this.extra.rentalBikes;
					var fiets_marker = L.marker([this.lat,this.lng], {icon: fietsIcon,title:this.description,alt:this.url}).addTo(map);
					fiets_marker.bindPopup("<h3>" + this.name + "</h3><br>Fietsen beschikbaar: " + this.extra.rentalBikes, {autoClose: false});
					markers.push(fiets_marker);

					// var popup = new L.Popup();
					// var popupLocation = new L.LatLng(this.lat, this.lng);
					// var popupContent = "<h3>" + this.name + "</h3><br>Fietsen beschikbaar: " + this.extra.rentalBikes;
					// popup.setLatLng(popupLocation);
					// popup.setContent(popupContent);
					//
					// map.addLayer(popup);
					// markers.push(popup);
				}
			}
		});

	});
}

function showEventsOld()
{
	var eventsJsonUrl = 'data/Evenementen.json';

	$.getJSON(eventsJsonUrl).done(function(eventsJson){
		//console.log(eventsJsonUrl);
		// console.log(eventsJson);

		var camIcon = L.icon({
			iconUrl: 'images/events_marker.svg',

			iconSize:     [35, 40],
			iconAnchor:   [17.5, 40],
			popupAnchor:  [0, -50]
		});

		$.each(eventsJson, function(key,value) {


			var current_date = getCurrentDateOnly();

			if(typeof(this.dates.singles)=='object')
			{
				//console.log(this.dates.singles);
				if(this.dates.singles.indexOf(current_date)>=0)
				{
					var latitude = this.location.latitude.replace(',','.');
					var longitude = this.location.longitude.replace(',','.');
					var event_marker = L.marker([latitude,longitude], {icon: camIcon,title:this.details.nl.title}).addTo(map);
					event_marker.bindPopup("<h3>" + this.title + "</h3><br>" + this.details.nl.shortdescription + '<br><a target="blank" href="' +  this.urls[0] + '">Website >></a>' , {autoClose: false});
					markers.push(event_marker);
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
	console.log(eventsJsonUrl);
	$.getJSON(eventsJsonUrl).done(function(eventsJson){

		$.each(eventsJson, function(key,value) {

			if(this.attending>100)
			{
				var radius = 10;
				var dindex = 0;
				var color = '#50E6DB';
			}
			if(this.attending>500)
			{
				var radius = 15;
				var dindex = 0.6;
				var color = '#F5A623';
			}
			if(this.attending>1000)
			{
				var radius = 20;
				var dindex = 1;
				var color = '#DB322A';
			}

			if(this.attending>100)
			{
				console.log(this);
				markers[key] = L.circleMarker([this.lat,this.long], {
					color: color,
					fillColor: color,
					fillOpacity: 1,
					radius: (12),
					name: this.location
				});
				markers[key].addTo(map);
				$(markers[key]._path).attr('stroke-width' , 8);
				$(markers[key]._path).attr('stroke-opacity' , 0.4);
				$(markers[key]._path).attr('stroke' , color);
				markers[key].bindPopup("<h3>" + this.location + ' - ' + this.date +'</h3><br><img src="'+this.img+'"><br><p>'+this.title+'</p><p>Bezoekers: '+this.attending+'</p>', {autoClose: false});
				markers[key].on("click", function(e){
					var clickedCircle = e.target;

				});
			}

		});

	});
}

function showMuseum()
{
	var eventsJsonUrl = 'data/MuseaGalleries.json';

	$.getJSON(eventsJsonUrl).done(function(eventsJson){
		// console.log(eventsJson);

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

	$.getJSON(parcJsonUrl).done(function(parcJson){
		//console.log(parcJson);
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
	//var parkJsonUrl = "http://opd.it-t.nl/data/amsterdam/ParkingLocation.json"; /* cors not enabled
	var marketJsonUrl = 'data/MARKTEN.json';

	$.getJSON(marketJsonUrl).done(function(marketJson){
		//console.log(marketJson);
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

function showGoogle()
{
	// var googleJsonUrl = 'http://apis.quantillion.io:3001/gemeenteamsterdam/locations/realtime/current';
	var googleJsonUrl =  realtimeUrl;

	$.getJSON(googleJsonUrl).done(function(googleJson){
		console.log(googleJsonUrl);


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

		iconSize:     [35, 40],
		iconAnchor:   [17.5, 40],
		popupAnchor:  [0, -50]
	});

	var title = 'Watermeetpunt Prinsegracht';
	var latitude = '52.375389';
	var longitude = '4.883740';
	var event_marker = L.marker([latitude,longitude], {icon: waterIcon,title:title}).addTo(map);
	event_marker.bindPopup("<h3>"+title+"</h3>", {autoClose: false});
	markers.push(event_marker);

	openThemaDetails('water_content');

}





























