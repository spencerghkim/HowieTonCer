

console.log("Hello, EECS485")


function comparePWs() {
    var pass1 = document.getElementById("pass1").value;
    var pass2 = document.getElementById("pass2").value;
    var ok = true;
    if (pass1 != pass2) {
        alert("Passwords Do not match");
        // document.getElementById("pass1").style.borderColor = "#E34234";
        // document.getElementById("pass2").style.borderColor = "#E34234";
        ok = false;
    }
    else {
        alert("Passwords Match!!!");
    }
    return ok;
}

function checkPass()
{
    //Store the password field objects into variables ...
    var pass1 = document.getElementById('password1');
    var pass2 = document.getElementById('password2');
    //Store the Confimation Message Object ...
    var message = document.getElementById('confirmMessage');
    //Set the colors we will be using ...
    var goodColor = "#66cc66";
    var badColor = "#ff6666";
    //Compare the values in the password field 
    //and the confirmation field
    var signupbtn = document.getElementById('signupbtn');
    // var signup = document.getElementById('signup');
    if(pass1.value == pass2.value){
        //The passwords match. 
        //Set the color to the good color and inform
        //the user that they have entered the correct password 
        pass2.style.backgroundColor = goodColor;
        message.style.color = goodColor;
        signupbtn.disabled=false;
        message.innerHTML = "Passwords Match!"
        // signup.disabled=false;
    }else{
        //The passwords do not match.
        //Set the color to the bad color and
        //notify the user.
        pass2.style.backgroundColor = badColor;
        message.style.color = badColor;
        signupbtn.disabled=true;
        message.innerHTML = "Passwords Do Not Match!"
    }
}  