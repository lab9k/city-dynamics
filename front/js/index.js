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
var current_date;
var is_now = true;
var vollcode;

var origin = 'http://127.0.0.1:8117';
var dindex_api = 'http://127.0.0.1:8117/citydynamics/drukteindex/?format=json&op=';
var dindex_hours_api = 'http://127.0.0.1:8117/citydynamics/recentmeasures/?level=day&format=json';
var dindex_days_api = 'http://127.0.0.1:8117/citydynamics/recentmeasures/?level=week&format=json';
var jsonCallback = '&callback=?';
var jsonCallback = '';


// layers
var theme_layer;
var geojson;


var vdata = new Array();

vdata["A00"] = {vindex:8053};
vdata["A01"] = {vindex:3957};
vdata["A02"] = {vindex:3444};
vdata["A03"] = {vindex:3925};
vdata["A04"] = {vindex:1094};
vdata["A05"] = {vindex:1999};
vdata["A06"] = {vindex:2129};
vdata["A07"] = {vindex:3174};
vdata["A08"] = {vindex:989};
vdata["A09"] = {vindex:481};
vdata["B10"] = {vindex:19};
vdata["E12"] = {vindex:151};
vdata["E13"] = {vindex:300};
vdata["E14"] = {vindex:1012};
vdata["E15"] = {vindex:309};
vdata["E16"] = {vindex:748};
vdata["E17"] = {vindex:1178};
vdata["E18"] = {vindex:2639};
vdata["E19"] = {vindex:1605};
vdata["E20"] = {vindex:1042};
vdata["E21"] = {vindex:1186};
vdata["E22"] = {vindex:1242};
vdata["E36"] = {vindex:95};
vdata["E37"] = {vindex:889};
vdata["E38"] = {vindex:486};
vdata["E39"] = {vindex:501};
vdata["E40"] = {vindex:954};
vdata["E41"] = {vindex:1252};
vdata["E42"] = {vindex:1646};
vdata["E43"] = {vindex:694};
vdata["E75"] = {vindex:1010};
vdata["F11"] = {vindex:113};
vdata["F76"] = {vindex:619};
vdata["F77"] = {vindex:201};
vdata["F78"] = {vindex:367};
vdata["F79"] = {vindex:46};
vdata["F80"] = {vindex:8};
vdata["F81"] = {vindex:770};
vdata["F82"] = {vindex:478};
vdata["F83"] = {vindex:486};
vdata["F84"] = {vindex:440};
vdata["F85"] = {vindex:223};
vdata["F86"] = {vindex:297};
vdata["F87"] = {vindex:324};
vdata["F88"] = {vindex:174};
vdata["F89"] = {vindex:465};
vdata["K23"] = {vindex:567};
vdata["K24"] = {vindex:2837};
vdata["K25"] = {vindex:1823};
vdata["K26"] = {vindex:911};
vdata["K44"] = {vindex:744};
vdata["K45"] = {vindex:846};
vdata["K46"] = {vindex:309};
vdata["K47"] = {vindex:656};
vdata["K48"] = {vindex:387};
vdata["K49"] = {vindex:496};
vdata["K52"] = {vindex:855};
vdata["K53"] = {vindex:646};
vdata["K54"] = {vindex:283};
vdata["K59"] = {vindex:265};
vdata["K90"] = {vindex:182};
vdata["K91"] = {vindex:141};
vdata["M27"] = {vindex:834};
vdata["M28"] = {vindex:664};
vdata["M29"] = {vindex:2052};
vdata["M30"] = {vindex:859};
vdata["M31"] = {vindex:1580};
vdata["M32"] = {vindex:354};
vdata["M33"] = {vindex:417};
vdata["M34"] = {vindex:12};
vdata["M35"] = {vindex:144};
vdata["M50"] = {vindex:150};
vdata["M51"] = {vindex:150};
vdata["M55"] = {vindex:133};
vdata["M56"] = {vindex:93};
vdata["M57"] = {vindex:30};
vdata["M58"] = {vindex:101};
vdata["N60"] = {vindex:460};
vdata["N61"] = {vindex:298};
vdata["N62"] = {vindex:295};
vdata["N63"] = {vindex:352};
vdata["N64"] = {vindex:858};
vdata["N65"] = {vindex:267};
vdata["N66"] = {vindex:79};
vdata["N67"] = {vindex:75};
vdata["N68"] = {vindex:262};
vdata["N69"] = {vindex:567};
vdata["N70"] = {vindex:304};
vdata["N71"] = {vindex:264};
vdata["N72"] = {vindex:420};
vdata["N73"] = {vindex:4};
vdata["N74"] = {vindex:95};
vdata["T92"] = {vindex:891};
vdata["T93"] = {vindex:618};
vdata["T94"] = {vindex:220};
vdata["T95"] = {vindex:67};
vdata["T96"] = {vindex:340};
vdata["T97"] = {vindex:289};
vdata["T98"] = {vindex:8};

var vdata2 = new Array();

vdata2["A00"] = {vindex:0.9};
vdata2["A01"] = {vindex:0.9};
vdata2["A02"] = {vindex:0.9};
vdata2["A03"] = {vindex:0.9};
vdata2["A04"] = {vindex:0.9};
vdata2["A05"] = {vindex:0.9};
vdata2["A06"] = {vindex:0.9};
vdata2["A07"] = {vindex:0.9};
vdata2["A08"] = {vindex:0.9};
vdata2["A09"] = {vindex:0.9};
vdata2["B10"] = {vindex:0.5};
vdata2["E12"] = {vindex:0.5};
vdata2["E13"] = {vindex:0.5};
vdata2["E14"] = {vindex:0.5};
vdata2["E15"] = {vindex:0.5};
vdata2["E16"] = {vindex:0.5};
vdata2["E17"] = {vindex:0.5};
vdata2["E18"] = {vindex:0.5};
vdata2["E19"] = {vindex:0.5};
vdata2["E20"] = {vindex:0.5};
vdata2["E21"] = {vindex:0.5};
vdata2["E22"] = {vindex:0.5};
vdata2["E36"] = {vindex:0.5};
vdata2["E37"] = {vindex:0.5};
vdata2["E38"] = {vindex:0.5};
vdata2["E39"] = {vindex:0.5};
vdata2["E40"] = {vindex:0.5};
vdata2["E41"] = {vindex:0.5};
vdata2["E42"] = {vindex:0.5};
vdata2["E43"] = {vindex:0.5};
vdata2["E75"] = {vindex:0.5};
vdata2["F11"] = {vindex:0.5};
vdata2["F76"] = {vindex:0.5};
vdata2["F77"] = {vindex:0.5};
vdata2["F78"] = {vindex:0.5};
vdata2["F79"] = {vindex:0.5};
vdata2["F80"] = {vindex:0.5};
vdata2["F81"] = {vindex:0.5};
vdata2["F82"] = {vindex:0.5};
vdata2["F83"] = {vindex:0.5};
vdata2["F84"] = {vindex:0.5};
vdata2["F85"] = {vindex:0.5};
vdata2["F86"] = {vindex:0.5};
vdata2["F87"] = {vindex:0.5};
vdata2["F88"] = {vindex:0.5};
vdata2["F89"] = {vindex:0.5};
vdata2["K23"] = {vindex:0.5};
vdata2["K24"] = {vindex:0.5};
vdata2["K25"] = {vindex:0.5};
vdata2["K26"] = {vindex:0.5};
vdata2["K44"] = {vindex:0.5};
vdata2["K45"] = {vindex:0.5};
vdata2["K46"] = {vindex:0.5};
vdata2["K47"] = {vindex:0.5};
vdata2["K48"] = {vindex:0.5};
vdata2["K49"] = {vindex:0.5};
vdata2["K52"] = {vindex:0.5};
vdata2["K53"] = {vindex:0.5};
vdata2["K54"] = {vindex:0.5};
vdata2["K59"] = {vindex:0.5};
vdata2["K90"] = {vindex:0.5};
vdata2["K91"] = {vindex:0.5};
vdata2["M27"] = {vindex:0.5};
vdata2["M28"] = {vindex:0.5};
vdata2["M29"] = {vindex:0.5};
vdata2["M30"] = {vindex:0.5};
vdata2["M31"] = {vindex:0.5};
vdata2["M32"] = {vindex:0.5};
vdata2["M33"] = {vindex:0.5};
vdata2["M34"] = {vindex:0.5};
vdata2["M35"] = {vindex:0.5};
vdata2["M50"] = {vindex:0.5};
vdata2["M51"] = {vindex:0.5};
vdata2["M55"] = {vindex:0.5};
vdata2["M56"] = {vindex:0.5};
vdata2["M57"] = {vindex:0.5};
vdata2["M58"] = {vindex:0.5};
vdata2["N60"] = {vindex:0.5};
vdata2["N61"] = {vindex:0.5};
vdata2["N62"] = {vindex:0.5};
vdata2["N63"] = {vindex:0.5};
vdata2["N64"] = {vindex:0.5};
vdata2["N65"] = {vindex:0.5};
vdata2["N66"] = {vindex:0.5};
vdata2["N67"] = {vindex:0.5};
vdata2["N68"] = {vindex:0.5};
vdata2["N69"] = {vindex:0.5};
vdata2["N70"] = {vindex:0.5};
vdata2["N71"] = {vindex:0.5};
vdata2["N72"] = {vindex:0.5};
vdata2["N73"] = {vindex:0.5};
vdata2["N74"] = {vindex:0.5};
vdata2["T92"] = {vindex:0.5};
vdata2["T93"] = {vindex:0.5};
vdata2["T94"] = {vindex:0.5};
vdata2["T95"] = {vindex:0.5};
vdata2["T96"] = {vindex:0.5};
vdata2["T97"] = {vindex:0.5};
vdata2["T98"] = {vindex:0.5};

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

	var hours = getHours();
	$( "#time_i" ).val(hours);
	$( ".time_i_content .time"+hours.substring(0, 2) ).addClass('active');

	// wgs map
	map = L.map('mapid').setView([52.36, 4.95], 12);

	L.tileLayer('https://t1.data.amsterdam.nl/topo_wm_zw/{z}/{x}/{y}.png', {
		minZoom: 12,
		maxZoom: 16
	}).addTo(map);

	var dindexJsonUrl = dindex_api + getCurrentDate() + jsonCallback;
	// var dindexJsonUrl = 'data/dindex.json';
	console.log(dindexJsonUrl);

	var geoJsonUrl = 'https://map.data.amsterdam.nl/maps/gebieden?REQUEST=GetFeature&Typename=ms:buurtcombinatie&version=2.0.0&service=wfs&outputformat=geojson&srsname=epsg:4326';

	$.getJSON(dindexJsonUrl).done(function (dindexJson) {

		console.log(dindexJson);

		var calc_index = 0;
		var count_index = 0;

		$.each(dindexJson.results, function (key, value) {
			var buurtcode = this.vollcode;
			var $dataset = [];
			//$dataset["buurt"] = this.naam + '-' + buurtcode;
			$dataset["buurt"] = this.naam;
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
			geojson = L.geoJSON(geoJson, {style: style, onEachFeature: onEachFeature}).addTo(map);

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
	var today = '07-12-2017';

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
			$dataset["buurt"] = this.naam;
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

	var data2 = new Array;

	data2[0] = {time:"00", dindex:0.3};
	data2[1] = {time:"01", dindex:0.3};
	data2[2] = {time:"02", dindex:0.3};
	data2[3] = {time:"03", dindex:0.4};
	data2[4] = {time:"04", dindex:0.5};
	data2[5] = {time:"05", dindex:0.6};
	data2[6] = {time:"06", dindex:1};
	data2[7] = {time:"07", dindex:1};
	data2[8] = {time:"08", dindex:1};
	data2[9] = {time:"09", dindex:1};
	data2[10] = {time:"10", dindex:1};
	data2[11] = {time:"11", dindex:1};
	data2[12] = {time:"12", dindex:1};
	data2[13] = {time:"13", dindex:1};
	data2[14] = {time:"14", dindex:1};
	data2[15] = {time:"15", dindex:1};
	data2[16] = {time:"16", dindex:1};
	data2[17] = {time:"17", dindex:1};
	data2[18] = {time:"18", dindex:1};
	data2[19] = {time:"19", dindex:1};
	data2[20] = {time:"20", dindex:1};
	data2[21] = {time:"21", dindex:1};
	data2[22] = {time:"22", dindex:0.4};
	data2[23] = {time:"23", dindex:0.3};

	var hoursJsonUrl = dindex_hours_api+'&vollcode='+vollcode+'&timestamp='+ getCurrentDate() + jsonCallback;
	//var hoursJsonUrl = 'data/hours.json';
	console.log(hoursJsonUrl);

	$.getJSON(hoursJsonUrl).done(function(hoursJson) {
		console.log(hoursJson);
		var i = 0;
		$.each(hoursJson.results, function (key, value) {
			var buurtcode = this.vollcode;
			var $dataset = [];
			//$dataset["buurt"] = this.naam;
			// $dataset["dindex"] = this.drukte_index * 100 * data2[i].dindex;
			$dataset["dindex"] = this.drukte_index * 100;
			// console.log(data2[i].dindex);
			$dataset["time"] = this.timestamp.substr(11, 2);
			i++;
			data.push($dataset);
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

function initWeekGraph(vollcode)
{
	var data = new Array;

	var weekdays = new Array;
	weekdays[1] = 'Maandag';
	weekdays[2] = 'Dinsdag';
	weekdays[3] = 'Woensdag';
	weekdays[4] = 'Donderdag';
	weekdays[5] = 'Vrijdag';
	weekdays[6] = 'Zaterdag';
	weekdays[7] = 'Zondag';

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
	return $('.hotspots_content').clone();
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


























