function addHeader() {
    $(function () {
        $("#header").append('<link rel="stylesheet" href="header/header.css">');
        $("#header").append($("<div>").load("header/header.html"));
    });
}

function removeHeader() {
    $(function () {
        $("#header").empty();
    });
}

function setPage(page, css = null) {
    $(function () {
        $("#current_page").empty();
        if (css != null) {
            $("#current_page").append(css)
        }
        $("#current_page").append($("<div>").load(page));
    });
}