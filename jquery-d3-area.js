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
			if(graph.width > 360)
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
				.y(function(d) { return y(d.y); });

			// define area
			graph.area = d3.area()
				.x(function(d) { return x(d.x); })
				.y0(y(0))
				.y1(function(d) { return y(d.y); });
			//.curve(d3.curveBasis); // d3.curveNatural , d3.curveLinear


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
			graph.svg.append("path")
				.datum(graph.data)
				.attr("class", "area")
				.attr("d", graph.area);

			graph.svg.append("path")
				.datum(graph.data)
				.attr("class", "area-line")
				.attr("d", graph.topline);

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
				// .attr("mask",'url(#cut-middle-line)')
				.attr("transform", 'translate(' + Math.round(graph.currentHour * graph.width/graph.hours) + ',0)')
				.attr("time", graph.currentHour)
				.call(d3.drag()
					.on("start", dragstarted)
					.on("drag", dragged)
					.on("end", dragended));

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

			graph.line = graph.lineGroup.append("line")
				.attr("class", "nowline")
				.attr("x1",'0')
				.attr("x2",'0')
				.attr("y1",'0')
				.attr("y2",graph.height)
				.attr("style",'stroke:rgb(255,255,255);stroke-width:16');



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

				console.log(newData);

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

					var hours = getHourDigit();

					graph.realtime_bar
						.attr("height", (realtime * graph.height))
						.attr('width', '20px')
						.attr('y', graph.height - (realtime*100))
						.attr('x', (100/graph.hours*hours)+'%')
						.attr('rx', 5)
						.attr('ry', 5)
						.attr("stroke", "#4a4a4a")
						.attr("fill", "#ffffff")
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
					graph.lineGroup
						.attr('state','pause')
						.transition()
						.duration( 0 );
				}
				else
				{
					console.log('play');
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

				console.log('pause');
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
