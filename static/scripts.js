function test2() {
    alert("Test2 executed!")
}


function get_status() {
    currentText = document.getElementById('userUpdate').innerText
    fetch('/status')
        .then(function (response) {
            return response.json(); // But parse it as JSON this time
        })
        .then(function (json) {
            // console.log('GET response as JSON:');
            // console.log(json); // Here’s our JSON object
            // alert(JSON.stringify(json.status))
            // console.log(JSON.stringify(json.status))
            console.log(JSON.stringify(json.status))
            console.log("tHIS IS CURRENT TEXT:" + currentText)
            document.getElementById('userUpdate').innerText = JSON.stringify(json.status)
    
        })
        setTimeout(get_status, 5000);
    }

// function get_status() {
//     fetch('/status')
//         .then(function (response) {
//             return response.json()
//         })
//         .then(function (json) {
//             return json.status
//         })
//         .then(function (status) {
//             document.getElementById("status").innerHTML = status
//         })
//         // setTimeout(get_status, 1000);
//     }
