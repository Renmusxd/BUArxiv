function img_src_from_data(d) {
    if (d['image_url'] != null && d['image_url'] !== "") {
        return d['image_url'];
    }
    return "";
}

function textdiv_html_from_data(d) {
    var display_summary = '';
    if (d['summary'] != null && d['summary'] !== "") {
        display_summary = d['summary'];
    }

    var journal_html = '';
    if (d['journal_ref'] != null) {
      journal_html = '<br><b>' + d['journal_ref'] + '</b>'
    } else {
      journal_html = '<br><b>arXiv:' + d['id'] + "</b>"
    }

    var tagstr = "";
    if (d['tags'] != null && d['tags'] !== "") {
        var tags = [...new Set(d['tags'].split(',').map(function (tag) {
            return tag.split('.')[0].trim();
        }))].sort();
        tagstr = tags.map(function (tag) {
            return '<div class="tagdiv-entry">' + tag.trim() + '</div>';
        }).join('');
    }
    var time = d['timestamp'].split(' ').slice(0, 4).join(' ');

    var anchor_prefix = "";
    var anchor_suffix = "";
    if (d['url'] != null && d['url'] !== "") {
        anchor_prefix = "<a href=\"" + d['url'] + "\">";
        anchor_suffix = "</a>";
    }

    return anchor_prefix + "<h3>" + d['title'] + "</h3>" + anchor_suffix +
        "<i>" + d['authors'] + "</i>" +
        journal_html +
        "<p>" + display_summary + "</p>" +
        "<div class=\"tagdiv\">" + time + "</div>";
}

function html_from_data(d) {
    let imgsrc = img_src_from_data(d);
    var img = "";
    if (imgsrc) {
        let alttext = "Image for entry " + d['id'];
        img = "<img src=\"" + imgsrc + "\" alt=\"" + alttext + "\" class=\"listimg\" />";
    }

    let textdiv = textdiv_html_from_data(d);
    return img + "<div class=\"textdiv\">" + textdiv + "</div>"
}

function populate_all() {
    // Check for queryparams like ?only_published=True
    const wurl = window.location.search;
    var wurl_split = wurl.split('?');
    var queryString = (wurl_split.length === 2) ? wurl.split('?')[1] : '';
    if (queryString !== '') {
        queryString = "?" + queryString;
    }

    d3.json('feed/24' + queryString, function (error, data) {
        var div = d3.select('.list');
        div.selectAll('div')
            .data(data)
            .enter()
            .append('div')
            .attr('class', 'list-entry')
            .html(html_from_data);

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
}