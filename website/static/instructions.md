# Prepublication Feed
[https://physics.bu.edu/cmt-arxiv](https://physics.bu.edu/cmt-arxiv) hosts a feed of articles scraped nightly from arXiv, authored by BU physics department faculty. Currently the author search is limited to the CMT group, though this can easily be expanded in the future if desired.

The index page mentioned above displays the articles, however there is also an API for fetching json objects instead: `https://physics.bu.edu/cmt-arxiv/feed/<n>-<m>` This will fetch the entries for the nth through mth most recent additions to arxiv, sorted by initial prepublication date. Omitting the `<n>-` fills in a default value of 0 and pulls the m most recent entries. `https://physics.bu.edu/cmt-arxiv/feed/<m>`

JSON entries appear as follows:

```
[
  {
    "abstract": "...", // not currently used
    "authors": "John A. Doe, Jane B. Doe", // comma separated list
    "autoupdate": false, // Deprecated, see "unstructured"
    "doi": null, // or a doi id, will be used instead of url if present.
    "id": "1234.5678", // arxiv id
    "image_url": "static/img/1234.5678.png", // image if uploaded
    "journal_ref": null, // or journal reference
    "summary": "This paper rocks.", // A short summary to be displayed
    "tags": "...", // comma separated list, used for filtering
    "timestamp": "Thu, 31 Jan 1970 00:00:00 GMT", // arxiv upload time
    "title": "A Great Paper",
    "unstructured": "{\"autoupdates\": [\"doi\", \"journal\"]}", // advanced settings
    "url": "http://arxiv.org/abs/1234.5678" // url, not necessarily arxiv
  },
  ...
]
```

You can also retrieve papers from the last `<d>` days: `https://physics.bu.edu/cmt-arxiv/last/<d>`

## List of query parameters:

Query parameters may be used to further filter the feed. 
For example to restrict to only published papers one may add the `only_published=True` query parameter, like so: [https://physics.bu.edu/cmt-arxiv/feed/30?only_published=True](https://physics.bu.edu/cmt-arxiv/feed/30?only_published=True) 

The full list is presented below:

| Parameter        | Values     | Operation                                  |
|------------------|------------|--------------------------------------------|
| `only_published`   | True/False | `"journal_ref"` must be filled/empty       |
| `authors_includes` | string     | `"authors"` must include subtring          |
| `authors_excludes` | string     | `"authors"` must not include subtring      |
| `tags_includes`    | string     | `"tags"` must include substring            |
| `tags_excludes`    | string     | `"tags"` must not include substring        |
| `journal_includes` | string     | `"journal_ref"` must include substring     |
| `journal_excludes` | string     | `"journal_ref"` must not include substring |

The `tags_*` parameters offer a large amount of control over the feed.
Tags are added based off the author, author list, and arXiv category.
For authors with multiple entries in the author list (such as with/without middle initial), an author tag with their BUID may be the best way to filter:
`tags_includes=author_tags:<id>`

# How to Add/Edit
New entries are scraped nightly from arXiv, if the paper has not been seen before a new entry is created and some fields are filled out. Notable the `summary` and `image_url` will be left blank. To edit these fields you may visit `https://physics.bu.edu/cmt-arxiv/edit/<id>` where <id> is the arXiv id. If you want to find your paper among the most recently scraped papers you may visit [https://physics.bu.edu/cmt-arxiv/edit](https://physics.bu.edu/cmt-arxiv/edit) directly then click on your paper's title.

## Adding an Image
You can add an image to your paper's entry by either directly editing the **Image URL** field on the edit page to point towards a preexisting image, or by uploading an image in the Image field where it says *Choose File*. Images are displayed at at maximum resolution of 128x128.

## Adding a Summary
Summaries appear on the board below the author list and journal, they should remain short, between 1 or 2 sentences.

## Adding a whole paper
Some papers may not appear on arXiv and will therefore not have entries made automatically, if you would still like your paper to appear you may visit [https://physics.bu.edu/cmt-arxiv/new](https://physics.bu.edu/cmt-arxiv/new) to make a new entry with a randomly created id, or `https://physics.bu.edu/cmt-arxiv/new/<id>` with a handpicked `id`, it is not allowed to clobber an existing id. All fields will start blank and it will be up to you to fill them out manually.