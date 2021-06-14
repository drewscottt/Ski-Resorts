/*
 * File: trips.js
 * Author: Drew Scott
 * Description: Contains functions for correctly displaying the trips table (i.e. adding event listeners to buttons
 * 	to change the display, loading in the people on a trip, etc.)
 */

// global id prefixes
var editButtonIdPrefix = "trip_button";
var addPersonButtonIdPrefix = "add_person";
var cancelButtonIdPrefix = "cancel_button";
var tripRowIdPrefix = "trip_row";
var removePersonButtonIdPrefix = "remove_person";
var personDivIdPrefix = "person";

/*
 * On the load of the page, add the eventListeners to the buttons and load the people
 */
window.onload = function() {
	var i = 1;

        var editButtonElement = document.getElementById(editButtonIdPrefix + i);
	var addPersonButtonElement, cancelButtonElement;
        while (editButtonElement) {
                editButtonElement.addEventListener('click', showEditRow);
		
		addPersonButtonElement = document.getElementById(addPersonButtonIdPrefix + i);
		addPersonButtonElement.addEventListener('click', addPerson);

		cancelButtonElement = document.getElementById(cancelButtonIdPrefix + i);
		cancelButtonElement.addEventListener('click', cancel);

		loadPeople(i);

                i++;
                editButtonElement = document.getElementById(editButtonIdPrefix + i);
        }
	
	var locsSelectElement = document.getElementById("locsSelect");
	locsSelectElement.addEventListener('change', initMap);
}

/*
 * Puts all of the people already saved to a trip into the text forms, so that the user can see/edit them
 */
function loadPeople(tripNum) {
	// get the div that the loaded people info is hidden in
	var people_defaults = "people_defaults";
	var defaultPeopleDiv = document.getElementById(people_defaults + tripNum);

	// get each person's info from the div, and set the form fields for them
	var i = 0;
	var personInfo = defaultPeopleDiv.querySelector(".default_person" + i);
	while (personInfo) {
		// add the name and age form fields
		addPersonById(addPersonButtonIdPrefix + tripNum);

		// get the name and age form fields
		var peopleDiv = document.getElementById("people" + tripNum);
		var newPersonDiv = peopleDiv.lastChild;
		var nameField = newPersonDiv.querySelector(".person_name");
		var ageField = newPersonDiv.querySelector(".person_age");

		// set the values of the name and age form fields
		nameField.setAttribute("value", personInfo.querySelector(".name").innerHTML);
		ageField.setAttribute("value", personInfo.querySelector(".age").innerHTML);

		// get the next person from the div
		i++;
		personInfo = defaultPeopleDiv.querySelector(".default_person" + i);
	}
}

/*
 * Hides the edit row of the event target
 */
function cancel(event) {
	var targetId = event.currentTarget.id;

	var tripNum = targetId.substring(cancelButtonIdPrefix.length);

	var tripRowElement = document.getElementById(tripRowIdPrefix + tripNum);

	tripRowElement.style.display = "none";
}

/*
 * Adds name and age fields in the edit row of the event target
 */
function addPerson(event) {
	addPersonById(event.currentTarget.id);
}

/*
 * Adds name and age fields in the edit row of the input target.
 * The input targetId must be the id for an addPerson button.
 */
function addPersonById(targetId) {
	// get the number at the end of the id
	var tripNum = targetId.substring(addPersonButtonIdPrefix.length);

	// get the parent div that holds the button and the people
	var parentElement = document.getElementById("people" + tripNum);

	// get the number for this person
	var nameStart = personDivIdPrefix + tripNum;
	var nameNum = 1;
	var lastChild = parentElement.lastChild;
	if (lastChild.hasAttribute("class") && lastChild.getAttribute("class") === personDivIdPrefix){
		nameNum = parseInt(lastChild.id.substring(nameStart.length + 1)) + 1;
	}

	// create the new person div, and then add the name and age elements to it

	var personDiv = document.createElement("DIV");
	personDiv.setAttribute("class", personDivIdPrefix);
	personDiv.setAttribute("id", nameStart + "-" + nameNum);

	var nameText = document.createElement("P");
	nameText.innerHTML = "Name:";
	personDiv.appendChild(nameText);
	
	var nameField = document.createElement("INPUT");
	nameField.setAttribute("name", personDivIdPrefix + nameNum);
	nameField.setAttribute("class", "person_name");
	personDiv.appendChild(nameField);

	var ageText = document.createElement("P");
	ageText.innerHTML = "Age:";
	personDiv.appendChild(ageText);

	var ageField = document.createElement("INPUT");
	ageField.setAttribute("name", "age" + nameNum);
	ageField.setAttribute("class", "person_age");
	personDiv.appendChild(ageField);

	var removeButton = document.createElement("BUTTON");
	removeButton.setAttribute("type", "button");
	removeButton.setAttribute("id", removePersonButtonIdPrefix + tripNum + "-" + nameNum);
	removeButton.setAttribute("class", "remove_person_button");
	removeButton.innerText = "Remove Person";
	removeButton.addEventListener("click", removePerson);
	personDiv.appendChild(removeButton);

	// add the new person div to the people div for this trip
	parentElement.appendChild(personDiv);
}

function removePerson(event) {
	var personDiv = document.getElementById(event.currentTarget.id).parentElement;
	var tripNum = personDiv.id.substring(personDivIdPrefix.length, personDiv.id.indexOf("-"));
	var personNum = personDiv.id.substring(personDiv.id.indexOf("-") + 1);

	var nextPersonDiv = personDiv.nextSibling;

	// remove the person's div
	personDiv.remove();

	// update the id's so that there isn't a gap in numbers
	while (nextPersonDiv) {
		nextPersonDiv.id = personDivIdPrefix + tripNum + "-" + personNum;
		nextPersonDiv.querySelector(".person_name").name = "person" + personNum;
		nextPersonDiv.querySelector(".person_age").name = "age" + personNum;
		nextPersonDiv.querySelector(".remove_person_button").id = removePersonButtonIdPrefix + tripNum + "-" + personNum;

		personNum = (parseInt(personNum) + 1).toString();
		nextPersonDiv = nextPersonDiv.nextSibling;
	}
}

/*
 * Shows the edit row for the of the event target
 */
function showEditRow(event) {
	var targetId = event.currentTarget.id;

	var tripNum = targetId.substring(editButtonIdPrefix.length);
	
	var tripRowElement = document.getElementById(tripRowIdPrefix + tripNum);
	tripRowElement.style.display = "table-row";
}
