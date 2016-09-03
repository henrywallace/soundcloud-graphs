var width = 1200,
    height = 600

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

var force = d3.layout.force()
    .gravity(0.10)
    .linkDistance(150)
    .linkStrength(0.1)
    .charge(-1000)
    .size([width, height]);

var padding = 1,
    radius = 10;

function collide(node) {
    var r = node.radius + 20,
	nx1 = node.x - r,
	nx2 = node.x + r,
	ny1 = node.y - r,
	ny2 = node.y + r;
    return function(quad, x1, y1, x2, y2) {
	if (quad.point && (quad.point !== node)) {
	    var x = node.x - quad.point.x,
		y = node.y - quad.point.y,
		l = Math.sqrt(x * x + y * y),
		r = node.radius + quad.point.radius;
	    if (l < r) {
		l = (l - r) / l * .5;
		node.x -= x *= l;
		node.y -= y *= l;
		quad.point.x += x;
		quad.point.y += y;
	    }
	}
	return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
    };
}

function sigmoid(t) { with (Math) { return 1 / (1 + exp(-2*t)); } }

d3.json("graph.json", function(error, json) {
    if (error) throw error;
    
    force
        .nodes(json.nodes)
        .links(json.links)
        .start();
    
    var link = svg.selectAll(".link")
        .data(json.links)
        .enter().append("line")
        .attr("class", "link")
        .style("stroke-opacity", function(d) { return d.weight/3; })
        .style("stroke-width", 3)
	.style("stroke", "gray")
        // .linkStrength(2);

    
    var node = svg.selectAll(".node")
        .data(json.nodes)
        .enter().append("g")
        .attr("class", "node")
        .call(force.drag);
    
    // node.append("circle")
    // 	.attr("r", 20)
    //     .style("fill", "gray"),
    //     .style("stroke", "black")
    //     .style("stroke-width", 3)
    //     .append("svg:image")
    //     .append("xlink:href", function(d) {return d.image})
	
    node.append("image")
        .attr("xlink:href", function(d) {
            return d.image
        })
        .attr("x", -8)
        .attr("y", -8)
        .attr("width", 50)
        .attr("height", 50);
        // .style("opacity", function(d) { return d.weight/4 });
    
    node.append("text")
        // .attr("dx", 25)
        .attr("dy", "-1em")
        .text(function(d) {
            return d.name
        });
    
    force.on("tick", function() {
        link.attr("x1", function(d) {
            return d.source.x;
        })
            .attr("y1", function(d) {
               return d.source.y;
            })
            .attr("x2", function(d) {
                return d.target.x;
            })
            .attr("y2", function(d) {
                return d.target.y;
            });
	
        node.attr("transform", function(d) {
            return "translate(" + d.x + "," + d.y + ")";
        });
    });
});
