/**
 * File: user.js
 * Author: Drew Scott
 * Description: Contains user sign up/login functions
 */

function signUp() {
	console.log("Sign up");

	var signUpBox = document.getElementById("signup_box");
	signUpBox.style.display = "block";

	var loginBox = document.getElementById("login_box");
	loginBox.style.display = "none";
}

function login() {
	console.log("Login");
	
	var loginBox = document.getElementById("login_box");
	loginBox.style.display = "block";
	
	var signUpBox = document.getElementById("signup_box");
	signUpBox.style.display = "none";
}

function cancelUser() {
	var loginBox = document.getElementById("login_box");
	loginBox.style.display = "none";
	
	var signUpBox = document.getElementById("signup_box");
	signUpBox.style.display = "none";
	
}
