(function ($) {
	$.fn.areaGraph = function (data) {
		this.each(function () {
			var graph = {};

			graph.container = $(this);
			graph.data = data;
			graph.time = 24000;

			// set the dimensions and margins of the graph
			graph.margin = {top: 0, right: 0, bottom: 20, left: 0};
			graph.width = graph.container.width() - graph.margin.left - graph.margin.right;
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
				.on('click', function(){ graph.stopResumeCount(); })
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
				.call(d3.axisBottom(x).tickFormat( function(d) { return (d < 10) ? "0"+ d : d; } ).ticks(25, ",f"))
				.selectAll("text")
				.style("text-anchor", "middle")
				.attr("dx", "0")
				.attr("dy", ".15em");

			graph.lineGroup = graph.svg.append("g")
				.attr("class", "line-group")
				.attr('state','play')
				.attr("time",0);

			graph.line = graph.lineGroup.append("line")
				.attr("class", "nowline")
				.attr("x1",'0')
				.attr("x2",'0')
				.attr("y1",'0')
				.attr("y2",graph.height)
				.attr("style",'stroke:rgb(255,255,255);stroke-width:2');

			graph.svg.append("text")
				.attr("x", '10px')
				.attr('y','100%')
				.attr("dy", "-30px")
				.attr("text-anchor", "start")
				.attr("fill",'#fff')
				.attr("font-size",'12px')
				.text('Rustig');

			graph.svg.append("text")
				.attr("x", '10px')
				.attr('y','0')
				.attr("dy", "20px")
				.attr("text-anchor", "start")
				.attr("fill",'#fff')
				.attr("font-size",'12px')
				.text('Druk');


			graph.update = function(newData){

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
			}

			graph.startCount = function(){

				repeat();

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
				// stop hotspots animation
				stopAnimation();

				console.log('pause');
				graph.lineGroup
					.attr('state','pause')
					.transition()
					.duration( 0 );


			}




			// export update function
			graph.container[0].update = graph.update;
			graph.container[0].startCount = graph.startCount;
			graph.container[0].stopResumeCount = graph.stopResumeCount;
			graph.container[0].stop = graph.stop;
		});
		// return
		return this;
	}
}(jQuery));
