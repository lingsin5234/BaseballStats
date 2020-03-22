// this script helps select the radio buttons
// and SUBMIT the form on the runJobs.html page

// Ajax Request protection
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

// once document is in ready state
//$(document).ready(function(){
var form = document.getElementById("extract-form");
console.log("#extract-form exists");
console.log(form);
form.addEventListener("submit", myFunction);
document.getElementById("extract-form").addEventListener("submit", event => {console.log("works?")});
function myFunction(e) {
    console.log("Start");
    /*var data = new FormData(form);
    var output = "Hello";
    for (const entry of data) {
        output = output + entry[0] + "=" + entry[1];
    };
    window.alert(output);*/
    e.preventDefault();
};
//});

