function handle_preview(e) {
    let paths = document.location.pathname.split('/');
    let id = paths[paths.length-1];

    const file = document.getElementById("image").files[0]
    if (e.target != null && e.target.name === "image") {
        if (file) {
            document.getElementById("image_url").value = "static/img/thumbnails/" + id + ".png";
        }
    }
    let image_url = document.getElementById("image_url").value;
    if (image_url.startsWith("static/")) {
        image_url = "../" + image_url;
    }
    if (file) {
        image_url = URL.createObjectURL(file);
        console.log("Found file: "+image_url);
        console.log(e.target);
    }

    let data = {
        "id": id,
        "title": document.getElementById("titlearea").value,
        "authors": document.getElementById("authorsarea").value,
        "journal_ref": document.getElementById("journalarea").value,
        "doi": document.getElementById("doiarea").value,
        "url": document.getElementById("post_url").value,
        "timestamp": document.getElementById("publish").value,
        "summary": document.getElementById("summaryarea").value,
        "abstract": document.getElementById("abstractarea").value,
        "image_url": image_url,
        "tags": document.getElementById("tags").value,
        "unstructured": document.getElementById("unstructuredarea").value,
        "hidden": document.getElementById("hidden").value,
    };

    let preview = document.getElementById("entry-preview");
    let imgsrc_field = document.getElementById("image_url");
    let imgfile_field = document.getElementById("image");
    let imgsrc = img_src_from_data(data);
    let [img] = preview.getElementsByTagName("IMG");
    if (imgsrc && !img) {
        // Rebuild whole thing.
        preview.innerHTML = html_from_data(data);
    } else if (imgsrc && img && (e.target === imgfile_field || e.target === imgsrc_field)) {
        img.src = imgsrc;
    }

    let [textdiv] = document.getElementsByClassName("textdiv");
    if (!textdiv) {
        // Rebuild whole thing.
        preview.innerHTML = html_from_data(data);
    } else {
        textdiv.innerHTML = textdiv_html_from_data(data);
    }
}

function setup_preview(formid) {
    let form = document.getElementById(formid);
    for (let i = 0; i < form.children.length; i++) {
      let child = form.children[i];
      if (child.tagName === "INPUT" ||  child.tagName === "TEXTAREA") {
           child.addEventListener("input", handle_preview);
           child.addEventListener("propertyChange", handle_preview);
       }
    }
    handle_preview({});
}