function fwd() {

	var isiDevice = /ipad|iphone|ipod/i.test(navigator.userAgent.toLowerCase());

	if (isiDevice == false){
		var xhttp = new XMLHttpRequest();
		xhttp.open("GET", "?cmd=fwd", true);
		xhttp.send();
	}
}

function fwdi() {

	var isiDevice = /ipad|iphone|ipod/i.test(navigator.userAgent.toLowerCase());

	if (isiDevice == true){
		var xhttp = new XMLHttpRequest();
		xhttp.open("GET", "?cmd=fwd", true);
		xhttp.send();
	}

}


function left() {

	var isiDevice = /ipad|iphone|ipod/i.test(navigator.userAgent.toLowerCase());

	if (isiDevice == false){
		var xhttp = new XMLHttpRequest();
		xhttp.open("GET", "?cmd=left", true);
		xhttp.send();
	}
}

function lefti() {

	var isiDevice = /ipad|iphone|ipod/i.test(navigator.userAgent.toLowerCase());

        if (isiDevice == true){
		var xhttp = new XMLHttpRequest();
		xhttp.open("GET", "?cmd=left", true);
		xhttp.send();
	}

}

function stop() {
	var xhttp = new XMLHttpRequest();
	xhttp.open("GET", "?cmd=stop", true);
	xhttp.send();
}

function right() {
	var isiDevice = /ipad|iphone|ipod/i.test(navigator.userAgent.toLowerCase());

	if (isiDevice == false){
		var xhttp = new XMLHttpRequest();
		xhttp.open("GET", "?cmd=right", true);
		xhttp.send();
	}
}

function righti() {
	var isiDevice = /ipad|iphone|ipod/i.test(navigator.userAgent.toLowerCase());

        if (isiDevice == true){
		var xhttp = new XMLHttpRequest();
		xhttp.open("GET", "?cmd=right", true);
		xhttp.send();
	}

}


function bwd() {
	
	var isiDevice = /ipad|iphone|ipod/i.test(navigator.userAgent.toLowerCase());

	if (isiDevice != true){
		var xhttp = new XMLHttpRequest();
		xhttp.open("GET", "?cmd=bwd", true);
		xhttp.send();
	}
}

function bwdi() {
	
	var isiDevice = /ipad|iphone|ipod/i.test(navigator.userAgent.toLowerCase());

        if (isiDevice == true){
		var xhttp = new XMLHttpRequest();
		xhttp.open("GET", "?cmd=bwd", true);
		xhttp.send();
	}
}


function camleft() {
	var xhttp = new XMLHttpRequest();
	xhttp.open("GET", "?cmd=camleft", true);
	xhttp.send();
}

function camcenter() {
	var xhttp = new XMLHttpRequest();
	xhttp.open("GET", "?cmd=camcenter", true);
	xhttp.send();
}

function camup() {
	var xhttp = new XMLHttpRequest();
	xhttp.open("GET", "?cmd=camup", true);
	xhttp.send();
}

function camdown() {
	var xhttp = new XMLHttpRequest();
	xhttp.open("GET", "?cmd=camdown", true);
	xhttp.send();
}

function camright() {
	var xhttp = new XMLHttpRequest();
	xhttp.open("GET", "?cmd=camright", true);
	xhttp.send();
}

function salir() {
	var xhttp = new XMLHttpRequest();
	xhttp.open("GET", "?cmd=salir", true);
	xhttp.send();
}

image1 = new Image();
image1.src = "/media/temperaturagris.png";
image1alt = new Image();
image1alt.src = "/media/temperatura.png";

image2 = new Image();
image2.src = "/media/humedadgris.png";
image2alt = new Image();
image2alt.src = "/media/humedad.png";

image3 = new Image();
image3.src = "/media/gasgris.png";
image3alt = new Image();
image3alt.src = "/media/gas.png";

image4 = new Image();
image4.src = "/media/luzgris.png";
image4alt = new Image();
image4alt.src = "/media/luz.png";

image5 = new Image();
image5.src = "/media/camaragris.png";
image5alt = new Image();
image5alt.src = "/media/camara.png";

image6 = new Image();
image6.src = "/media/manualgris.png";
image6alt = new Image();
image6alt.src = "/media/manual.png";

image7 = new Image();
image7.src = "/media/automaticogris.png";
image7alt = new Image();
image7alt.src = "/media/automatico.png";

image8 = new Image();
image8.src = "/media/gpsgris.png";
image8alt = new Image();
image8alt.src = "/media/gps.png";

image9 = new Image();
image9.src = "/media/fuegogris.png";
image9alt = new Image();
image9alt.src = "/media/fuego.png";

function cambiar1() {
	if (document.getElementById('checkbox_f1').src != image1.src ) {
 		document.getElementById('checkbox_f1').checked = true;		
 		document.getElementById('checkbox_f1').src = image1.src;

	} 
	else {
		document.getElementById('checkbox_f1').checked = false;
 		document.getElementById('checkbox_f1').src = image1alt.src;
	}
}
function cambiar2() {

	if (document.getElementById('checkbox_f2').src != image2.src ) {
 		document.getElementById('checkbox_f2').src = image2.src;
 		document.getElementById('checkbox_f2').checked = true;

	} 
	else {
 		document.getElementById('checkbox_f2').src = image2alt.src;
 		document.getElementById('checkbox_f2').checked = false;

	}
}
function cambiar3() {

	if (document.getElementById('checkbox_f3').src != image3.src ) {
 		document.getElementById('checkbox_f3').src = image3.src;
 		document.getElementById('checkbox_f3').checked = true;

	} 
	else {
 		document.getElementById('checkbox_f3').src = image3alt.src;
 		document.getElementById('checkbox_f3').checked = false;

	}
}
function cambiar4() {

	if (document.getElementById('checkbox_f4').src != image4.src ) {
 		document.getElementById('checkbox_f4').src = image4.src;
 		document.getElementById('checkbox_f4').checked = true;

	} 
	else {
 		document.getElementById('checkbox_f4').src = image4alt.src;
 		document.getElementById('checkbox_f4').checked = false;

	}
}
function cambiar5() {

	if (document.getElementById('checkbox_f5').src != image5.src ) {
 		document.getElementById('checkbox_f5').src = image5.src;
 		document.getElementById('checkbox_f5').checked = true;

	} 
	else {
 		document.getElementById('checkbox_f5').src = image5alt.src;
 		document.getElementById('checkbox_f5').checked = false;

	}
}

function cambiar8() {

	if (document.getElementById('checkbox_f8').src != image8.src ) {
 		document.getElementById('checkbox_f8').src = image8.src;
 		document.getElementById('checkbox_f8').checked = true;

	} 
	else {
 		document.getElementById('checkbox_f8').src = image8alt.src;
 		document.getElementById('checkbox_f8').checked = false;

	}
}


function cambiar9() {

	if (document.getElementById('checkbox_f9').src != image9.src ) {
 		document.getElementById('checkbox_f9').src = image9.src;
 		document.getElementById('checkbox_f9').checked = true;

	} 
	else {
 		document.getElementById('checkbox_f9').src = image9alt.src;
 		document.getElementById('checkbox_f9').checked = false;

	}
}

function cambiar6() {
 		document.getElementById('checkbox_f6').src = image6alt.src;
}

function cambiar6alt() {
 		document.getElementById('checkbox_f6').src = image6.src;
}

function cambiar7() {
 		document.getElementById('checkbox_f7').src = image7alt.src;
}

function cambiar7alt() {
 		document.getElementById('checkbox_f7').src = image7.src;
}

