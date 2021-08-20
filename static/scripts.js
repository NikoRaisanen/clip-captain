function get_status() {
    currentText = document.getElementById('userUpdate').innerText
    fetch('/status')
        .then(function (response) {
            return response.json(); // But parse it as JSON this time
        })
        .then(function (json) {
            console.log(JSON.stringify(json.status))
            console.log("tHIS IS CURRENT TEXT:" + currentText)
            document.getElementById('userUpdate').innerText = JSON.stringify(json.status)
    
        })
        setTimeout(get_status, 5000);
    }

var slider = document.getElementById("myRange");
var output = document.getElementById("numClips");
output.innerHTML = "Number of clips to use: <strong>" + String(slider.value) + "</strong>";

// Dynamically update slider value
slider.oninput = function() {
    output.innerHTML = "Number of clips to use: <strong>" + String(this.value) + "</strong>"
}