var geomap1 = 'https://t1.data.amsterdam.nl/topo_wm/{z}/{x}/{y}.png';
var geomap2 = 'https://t1.data.amsterdam.nl/topo_wm_zw/{z}/{x}/{y}.png';
var geomap3 = 'https://t1.data.amsterdam.nl/topo_wm_light/{z}/{x}/{y}.png';

var color_array = [];
color_array['OVFiets'] = "#4979ff";
color_array['CMSA'] = "#87ff68";
color_array['Parkeren'] = "#ffb13e";
color_array['GVB'] = "#ff5348";
color_array['GVBBus'] = "#b7daff";
color_array['VIS'] = "#ff65c1";

var icon_array = [];
icon_array['Telling'] = 'poll';
icon_array['Sensor telling'] = 'poll';
icon_array['Tel camera'] = 'videocam';
icon_array['WiFi sensor'] = 'wifi';
icon_array['3D camera'] = '3d_rotation';
icon_array['Fiets'] = 'directions_bike';
icon_array['Auto'] = 'directions_car';
icon_array['Voetganger'] = 'directions_run';

var convertTypeArray = [];
convertTypeArray['TV Camera'] = 'Tel camera';
convertTypeArray['Kentekencamera, reistijd (MoCo)'] = 'Tel camera';
convertTypeArray['Trigger-camera'] = 'Tel camera';
convertTypeArray['Lustelpunt'] = 'Sensor telling';
convertTypeArray['Telcamera'] = 'Tel camera';
convertTypeArray['WiFi sensor'] = 'WiFi sensor';
convertTypeArray['3D sensor'] = '3D camera';

var function_data;

var point_layer;
var heat_layer;

var custom_shape;
var polyType;

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
var mapLayerMobtype = {};
var mapAllLayers = {};

cmsaTelcamerasUrl = 'data/telcamera.json';
cmsaWifisensorsUrl = 'data/wifisensor.json';
cmsa3densorsUrl = 'data/3dsensor.json';
parkUrl = 'data/parkjson.json';
fietsUrl = 'data/ovfiets.json';
gvbUrl = 'data/gvb.json';
gvbBusUrl = 'data/gvbbus.json';
visUrl = 'data/verkeersensoren.json';
functieUrl = 'data/functiekaart.json';


// ######### on load init sequence ###############
$(document).ready(function() {

	initMap();

	$.when( $.getJSON(fietsUrl),
			$.getJSON(functieUrl),
			$.getJSON(visUrl),
			$.getJSON(parkUrl),
			$.getJSON(gvbUrl),
			$.getJSON(gvbBusUrl),
			$.getJSON(cmsaTelcamerasUrl),
			$.getJSON(cmsaWifisensorsUrl),
			$.getJSON(cmsa3densorsUrl)).done(
		function(fietsJson,functieJson,visJson,parkJson,gvbJson,gvbBusJson,cmsaTelcamerasJson,cmsaWifisensorJson,cmsa3densorsJson){

			// console.log(parkJson[0]);
			// console.log(cmsaTelcamerasJson[0]);
			// console.log(cmsaWifisensorJson[0]);
			// console.log(cmsa3densorsJson[0]);


			fietsPreprocessor(fietsJson[0]);
			visPreprocessor(visJson[0]);
			parkPreprocessor(parkJson[0]);
			gvbPreprocessor(gvbJson[0]);
			gvbBusPreprocessor(gvbBusJson[0]);
			cmsaPreprocessor(cmsaTelcamerasJson[0]);
			cmsaPreprocessor(cmsaWifisensorJson[0]);
			cmsaPreprocessor(cmsa3densorsJson[0]);

			function_data = functieJson[0];

			showFunctionData();

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

			$('.filter_layer_mobtype li').on('click', function(){

				var layer = $(this).attr('layer');
				if($(this).hasClass( "active" ))
				{
					var lg = mapLayerMobtype[layer];
					map.removeLayer(lg);
					doRecount();
				}
				else
				{
					var lg = mapLayerMobtype[layer];
					map.addLayer(lg);
					doRecount();
				}
				$(this).toggleClass('active');
			});


			$('.layer_both').on('click', function(){

				$('.btn-group button').removeClass('active');

				if($(this).hasClass( "active" ))
				{

				}
				else
				{
					map.removeLayer(point_layer);
					map.removeLayer(heat_layer);

					map.addLayer(point_layer);
					map.addLayer(heat_layer);
					$(this).addClass('active');
				}

			});

			$('.layer_heat').on('click', function(){

				$('.btn-group button').removeClass('active');

				if($(this).hasClass( "active" ))
				{

				}
				else
				{
					map.removeLayer(point_layer);
					map.removeLayer(heat_layer);

					map.addLayer(heat_layer);
					$(this).addClass('active');
				}

			});

			$('.layer_dots').on('click', function(){

				$('.btn-group button').removeClass('active');

				if($(this).hasClass( "active" ))
				{

				}
				else
				{
					map.removeLayer(point_layer);
					map.removeLayer(heat_layer);

					map.addLayer(point_layer);
					$(this).addClass('active');
				}

			});

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

	// add drawing option to map

	// Initialise the FeatureGroup to store editable layers
	var editableLayers = new L.FeatureGroup();
	map.addLayer(editableLayers);

	var drawPluginOptions = {
		position: 'topright',
		draw: {
			polyline: false,
			polygon: {shapeOptions: {
				color: '#3c3c3c',
				fillColor: '#ffffff',
				fillOpacity: '0'
			}},
			circle: {shapeOptions: {
				color: '#3c3c3c',
				fillColor: '#ffffff',
				fillOpacity: '0'
			}},
			circlemarker: false,
			rectangle: {shapeOptions: {
				color: '#3c3c3c',
				fillColor: '#ffffff',
				fillOpacity: '0'
			}},
			marker: false
		},
		edit: false
	};

	// Initialise the draw control and pass it the FeatureGroup of editable layers
	var drawControl = new L.Control.Draw(drawPluginOptions);
	map.addControl(drawControl);


	var editableLayers = new L.FeatureGroup();
	map.addLayer(editableLayers);

	map.on('draw:drawstart', function() {
		// remove previous schape
		editableLayers.removeLayer(custom_shape);
		custom_shape = false;

		map.removeLayer(point_layer);
		map.removeLayer(heat_layer);

		addGeoLayer();
		doRecount();
	});

	map.on('draw:drawstop', function() {

	});

	map.on('draw:created', function(e) {

		var type = e.layerType;
		custom_shape = e.layer;
console.log(type);
		polyType = type;
		map.removeLayer(point_layer);
		map.removeLayer(heat_layer);
		//point_layer = false;
		addGeoLayer();
		doRecount();
		showFunctionData();

		editableLayers.addLayer(custom_shape);
	});



}

function clearCatagoryLayers()
{
	$.each( mapLayerSensors, function( key, item ) {
		item.clearLayers();
	});
	$.each( mapLayerSource, function( key, item ) {
		item.clearLayers();
	});
	$.each( mapLayerRealtime, function( key, item ) {
		item.clearLayers();
	});
	$.each( mapLayerMobtype, function( key, item ) {
		item.clearLayers();
	});
	$.each( mapAllLayers, function( key, item ) {
		item.clearLayers();
	});
}

function addGeoLayer()
{
	// console.log(geojson);
	// console.log(JSON.stringify(geojson));

	// clear layers
	clearCatagoryLayers();

	point_layer = L.geoJSON(geojson,{pointToLayer: pointToLayer,onEachFeature: onEachFeature, filter: polyFilter}).addTo(map);

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
		radius: 4,
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

function polyFilter(feature)
{
	var doCount = true;

	if(custom_shape)
	{
		var latlng = {'lat':feature.geometry.coordinates[1],'lng':feature.geometry.coordinates[0]};


		if(polyType=='polygon')
		{
			doCount = pointInPoly(custom_shape,latlng);
		}
		if(polyType=='rectangle')
		{
			doCount = custom_shape.getBounds().contains(latlng);
		}
		if(polyType=='circle')
		{
			doCount = custom_shape.getLatLng().distanceTo(latlng) < custom_shape.getRadius();
		}
	}

	// console.log(doCount);
	return doCount;
}

function onEachFeature(feature, featureLayer) {

	// console.log(feature.properties.mobtype);

	// count the different categorie items
	if (counter_array[feature.properties.sensor] == undefined) {
		counter_array[feature.properties.sensor] = 1;
	}
	else {
		counter_array[feature.properties.sensor]++;
	}

	if (counter_array[feature.properties.source] == undefined) {
		counter_array[feature.properties.source] = 1;
	}
	else {
		counter_array[feature.properties.source]++;
	}

	if (counter_array[feature.properties.realtime] == undefined) {
		counter_array[feature.properties.realtime] = 1;
	}
	else {
		counter_array[feature.properties.realtime]++;
	}

	if (counter_array[feature.properties.mobtype] == undefined) {
		counter_array[feature.properties.mobtype] = 1;
	}
	else {
		counter_array[feature.properties.mobtype]++;
	}

	if (counter_array["total"] == undefined) {
		counter_array["total"] = 1;
	}
	else {
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

	//does layerGroup already exist? if not create it and add to map
	var lg = mapLayerMobtype[feature.properties.mobtype];

	if (lg === undefined) {
		lg = new L.layerGroup();
		//add the layer to the map
		lg.addTo(map);
		//store layer
		mapLayerMobtype[feature.properties.mobtype] = lg;
		mapAllLayers[feature.properties.mobtype] = lg;
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

function pointInPoly(polygon,coordinates) {
	var bounds = polygon.getBounds();

	var x_min  = bounds.getEast();
	var x_max  = bounds.getWest();
	var y_min  = bounds.getSouth();
	var y_max  = bounds.getNorth();

	var lat = coordinates.lat;
	var lng = coordinates.lng;

	var point  = turf.point([lng, lat]);
	var poly   = polygon.toGeoJSON();

	var inside = turf.inside(point, poly);

	if (inside) {
		return true;
	} else {
		return false;
	}
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

		// filters. in order of importance
		if(custom_shape)
		{
			var latlng = {'lat':item.geometry.coordinates[1],'lng':item.geometry.coordinates[0]};
			// console.log(latlng);
			// console.log(item.geometry.coordinates);

			if(polyType=='polygon')
			{
				doCount = pointInPoly(custom_shape,latlng);
			}
			if(polyType=='rectangle')
			{
				doCount = custom_shape.getBounds().contains(latlng);
			}
			if(polyType=='circle')
			{
				doCount = custom_shape.getLatLng().distanceTo(latlng) < custom_shape.getRadius();
			}

			// console.log(doCount);
		}

		if(skip_layer_array.indexOf(item.properties.sensor) > -1 || skip_layer_array.indexOf(item.properties.source) > -1 || skip_layer_array.indexOf(item.properties.realtime) > -1 || skip_layer_array.indexOf(item.properties.mobtype) > -1)
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

			if(temp_counter_array[item.properties.mobtype] == undefined)
			{
				temp_counter_array[item.properties.mobtype] = 1;
			}
			else
			{
				temp_counter_array[item.properties.mobtype]++;
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
		temp_item.mobtype = "Auto";

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
			temp_item.mobtype = "Fiets";

			temp_data.push(temp_item);
		}
	});

	convertData(temp_data,'OVFiets','Ja');
}



function visPreprocessor(data)
{
	var temp_data = [];
	var add_array = ['Kentekencamera, reistijd (MoCo)','Trigger-camera','Lustelpunt'];

	$.each( data.features, function( key, item ) {
		if(add_array.indexOf(item.properties.Soort)>-1)
		{
			var temp_item = {};
			temp_item.coordinates = item.geometry.coordinates;
			temp_item.name = item.properties.Objectnummer_Amsterdam;
			temp_item.sensor = convertTypeArray[item.properties.Soort];
			temp_item.mobtype = "Auto";

			temp_data.push(temp_item);
		}
	});

	convertData(temp_data,'VIS','Ja');

}

function gvbPreprocessor(data)
{
	var temp_data = [];

	$.each( data.features, function( key, item ) {
		var temp_item = {};
		temp_item.coordinates = item.geometry.coordinates;
		temp_item.name = item.properties.Modaliteit +' '+ item.properties.Lijn;
		temp_item.sensor = "Telling";
		temp_item.mobtype = "Voetganger";

		temp_data.push(temp_item);
	});

	convertData(temp_data,'GVB','Nee');

}

function gvbBusPreprocessor(data)
{
	var temp_data = [];

	$.each( data, function( key, item ) {
		var temp_item = {};
		temp_item.coordinates =  [item.lng, item.lat];
		temp_item.name = item.name;
		temp_item.sensor = "Telling";
		temp_item.mobtype = "Voetganger";

		temp_data.push(temp_item);
	});

	convertData(temp_data,'GVBBus','Nee');

}

function cmsaPreprocessor(data)
{
	var temp_data = [];

	$.each( data, function( key, item ) {
		var temp_item = {};
		temp_item.coordinates = [item.LNGMAX,item.LATMAX];
		temp_item.name = item.LABEL;
		temp_item.sensor = convertTypeArray[item.SELECTIE];
		temp_item.mobtype = "Voetganger";

		temp_data.push(temp_item);
	});

	convertData(temp_data,'CMSA','Ja');

}

function showFunctionData()
{
	data = function_data;

	// empty lists
	$('.function0_list').html('');
	$('.function1_list').html('');
	$('.function2_list').html('');

	var functie1_array = {};
	var functie1_total_array = {};
	var functie2_array = {};
	var functie2_total_array = {};

	var business_array = ['Bedrijven','Kantoren'];
	var activity_array = ['Activiteiten en Ontmoeting','sport','Zorg','Onderwijs','Religie','Parkeren','Openbaar vervoer'];
	var shopping_array = ['Detailhandel',]
	var tourism_array = ['Uitgaan en Toerisme','Horeca'];
	var other_array = ['Onduidelijk'];

	var functie0_array = {'Business':0,'Activity':0,'Tourism':0,'Shopping':0,'Other':0};
	var functie0_total_array = {'Business':0,'Activity':0,'Tourism':0,'Shopping':0,'Other':0};

	var part_total = 0;
	var total = 0;

	$.each( data.features, function( key, item ) {

		var doCount = true;

		// filters. in order of importance
		if(custom_shape)
		{

			if(item.geometry.type == 'MultiPolygon')
			{
				var coordinates = item.geometry.coordinates[0][0][0];
			}
			else
			{
				var coordinates = item.geometry.coordinates[0][0];
			}

			var latlng = {'lat':coordinates[1],'lng':coordinates[0]};


			if(polyType=='polygon')
			{
				doCount = pointInPoly(custom_shape,latlng);
			}
			if(polyType=='rectangle')
			{
				doCount = custom_shape.getBounds().contains(latlng);
			}
			if(polyType=='circle')
			{
				doCount = custom_shape.getLatLng().distanceTo(latlng) < custom_shape.getRadius();
			}
		}

		if(doCount)
		{

			if(business_array.indexOf(item.properties.FUNCTIE1_OMS) > -1 )
			{
				functie0_array['Business']++;
			}

			if(activity_array.indexOf(item.properties.FUNCTIE1_OMS) > -1)
			{
				functie0_array['Activity']++;
			}

			if(tourism_array.indexOf(item.properties.FUNCTIE1_OMS) > -1)
			{
				functie0_array['Tourism']++;
			}

			if(shopping_array.indexOf(item.properties.FUNCTIE1_OMS) > -1)
			{
				functie0_array['Shopping']++;
			}

			if(other_array.indexOf(item.properties.FUNCTIE1_OMS) > -1)
			{
				functie0_array['Other']++;
			}


			var lg = functie1_array[item.properties.FUNCTIE1_OMS];
			if (lg === undefined)
			{
				functie1_array[item.properties.FUNCTIE1_OMS] = 1;
			}
			else
			{
				functie1_array[item.properties.FUNCTIE1_OMS]++;
			}

			var lg = functie2_array[item.properties.FUNCTIE2_OMS];
			if (lg === undefined)
			{
				functie2_array[item.properties.FUNCTIE2_OMS] = 1;
			}
			else
			{
				functie2_array[item.properties.FUNCTIE2_OMS]++;
			}

			part_total++;
		}


		if(business_array.indexOf(item.properties.FUNCTIE1_OMS) > -1 )
		{
			functie0_total_array['Business']++;
		}

		if(activity_array.indexOf(item.properties.FUNCTIE1_OMS) > -1)
		{
			functie0_total_array['Activity']++;
		}

		if(tourism_array.indexOf(item.properties.FUNCTIE1_OMS) > -1)
		{
			functie0_total_array['Tourism']++;
		}

		if(shopping_array.indexOf(item.properties.FUNCTIE1_OMS) > -1)
		{
			functie0_total_array['Shopping']++;
		}

		if(other_array.indexOf(item.properties.FUNCTIE1_OMS) > -1)
		{
			functie0_total_array['Other']++;
		}


		var lg = functie1_total_array[item.properties.FUNCTIE1_OMS];
		if (lg === undefined)
		{
			functie1_total_array[item.properties.FUNCTIE1_OMS] = 1;
		}
		else
		{
			functie1_total_array[item.properties.FUNCTIE1_OMS]++;
		}

		var lg = functie2_total_array[item.properties.FUNCTIE2_OMS];
		if (lg === undefined)
		{
			functie2_total_array[item.properties.FUNCTIE2_OMS] = 1;
		}
		else
		{
			functie2_total_array[item.properties.FUNCTIE2_OMS]++;
		}

		total++;

	});

	$('.function_header .function_count').html(part_total);
	$('.function_header .function_total').html(total);

	$.each(functie0_array, function( key, item ) {
		$('.function0_list').append('<li layer="'+ key +'" class="">'+key+'</span> (<span class="count">'+ item +'</span>/'+ functie0_total_array[key] +')</li>');
	});

	$.each(functie1_array, function( key, item ) {
		$('.function1_list').append('<li layer="'+ key +'" class="">'+key+'</span> (<span class="count">'+ item +'</span>/'+ functie1_total_array[key] +')</li>');
	});

	$.each(functie2_array, function( key, item ) {
		$('.function2_list').append('<li layer="'+ key +'" class="">'+key+'</span> (<span class="count">'+ item +'</span>/'+ functie2_total_array[key] +')</li>');
	});

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
		temp_feature.properties.mobtype = item.mobtype;



		geojson.features.push(temp_feature);
	});
}

function populatePage()
{
	$('.sensor_header span').html(counter_array["total"]);

	$.each( mapLayerSensors, function( key, item ) {
		$('.filter_layer_sensors').append('<li layer="'+ key +'" class="active"><span><i style="color:#fff;" class="material-icons searchclose">'+ icon_array[key] +'</i> '+key+'</span> (<span class="count">'+ counter_array[key] +'</span>/'+ counter_array[key] +')</li>')
	});

	$.each( mapLayerSource, function( key, item ) {
		$('.filter_layer_source').append('<li layer="'+ key +'" class="active"><span><i style="color:'+ color_array[key] +';" class="material-icons searchclose">bubble_chart</i> '+key+'</span> (<span class="count">'+ counter_array[key] +'</span>/'+ counter_array[key] +')</li>')
	});

	$.each( mapLayerRealtime, function( key, item ) {
		$('.filter_layer_realtime').append('<li layer="'+ key +'" class="active"><span><i style="color:#fff;" class="material-icons searchclose">timer</i> '+key+'</span> (<span class="count">'+ counter_array[key] +'</span>/'+ counter_array[key] +')</li>')
	});

	$.each( mapLayerMobtype, function( key, item ) {
		$('.filter_layer_mobtype').append('<li layer="'+ key +'" class="active"><span><i style="color:#fff;" class="material-icons searchclose">'+ icon_array[key] +'</i> '+key+'</span> (<span class="count">'+ counter_array[key] +'</span>/'+ counter_array[key] +')</li>')
	});

}




