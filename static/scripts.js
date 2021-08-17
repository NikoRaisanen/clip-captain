function test2() {
    alert("Test2 executed!")
}

function get_status() {
    fetch('/status')
        .then(function (response) {
            return response.json(); // But parse it as JSON this time
        })
        .then(function (json) {
            // console.log('GET response as JSON:');
            console.log(json); // Here’s our JSON object
        })
        // setTimeout(get_status, 1000);
    }
