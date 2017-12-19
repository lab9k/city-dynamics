var geojson;
var map;
var legend;
var buurtcode_prop_array = new Array();
var marker;
var lastClickedLayer;
var total_index;
var gauge;
var def = '+proj=sterea +lat_0=52.15616055555555 +lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel +towgs84=565.4171,50.3319,465.5524,1.9342,-1.6677,9.1019,4.0725 +units=m +no_defs ';
var proj4RD = proj4('WGS84', def);
var markers = new Array();

var origin = 'http://127.0.0.1:8000';
var dindex_api = 'http://127.0.0.1:8000/citydynamics/api/drukteindex/?format=json&op=';
var dindex_hours_api = 'http://127.0.0.1:8000/citydynamics/api/recentmeasures/?format=json';
var jsonCallback = '&jsonp=?';
//var jsonCallback = '';


var current_date;
var vollcode;


// layers
var parkjson;
var geojson;

$(document).ready(function(){

	$( "#date_i" ).datepicker({
		onSelect: function(date) {
			submitQuery();
		},
		dateFormat: 'dd-mm-yy'
	});

	$( "#date_i" ).val(getDate());


	$('.time_i').on('click',function () {
		$(".time_i_content").show();
		$(".time_i_content").position({
			of: ".time_i",
			my: "left top",
			at: "left bottom"
		});
	});

	$( "#time_i" ).val(getHours());


	// wgs map
	map = L.map('mapid').setView([52.36, 4.95], 12);

	L.tileLayer('https://t1.data.amsterdam.nl/topo_wm_zw/{z}/{x}/{y}.png', {
		minZoom: 12,
		maxZoom: 16
	}).addTo(map);

	var dindexJsonUrl = dindex_api + getCurrentDate() + jsonCallback;
	console.log(dindexJsonUrl);
	//var dindexJsonUrl = 'data/dindex.json';

	var geoJsonUrl = 'https://map.data.amsterdam.nl/maps/gebieden?REQUEST=GetFeature&Typename=ms:buurtcombinatie&version=2.0.0&service=wfs&outputformat=geojson&srsname=epsg:4326';

	jQuery.ajax({
		async: true,
		url: dindexJsonUrl,
		method: "GET"
	}).done(function(dindexJson) {

	// $.getJSON(dindexJsonUrl).done(function(dindexJson) {

		console.log(dindexJson);

		var calc_index = 0;
		var count_index = 0;

		$.each(dindexJson.select, function(key,value) {
			var buurtcode = this.vollcode;
			var $dataset = [];
			$dataset["buurt"] = this.naam;
			$dataset["index"] =  this.drukte_index;

			calc_index += Math.round($dataset["index"] * 100);
			count_index++;

			buurtcode_prop_array[buurtcode] = $dataset;
		});

		total_index = Math.round(calc_index / count_index );

		gauge = $('.gauge').arcGauge({
			value: total_index,
			colors: '#014699',
			transition: 500,
			thickness:10,
			onchange: function (value) {
				$('.gauge-text .value').text(value);
			} });

		$.getJSON(geoJsonUrl).done(function(geoJson){
			geojson = L.geoJSON(geoJson,{style: style, onEachFeature: onEachFeature}).addTo(map);

			geojson.eachLayer(function (layer) {
				layer._path.id = 'feature-' + layer.feature.properties.vollcode;
				buurtcode_prop_array[layer.feature.properties.vollcode]['layer'] = layer;
			});
		});
	});

	// init auto complete
	$('#loc_i').autocomplete({
		source: function (request, response) {
			$.getJSON("https://api.data.amsterdam.nl/atlas/typeahead/bag/?q=" + request.term).done( function (data) {
				//console.log(data[0]);
				response($.map(data[0].content, function (value, key) {
					//console.log(value._display);
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
			//console.log(ui);
			event.preventDefault();
			$('#loc_i').val(ui.item.label);

			$.getJSON("https://api.data.amsterdam.nl/" + ui.item.value).done( function (data) {
				//console.log(data);

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

						iconSize:     [60, 60], // size of the icon
						iconAnchor:   [30, 52], // point of the icon which will correspond to marker's location
						popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
					});

					marker = L.marker(latLang, {icon: blackIcon}).addTo(map);
					//marker = L.marker(latLang).addTo(map);
					map.setView(latLang);
				}
				else
				{
					//alert('Vul een adres in plus huisnummer voor het bepalen van de locatie.');
				}

				var active_layer = buurtcode_prop_array[data._buurtcombinatie.vollcode].layer;
				setLayerActive(active_layer);

				$('.detail h2').html(buurtcode_prop_array[data._buurtcombinatie.vollcode].buurt);
				$('.detail').show();

			});

		}
	});



	$('.info_b i').on('click',function () {
		$(".info").toggle();
	});

	$('.analyse_b, .back_b').on('click',function () {

		if($(this).attr('class') == 'analyse_b')
		{
			if(lastClickedLayer){
				geojson.resetStyle(lastClickedLayer);
				$(lastClickedLayer.getElement()).removeClass("active_path");
			}

			if (marker) {
				map.removeLayer(marker);
			}

			$( ".info" ).fadeOut( "slow" );
			$( ".legend" ).fadeOut( "slow" );
			$( ".themas" ).fadeOut( "slow" );
			$( ".detail" ).fadeOut( "slow" );

			$( ".analyses_1" ).fadeIn( "slow" );
			$( ".analyses_2" ).fadeIn( "slow" );
		}
		else
		{
			$( ".info" ).fadeIn( "slow" );
			$( ".legend" ).fadeIn( "slow" );
			$( ".themas" ).fadeIn( "slow" );
			$( ".detail" ).fadeIn( "slow" );

			$( ".analyses_1" ).fadeOut( "slow" );
			$( ".analyses_2" ).fadeOut( "slow" );
		}


		$(this).toggleClass('analyse_b');
		$(this).toggleClass('back_b');
	});

	$('.detail_top i').on('click',function () {
		$('.detail').removeClass('open');
	});

	$('.leftbox_top i').on('click',function () {
		hideLeftBox();
	});

	$( document).on('click', ".cam_b",function () {
		if($(this).hasClass('active'))
		{
			hideMarkers();
			$(this).removeClass('active');
		}
		else
		{
			showFeeds();
			$(this).addClass('active');
		}
	});

	$( document).on('click', ".park_b",function () {
		if($(this).hasClass('active'))
		{
			removeParkLayer();
			$(this).removeClass('active');
		}
		else
		{
			addParkLayer();
			$(this).addClass('active');
		}
	});


	$(document).mouseup(function(e)
	{
		var container = $(".time_i_content");
		if (!container.is(e.target) && container.has(e.target).length === 0)
		{
			container.hide();
		}
	});

	$('.time_i_content li').on('click',function () {
		$('.time_i').val($(this).html() + ':00');
		$(".time_i_content").hide();

		submitQuery();
	});

	$('.controls').on('click',function(){
		map.setView([52.36, 4.95], 12);
	});

});

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



	return hh + ':00';
}

function getCurrentDate()
{
	// get date
	var date = $('.date_i').val();
	//var date = $( ".date_i" ).datepicker({ dateFormat: 'yy-mm-dd' }).val();

	// get time
	var time = $('.time_i').val();

	current_date = date.replace('/','-').replace('/','-')+'-'+time.replace(':','-')+'-00';

	return current_date;
}

function submitQuery()
{
	current_date = getCurrentDate();

	var dindexJsonUrl = dindex_api + current_date + jsonCallback;
	// var dindexJsonUrl = 'data/dindex2.json';

	console.log(dindexJsonUrl);

	$.getJSON(dindexJsonUrl).done(function(dindexJson) {

		console.log(dindexJson);

		var calc_index = 0;
		var count_index = 0;

		$.each(dindexJson.results, function(key,value) {
			var buurtcode = this.vollcode;
			var $dataset = [];
			$dataset["buurt"] = this.naam;
			$dataset["index"] =  1-this.drukte_index;

			calc_index += Math.round($dataset["index"] * 100);
			count_index++;

			buurtcode_prop_array[buurtcode] = $dataset;

			// set color polygon on id
			$('#feature-'+buurtcode).attr('fill', getColor($dataset["index"]));
		});

		var dindex = Math.round(calc_index / count_index ) / 100;

		if(vollcode)
		{
			dindex = buurtcode_prop_array[vollcode].index;
		}

		// set gauge
		gauge[0].set(Math.round(dindex * 100) );
	});
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
	var a = '#FFFFFF';
	var b = '#014699';

	var ah = parseInt(a.replace(/#/g, ''), 16),
		ar = ah >> 16, ag = ah >> 8 & 0xff, ab = ah & 0xff,
		bh = parseInt(b.replace(/#/g, ''), 16),
		br = bh >> 16, bg = bh >> 8 & 0xff, bb = bh & 0xff,
		rr = ar + dindex * (br - ar),
		rg = ag + dindex * (bg - ag),
		rb = ab + dindex * (bb - ab);

	return '#' + ((1 << 24) + (rr << 16) + (rg << 8) + rb | 0).toString(16).slice(1);

	// if(dindex > 0.80)
	// {
	// 	return "#b30000";
	// }
	// else if(dindex > 0.60)
	// {
	// 	return "#e34a33";
	// }
	// else if(dindex > 0.40)
	// {
	// 	return "#fc8d59";
	// }
	// else if(dindex > 0.20)
	// {
	// 	return "#fdcc8a";
	// }
	// else
	// {
	// 	return  "#fef0d9";
	// }


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

	var buurt = buurtcode_prop_array[layer.feature.properties.vollcode].buurt;
	var dindex = buurtcode_prop_array[layer.feature.properties.vollcode].index;

	layer.bindPopup('<div><h3>' + buurt + '</h3></div>'); //<span>'+ Math.round(dindex * 100) +'</span>
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

	// set gauge
	gauge[0].set(Math.round(dindex * 100) );

	// open detail
	$('.detail').addClass('open');

	// set name
	$('.detail h2').html(buurt);

	initHourGraph();

	$(layer.getElement()).addClass("active_path");

	layer.setStyle({
		weight: 2,
		color: '#fe0000',
		opacity: 0.8,
		fillOpacity: 0.6,
		className: 'path_active'
	});

	if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
		layer.bringToFront();
	}

	lastClickedLayer = layer;
}

function initHourGraph(vollcode)
{
	var data = new Array;

	data[0] = {time:"00", dindex:"20"};
	data[1] = {time:"01", dindex:"15"};
	data[2] = {time:"02", dindex:"10"};
	data[3] = {time:"03", dindex:"9"};
	data[4] = {time:"04", dindex:"7"};
	data[5] = {time:"05", dindex:"9"};
	data[6] = {time:"06", dindex:"14"};
	data[7] = {time:"07", dindex:"36"};
	data[8] = {time:"08", dindex:"75"};
	data[9] = {time:"09", dindex:"66"};
	data[10] = {time:"10", dindex:"60"};
	data[11] = {time:"11", dindex:"40"};
	data[12] = {time:"12", dindex:"49"};
	data[13] = {time:"13", dindex:"50"};
	data[14] = {time:"14", dindex:"53"};
	data[15] = {time:"15", dindex:"46"};
	data[16] = {time:"16", dindex:"45"};
	data[17] = {time:"17", dindex:"69"};
	data[18] = {time:"18", dindex:"81"};
	data[19] = {time:"19", dindex:"56"};
	data[20] = {time:"20", dindex:"31"};
	data[21] = {time:"21", dindex:"40"};
	data[22] = {time:"22", dindex:"32"};
	data[23] = {time:"23", dindex:"29"};

	var hoursJsonUrl = dindex_hours_api+'&vollcode='+vollcode+'&timestamp='+ getCurrentDate() + jsonCallback;

	$.getJSON(hoursJsonUrl).done(function(hoursJson) {

		$.each(hoursJson.results, function (key, value) {
			var buurtcode = this.vollcode;
			var $dataset = [];
			$dataset["buurt"] = this.naam;
			$dataset["dindex"] = 1 - this.drukte_index;
			$dataset["time"] = this.timestamp.substr(11, 2);

			buurtcode_prop_array[buurtcode] = $dataset;
		});


		var svg = d3.select(".svg_hours"),
			margin = {top: 0, right: 0, bottom: 20, left: 0},
			width = +svg.attr("width") - margin.left - margin.right,
			height = +svg.attr("height") - margin.top - margin.bottom;

		var x = d3.scaleBand().rangeRound([0, width]).padding(0.6),
			y = d3.scaleLinear().rangeRound([height, 0]);

		var g = svg.append("g")
			.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

		x.domain(data.map(function (d) {
			return d.time;
		}));
		y.domain([0, 100]);

		g.append("g")
			.attr("class", "axis")
			.attr("transform", "translate(0," + height + ")")
			.call(d3.axisBottom(x))
			.selectAll("text")
			.style("text-anchor", "end")
			.attr("dx", "5px")
			.attr("dy", ".15em");

		g.selectAll(".bar")
			.data(data)
			.enter().append("rect")
			.attr("class", "bar")
			.attr("x", function (d) {
				return x(d.time);
			})
			.attr("y", function (d) {
				return y(d.dindex);
			})
			.attr("width", x.bandwidth())
			.attr("rx", 3)
			.attr("height", function (d) {
				return height - y(d.dindex);
			});

	});
}

function showFeeds()
{
	var feeds = new Array();

	feeds[0] = {name:"Dam",url:"https://www.youtube.com/embed/ZMQFsNqGavU?rel=0&amp;controls=0&amp;showinfo=0&amp;autoplay=1", lat:"52.3732104", lon:"4.8914401"};
	feeds[1] = {name:"Oudezijds Voorburgwal",url:"https://www.youtube.com/embed/_uj8ELeiYKs?rel=0&amp;controls=0&amp;showinfo=0&amp;autoplay=1", lat:"52.3747178", lon:"4.8991389"};

	var camIcon = L.icon({
		iconUrl: 'images/cam_marker.svg',

		iconSize:     [60, 60], // size of the icon
		iconAnchor:   [30, 52], // point of the icon which will correspond to marker's location
		popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
	});

	$.each(feeds, function(key,value) {
		var cam_marker = L.marker([this.lat,this.lon], {icon: camIcon,title:this.name,alt:this.url}).addTo(map).on('click', function(){showFeed(this.options.title,this.options.alt);});
		markers.push(cam_marker);
	});

	return feeds;
}

function showLeftBox(content,header)
{
	$( ".leftbox .content" ).html('');
	$( ".leftbox .content h2" ).html('');

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
	$( ".leftbox .content h2" ).html('');
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

function addParkLayer()
{
	var parkJsonUrl = "http://opd.it-t.nl/data/amsterdam/ParkingLocation.json?jsonp=?";
	//var parkJsonUrl = 'data/parkjson.json';

	// $.getJSON(parkJsonUrl).done(function(parkJson) {
	// 	$.each(parkJson, function(key,value) {
	// 		var cam_marker = L.marker([this.lat,this.lon], {icon: camIcon,title:this.name,alt:this.url}).addTo(map).on('click', function(){showFeed(this.options.title,this.options.alt);});
	// 		markers.push(cam_marker);
	// 	});
	// });

	$.getJSON(parkJsonUrl).done(function(parkJson){
		console.log(parkJson);
		parkjson = L.geoJSON(parkJson,{style: stylePark, onEachFeature: onEachFeaturePark}).addTo(map);

		// geojson.eachLayer(function (layer) {
		// 	layer._path.id = 'feature-' + layer.feature.properties.vollcode;
		// 	buurtcode_prop_array[layer.feature.properties.vollcode]['layer'] = layer;
		// });
	});

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
/*	layer.on({
		mouseover: highlightFeature,
		mouseout: resetHighlight,
		click: zoomToFeature
	});

	var buurt = buurtcode_prop_array[layer.feature.properties.vollcode].buurt;
	var dindex = buurtcode_prop_array[layer.feature.properties.vollcode].index;

	layer.bindPopup('<div><h3>' + buurt + '</h3><span>'+ Math.round(dindex * 100) +'</span></div>');
	layer.on('mouseover', function (e) {
		this.openPopup();
	});
	layer.on('mouseout', function (e) {
		this.closePopup();
	});*/
}


function removeParkLayer()
{
	map.removeLayer(parkjson);
}














