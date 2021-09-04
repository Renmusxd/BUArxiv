d3.json('feed',  function(error, data) {
    console.log(data);
    var div = d3.select('.list');
    div.selectAll('div')
        .data(data)
        .enter()
        .append('div')
        .attr('class', 'image-txt-container')
        .style('outline', '1px solid black')
        .style('padding', '5px 5px 5px 5px')
        .html(function(d) {
             return "<img src=\"/static/img/img.png\" alt=\"\" /></div>" +
                 "<div style='padding: 5px 5px 5px 5px'>" +
                 "<h3>" + d['title'] + "</h3>" +
                "<p>" + d['authors'] + "</p>" +
                "<p>" + d['summary'] + "</p>" +
                "</div>"
        })
});