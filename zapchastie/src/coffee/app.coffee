'use strict'

### Declare app level module which depends on filters, and services ###

app_name = 'zapchastie'
app = angular.module app_name, ['ngResource', 'ngRoute', 'djng.forms', 'djng.urls']

app.config ['$httpProvider', ($httpProvider) ->
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken'
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
    $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded'
]

