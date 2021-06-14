/*
 * File: map.js
 * Author: Drew Scott
 * Description: Uses the Google Maps API to add all of the searched for ski results to the map
 */

/*
 * getLocs(locsToDisplay) -- returns a 2D array, where each subarray contains info about a location
 * the subarrays look like: [name:string, latitude:float, longitude:float]
 * this location info is found from the document elements with ids like: name<num>, lat<num>, lng<num>
 * where they can either have a prefix "search" or "trips" depending on what locations the user wants to display
 */
function getLocs(locsToDisplay) {
	if (locsToDisplay === "none") return [];

	locs = [];
	
	var latStr = locsToDisplay + "_lat";
	var lngStr = locsToDisplay + "_lng";
	var nameStr = locsToDisplay + "_name";

	var count = 1;
	
	var latEl = document.getElementById(latStr + count);
	var lat, lng, name;
	var curLoc = [];
	while (latEl) {
		// get all relevant data for this location (name, lat, lng)
		lat = latEl.innerHTML;
		lng = document.getElementById(lngStr + count.toString()).innerHTML;
		name = document.getElementById(nameStr + count.toString()).innerHTML;
		
		// add this location to locs list
		curLoc.push(name);
		curLoc.push(parseFloat(lat));
		curLoc.push(parseFloat(lng));

		locs.push(curLoc);

		// prep for next loop
		curLoc = [];
		count++;
		latEl = document.getElementById(latStr + count.toString());
	}

	return locs;
}

/*
 * findCenter(locs) -- finds the average of the lats/lngs in locs, and returns a loc object with those averages
 * locs is formatted as getLocs creates locs
 */
function findCenter(locs) {
	var length = locs.length;
	var latSum = 0;
	var lngSum = 0;

	for (var i = 0; i < length; i++) {
		latSum += locs[i][1];
		lngSum += locs[i][2];
	}

	var latAvg = latSum / length;
	var lngAvg = lngSum / length;

	var center = {lat: latAvg, lng: lngAvg };

	return center;
}

/*
 * findExtremes(locs) -- returns an array of size 2 with location objects, the first is the location of the highest lat/lng
 * and the second is the location of the smallest lat/lng (i.e. these two points create a diagonal for a box which all point lie
 * inside)
 */
function findExtremes(locs) {
	var length = locs.length;

	var maxLat = locs[0][1];
	var minLat = locs[0][1];
	
	var maxLng = locs[0][2];
	var minLng = locs[0][2];

	var curLat, curLng;
	for (var i = 1; i < length; i++) {
		curLat = locs[i][1];
		if (curLat > maxLat) maxLat = curLat;
		if (curLat < minLat) minLat = curLat;

		curLng = locs[i][2];
		if (curLng > maxLng) maxLng = curLng;
		if (curLng < minLng) minLng = curLng;
	}

	var maxLoc = {lat: maxLat, lng: maxLng };
	var minLoc = {lat: minLat, lng: minLng };

	var extremes = [maxLoc, minLoc];

	return extremes;
}

/*
 * findDistance(locs) -- returns the distances between to locations objects, using Pythagorean Theorem
 */
function findDistance(locs) {
	var latsDist = locs[0]['lat'] - locs[1]['lat'];
	var lngsDist = locs[0]['lng'] - locs[1]['lng'];

	var dist = Math.sqrt((latsDist * latsDist) + (lngsDist + lngsDist));

	return dist;
}

/*
 * initMap() -- creates the map using Google Maps API
 */
function initMap() {
	// determine where we get locations from (either search or trips)
	var locsToDisplay = document.getElementById("locsSelect").value;

	// create array of location info
	var locs = getLocs(locsToDisplay);

	// if there are no locs, empty out map div and return (i.e. display nothing)
	if (locs.length == 0) {
		document.getElementById("map").innerHTML = "";
		return;
	}

	// find center of locs
	var center = findCenter(locs);

	// find extremes of locs
	var extremes = findExtremes(locs);
	var distance = findDistance(extremes);

	var zoom = Math.min(18-distance, 5.5);

	// create the map, centered at the center found above
	const map = new google.maps.Map(document.getElementById("map"), {
		zoom: zoom,
		center: center,
	});

	// create infowindow, which will show the place name on the markers, when clicked
	var infowindow = new google.maps.InfoWindow();
	
	// add all of the locations to the map using markers
	var marker, loc;
	
	var length = locs.length;
	for (var i = 0; i < length; i++) {
		loc = {lat: locs[i][1], lng: locs[i][2]};

		var marker = new google.maps.Marker({
			position: loc,
			map: map,
		});
		
		google.maps.event.addListener(marker, 'click', (function(marker, i) {
			return function() {
			  infowindow.setContent(locs[i][0]);
			  infowindow.open(map, marker);
			}
		})(marker, i));
	}
}
