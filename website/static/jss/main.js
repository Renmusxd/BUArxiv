d3.json('feed/20',  function(error, data) {
    var div = d3.select('.list');
    div.selectAll('div')
        .data(data)
        .enter()
        .append('div')
        .attr('class', 'list-entry')
        .style('outline', '1px solid black')
        .style('padding', '5px 5px 5px 5px')
        .html(function(d) {
            var img = "";
            if (d['image_url'] != null) {
                img = "<img src=\"" + d['image_url'] + "\" alt=\"\" class=\"listimg\" />";
            }

            var display_summary = '';
            if (d['summary'] != null) {
                display_summary = d['summary'];
            }

            var journal_html = '';
            if (d['journal_ref'] != null) {
                journal_html = '<br><b>' + d['journal_ref'] + '</b>'
            }

            var tagstr = "";
            if (d['tags'] != null) {
                var tags = [...new Set(d['tags'].split(',').map(function(tag) {
                    return tag.split('.')[0].trim();
                }))].sort();
                tagstr = tags.map(function(tag) {
                    return '<div class="tagdiv-entry">' + tag.trim() + '</div>';
                }).join('');
            }

            return img + "</div>" +
                 "<div style='padding: 5px 5px 5px 5px; flex-grow: 10;'>" +
                 "<a href=\"" + d['url'] + "\" style=\"color:black\"><h3>" + d['title'] + "</h3></a>" +
                 "<i>" + d['authors'] + "</i>" +
                 journal_html +
                 "<p>" + display_summary + "</p>" +
                "<div class=\"tagdiv\">" + tagstr + "</div>"
                 "</div>"
        });

    if (typeof renderMathInElement !== 'undefined') {
        renderMathInElement(document.body, {
            // customised options
            // • auto-render specific keys, e.g.:
            delimiters: [
                {left: '$$', right: '$$', display: true},
                {left: '$', right: '$', display: false},
                {left: '\\(', right: '\\)', display: false},
                {left: '\\[', right: '\\]', display: true}
            ],
            // • rendering keys, e.g.:
            throwOnError: false
        });
    }
});