var app = angular.module('ssskl', ['ui', 'ngCookies']).run(function($rootScope, $http, $cookies){
	$rootScope.online_users = [];
	$http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
});


var my_app = angular.module('ssskl').config(function($interpolateProvider) {
	$interpolateProvider.startSymbol('{$');
	$interpolateProvider.endSymbol('$}');
});

app.controller('InitialController', function($scope, $log, $http) {


	$( ".selectable label" ).click(function() {
		$(".selectable label").removeClass("selected");
		$(this).addClass('selected');
	});

	$( "input[type=checkbox]" ).change(function() {
		if($(this).prop('checked')){
			$(this).parent('label').addClass('selected');
		}
		else{
			$(this).parent('label').removeClass('selected');
		}
	});



});

