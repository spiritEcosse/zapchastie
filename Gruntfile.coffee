
module.exports = (grunt) ->
    grunt.initConfig(
        pkg: grunt.file.readJSON('package.json')
        coffee:
            compile:
                files:
                    'static_root/src/js/coffee_common/app.js': ['auto_parts/src/coffee/*.coffee', 'apps/**/*.coffee'],
                    'static/src/js/coffee_common/app.js': ['auto_parts/src/coffee/*.coffee', 'apps/**/*.coffee']
        uglify:
            all_src:
                options:
                    sourceMap: true,
                    sourceMapName: 'static/build/js/sourceMap.map'
                    report: 'gzip'
                files:
                    'static/build/js/script.min.js': ["static/bower_components/jquery/dist/jquery.min.js",
                        'static/bower_components/bootstrap/dist/js/bootstrap.min.js',
                        'static/bower_components/angular/angular.js',
                        'static/bower_components/angular-resource/angular-resource.js',
                        'static/bower_components/angular-route/angular-route.min.js',
                        'static_root/djng/js/django-angular.js',
                        'static/oscar/js/oscar/ui.js',
                        "static/oscar/js/bootstrap-datetimepicker/bootstrap-datetimepicker.js",
                        "oscar/js/bootstrap-datetimepicker/locales/bootstrap-datetimepicker.all.js",
                        "static/src/js/**/*.js",
                    ]
        imagemin:
            dist:
                files: [{
                    expand: true,
                    cwd: 'static/',
                    src: ['**/*.{png,jpg,gif}'],
                    dest: 'static/'
                }]
    );

    grunt.loadNpmTasks 'grunt-contrib-coffee'
    grunt.loadNpmTasks 'grunt-contrib-uglify'
    grunt.loadNpmTasks 'grunt-contrib-imagemin'
    grunt.registerTask 'default', ['coffee', 'uglify', 'imagemin']
