(function() {
  'use strict';

  /* Declare app level module which depends on filters, and services */
  var app, app_name;

  app_name = 'zapchastie';

  app = angular.module(app_name, ['ngResource', 'ngRoute', 'djng.forms', 'djng.urls']);

  app.config([
    '$httpProvider', function($httpProvider) {
      $httpProvider.defaults.xsrfCookieName = 'csrftoken';
      $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
      $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
      return $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
    }
  ]);

}).call(this);

(function() {
  'use strict';

  /* Controllers */
  var app, app_name;

  app_name = "zapchastie";

  app = angular.module(app_name);

  app.controller('Product', [
    '$http', '$scope', '$window', 'djangoForm', '$document', function($http, $scope, $window, djangoForm, $document) {
      $scope.alert = null;
      $scope.disabled_button = false;
      $scope.remove_alert = function() {
        return $scope.alert = null;
      };
      return $scope.submit = function() {
        if ($scope.product_question) {
          $scope.disabled_button = true;
          $scope.alert = null;
          $scope.button.actual = $scope.button.sending;
          return $http.post(".", $scope.product_question).success(function(data) {
            if (!djangoForm.setErrors($scope.product_question_form, data.errors)) {
              $scope.alert = {
                msg: data.msg,
                type: 'alert-success'
              };
            }
            $scope.button.actual = $scope.button.send;
            return $scope.disabled_button = false;
          }).error(function() {
            return console.error('An error occurred during submission');
          });
        }
      };
    }
  ]);

  app.directive('alertSuccess', ['$scope', function($scope) {}]);

}).call(this);
