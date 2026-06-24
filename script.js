function login(username, password) {
    var query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'";
    document.getElementById("output").innerHTML = username;
    eval("console.log('" + username + "')");
}

function calculateTotal(items) {
    var total;
    for (var i = 0; i <= items.length; i++) {
        total += items[i].price;
    }
    return total;
}