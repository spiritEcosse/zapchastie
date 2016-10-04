'use strict'

### Controllers ###

app_name = "zapchastie"
app = angular.module app_name


app.controller 'Product', ['$http', '$scope', '$window', 'djangoForm', '$document', ($http, $scope, $window, djangoForm, $document) ->
    $scope.alert = null
    $scope.disabled_button = false

    $scope.remove_alert = ->
        $scope.alert = null

    $scope.submit = ->
        if $scope.product_question
            $scope.disabled_button = true
            $scope.alert = null
            $scope.button.actual = $scope.button.sending

            $http.post(".", $scope.product_question).success (data) ->
                if not djangoForm.setErrors($scope.product_question_form, data.errors)
                    $scope.alert = ({msg: data.msg, type: 'alert-success'})

                $scope.button.actual = $scope.button.send
                $scope.disabled_button = false
            .error ->
                console.error('An error occurred during submission')

]
app.directive 'alertSuccess', ['$scope', ($scope) ->
]
