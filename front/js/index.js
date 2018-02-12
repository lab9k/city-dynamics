var geojson;
var map;
var legend;
var buurtcode_prop_array = [];
var hotspot_array = [];
var amsterdam_array = [];
var marker;
var lastClickedLayer;
var total_index;
var gauge;
var areaGraph;
var def = '+proj=sterea +lat_0=52.15616055555555 +lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel +towgs84=565.4171,50.3319,465.5524,1.9342,-1.6677,9.1019,4.0725 +units=m +no_defs ';
var proj4RD = proj4('WGS84', def);

var current_date;
var is_now = true;
var vollcode;
var mobile = false;

var geomap1 = 'https://t1.data.amsterdam.nl/topo_wm/{z}/{x}/{y}.png';
var geomap2 = 'https://t1.data.amsterdam.nl/topo_wm_zw/{z}/{x}/{y}.png';
var geomap3 = 'https://t1.data.amsterdam.nl/topo_wm_light/{z}/{x}/{y}.png';

var origin = 'http://127.0.0.1:8117';
var dindex_api = 'http://127.0.0.1:8117/citydynamics/drukteindex/?format=json&op=';
var dindex_hours_api = 'http://127.0.0.1:8117/citydynamics/recentmeasures/?level=day&format=json';
var dindex_days_api = 'http://127.0.0.1:8117/citydynamics/recentmeasures/?level=week&format=json';
var dindex_hotspots_api = 'http://127.0.0.1:8117/citydynamics/hotspots/?format=json';

var geoJsonUrl = 'data/buurtcombinaties.json';
var geoJsonUrl = 'http://localhost:8117/citydynamics/buurtcombinatie/';

var jsonCallback = '&callback=?';
var jsonCallback = '';


// layers
var theme_layer;
var geojson;
var markers = [];


$(document).ready(function(){

	// check device resolution
	mobile = ($( document ).width()<=360);

	if(mobile) {
		var map_center = [52.368, 4.897];
		var zoom = 13.5;
	}
	else {
		var map_center = [52.36, 4.95];
		var zoom = 12;
	}


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

	var hours = getHours();
	$( "#time_i" ).val(hours);
	$( ".time_i_content .time"+hours.substring(0, 2) ).addClass('active');

	// wgs map
	map = L.map('mapid').setView(map_center, zoom);

	L.tileLayer(geomap2, {
		minZoom: 12,
		maxZoom: 16
	}).addTo(map);

	var dindexJsonUrl = dindex_api + getCurrentDate() + jsonCallback;
	console.log(dindexJsonUrl);

	if(mobile)
	{

		dindex_hotspots_api = 'data/hotspots.json';
		var hotspotsJsonUrl = dindex_hotspots_api+'?timestamp='+ getCurrentDate() + jsonCallback;

		console.log(hotspotsJsonUrl);

		$.getJSON(hotspotsJsonUrl).done(function(hotspotsJson) {
			console.log(hotspotsJson);

			$.each(hotspotsJson.results, function (key, value) {

				var dataset = this;

				hotspot_array.push(dataset);

			});

			// console.log(hotspot_array);
			initLineGraph();

			var skipAmsterdam = true;
			var circles = new Array();
			$.each(hotspot_array, function (key, value) {

				if(!skipAmsterdam)
				{
					var hh = getHourDigit();
					var dindex = this.timeIndex[hh].d;

					circles[key] = L.circle(this.latlong, {
						color: '#61FEEE',
						fillColor: '#61FEEE',
						stroke: 0,
						fillOpacity: 0.7,
						radius: (dindex * 100),
						name: this.name
					});
					circles[key].addTo(map);
					$(circles[key]._path).attr('hotspot' , this.id);
					$(circles[key]._path).addClass('hotspot_'+ this.id);
					circles[key].bindPopup("<b>" + this.name + "</b>", {autoClose: false});
					circles[key].on("click", circleClick);


				}

				d3.select('path.hotspot_'+ this.id)
					.datum(graph.data)
					.transition()
					.duration(1000)
					.attrTween('d', function() {
						var interpolator = d3.interpolateArray( graph.data, newData );
						return function( t ) {
							var show = interpolator( t );
							return graph.topline( interpolator( t ) );
						}
					});

				skipAmsterdam = false;

			});



		});

	}
	else
	{
		$.getJSON(dindexJsonUrl).done(function (dindexJson) {

			console.log(dindexJson);

			var calc_index = 0;
			var count_index = 0;

			$.each(dindexJson.results, function (key, value) {
				var buurtcode = this.vollcode;
				var $dataset = [];

				if(this.drukte_index>0)
				{
					dindex = fixIndex(this.drukte_index,buurtcode);
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

			console.log(buurtcode_prop_array);

			total_index = Math.round(calc_index / count_index);

			gauge = $('.gauge').arcGauge({
				value     : total_index,
				colors    : '#014699',
				transition: 500,
				thickness : 10,
				onchange  : function (value) {
					$('.gauge-text .value').text(value);
				}
			});

			$.getJSON(geoJsonUrl).done(function (geoJson) {
				geojson = L.geoJSON(geoJson.results, {style: style, onEachFeature: onEachFeature}).addTo(map);

				geojson.eachLayer(function (layer) {
					layer._path.id = 'feature-' + layer.feature.properties.vollcode;
					buurtcode_prop_array[layer.feature.properties.vollcode]['layer'] = layer;
					buurtcode_prop_array[layer.feature.properties.vollcode]['buurt'] = layer.feature.properties.naam;
				});

			});
		});
	}

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
						popupAnchor:  [0, -50] // point from which the popup should open relative to the iconAnchor
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
				$('.details_graph').show();

			});

		}
	});


	$('h1').on('click',function () {
		document.location.reload();
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

			removeMainLayer();
			hideTopControls();
			resetTheme();
			hideMapControls();
			changeTitleAnalyses();

			$( ".info" ).fadeOut( "slow" );
			$( ".legend" ).fadeOut( "slow" );
			$( ".themas" ).fadeOut( "slow" );
			$( ".detail" ).fadeOut( "slow" );
			$( ".cta" ).fadeOut( "slow" );

			$(".header").addClass('open');

			$( ".header_analyses" ).fadeIn( "slow" );

		}
		else
		{
			addMainLayer();
			showTopControls();
			showMapControls();
			changeTitledefault();

			//$( ".info" ).fadeIn( "slow" );
			$( ".legend" ).fadeIn( "slow" );
			$( ".themas" ).fadeIn( "slow" );
			$( ".detail" ).fadeIn( "slow" );
			$( ".cta" ).fadeIn( "slow" );

			$(".header").removeClass('open');

			$( ".header_analyses" ).fadeOut( "slow" );
		}


		$(this).toggleClass('analyse_b');
		$(this).toggleClass('back_b');
	});

	$('.graph_hours_b').on('click',function () {
		$('.hours_graph').show();
		$('.days_graph').hide();
		$('.graph_hours_b').addClass('active');
		$('.graph_days_b').removeClass('active');
	});

	$('.graph_days_b').on('click',function () {
		$('.days_graph').show();
		$('.hours_graph').hide();
		$('.graph_days_b').addClass('active');
		$('.graph_hours_b').removeClass('active');
	});

	$('.detail_top i').on('click',function () {
		closeDetails();
	});

	$('.leftbox_top i').on('click',function () {
		hideLeftBox();
	});

	$( document).on('click', ".fiets_b",function () {
		if($(this).hasClass('active'))
		{
			hideMarkers();
			$(this).removeClass('active');
		}
		else
		{
			resetTheme();
			showOvFiets();
			$(this).addClass('active');
		}
	});

	$( document).on('click', ".cam_b",function () {
		if($(this).hasClass('active'))
		{
			hideMarkers();
			$(this).removeClass('active');
		}
		else
		{
			resetTheme();
			showFeeds();
			$(this).addClass('active');
		}
	});

	$( document).on('click', ".events_b",function () {
		if($(this).hasClass('active'))
		{
			hideMarkers();
			$(this).removeClass('active');
		}
		else
		{
			resetTheme();
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
			var content = getHotspotsContent();
			openThemaDetails(content);
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
			removeParkLayer();
			$(this).removeClass('active');
		}
		else
		{
			resetTheme();
			addParkLayer();
			$(this).addClass('active');
		}
	});

	$( document).on('click', ".water_b",function () {
		if($(this).hasClass('active'))
		{
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

		$('.time_i_content li').removeClass('active');
		$(this).addClass('active');

		submitQuery();
	});

	$('.controls').on('click',function(){
		map.setView([52.36, 4.95], 12);
	});

	$('.now_b').on('click',function () {
		$( "#date_i" ).val(getDate());
		$( "#time_i" ).val(getHours());
		submitQuery();
	});

});

function circleClick(e) {
	var clickedCircle = e.target;

	updateLineGraph($(clickedCircle._path).attr('hotspot'));

	// do something, like:
	$('.location').text(clickedCircle.options.name);
}

function startAnimation()
{

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

function getCurrentDateOnly()
{
	// get date
	var date = $('.date_i').val();

	return date.replace('/','-').replace('/','-');
}

function submitQuery()
{
	// reset themes
	resetTheme();

	current_date = getCurrentDate();
	var now_date = getNowDate();
	console.log(current_date+" "+now_date);
	if(current_date != now_date)
	{
		is_now = false;
	}
	else
	{
		is_now = true;
	}

	// set now conditions
	setNowConditions(is_now);

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
			if(this.drukte_index>0)
			{
				dindex = fixIndex(this.drukte_index,buurtcode);
				$dataset["index"] = dindex;
			}
			else
			{
				$dataset["index"] = 0;
			}

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

function setNowConditions(is_now)
{
	if(!is_now)
	{
		$('.now_b').removeClass('active');
		$('.themas_buttons li[now]').fadeOut('slow');
	}
	else
	{
		$('.now_b').addClass('active');
		$('.themas_buttons li[now]').fadeIn('slow');
	}
}

function openThemaDetails(content)
{
	// open detail
	$('.themas').addClass('open');

	// set content
	$('.themas .themas_content').html(content);
}

function closeThemaDetails()
{
	// close detail
	$('.themas').removeClass('open');

	// remove content
	$('.themas .themas_content').html('');
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

function getLatLangArray(point) {
	return lnglat = proj4RD.inverse([point.x, point.y]);
}

function getLatLang(point) {
	var lnglat = proj4RD.inverse([point.x, point.y]);
	return L.latLng(lnglat[1], lnglat[0]);
}

function getColor(dindex)
{
	var a = '#50e6db';
	var b = '#ff0000';

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

	// set gauge
	gauge[0].set(Math.round(dindex * 100) );

	// open detail
	openDetails();

	// set name
	$('.detail h2').html(buurt);

	// open detail
	$('.details_graph').show();
	initHourGraph(vollcode);
	initWeekGraph(vollcode);

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

	var hoursJsonUrl = dindex_hours_api+'&vollcode='+vollcode+'&timestamp='+ getCurrentDate() + jsonCallback;
	//var hoursJsonUrl = 'data/hours.json';
	console.log(hoursJsonUrl);

	$.getJSON(hoursJsonUrl).done(function(hoursJson) {
		console.log(hoursJson);
		var i = 0;
		$.each(hoursJson.results, function (key, value) {
			var buurtcode = this.vollcode;
			var $dataset = [];

			$dataset["dindex"] = this.drukte_index * 100;

			$dataset["time"] = this.timestamp.substr(11, 2);
			i++;
			data.push($dataset);
		});


		var svg = d3.select(".svg_hours"),
			margin = {top: 0, right: 0, bottom: 20, left: 0},
			width = +svg.attr("width") - margin.left - margin.right,
			height = +svg.attr("height") - margin.top - margin.bottom;

		var valueline = d3.line()
			.x(function(d) { return x(d.time); })
			.y(function(d) { return y(d.dindex); });

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

		g.append("path")
			.data(data)
			.attr("class", "line")
			.attr("d", valueline);

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

function initLineGraph()
{
	var data = [];

	$.each(hotspot_array[0].timeIndex, function (key, value) {

		var dataset = {};
		dataset.y = Math.round(this.d * 100);
		dataset.x = parseInt(this.h);

		data.push(dataset);
	});

	areaGraph = $('.m_graph').areaGraph(data);

	setTimeout(areaGraph[0].startCount(),3000); //todo: replace timeout for proper load flow

}

function updateLineGraph(hotspot)
{
	// get proper data from json array
	var data = [];

	$.each(hotspot_array[hotspot].timeIndex, function (key, value) {

		var dataset = {};
		dataset.y = Math.round(this.d * 100);
		dataset.x = parseInt(this.h);

		data.push(dataset);
	});


	areaGraph[0].update(data);
}


function initWeekGraph(vollcode)
{
	var data = new Array;

	var weekdays = new Array;
	weekdays[0] = 'Ma';
	weekdays[1] = 'Di';
	weekdays[2] = 'Wo';
	weekdays[3] = 'Do';
	weekdays[4] = 'Vr';
	weekdays[5] = 'Za';
	weekdays[6] = 'Zo';

	var daysJsonUrl = dindex_days_api+'&vollcode='+vollcode+'&timestamp='+ getCurrentDate() + jsonCallback;
	//var daysJsonUrl = 'data/days.json';
	console.log(daysJsonUrl);

	$.getJSON(daysJsonUrl).done(function(daysJson) {
		console.log(daysJson);

		$.each(daysJson.results, function (key, value) {
			var $dataset = [];
			//$dataset["buurt"] = this.naam;
			$dataset["dindex"] = this.drukte_index * 100;
			$dataset["day"] = weekdays[this.weekday];
			data.push($dataset);
		});


		var svg = d3.select(".svg_days"),
			margin = {top: 0, right: 0, bottom: 20, left: 0},
			width = +svg.attr("width") - margin.left - margin.right,
			height = +svg.attr("height") - margin.top - margin.bottom;

		var x = d3.scaleBand().rangeRound([0, width]).padding(0.6),
			y = d3.scaleLinear().rangeRound([height, 0]);

		var g = svg.append("g")
			.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

		x.domain(data.map(function (d) {
			return d.day;
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
				return x(d.day);
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
	var feeds = new Array();

	feeds[0] = {name:"Dam",url:"https://www.youtube.com/embed/ZMQFsNqGavU?rel=0&amp;controls=0&amp;showinfo=0&amp;autoplay=1", lat:"52.3732104", lon:"4.8914401"};
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

		iconSize:     [35, 40], // size of the icon
		iconAnchor:   [17.5, 40], // point of the icon which will correspond to marker's location
		popupAnchor:  [0, -50] // point from which the popup should open relative to the iconAnchor
	});

	$.each(feeds, function(key,value) {
		var cam_marker = L.marker([this.lat,this.lon], {icon: camIcon,title:this.name,alt:this.url}).addTo(map).on('click', function(){showFeed(this.options.title,this.options.alt);});
		cam_marker.bindPopup("<b>" + this.name + "</b>", {autoClose: false});
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

function removeMainLayer()
{
	map.removeLayer(geojson);
}

function addMainLayer()
{
	map.addLayer(geojson);
}

function hideTopControls()
{
	$('.ui-widget').fadeOut('slow');
}


function showTopControls()
{
	$('.ui-widget').fadeIn('slow');
}

function hideMapControls()
{
	$('.leaflet-control-zoom,.controls').fadeOut('slow');
}


function showMapControls()
{
	$('.leaflet-control-zoom,.controls').fadeIn('slow');
}

function changeTitleAnalyses()
{
	$('h1 span').text('Analyse');
}

function changeTitledefault()
{
	$('h1 span').text('DrukteRadar');
}

function addParkLayer()
{

	//var parkJsonUrl = "http://opd.it-t.nl/data/amsterdam/ParkingLocation.json";
	var parkJsonUrl = 'data/parkjson.json';

	$.getJSON(parkJsonUrl).done(function(parkJson){
		console.log(parkJson);
		theme_layer = L.geoJSON(parkJson,{style: stylePark, onEachFeature: onEachFeaturePark, pointToLayer: pointToLayerPark}).addTo(map);
	});

}

function pointToLayerPark(feature, latlng) {

	if(feature.properties.Name.includes("P+R"))
	{
		var parkIcon = L.icon({
			iconUrl: 'images/park_marker_green.svg',

			iconSize:     [35, 40], // size of the icon
			iconAnchor:   [17.5, 40], // point of the icon which will correspond to marker's location
			popupAnchor:  [0, -50] // point from which the popup should open relative to the iconAnchor
		});
	}
	else
	{
		var parkIcon = L.icon({
			iconUrl: 'images/park_marker.svg',

			iconSize:     [35, 40], // size of the icon
			iconAnchor:   [17.5, 40], // point of the icon which will correspond to marker's location
			popupAnchor:  [0, -50] // point from which the popup should open relative to the iconAnchor
		});
	}


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
	var fietsJsonUrl = 'http://fiets.openov.nl/locaties.json';

	$.getJSON(fietsJsonUrl).done(function(fietsJson){
		//console.log(fietsJson);

		var ams_locaties = ['ASB','RAI','ASA','ASDM','ASDZ','ASD','ASDL','ASS'];

		var camIcon = L.icon({
			iconUrl: 'images/fiets_marker.svg',

			iconSize:     [35, 40], // size of the icon
			iconAnchor:   [17.5, 40], // point of the icon which will correspond to marker's location
			popupAnchor:  [0, -50] // point from which the popup should open relative to the iconAnchor
		});

		$.each(fietsJson.locaties, function(key,value) {
			if(ams_locaties.indexOf(this.stationCode)>=0)
			{
				console.log(this.stationCode);
				if(this.lat>0 && this.lng>0)
				{
					var marker_info = {};
					marker_info.name = this.name;
					marker_info.free = this.extra.rentalBikes;
					var fiets_marker = L.marker([this.lat,this.lng], {icon: camIcon,title:this.description,alt:this.url}).addTo(map);
					fiets_marker.bindPopup("<h3>" + this.name + "</h3><br>Fietsen beschikbaar: " + this.extra.rentalBikes, {autoClose: false});
					markers.push(fiets_marker);
				}
			}
		});

	});
}

function showEvents()
{
	var eventsJsonUrl = 'data/Evenementen.json';

	$.getJSON(eventsJsonUrl).done(function(eventsJson){
		console.log(eventsJsonUrl);
		// console.log(eventsJson);

		var camIcon = L.icon({
			iconUrl: 'images/events_marker.svg',

			iconSize:     [35, 40], // size of the icon
			iconAnchor:   [17.5, 40], // point of the icon which will correspond to marker's location
			popupAnchor:  [0, -50] // point from which the popup should open relative to the iconAnchor
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

function getHotspotsContent()
{
	var content =  $('.hotspots_content').clone();

	$(content).show();

	return content;
}

function showMuseum()
{
	var eventsJsonUrl = 'data/MuseaGalleries.json';

	$.getJSON(eventsJsonUrl).done(function(eventsJson){
		console.log(eventsJsonUrl);
		// console.log(eventsJson);

		var camIcon = L.icon({
			iconUrl: 'images/musea_marker.svg',

			iconSize:     [35, 40], // size of the icon
			iconAnchor:   [17.5, 40], // point of the icon which will correspond to marker's location
			popupAnchor:  [0, -50] // point from which the popup should open relative to the iconAnchor
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
		console.log(parcJson);
		theme_layer = L.geoJSON(parcJson,{style: styleParc, onEachFeature: onEachFeatureParc, pointToLayer: pointToLayerParc}).addTo(map);
	});

}

function pointToLayerParc(feature, latlng) {
	var parkIcon = L.icon({
		iconUrl: 'images/parc_marker.svg',

		iconSize:     [35, 40], // size of the icon
		iconAnchor:   [17.5, 40], // point of the icon which will correspond to marker's location
		popupAnchor:  [0, -50] // point from which the popup should open relative to the iconAnchor
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
		console.log(marketJson);
		theme_layer = L.geoJSON(marketJson,{style: styleMarket, onEachFeature: onEachFeatureMarket, pointToLayer: pointToLayerMarket}).addTo(map);
	});

}

function pointToLayerMarket(feature, latlng) {
	var marketIcon = L.icon({
		iconUrl: 'images/market_marker.svg',

		iconSize:     [35, 40], // size of the icon
		iconAnchor:   [17.5, 40], // point of the icon which will correspond to marker's location
		popupAnchor:  [0, -50] // point from which the popup should open relative to the iconAnchor
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
	var googleJsonUrl = 'http://apis.quantillion.io:3001/gemeenteamsterdam/locations/realtime/current';

	$.getJSON(googleJsonUrl).done(function(googleJson){
		console.log(googleJsonUrl);

		$.each(googleJson, function(key,value) {

			var ratio =  this['Real-time'] / this['Expected'] * 100;
			//console.log(ratio);

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

				iconSize:     [35, 40], // size of the icon
				iconAnchor:   [17.5, 40], // point of the icon which will correspond to marker's location
				popupAnchor:  [0, -50] // point from which the popup should open relative to the iconAnchor
			});

			var header = this.name;
			var content = '<p>Expected' + this.Expected +  '</p>'  + '<p>Realtime' + this['Real-time'] +  '</p>'  + '<p>' + this.formatted_address +  '</p>' + '<br /><a target="blank" href="' + this.url +  '">Website</a>';

			var latitude = this.lat;
			var longitude = this.lng;
			var event_marker = L.marker([latitude,longitude], {icon: googleIcon,title:this.name, alt:this['Real-time']}).addTo(map).on('click', function(){
				closeDetails();

				gauge[0].set(Math.round(this.options.alt * 100));
				$('.detail h2').html(this.options.title);

				showLeftBox(content,header);

			});

			event_marker.bindPopup("<b>" + this.name + "</b>", {autoClose: false});
			markers.push(event_marker);
		});

	});	
}

function showWater()
{
	var waterIcon = L.icon({
		iconUrl: 'images/water_marker.svg',

		iconSize:     [35, 40], // size of the icon
		iconAnchor:   [17.5, 40], // point of the icon which will correspond to marker's location
		popupAnchor:  [0, -50] // point from which the popup should open relative to the iconAnchor
	});

	var title = 'Watermeetpunt Prinsegracht';
	var latitude = '52.375389';
	var longitude = '4.883740';
	var event_marker = L.marker([latitude,longitude], {icon: waterIcon,title:title}).addTo(map);
	event_marker.bindPopup("<b>"+title+"</b>", {autoClose: false});
	markers.push(event_marker);

	var content = '<h3>Boot tellingen Prinsegracht</h3><img src="content/waterdrukte.png" />';

	openThemaDetails(content);

}


function fixIndex(in_index,buurtcode)
{
	// var vdata_ratio = (vdata[buurtcode].vindex / 10000 * 4);
	// var dindex = in_index * (vdata_ratio);
	// if(dindex>1) {dindex=1;}
	//console.log(in_index + ' * ' + vdata_ratio + ' = ' + dindex);

	// var vdata2_ratio = vdata2[buurtcode].vindex ;
	// var dindex = in_index * (vdata2_ratio);
	// if(dindex>1) {dindex=1;}
	// console.log(buurtcode + ':' + in_index + ' * ' + vdata2_ratio + ' = ' + dindex);

	//return dindex;
	return in_index;
}





























