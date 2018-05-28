(function ($) {
	$.fn.areaGraph = function (data,realtime) {
		this.each(function () {
			var graph = {};

			graph.container = $(this);
			graph.data = data;
			graph.time = 24000;
			graph.realtime = realtime;
			graph.hours = 24;

			// set the dimensions and margins of the graph
			graph.margin = {top: 20, right: 0, bottom: 20, left: 0};
			graph.width = graph.container.width() - graph.margin.left - graph.margin.right;
			if(graph.width > 750)
			{
				graph.width = graph.width - 16;
			}
			graph.height = graph.container.height() - graph.margin.top - graph.margin.bottom;

			graph.unit = graph.width/graph.hours;

			graph.setCurrentState = function()
			{
				graph.currentHour = getTimeInt();


				if(graph.currentHour >5 && graph.currentHour <24)
				{
					graph.currentPoint = Math.round(graph.currentHour * graph.unit - (5 * graph.unit));
				}
				else {
					graph.currentPoint = Math.round(graph.currentHour * graph.unit + (19 * graph.unit)) ;
				}
			}

			// console.log(graph.width);
			// console.log(graph.height);
			// console.log(graph.unit);

			graph.setCurrentState();


			// set the ranges
			var x = d3.scaleLinear().rangeRound([0, graph.width]);
			var y = d3.scaleLinear().range([graph.height, 0]);

			// define line
			graph.topline = d3.line()
				.x(function(d) { return x(d.x); })
				.y(function(d) { return y(d.y); })
				.curve(d3.curveBasis);

			// define area
			graph.area = d3.area()
				.x(function(d) { return x(d.x); })
				.y0(y(0))
				.y1(function(d) { return y(d.y); })
				.curve(d3.curveBasis); // d3.curveNatural , d3.curveLinear


			// append the svg obgect to the body of the page
			graph.svg = d3.select(graph.container[0]).append("svg")
				.on('click', function(){
					//graph.stopResumeCount();
				})
				.attr("width", '100%')
				.attr("height", graph.height +  graph.margin.top +  graph.margin.bottom)
				.attr("class", "indexgraph")
				.append("g")
				.attr("transform",
					"translate(" +  graph.margin.left + "," +  graph.margin.top + ")");


			// Scale the range of the data
			x.domain(d3.extent(graph.data, function (d) {
				return d.x;
			}));
			y.domain([0, 100]);

			// add background lines
			var lineCount = 0;
			do {

				graph.svg.append("line")
					.attr("class", "nowline")
					.attr("x1", lineCount*graph.unit)
					.attr("x2", lineCount*graph.unit)
					.attr("y1",'0')
					.attr("y2",graph.height)
					.attr("style",'stroke:rgba(150,150,150,0.5);stroke-width:1');
				lineCount++
			}
			while(lineCount<=24)



			// Add the valueline path.

			graph.svg.append("rect")
				.attr("x", "0")
				.attr("y", "0")
				.attr("width", "100%")
				.attr("height", graph.height)
				.attr("fill", "url(#gradient)")
				.attr("clip-path", "url(#graphclip)");

			graph.defs = graph.svg.append("defs");
			graph.clipPath = graph.svg.append("clipPath").attr("id", "graphclip");

			graph.clipPath.append("path")
				.datum(graph.data)
				.attr("class", "area")
				.attr("d", graph.area);

			// graph.svg.append("path")
			// 	.datum(graph.data)
			// 	.attr("class", "area-line")
			// 	.attr("d", graph.topline);

			// Add the X Axis
			graph.svg.append("g")
				.attr("class", "axis")
				.attr("transform", "translate(0," + graph.height + ")")
				.call(d3.axisBottom(x).tickFormat( function(d) {
					if(d==0 || d==24)
					{
						return '';
					}
					d=d+5;
					if(d>23)
					{
						d=d-24;
					}
					var text = (d < 10) ? "0"+ d : d;
					return text;
				} ).ticks(graph.hours+1, ",f"))
				.selectAll("text")
				.style("text-anchor", "middle")
				.attr("dx", "0")
				.attr("dy", ".15em");

			graph.lineGroupCurrent = graph.svg.append("g")
				.attr("transform", 'translate(' + graph.currentPoint + ',0)')
				.attr("class", "line-group-current");


			graph.currentline = graph.lineGroupCurrent.append("line")
				.attr("class", "currentline")
				.attr("x1",'0')
				.attr("x2",'0')
				.attr("y1",'0')
				.attr("y2",graph.height)
				.attr("stroke-dasharray",'5, 5')
				.attr("style",'stroke:rgba(255, 255, 255, 0.8);stroke-width:3');

			graph.lineGroup = graph.svg.append("g")
				.attr("class", "line-group")
				.attr("id", "line-group")
				.attr('state','play')
				.attr('width','20px')
				// .attr("mask",'url(#cut-middle-line)')
				.attr("transform", 'translate(' + graph.currentPoint + ',0)')
				.attr("time", graph.currentHour)
				.call(d3.drag()
					.on("start", dragstarted)
					.on("drag", dragged)
					.on("end", dragended));

			graph.line = graph.lineGroup.append("rect")
				.attr("x",'-10')
				.attr("y",'0')
				.attr("width",'20')
				.attr("height",graph.height)
				.attr("style",'fill:rgba(255,255,255,0.2);stroke-width:0');

			graph.line = graph.lineGroup.append("line")
				.attr("class", "nowline")
				.attr("x1",'0')
				.attr("x2",'0')
				.attr("y1",'0')
				.attr("y2",graph.height)
				.attr("style",'stroke:rgba(255,255,255,0.8);stroke-width:3');

			graph.controlGroup = graph.svg.append("g")
				.attr("transform", 'translate(' + 0 + ',0)')
				.attr("class", "control-group");

			graph.pause = graph.controlGroup.append("image")
				.on('click', function(){
					graph.stop();
				})
				.attr("xlink:href","images/pause.svg")
				.attr("width", 18)
				.attr("height", 18)
				.attr("x", graph.width - 30 )
				.attr("class", 'graph-pause');

			graph.play = graph.controlGroup.append("image")
				.on('click', function(){
					graph.startCount();
				})
				.attr("xlink:href","images/play.svg")
				.attr("width", 18)
				.attr("height", 18)
				.attr("x", graph.width - 30 )
				.attr("style", 'display:none;')
				.attr("class", 'graph-play');

			function dragstarted() {
				graph.stop();
				d3.select(this).classed("active", true);
			}

			function dragged() {
				if(graph.width>d3.event.x && d3.event.x>=0) {
					d3.select(this).attr("transform", 'translate(' + d3.event.x + ',0)');
					if(d3.event.x < 19*graph.unit)
					{
						var dragTime = d3.event.x * graph.hours/graph.width + 5;
					}
					else
					{
						var dragTime = d3.event.x * graph.hours/graph.width - 19;
					}

					d3.select(this).attr("time", dragTime );
					dragAnimation();
				}
			}

			function dragended() {
				d3.select(this).classed("active", false);
			}



			graph.unsetRealtime = function() {
				graph.realtime_bar.attr("height",0);
				graph.realtime_bar_top.remove();
				// graph.realtime_bar_text.remove();
			}

			graph.setRealtime = function(){
				var bar_height =  Math.round(graph.realtime * graph.height);
				var bar_y =  graph.height - bar_height;

				graph.realtime_bar
					.attr("height", bar_height+2 )
					.attr('width', '20px')
					.attr('y', bar_y-2)
					.attr('x', -10)
					.attr("transform", 'translate(' + graph.currentPoint + ',0)')
					.attr('rx', 2)
					.attr('ry', 2)
					.attr("fill", 'rgba(66,66,66,0.6)')
					.attr("class", "realtime_bar");

				graph.realtime_bar_top = graph.svg.append("rect")
					.attr("height", bar_height)
					.attr('width', '16px')
					.attr('y', bar_y)
					.attr('x', -8)
					.attr("transform", 'translate(' + graph.currentPoint + ',0)')
					// .attr('rx', 5)
					// .attr('ry', 5)
					.attr("fill", getColor(graph.realtime))
					.attr("class", "realtime_bar_top");

				// graph.realtime_bar_text = graph.svg.append("text")
				// 	.attr("transform", 'translate(' + (graph.currentPoint-10) + ','+ (bar_y  - 4)+')')
				// 	.attr("fill", "#ffffff")
				// 	.attr("class", "realtime_bar_text")
				// 	.text(Math.round(graph.realtime*100));
			}

			//add realtime
			graph.realtime_bar = graph.svg.append("rect");
			if(graph.realtime>0)
			{
				graph.setRealtime();
			}


			graph.update = function(newData,realtime){

				graph.svg.selectAll('path.area')
					.datum(graph.data)
					.transition()
					.duration(1000)
					.attrTween('d', function() {
						var interpolator = d3.interpolateArray( graph.data, newData );
						return function( t ) {
							var show = interpolator( t );
							return graph.area( interpolator( t ) );
						}
					});

				graph.svg.selectAll('path.area-line')
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


				graph.unsetRealtime();
				if(realtime>0)
				{
					graph.realtime = realtime;
					graph.setRealtime();
				}

				setTimeout(function(){graph.data = newData},1001);

			}

			graph.updateTime = function(){

				// set new time
				graph.setCurrentState();

				// update time indicator
				graph.lineGroupCurrent.attr("transform", 'translate(' + graph.currentPoint + ',0)');
			}

			graph.setToTime = function(){
				//stop
				graph.stop();
				// set new time
				graph.setCurrentState();

				// update time indicator
				setTimeout(function(){
					graph.lineGroup.attr("transform", 'translate(' + graph.currentPoint + ',0)')
						.attr('time',graph.currentHour);
				},100);

			}

			graph.startCount = function(){

				repeat();
				graph.play.attr('style', 'display:none;');
				graph.pause.attr('style', 'display:inherit;');

				function repeat() {

					var elapsedTime = graph.lineGroup.attr("time");

					// start hotspots animation
					startAnimation();

					if(elapsedTime >= 5 && elapsedTime < 24)
					{
						var duration_day1 =  24000 - (graph.lineGroup.attr("time") * 1000);
						var duration_day2 =  5000;

						graph.lineGroup
							.transition()
							.ease(d3.easeLinear)
							.duration(duration_day1)
							.attr("transform", "translate("+ ((graph.width / 24) * 19) +", 0)")
							.attr("time",23)
							.transition()
							.duration(0)
							.attr("time",0)
							.attr("day",2)
							.transition()
							.duration(duration_day2)
							.attr("transform", "translate("+ graph.width +", 0)")
							.attr("time",5)
							.transition()
							.duration(0)
							.attr("day",1)
							.attr("transform", "translate(0, 0)")
							.on("end", repeat);

					}
					else
					{
						var duration_day1 = 19000;
						var duration_day2 = 5000 - (graph.lineGroup.attr("time") * 1000);

						graph.lineGroup
							.transition()
							.ease(d3.easeLinear)
							.attr("time",0)
							.attr("day",2)
							.transition()
							.duration(duration_day2)
							.attr("transform", "translate("+ graph.width +", 0)")
							.attr("time",5)
							.transition()
							.duration(0)
							.attr("day",1)
							.attr("transform", "translate(0, 0)")
							.on("end", repeat);
					}
				};
			}

			graph.stopResumeCount = function(){
				if(graph.lineGroup.attr('state') == 'play')
				{
					// stop hotspots animation
					stopAnimation();

					console.log('pause');
					if(debug) { console.log('pause') };
					graph.lineGroup
						.attr('state','pause')
						.transition()
						.duration( 0 );
				}
				else
				{
					if(debug) { console.log('play') };
					graph.lineGroup
						.attr('state','play');

					graph.startCount();
				}

			}
			graph.stop = function(){

				graph.pause.attr('style', 'display:none;');
				graph.play.attr('style', 'display:inherit;');

				// stop hotspots animation
				stopAnimation();

				if(debug) { console.log('pause') };
				graph.lineGroup
					.attr('state','pause')
					.transition()
					.duration( 0 );
			}

			// update time indicator every x seconds
			setInterval(function () {
				graph.updateTime();
			}, 60000);

			// export update function
			graph.container[0].update = graph.update;
			graph.container[0].updateTime = graph.updateTime;
			graph.container[0].setToTime = graph.setToTime;
			graph.container[0].startCount = graph.startCount;
			graph.container[0].stopResumeCount = graph.stopResumeCount;
			graph.container[0].stop = graph.stop;
		});
		// return
		return this;
	}
}(jQuery));
