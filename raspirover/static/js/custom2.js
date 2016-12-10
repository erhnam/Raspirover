	

function auto_load(){
	$.ajax({
	  url: "manual",
	  cache: true,
	  success: function(data){
		 $("#datos").html(data);
	  } 
	});
}
 
$(document).ready(function(){
 
	auto_load();
 
});

setInterval(auto_load,1000);
	


$(function() {
	$("#temp").click(function(evt) {
		$("#randomdiv").load("/mostrarGrafica/{{explo.id_exploracion}}/{{h}}")
         evt.preventDefault();
	})
})
