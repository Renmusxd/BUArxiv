function validateForm() {
  let title = document.forms["entryform"]["title"].value;
  if (title === "") {
    alert("Title may not be empty");
    return false;
  }

  let authors = document.forms["entryform"]["authors"].value;
  if (authors === "") {
    alert("Authors may not be empty");
    return false;
  }
  return true;
}