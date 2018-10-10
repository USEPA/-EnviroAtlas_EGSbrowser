/*
	U.S. Environmental Protection Agency - Ecosystem Goods and Services (egs)
	
	script to render content from web service that returns JSON formatted data that navigates starting with Seven Enviroatlas Benefit Categories
	
	Hierarchy is 
	
	benefit_category - Benefit Category (Seven Broad Benefit Categories)
		ecosystem_type - Ecosystem Type
			contribution_pathway - Goods and Services (was Benefit Name)
				benefit_type - Benefit Type (Demander, Supplier, or Driver)
					data_layer - Data Layer
					
					
	A good complex example is 
	Clean & Plentiful Waters
		Rivers and Streams
			Materials
				Demander
				Supplier
				Driver

	Jimmy Bisese
	Tetra Tech, Inc.
	2018-March-29
	
*/
(function() {
	
	var page_title = 'Ecosystem Goods & Services';
	var site_title = 'Explore the Seven EnviroAtlas Benefit Categories';
	
	var ecosystem_goods_and_services_web_service = "/epa_egs-cgi/index.py";
	
	var images_directory = 'images/';
	
	var margin = {top: 20, right: 20, bottom: 30, left: 10};
	var svgWidth = 520;
	var barHeight = 22;
	var barWidth = 500; // widest is Biodiversity > Rivers and Streams > Experience > Supplier > Maximum modeled threatened and endangered vertebrate species - southwest

	var whiteColor = "#fff";
	var offWhiteColor = "#000";
	var grayColor = "#808080";
	var nodeMarginColor = '#c0c0c0'
	var pathLinkColor = '#9ecae1';
	
	var highLighted = true;
		
	// colors from Peter Cada April 24, 2017
	// Note: the highlight colors are overridden here - they were not really necessary, and the colors were to similar
	// The code is still there to 'highlight' selected elements
	var benefitCategoryColor = "rgba(10,75,116, 0.7)";
	var benefitCategoryColorHighlighted = benefitCategoryColor;// "rgba(10,75,116, 1)"

	var ecosystemColor = "rgba(14,85,130, 0.7)";
	var ecosystemColorHighlighted = ecosystemColor; // "rgba(14,85,130, 1)";
	
	var contributionPathwayColor = "rgba(25,122,187, 0.7)";
	var contributionPathwayColorHighlighted = contributionPathwayColor; // "rgba(25,122,187, 1)";
	
	// these are the benefit_type options
	var supplierColor = 'rgba(145,159,142, 0.7)';
	var supplierColorHighlighted = supplierColor; // 'rgba(145,159,142, 1)';
	var driverColor = 'rgba(177,142,141, 0.7)';
	var driverColorHighlighted = driverColor; // 'rgba(177,142,141, 1)';
	var demanderColor = 'rgba(156,168,208, 0.7)';
	var demanderColorHighlighted = demanderColor; // 'rgba(156,168,208, 1)';

	/*** set the order and text labels for each of the 3 Benefit Types ***/
	var benefit_typesMap = new Map([
		['Demander', { 'label': 'Demander of Ecosystem Good or Service'}],
		['Supplier', { 'label': 'Supplier of Ecosystem Good or Service'}],
		['Driver',	 { 'label': 'Drivers of Change'}],
	]);
	var benefit_types = [
		['Demander', 'Demander of Ecosystem Good or Service'],
		['Supplier', 'Supplier of Ecosystem Good or Service'],
		['Driver',	 'Drivers of Change']
	];
	/*** set the order and content of the Legend ***/
	var legend_data_levelsMap = new Map([
			['benefit_category', { 'short_title': 'Broad Benefit Category', 'title': 'Broad Benefit Category (7 options)', 'fill': whiteColor, 'indent': 1}],
			['ecosystem_type', { 'short_title': 'Ecosystem Type', 'title': 'Ecosystem Type (15 options)', 'indent': 10}],
			['contribution_pathway', { 'short_title': 'Contribution Pathway', 'title': 'Contribution Pathway (8 options)', 'indent': 20}],
			['benefit_typeD', { 'short_title': 'Benefit Type', 'title': 'Benefit Type: Demander', 'background-color': demanderColor, 'indent': 30}],
			['benefit_typeS', { 'title': 'Benefit Type: Supplier', 'background-color': supplierColor, 'indent': 30}],
			['benefit_typeDR', { 'title': 'Benefit Type: Driver', 'background-color': driverColor, 'indent': 30}],
			['data_layer', { 'title': 'Data Layer', 'background-color': driverColor, 'indent': 40}],
	]);
	var legend_data_levels = {
		'benefit_category': { 'short_title': 'Broad Benefit Category', 'title': 'Broad Benefit Category (7 options)', 'fill': whiteColor, 'indent': 1},
		'ecosystem_type': { 'short_title': 'Ecosystem Type', 'title': 'Ecosystem Type (15 options)', 'indent': 10},
		'contribution_pathway': { 'short_title': 'Contribution Pathway', 'title': 'Contribution Pathway (8 options)', 'indent': 20},
		'benefit_typeD': { 'short_title': 'Benefit Type', 'title': 'Benefit Type: Demander', 'background-color': demanderColor, 'indent': 30},
		'benefit_typeS': { 'title': 'Benefit Type: Supplier', 'background-color': supplierColor, 'indent': 30},
		'benefit_typeDR': { 'title': 'Benefit Type: Driver', 'background-color': driverColor, 'indent': 30},
		'data_layer': { 'title': 'Data Layer', 'background-color': driverColor, 'indent': 40},
	};
	/*** set the order and content of the images shown for each of the Seven Broad Benefit Categories ***/
	var benefit_categoriesMap = new Map([
			['Biodiversity', 				{ 'image': 'bio'}],
			['Clean Air', 					{ 'image': 'air'}],
			['Clean and Plentiful Waters', 	{ 'image': 'water'}],
			['Climate_Stabilization', 		{ 'image': 'clim'}],
			['Food_Fuel_and_Materials', 	{ 'image': 'food'}],
			['Natural Hazard Mitigation', 	{ 'image': 'haz'}],
			['Recreation', 					{ 'image': 'rec'}]
	]);
	var benefit_categories = {
		'Biodiversity': 'bio',
		'Clean Air': 'air',
		'Clean and Plentiful Waters': 'water',
		'Climate_Stabilization': 'clim',
		'Food_Fuel_and_Materials': 'food',
		'Natural Hazard Mitigation': 'haz',
		'Recreation': 					 'rec'
	};
	var i = 0;
	var duration = 400;
	var root;
	
	// set the page title and the title text displayed on the screen
	document.title = page_title;
	
	d3.select("#site-title").html(site_title);
	
	var tree = d3.layout.tree()
		.nodeSize([0, 20]);
	
	var diagonal = d3.svg.diagonal()
		.projection(function(d) { return [d.y, d.x]; });
	
	// Redraw the three panels based on the new size whenever the browser window is resized.
	function redraw(){
		var bodyHeight = $(document).height();
		var options = ['left', 'center', 'right'];
		for (var i in options)
		{
			$('#' + options[i] + '_panel').height(bodyHeight * .85);
		}
	}
	
	// call the redraw() function
	redraw();
	
	// set a listener for when the browser is resized
	window.addEventListener("resize", redraw);

	/*************
	 * 
	 *  set up the 3-columns (left_panel, center_panel, right_panel)
	 *  
	 *  Note: removed per directions 8/24/2018
	 * 
	 */
	d3.select("#left_panel")
		.attr("height", 1200)
	
	/*** this D3 layout can be found online searching for Collapsible Indented Tree ***/
	var svg = d3.select("#collapsible_indented_tree").append("svg")
		.attr("width", svgWidth)
		.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	
	d3.select("#center_panel")
		.attr("height", 1200)
		
	d3.select("#right_panel")
		.attr("height", 1200)
	
	/*** build the legend ***/
	
	var svg_legend = d3.select("#legend");
	
	/********
	 * 
	 * this is turned off per-directions of EPA staff.
	 */
	
	/*
	for (var key in legend_data_levels)
	{
		var values = legend_data_levels[key];
		svg_legend.append('div')
			.attr('class', 'legend_item')
			.style('color', values['fill'] || '#000')
			.style('background-color', values['background-color'] || fill_color({primary_key: key}))
			.style("margin-left", values['indent'] + "px")	
			.html('&nbsp;' + values['title']);
	}
	svg_legend.style("visibility", "visible");
	
	// version using Map() which failed in IE11
//	for ([key, value] of legend_data_levelsMap)
//	{
//		svg_legend.append('div')
//			.attr('class', 'legend_item')
//			.style('color', value['fill'] || '#000')
//			.style('background-color', value['background-color'] || fill_color({primary_key: key}))
//			.style("margin-left", value['indent'] + "px")	
//			.html('&nbsp;' + value['title']);
//	}
	*/
	
	
	/*
	 * 
	 * get the initial data from the service
	 *
	 */ 
	d3.json(data_url(), function(error, d) {
		
		if (error) throw error;
	
		d.x0 = 0;
		d.y0 = 0;
		update(root = d);
	});

	
	/**************
	 * 
	 * this builds up all the 'nodes' shown in the left-side Collapsible Indented Tree
	 * 
	 * Note: there is some extra code from an attempt to make the top-most nodes larger than their children.
	 * I could not get it working, but left in the code since it is a start. I tried to set the 'height' and 'y' values.
	 * 
	 */
	function update(source) {
	
		// Compute the flattened node list. TODO use d3.layout.hierarchy.
		var nodes = tree.nodes(root);

		var height = Math.max(500, nodes.length * barHeight + margin.top + margin.bottom);
	
		d3.select("svg").transition()
			.duration(duration)
			.attr("height", height);
	
		d3.select(self.frameElement).transition()
			.duration(duration)
			.style("height", height + "px");
	
		// Compute the "layout" space - y-axis.
		nodes.forEach(function(n, i) {
			if (n.primary_key == 'benefit_category')
				n.x = i * barHeight; // if you add * 3 it will still work in the y-axis. this only seems to affect y, not x
			else
				n.x = i * barHeight;
		});
	
		// Update the nodes…
		var node = svg.selectAll("g.node")
			.data(nodes, function(d) { return d.id || (d.id = ++i); });
	
		var nodeEnter = node.enter().append("g")
			.attr("class", "node")
			.attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
			.style("opacity", 1e-6);
	
		// Enter any new nodes at the parent's previous position.
		nodeEnter.append("rect")
			.attr("y", function(d){ 
					if (d.primary_key && d.primary_key == "benefit_category")
					{
						return -1 * ((barHeight) / 2);
					}
				else
					{
						return -barHeight / 2;
					}
			})
			.attr("height", function(d){ 
					if (d.primary_key && d.primary_key == "benefit_category")
					{
						return barHeight;
					}
				else
					{
						return barHeight;
					}
			})
			.attr("rx", 3) // radius
			.attr("ry", 3)
			.attr("width", function(d){ 
				if (d.primary_key && d.primary_key == "benefit_category")
				{
					return barWidth;
				}

				else if (d.primary_key && d.primary_key == "ecosystem_type")
				{
					return barWidth - ((barHeight) * 2) + 4;
				}
				else if (d.primary_key && d.primary_key == "contribution_pathway")
				{
					return barWidth - ((barHeight) * 3) + 6;
				}
				else if (d.primary_key && d.primary_key == "benefit_type")
				{
					return barWidth - ((barHeight) * 4) + 8;
				}				
				else if (d.primary_key && d.primary_key == "data_layer")
				{
					return barWidth - ((barHeight) * 5) + 10;
				}				
				else
				{
					return barWidth;
				}
			})
			.on("mouseover", handleMouseOver)
			.on("mouseout", handleMouseOut)
			.on("click", click);
		
		nodeEnter.append("text")
			.attr("vertical-align", "middle")
			.attr("fill", function(d){ 
				if (d.primary_key && d.primary_key == "benefit_category")
				{
					return whiteColor;
				}
				else
				{
					if (d.depth == 0)
					{
						return whiteColor;
					}
					else if (d.is_available && d.is_available == "False")
					{
						return grayColor; 
					}
					else
					{
						return offWhiteColor;
					}
				}
			})
			.attr("dy", 3.5)
			.attr("dx", function(d){ 
				// shift the text over if there is an image on this row
				if (d.primary_key && d.primary_key == "benefit_category")
				{
					return barHeight + 5
				}
				else
				{
					return 5;
				}
			})
			.text(function(d) { 
				return d.name
			});

		// add an image to each Benefit Category node
		nodeEnter.append("svg:image")
			.attr("xlink:href", function(d){ 
				if (d.primary_key && d.primary_key == "benefit_category")
				{
					return benefit_category_image(d.code, 1);
				}
				else
				{
					return '';
				}
			})
			.attr("width", barHeight)
			.attr("height", barHeight)
			.attr("x", 0)
			.attr("y", -barHeight / 2);
	
		nodeEnter.transition()
			.duration(duration)
			.attr("transform", function(d) { 
				// this prevents the Seven Broad Benefit Categories from indenting
				return "translate(" + d.y * (d.primary_key == "benefit_category" ? 0 : 1) + "," + d.x + ")"; 
			})
			.style("opacity", 1);
	
		node.transition()
			.duration(duration)
			.attr("transform", function(d) { 
				// this prevents the Seven Broad Benefit Categories from indenting
				return "translate(" + d.y * (d.primary_key == "benefit_category" ? 0 : 1) + "," + d.x + ")"; 
			})
			.style("opacity", 1)
			.select("rect")
			.style("fill", function(d) { return fill_color(d); })			
			.style("stroke", nodeMarginColor)
			.style("stroke-width", 1);

		// Transition exiting nodes to the parent's new position.
		node.exit().transition()
			.duration(duration)
			.attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
			.style("opacity", 1e-6)
			.remove();
	
		// Update the links (the curvy lines between nodes)…
		var link = svg.selectAll("path.link")
			.data(tree.links(nodes), function(d) { 
				if (d.target.depth > 1) // this prevents the links from the 'Seven ...' menu bar
				{
					return d.target.id; 
				}
				
			});
		
		// Enter any new links at the parent's previous position.
		link.enter().insert("path", "g")
			.attr("class", "link")
			.style('stroke', pathLinkColor)
			.attr("d", function(d) {
				var o = {x: source.x0, y: source.y0};
				return diagonal({source: o, target: o});
			})
			.transition()
			.duration(duration)
			.attr("d", diagonal);
	
		// Transition links to their new position.
		link.transition()
			.duration(duration)
			.attr("d", diagonal);
	
		// Transition exiting nodes to the parent's new position.
		link.exit().transition()
			.duration(duration)
			.attr("d", function(d) {
				var o = {x: source.x, y: source.y};
				return diagonal({source: o, target: o});
			})
			.remove();
	
		// store the old positions for transition.
		nodes.forEach(function(d) {
			d.x0 = d.x;
			d.y0 = d.y;
		});
		
	}
	
	/*************
	 * helper functions
	 * 
	 * 
	 */

	// build the URL used to get data from the data server
	// this relies on the hierarchy being intact - which it should be since the 
	// hierarchy is coming from the nodes
	function data_url(d)
	{
		var url = ecosystem_goods_and_services_web_service;
		if (d)
		{
			if(d.primary_key == 'data_layer')
			{
				url = url + '/?data_layer=' + d.code + '&benefit_type=' + d.parent.code + '&contribution_pathway=' + d.parent.parent.code + '&ecosystem_type=' + d.parent.parent.parent.code + '&benefit_category=' + d.parent.parent.parent.parent.code;
			}
			else if(d.primary_key == 'benefit_type')
			{
				url = url + '/?benefit_type=' + d.code + '&contribution_pathway=' + d.parent.code + '&ecosystem_type=' + d.parent.parent.code + '&benefit_category=' + d.parent.parent.parent.code;
			}			
			else if(d.primary_key == 'contribution_pathway')
			{
				url = url + '/?contribution_pathway=' + d.code + '&ecosystem_type=' + d.parent.code + '&benefit_category=' + d.parent.parent.code;
			}
			else if (d.primary_key == 'ecosystem_type')
			{
				url = url + '/?ecosystem_type=' + d.code + '&benefit_category=' + d.parent.code;
			}
			else if (d.primary_key == 'benefit_category')
			{
				url = url + '/?benefit_category=' + d.code;
			}
		}
		return url;
	}
	
	function format_header(name_tx, value_tx)
	{
		return '<strong>'+ name_tx + ':</strong> ' + value_tx;
	}

	// manage the images shown on the Seven Broad Benefit Categories
	function benefit_category_image(benefit_category_tx, has_children)
	{
		//var options = benefit_categoriesMap.get(benefit_category_tx); //TODO: fix Map issue
		var img_tx = benefit_categories[benefit_category_tx];
		var image = has_children ? img_tx + '.png' : img_tx + '_bw.png';
		return images_directory + image;
	}
	
	
	/**************
	 * 
	 * Action Functions
	 * 
	 * 
	 */
	
	/* hide all child nodes */
	function collapse(d) {
		if (d.children) {
			d._children = d.children;
			d._children.forEach(collapse);
			d.children = null;
		}
	}
	
	/* show all child nodes */
	function expand(d) {
		if (d._children) {
			d.children = d._children;
			d.children.forEach(expand);
			d._children = null;
		}
	}
	
	/*
	 * these are to highlight nodes that are being acted on.
	 * 
	 * Note: there is also a CSS directive '.node:hover  text{ font-weight: bold;}' 
	 * 	that causes the text to turn bold when there is a mouse-over event
	 * 
	 */
	function handleMouseOver(d, i) {  // Add interactivity

		// return if this link is not available - greyed out
		if (d.depth == 0 || (d.is_available && d.is_available == "False"))
		{
			return;
		}
		
		// Use D3 to select element, change color and size
		d3.select(this).transition().style("fill", function (e) { 
			return fill_color(e, highLighted);
		});

	}
	function handleMouseOut(d, i) {
		// Use D3 to select element, change color back to normal
		d3.select(this).transition().style("fill", function (e) { 
			return fill_color(e);
		});
	}
	
	// Toggle children on click.
	function click(d)
	{
		// return if this link is not available - greyed out
		if (d.depth == 0 || (d.is_available && d.is_available == "False"))
		{
			return;
		}
		
		// find all the nodes at the same 'level' as the one that was clicked.
		var nodes = svg.selectAll("g.node")
			.filter(function(j) { 
				if (j.primary_key && j.primary_key == d.primary_key)
				{
					return j; 
				}
			});
		// and use that list to turn the font back to unhighlighted
		nodes.forEach(function(n, i) {
			n.forEach(function(z, i) {
				if (z.children)
				{
					var text_child = z.children[1];
					d3.select(text_child)
						.classed('bold_text', false);
				}
			})
		});
		
		// highlight the clicked node by setting its class to a bold, larger font
		d3.select(this.nextSibling)
			.attr('class', 'bold_text');
//			.style('fill', fill_color(this.parentNode.__data__, highLighted)); // this will change the font to highlighted color

		// there are no children showing and no children hidden and there is a code, and there are no data_layer_details for the node.
		if ( ! d.children && ! d._children && d.code && ! d.data_layer_details)
		{
			var url = data_url(d);

			// this is useful for debugging
//			console.log(url);
			
			d3.json(url, function(json)
			{
				if (json)
				{
					if (json.children)
					{
						json.children.forEach(function(node)
						{
							if (node.name != d.name)
							{
								(d._children || (d._children = [])).push(node);
							}
						});
					}
					else
					{
						console.log('no json.children for url==' + url)
					}
					
					if (json.data_layer_details)
					{
						d.data_layer_details = json.data_layer_details;
					}
					if (json.literature)
					{
						d.literature = json.literature;
					}
				}
				else
				{
					console.log('no json for url==' + url)
				}
				
				toggle_result_divs(d)

				if (d.children)
				{
					d._children = d.children;
					d.children = null;
				}
				else
				{
					d.children = d._children;
					d._children = null;
				}
				
				// If the node has a parent, then collapse its other child nodes
				if (d.parent) {
					d.parent.children.forEach(function(element) {
						if (d !== element) {
							collapse(element);
						}
					});
				}

				update(d);
			});
		}
		else if (!d.children && d._children && d.code) // this is the 'open' action when the children have already been loaded
		{
			toggle_result_divs(d)
			
			//now display the children
			if (d.primary_key == 'contribution_pathway')
			{
				expand(d); // show all the children recursively
			}
			else
			{
				d.children = d._children;
				d._children = null;
			}

			// If the node has a parent, then collapse its other child nodes
			if (d.parent) {
				d.parent.children.forEach(function(element) {
					if (d !== element) {
						collapse(element);
					}
				});
			}
			
			update(d);
		}
		else // this is the 'close' action on a click
		{
			toggle_result_divs(d);
			
			if (d.children)
			{
				d._children = d.children;
				d.children = null;
			}
			else
			{
				d.children = d._children;
				d._children = null;
			}

			update(d);
			
			// unhighlight the clicked node by removing the bold_text class
			if (d.children)
			{
				d3.select(this.nextSibling)
					.classed('bold_text', false);
//					.style('fill', fill_color(this.parentNode.__data__)); // this will change the font to highlighted color
;
			}
		}
	}
	/*
	 * this toggles the divs - things in the center and right columns.
	 * 
	 */
	function toggle_result_divs(d)
	{
		if (d.primary_key == 'data_layer')
		{
			set_data_layer_info_div(d);
		}
		else if (d.primary_key == 'benefit_type')
		{
			set_data_layer_info_div(d, "hidden");
			set_benefit_type_info_div(d);
		}					
		else if (d.primary_key == 'contribution_pathway')
		{
			set_data_layer_info_div(d, "hidden");
			set_benefit_type_info_div(d, "hidden");
			set_contribution_pathway_info_div(d, false);
			set_ecosystem_type_info_div(d.parent, true); // close the two divs above this one
			set_benefit_category_info_div(d.parent.parent, true);
		}					
		else if (d.primary_key == 'ecosystem_type')
		{
			set_data_layer_info_div(d, "hidden");
			set_benefit_type_info_div(d, "hidden");
			set_contribution_pathway_info_div(d, "hidden");
			set_ecosystem_type_info_div(d, false);
			set_benefit_category_info_div(d.parent, true); // close the div above this one
		}
		else if (d.primary_key == 'benefit_category')
		{
			set_data_layer_info_div(d, "hidden");
			set_benefit_type_info_div(d, "hidden");
			set_contribution_pathway_info_div(d, "hidden");
			set_ecosystem_type_info_div(d, "hidden");
			set_benefit_category_info_div(d, false);
		}
	}


	/**************
	 * 
	 * div specific functions to set the content of each of the center panel division, or to hide the div
	 * 
	 */
	function set_benefit_category_info_div(d, close)
	{
		var div = d3.select("#benefit_category-info");
		var image = benefit_category_image(d.code, 1);
		var was_closed = true; // (current_display == 'block');
		//var header_lead_tx = 'TODO MAP ISSUE2'; //TODO: fix Map legend_data_levels.get('benefit_category')["short_title"];
		var header_lead_tx = legend_data_levels['benefit_category']["short_title"];
		
		var children = div.selectAll(function() { return this.childNodes; })[0];
		if (children && children[1] !== undefined)
		{
			var current_display = d3.select(children[1]).style('display');
			was_closed = (current_display == 'none');
		}
		
		var is_same = (div.indexOf(d.name) > -1);
		var banner_div = div.select("header_line");
		
		if (is_same == false) // prevent replacing content if it hasn't changed (if it is the same)
		{
			div.style("visibility", "visible")
				.style("background-color", fill_color(d))
				.style("color", whiteColor)
				.html('');
			
			div.append('div')
				.attr('class', 'header_line')
				.html('<img width=' + barHeight + ' height=' + barHeight + '= src=' + image + '>&nbsp;' 
						+ format_header(header_lead_tx, d.name));
			
			div.append('div')
				.attr('class', 'content')
				.html(d.extended_text);
			
			div.on("click", function(d, i) {
				var children = d3.select(this).selectAll(function() { return this.childNodes; })[0];
				var current_display = d3.select(children[1]).style('display');
				d3.select(children[0]).classed('closed', current_display == 'none' ? false : true);
				d3.select(children[1]).style('display', current_display == 'none' ? 'block' : 'none');
			});

		} 
		// this 'closes' this panel (it gets called when a deeper node is called and it refreshes this part)
		//IE debugging - this doesn't get entered in IE this.hasOwnProperty('close') && 
		if (typeof close !== undefined)
		{
			var children = div.selectAll(function() { return this.childNodes; })[0];
			var current_display = d3.select(children[1]).style('display');
			
			if (close == false && current_display == 'none')
			{
				d3.select(children[0]).classed("closed", false); // change the + to - (open to close)
				d3.select(children[1]).style('display', 'none');
			}
			else if (close == true && current_display == 'block')
			{
				d3.select(children[0]).classed("closed", true); // change the - to + (close to open)
				d3.select(children[1]).style('display', 'none');
			}
		}
		else if (was_closed)
		{
			d3.selectAll(children[0]).classed("closed", true); // change the - to + (close to open)
			d3.select(children[1]).style('display', 'none');
		}
	}	
	
	
	function set_ecosystem_type_info_div(d, close)
	{
		var div = d3.select("#ecosystem_type-info");
		var was_closed = (div[0][0].className.split(' ').indexOf('closed') > -1);
		var is_same = (div.indexOf(d.name) > -1);
		var banner_div = div.select("header_line");
		//var header_lead_tx = 'TODO MAP ISSUE2'; //TODO: fix Map legend_data_levels.get('ecosystem_type')["short_title"];
		var header_lead_tx = legend_data_levels['ecosystem_type']["short_title"];
		
		if (close && close == 'hidden')
		{
			div.style("visibility", "hidden");
			return;
		}
		
		if (is_same == false) // prevent replacing content if it hasn't changed (if it is the same)
		{
			div.style("visibility", "visible")
				.style("background-color", fill_color(d))
//				.style("color", whiteColor)
				.html('');
			
			div.append('div')
				.attr('class', 'header_line')
				.html(format_header(header_lead_tx, d.name));
			
			div.append('div')
				.attr('class', 'content')
				.html(d.extended_text);
			
			div.on("click", function(d, i) {
				var children = d3.select(this).selectAll(function() { return this.childNodes; })[0];
				var current_display = d3.select(children[1]).style('display');
				d3.select(children[0]).classed('closed', current_display == 'none' ? false : true);
				d3.select(children[1]).style('display', current_display == 'none' ? 'block' : 'none');
			});

		} 
		// this 'closes' this panel (it gets called when a deeper node is called and it refreshes this part)
		if (typeof close !== undefined)
		{
			var children = div.selectAll(function() { return this.childNodes; })[0];
			var current_display = d3.select(children[1]).style('display');
			
			if (close == false && current_display == 'none')
			{
				d3.select(children[0]).classed("closed", false); // change the + to - (open to close)
				d3.select(children[1]).style('display', 'none');
			}
			else if (close == true && current_display == 'block')
			{
				d3.select(children[0]).classed("closed", true); // change the - to + (close to open)
				d3.select(children[1]).style('display', 'none');
			}
		}
	}	
	
	function set_contribution_pathway_info_div(d, close)
	{
		var div = d3.select("#contribution_pathway-info");
		var was_closed = (div[0][0].className.split(' ').indexOf('closed') > -1);
		var is_same = (div.indexOf(d.name) > -1);
		var banner_div = div.select("header_line");
		//var header_lead_tx = 'TODO MAP ISSUE2'; //TODO: fix Map legend_data_levels.get('contribution_pathway')["short_title"];
		var header_lead_tx = legend_data_levels['contribution_pathway']["short_title"];
		
		var lit = undefined;
		
		if (close && close == 'hidden')
		{
			div.style("visibility", "hidden");
			return;
		}
		
		if (is_same == false) // prevent replacing content if it hasn't changed (if it is the same)
		{
			div.style("visibility", "visible")
				.style("background-color", fill_color(d))
				.html('');
			
			div.append('div')
				.attr('class', 'header_line')
				.html(format_header(header_lead_tx, d.name));
			
			div.append('div')
				.attr('class', 'content')
				.html(d.extended_text);

			if (d.literature && d.literature[0] && d.literature[0].data && d.literature[0].data[d.code])
			{
				lit = d.literature[0].data[d.code];
			}
			
			div.append('div')
				.attr('class', 'literature_review')
				.html('<br><strong><u>Literature Review</u></strong><br>');
				
			var non_blank = false;
			
			benefit_types.forEach(function(arr)
			{
				key = arr[0];
				value = arr[1];
				if (lit && lit[key.toLowerCase()])
				{
					var item_text = lit[key.toLowerCase()];
					if (item_text != 'NA' && item_text != 'no literature review available at this time')
					{
						div.append('div')
							.attr('class', 'literature_indent')
							.html('<strong><u>' + value + ':</u></strong> ' + item_text );
						non_blank = true;
					}
				}
			});
			
/* Map() version
			for ([key, value] of benefit_types)
			{
				if (lit && lit[key.toLowerCase()])
				{
					var item_text = lit[key.toLowerCase()];
					if (item_text != 'NA' && item_text != 'no literature review available at this time')
					{
						div.append('div')
							.attr('class', 'literature_indent')
							.html('<strong><u>' + value['label'] + ':</u></strong> ' + item_text );
						non_blank = true;
					}
				}
				
			}
*/
			if (non_blank == false)
			{
				div.append('div')
					.attr('class', 'literature_indent')
					.html('<span>There is no literature for this Benefit Catetegory/Ecosystem Type/Contribution Pathway</span>');
			}
			
			div.on("click", function(d, i) {
				var children = d3.select(this).selectAll(function() { return this.childNodes; })[0];
				var current_display = d3.select(children[1]).style('display');
				d3.select(children[0]).classed('closed', current_display == 'none' ? false : true);
				for (var i = 1; i < children.length; i++) { 
					d3.select(children[i]).style('display', current_display == 'none' ? 'block' : 'none');
				}
			});

		} 
		
		// this 'closes' this panel (it gets called when a deeper node is called and it refreshes this part)
		if (typeof close !== undefined)
		{
			var children = div.selectAll(function() { return this.childNodes; })[0];
			var current_display = d3.select(children[1]).style('display');
			
			if (close == false && current_display == 'none')
			{
				d3.select(children[0]).classed("closed", false); // change the + to - (open to close)
				d3.select(children[1]).style('display', 'none');
				d3.select(children[2]).style('display', 'none');
			}
			else if (close == true && current_display == 'block')
			{
				d3.select(children[0]).classed("closed", true); // change the - to + (close to open)
				d3.select(children[1]).style('display', 'none');
				d3.select(children[2]).style('display', 'none');
			}
		}
	}	

	
	function set_benefit_type_info_div(d, close)
	{
		var div = d3.select("#benefit_type-info");
		var was_closed = (div[0][0].className.split(' ').indexOf('closed') > -1);
		var is_same = (div.indexOf(d.name) > -1);
		var banner_div = div.select("header_line");
		//var header_lead_tx = 'TODO MAP ISSUE2'; //TODO: fix Map legend_data_levels.get('benefit_typeD')["short_title"];
		var header_lead_tx = legend_data_levels['benefit_typeD']["short_title"];
		if (close && close == 'hidden')
		{
			div.style("visibility", "hidden");
			return;
		}
		
		if (is_same == false) // prevent replacing content if it hasn't changed (if it is the same)
		{
			div.style("visibility", "visible")
				.style("background-color", fill_color(d))
				.html('');
			
			div.append('div')
				.attr('class', 'header_line')
				.html(format_header(header_lead_tx, d.name));
			
			div.append('div')
				.attr('class', 'content')
				.html(d.extended_text);
			
			div.on("click", function(d, i) {
				var children = d3.select(this).selectAll(function() { return this.childNodes; })[0];
				var current_display = d3.select(children[1]).style('display');
				d3.select(children[0]).classed('closed', current_display == 'none' ? false : true);
				d3.select(children[1]).style('display', current_display == 'none' ? 'block' : 'none');
			});
		} 
		// this 'closes' this panel (it gets called when a deeper node is called and it refreshes this part)
		if (typeof close !== undefined)
		{
			var children = div.selectAll(function() { return this.childNodes; })[0];
			var current_display = d3.select(children[1]).style('display');
			
			if (close == false && current_display == 'none')
			{
				d3.select(children[0]).classed("closed", false); // change the + to - (open to close)
				d3.select(children[1]).style('display', 'none');
			}
			else if (close == true && current_display == 'block')
			{
				d3.select(children[0]).classed("closed", true); // change the - to + (close to open)
				d3.select(children[1]).style('display', 'none');
			}
		}
	}	

	function set_data_layer_info_div(d, hidden_flag)
	{
		var div = d3.select("#data_layer-info");
		//var header_lead_tx = 'TODO MAP ISSUE'; //TODO: fix Map issue legend_data_levels.get('data_layer')["title"];
		var header_lead_tx = legend_data_levels['data_layer']["title"];
		
		if (hidden_flag && hidden_flag == 'hidden')
		{
			div.style("visibility", "hidden");
			return;
		}
		div.style("visibility", "visible")
			.style("background-color", fill_color(d.parent))
			.html(format_header(header_lead_tx, ''));

		var intro_tx = '"#layer_name#" is important because it represents a #benefit_type#';
		switch(d.parent.code.toLowerCase()) {
			case 'driver': intro_tx += ' of change impacting the way "#ecosystem_type#" can provide ' +
				'Ecosystem Good or Services via the following contribution pathways, impacting'; break;
			case 'supplier': intro_tx += ' of one (or more) ' + 
				'Ecosystem Good or Services derived from "#ecosystem_type#" via the following contribution pathways, providing'; break;
			case 'demander': intro_tx += ' of "#ecosystem_type#" that provides one (or more) ' + 
				'Ecosystem Good or Services via the following contribution pathways and'; break;
		}
		
		intro_tx = intro_tx.replace('#layer_name#', '<strong><u>' + d.code + '</u></strong>' );
		intro_tx = intro_tx.replace('#benefit_type#', '<strong><u>' + d.parent.code + '</u></strong>' );
		intro_tx = intro_tx.replace('#ecosystem_type#', '<strong><u>' + d.parent.parent.parent.name + '</u></strong>');
		intro_tx += ' the highlighted EnviroAtlas Broad Benefit Category(ies):';
		
		div.append("span").html(intro_tx);
		
		var benefit_name_table = div.append("table")
		var thead = benefit_name_table.append("thead")
		var tr = thead.append("tr")
		tr.append("th").text("Contribution Pathways")
		tr.append("th").text("Seven Broad Benefit Categories")
		
		d.data_layer_details.forEach(function(node)
		{
			var benefit_name_table_tr = benefit_name_table.append("tr");
			benefit_name_table_tr.append("td")
				.text(node.name)
				.style("width", "62%")
				.style("word-wrap", "break-word");
			
			var image_html = '';
			if (node && node.children.length > 0)
			{
				node.children.forEach(function(child)
					{
						var image = benefit_category_image(child.code, child.is_available);
						image_html += '<image src="' + image + '" width="20" height="20">';
					});
			}
			else if (node)
			{
				for (var key in benefit_categories)
				{
					var value = benefit_categories[key];
					var image = benefit_category_image(key, false);
					image_html += '<image src="' + image + '" width="20" height="20">';
				}
//Map() version				
//				for ([key, value] of benefit_categories)
//				{
//					var image = benefit_category_image(key, false);
//					image_html += '<image src="' + image + '" width="20" height="20">';
//				}
				
			}
			benefit_name_table_tr.append('td')
				.style("width", "38%")
				.style("vertical-align", "middle")
				.style("text-align", "center")
				.html(image_html);
		});
		
		div.append("span")
			.html("Additional Resources")
			.append("ol")
			.append("li").text("Fact Sheet (hotlinks)")
			.append("li").text("Data Download")
			.append("li").text("Interactive Map")
			.append("li").text("Dynamic Data Matrix");
	}
	

	/*************
	 * 
	 *  Color specific functions
	 * 
	 */
	function fill_color(d, highlighted) 
	{
		var color = 'red'; // error color
		
		if (! d.primary_key)
		{
			color = benefitCategoryColorHighlighted;
		}
		else if (d.primary_key == 'benefit_category')
		{
			color = highlighted ? benefitCategoryColorHighlighted : benefitCategoryColor;
		}
		else if (d.primary_key == 'ecosystem_type')
		{
			color = highlighted ? ecosystemColorHighlighted : ecosystemColor;
		}
		else if (d.primary_key == 'contribution_pathway')
		{
			color = highlighted ? contributionPathwayColorHighlighted : contributionPathwayColor;
		}
		else if (d.primary_key == 'benefit_type' || d.primary_key == 'data_layer')
		{
			if (d.primary_key == 'data_layer')
			{
				d = d.parent;
			}
			switch (d.code.toLowerCase()) {
				case 'driver': color = highlighted ? driverColorHighlighted : driverColor; break; 
				case 'supplier': color = highlighted ? supplierColorHighlighted : supplierColor; break; 
				case 'demander': color = highlighted ? demanderColorHighlighted : demanderColor; break; 
			}
		}		

		return color;
	}
	
})();