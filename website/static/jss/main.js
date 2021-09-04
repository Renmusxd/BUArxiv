d3.json('feed',  function(error, data) {
    var div = d3.select('.list');
    div.selectAll('div')
        .data(data)
        .enter()
        .append('div')
        .attr('class', 'image-txt-container')
        .style('outline', '1px solid black')
        .style('padding', '5px 5px 5px 5px')
        .html(function(d) {
            var img = ""
            if (d['image_url'] != null) {
                img = "<img src=\"" + d['image_url'] + "\" alt=\"\" />";
            }

            return img + "</div>" +
                 "<div style='padding: 5px 5px 5px 5px'>" +
                 "<a href=\"" + d['url'] + "\" style=\"color:black\"><h3>" + d['title'] + "</h3></a>" +
                 "<i>" + d['authors'] + "</i>" +
                 "<p>" + d['summary'] + "</p>" +
                 "</div>"
        })
});