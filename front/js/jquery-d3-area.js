(function ($) {
	$.fn.areaGraph = function (data) {
		this.each(function () {
			var graph = {};

			graph.container = $(this);
			graph.data = data;
			graph.time = 24000;
			graph.currentHour = getTimeInt();
			graph.hours = 24;

			// set the dimensions and margins of the graph
			graph.margin = {top: 0, right: 0, bottom: 20, left: 0};
			graph.width = graph.container.width() - graph.margin.left - graph.margin.right;
			if(graph.width > 750)
			{
				graph.width = graph.width - 16;
			}
			graph.height = graph.container.height() - graph.margin.top - graph.margin.bottom;

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
					var text = (d < 10) ? "0"+ d : d;
					if(text==00 || text==24)
					{
						text='';
					}
					return text;
				} ).ticks(graph.hours+1, ",f"))
				.selectAll("text")
				.style("text-anchor", "middle")
				.attr("dx", "0")
				.attr("dy", ".15em");

			graph.lineGroupCurrent = graph.svg.append("g")
				.attr("transform", 'translate(' + Math.round(graph.currentHour * graph.width/graph.hours) + ',0)')
				.attr("class", "line-group-current");


			graph.currentline = graph.lineGroupCurrent.append("line")
				.attr("class", "currentline")
				.attr("x1",'0')
				.attr("x2",'0')
				.attr("y1",'0')
				.attr("y2",graph.height)
				.attr("stroke-dasharray",'5, 5')
				.attr("style",'stroke:rgba(219, 50, 42, 0.8);stroke-width:3');

			graph.lineGroup = graph.svg.append("g")
				.attr("class", "line-group")
				.attr("id", "line-group")
				.attr('state','play')
				.attr('width','20px')
				// .attr("mask",'url(#cut-middle-line)')
				.attr("transform", 'translate(' + Math.round(graph.currentHour * graph.width/graph.hours) + ',0)')
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
					d3.select(this).attr("time", d3.event.x * graph.hours/graph.width );
					dragAnimation();
				}
			}

			function dragended() {
				d3.select(this).classed("active", false);
			}





			// graph.svg.append("text")
			// 	.attr("x", '10px')
			// 	.attr('y','100%')
			// 	.attr("dy", "-30px")
			// 	.attr("text-anchor", "start")
			// 	.attr("fill",'#fff')
			// 	.attr("font-size",'12px')
			// 	.text('Rustig');
			//
			// graph.svg.append("text")
			// 	.attr("x", '10px')
			// 	.attr('y','0')
			// 	.attr("dy", "20px")
			// 	.attr("text-anchor", "start")
			// 	.attr("fill",'#fff')
			// 	.attr("font-size",'12px')
			// 	.text('Druk');

			//add realtime
			graph.realtime_bar = graph.svg.append("rect");


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

				graph.realtime_bar.attr("height",0);
				if(realtime>0)
				{


					var y = Math.round(graph.height - (realtime*100));
					var height =  Math.round(realtime * graph.height);

					graph.realtime_bar
						.attr("height", height )
						.attr('width', '20px')
						.attr('y', y)
						.attr('x', -10)
						.attr("transform", 'translate(' + Math.round(graph.currentHour * graph.width/graph.hours) + ',0)')
						// .attr('rx', 5)
						// .attr('ry', 5)
						.attr("style", "stroke-width:5;")
						.attr("stroke-dasharray", "20,"+((2*height)+20))
						.attr("stroke", getColorBucket(height/100))
						.attr("fill", "rgba(126,126,126,0.7)")
						.attr("class", "realtime_bar");
				}

				setTimeout(function(){graph.data = newData},1001);

			}

			graph.updateTime = function(){
				// set new time
				graph.currentHour = getTimeInt();

				// update time indicator
				graph.lineGroupCurrent.attr("transform", 'translate(' + Math.round(graph.currentHour * graph.width/graph.hours) + ',0)');
			}

			graph.setToTime = function(){
				//stop
				graph.stop();
				// set new time
				graph.currentHour = getTimeInt();

				// update time indicator
				setTimeout(function(){
					graph.lineGroup.attr("transform", 'translate(' + Math.round(graph.currentHour * graph.width/graph.hours) + ',0)')
						.attr('time',graph.currentHour);
				},100);

			}

			graph.startCount = function(){

				repeat();
				graph.play.attr('style', 'display:none;');
				graph.pause.attr('style', 'display:inherit;');

				function repeat() {



					var time = graph.time;
					var elapsedTime = graph.lineGroup.attr("time");

					if(elapsedTime > 0 )
					{
						time = graph.time - (graph.time * (elapsedTime/24));
					}

					// start hotspots animation
					startAnimation();

					// console.log(time);
					// console.log(elapsedTime);

					graph.lineGroup
						.transition()
						.ease(d3.easeLinear)
						.duration(time)
						.attr("transform", "translate("+ graph.width +", 0)")
						.attr("time",24)
						.transition()
						.duration(0)
						.attr("time",0)
						.attr("transform", "translate(0, 0)")
						.on("end", repeat);

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
