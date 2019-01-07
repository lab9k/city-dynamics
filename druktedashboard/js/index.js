var geomap1 = 'https://t1.data.amsterdam.nl/topo_wm/{z}/{x}/{y}.png';
var geomap2 = 'https://t1.data.amsterdam.nl/topo_wm_zw/{z}/{x}/{y}.png';
var geomap3 = 'https://t1.data.amsterdam.nl/topo_wm_light/{z}/{x}/{y}.png';

var color_array = [];
color_array['OVFiets'] = "#4979ff";
color_array['CMSA'] = "#87ff68";
color_array['Parkeren'] = "#ffb13e";
color_array['GVB'] = "#ff5348";

var icon_array = [];
icon_array['Telling'] = 'poll';
icon_array['Telcamera'] = 'videocam';
icon_array['WiFi sensor'] = 'wifi';
icon_array['3D sensor'] = '3d_rotation';

var point_layer;
var heat_layer;

counter_array = {};

var geojson_blueprint = {
	"type": "FeatureCollection",
	"features": [
		{
			"id": 1,
			"type": "Feature",
			"geometry": {
				"type": "Point",
				"coordinates": [4.91652,52.36599]
			},
			"properties": {
				"name": "",
				"type": "",
				"source": "",
				"radius": "",
				"realtime": ""

			}
		}
	]
};

var geojson = $.extend(true, {}, geojson_blueprint);
geojson.features = [];

var geojson_id = 0;
var mapLayerSensors = {};
var mapLayerSource = {};
var mapLayerRealtime = {};
var mapAllLayers = {};

cmsaTelcamerasUrl = 'data/telcamera.json';
cmsaWifisensorsUrl = 'data/wifisensor.json';
cmsa3densorsUrl = 'data/3dsensor.json';
parkUrl = 'data/parkjson.json';
fietsUrl = 'data/ovfiets.json';
gvbUrl = 'data/gvb.json';

// ######### on load init sequence ###############
$(document).ready(function() {

	initMap();

	$.when( $.getJSON(fietsUrl),
			$.getJSON(parkUrl),
			$.getJSON(gvbUrl),
			$.getJSON(cmsaTelcamerasUrl),
			$.getJSON(cmsaWifisensorsUrl),
			$.getJSON(cmsa3densorsUrl)).done(
		function(fietsJson,parkJson,gvbJson,cmsaTelcamerasJson,cmsaWifisensorJson,cmsa3densorsJson){

			// console.log(parkJson[0]);
			// console.log(cmsaTelcamerasJson[0]);
			// console.log(cmsaWifisensorJson[0]);
			// console.log(cmsa3densorsJson[0]);


			fietsPreprocessor(fietsJson[0]);
			parkPreprocessor(parkJson[0]);
			gvbPreprocessor(gvbJson[0]);
			cmsaPreprocessor(cmsaTelcamerasJson[0]);
			cmsaPreprocessor(cmsaWifisensorJson[0]);
			cmsaPreprocessor(cmsa3densorsJson[0]);

			addGeoLayer();

			populatePage();

			$('.filter_layer_sensors li').on('click', function(){

				var layer = $(this).attr('layer');
				if($(this).hasClass( "active" ))
				{
					var lg = mapLayerSensors[layer];
					map.removeLayer(lg);
					doRecount();
				}
				else
				{
					var lg = mapLayerSensors[layer];
					map.addLayer(lg);
					doRecount();
				}
				$(this).toggleClass('active');
			});

			$('.filter_layer_source li').on('click', function(){

				var layer = $(this).attr('layer');
				if($(this).hasClass( "active" ))
				{
					var lg = mapLayerSource[layer];
					map.removeLayer(lg);
					doRecount();
				}
				else
				{
					var lg = mapLayerSource[layer];
					map.addLayer(lg);
					doRecount();
				}
				$(this).toggleClass('active');
			});

			$('.filter_layer_realtime li').on('click', function(){

				var layer = $(this).attr('layer');
				if($(this).hasClass( "active" ))
				{
					var lg = mapLayerRealtime[layer];
					map.removeLayer(lg);
					doRecount();
				}
				else
				{
					var lg = mapLayerRealtime[layer];
					map.addLayer(lg);
					doRecount();
				}
				$(this).toggleClass('active');
			});

		}).fail(function(districtsIndexJson_t,districtsJson_t,hotspotsJson_t,hotspotsIndexJson_t,realtimeJson_t){
		console.error('One or more apis failed.');
	});

});

// ######### general init and get functions ###############
function initMap()
{

	var map_center = [52.35, 4.897];
	var zoom = 12.4;

	// wgs map
	map = L.map('map', {zoomControl: false}).setView(map_center, zoom);

	L.tileLayer(geomap2, {
		minZoom: 10,
		maxZoom: 20
	}).addTo(map);

	L.control.zoom({
		position:'topright'
	}).addTo(map);

}

function addGeoLayer()
{
	// console.log(geojson);
	// console.log(JSON.stringify(geojson));

	point_layer = L.geoJSON(geojson,{pointToLayer: pointToLayer,onEachFeature: onEachFeature}).addTo(map);

	var point_array = [];
	$.each( geojson.features, function( key, item ) {
		var temp_item = [item.geometry.coordinates[1],item.geometry.coordinates[0]];
		point_array.push(temp_item);
	});

	// console.log(point_array);
	heat_layer = L.heatLayer(point_array, {radius: 50}).addTo(map);
}

function pointToLayer(feature, latlng) {

	var color = color_array[feature.properties.source];

	var geojsonMarkerOptions = {
		radius: 6,
		fillColor: color,
		color: "#999999",
		weight: 1,
		opacity: 1,
		fillOpacity: 0.8
	};

	var marker = L.circleMarker(latlng, geojsonMarkerOptions);
	marker.bindPopup('<h5><i class="material-icons">'+ icon_array[feature.properties.sensor] +'</i> ' + feature.properties.name + '</h5>Type sensor: '+ feature.properties.sensor + '<br> Bron: '+ feature.properties.source + '<br> Realtime: '+ feature.properties.realtime, {autoClose: false});
	return marker;
}

function onEachFeature(feature, featureLayer) {

	// count the different categorie items
	if(counter_array[feature.properties.sensor] == undefined)
	{
		counter_array[feature.properties.sensor] = 1;
	}
	else
	{
		counter_array[feature.properties.sensor]++;
	}

	if(counter_array[feature.properties.source] == undefined)
	{
		counter_array[feature.properties.source] = 1;
	}
	else
	{
		counter_array[feature.properties.source]++;
	}

	if(counter_array[feature.properties.realtime] == undefined)
	{
		counter_array[feature.properties.realtime] = 1;
	}
	else
	{
		counter_array[feature.properties.realtime]++;
	}

	if(counter_array["total"] == undefined)
	{
		counter_array["total"] = 1;
	}
	else
	{
		counter_array["total"]++;
	}

	//does layerGroup already exist? if not create it and add to map
	var lg = mapLayerSensors[feature.properties.sensor];

	if (lg === undefined) {
		lg = new L.layerGroup();
		//add the layer to the map
		lg.addTo(map);
		//store layer
		mapLayerSensors[feature.properties.sensor] = lg;
		mapAllLayers[feature.properties.sensor] = lg;
	}

	//add the feature to the layer
	lg.addLayer(featureLayer);

	//does layerGroup already exist? if not create it and add to map
	var lg = mapLayerSource[feature.properties.source];

	if (lg === undefined) {
		lg = new L.layerGroup();
		//add the layer to the map
		lg.addTo(map);
		//store layer
		mapLayerSource[feature.properties.source] = lg;
		mapAllLayers[feature.properties.source] = lg;
	}

	//add the feature to the layer
	lg.addLayer(featureLayer);

	//does layerGroup already exist? if not create it and add to map
	var lg = mapLayerRealtime[feature.properties.realtime];

	if (lg === undefined) {
		lg = new L.layerGroup();
		//add the layer to the map
		lg.addTo(map);
		//store layer
		mapLayerRealtime[feature.properties.realtime] = lg;
		mapAllLayers[feature.properties.realtime] = lg;
	}

	//add the feature to the layer
	lg.addLayer(featureLayer);
}


function pointToLayerIcon(feature, latlng) {
	var custom_icon = L.icon({
		iconUrl: 'images/wifi.svg',

		iconSize:     [32, 28],
		iconAnchor:   [16, 28],
		popupAnchor:  [0, -50]
	});

	var marker = L.marker(latlng, {icon: custom_icon});
	marker.bindPopup("<h3>" + feature.properties.name + "</h3>", {autoClose: false});
	return marker;
}

function doRecount()
{
	var skip_layer_array = [];

	// check active layers
	$.each( mapAllLayers, function( key, item ) {
		// console.log(key + '=' + map.hasLayer(item));
		if(!map.hasLayer(item))
		{
			// console.log(item);
			skip_layer_array.push(key);
		}
	});

	// console.log(skip_layer_array);

	// set temp counter array
	temp_counter_array = [];
	new_point_array = [];

	$.each( geojson.features, function( key, item ) {

		var doCount = true;
		if(skip_layer_array.indexOf(item.properties.sensor) > -1 || skip_layer_array.indexOf(item.properties.source) > -1 || skip_layer_array.indexOf(item.properties.realtime) > -1)
		{
			doCount = false;
		}

		if(doCount)
		{
			// count the different categorie items
			if(temp_counter_array[item.properties.sensor] == undefined)
			{
				temp_counter_array[item.properties.sensor] = 1;
			}
			else
			{
				temp_counter_array[item.properties.sensor]++;
			}

			if(temp_counter_array[item.properties.source] == undefined)
			{
				temp_counter_array[item.properties.source] = 1;
			}
			else
			{
				temp_counter_array[item.properties.source]++;
			}

			if(temp_counter_array[item.properties.realtime] == undefined)
			{
				temp_counter_array[item.properties.realtime] = 1;
			}
			else
			{
				temp_counter_array[item.properties.realtime]++;
			}

			if(temp_counter_array["total"] == undefined)
			{
				temp_counter_array["total"] = 1;
			}
			else
			{
				temp_counter_array["total"]++;
			}

			var temp_item = [item.geometry.coordinates[1],item.geometry.coordinates[0]];
			new_point_array.push(temp_item);
		}


	});

	$.each( counter_array, function( key, item ) {
		// console.log(key +' - '+item);
		if(temp_counter_array[key])
		{
			counter_array[key] = temp_counter_array[key];
		}
		else
		{
			counter_array[key] = 0;
		}

		$('li[layer="'+ key + '"] .count').html(counter_array[key]);
	});

	$('.content-subheader .count').html(counter_array["total"]);

	// console.log(counter_array);

	map.removeLayer(heat_layer);

	heat_layer = L.heatLayer(new_point_array, {radius: 50}).addTo(map);

}


function parkPreprocessor(data)
{
	var temp_data = [];

	$.each( data.features, function( key, item ) {
		var temp_item = {};
		temp_item.coordinates = item.geometry.coordinates;
		temp_item.name = item.properties.Name;
		temp_item.sensor = "Telling";

		temp_data.push(temp_item);
	});

	convertData(temp_data,'Parkeren','Ja');

}

function fietsPreprocessor(data)
{
	var temp_data = [];

	var ams_locaties = ['ASB','RAI','ASA','ASDM','ASDZ','ASD','ASDL','ASS'];

	$.each( data.locaties, function( key, item ) {
		if(ams_locaties.indexOf(this.stationCode)>=0) {

			var temp_item = {};
			temp_item.coordinates = [item.lng, item.lat];
			temp_item.name = item.name;
			temp_item.sensor = "Telling";

			temp_data.push(temp_item);
		}
	});

	convertData(temp_data,'OVFiets','Ja');
}

function gvbPreprocessor(data)
{
	var temp_data = [];

	$.each( data.features, function( key, item ) {
		var temp_item = {};
		temp_item.coordinates = item.geometry.coordinates;
		temp_item.name = item.properties.Modaliteit +' '+ item.properties.Lijn;
		temp_item.sensor = "Telling";

		temp_data.push(temp_item);
	});

	convertData(temp_data,'GVB','Nee');

}

function cmsaPreprocessor(data)
{
	var temp_data = [];

	$.each( data, function( key, item ) {
		var temp_item = {};
		temp_item.coordinates = [item.LNGMAX,item.LATMAX];
		temp_item.name = item.LABEL;
		temp_item.sensor = item.SELECTIE;

		temp_data.push(temp_item);
	});

	convertData(temp_data,'CMSA','Ja');

}


function convertData(data,source,realtime)
{
	$.each( data, function( key, item ) {
		geojson_id++;
		//console.log(item.name);

		temp_feature = $.extend(true, {}, geojson_blueprint.features[0]);
		temp_feature.id = geojson_id;

		temp_feature.geometry.coordinates = item.coordinates;

		temp_feature.properties.name = item.name;
		temp_feature.properties.sensor = item.sensor;
		temp_feature.properties.source = source;
		temp_feature.properties.radius = 10;
		temp_feature.properties.realtime = realtime;



		geojson.features.push(temp_feature);
	});
}

function populatePage()
{
	$('.content-subheader span').html(counter_array["total"]);

	$.each( mapLayerSensors, function( key, item ) {
		$('.filter_layer_sensors').append('<li layer="'+ key +'" class="active"><span><i style="color:#fff;" class="material-icons searchclose">'+ icon_array[key] +'</i> '+key+'</span> (<span class="count">'+ counter_array[key] +'</span>/'+ counter_array[key] +')</li>')
	});

	$.each( mapLayerSource, function( key, item ) {
		$('.filter_layer_source').append('<li layer="'+ key +'" class="active"><span><i style="color:'+ color_array[key] +';" class="material-icons searchclose">bubble_chart</i> '+key+'</span> (<span class="count">'+ counter_array[key] +'</span>/'+ counter_array[key] +')</li>')
	});

	$.each( mapLayerRealtime, function( key, item ) {
		$('.filter_layer_realtime').append('<li layer="'+ key +'" class="active"><span><i style="color:#fff;" class="material-icons searchclose">timer</i> '+key+'</span> (<span class="count">'+ counter_array[key] +'</span>/'+ counter_array[key] +')</li>')
	});

}




