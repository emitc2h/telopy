// requirements

var gulp = require('gulp');
var gulpBrowser = require("gulp-browser");
var reactify = require('reactify');
var del = require('del');
var size = require('gulp-size');
var fs = require("fs");
var browserify = require("browserify");


// tasks

gulp.task('transform', function () {
    // Transform the jsx code into js
    browserify("./app/static/scripts/jsx/main.js")
        .transform("babelify", {presets: ["stage-2", "react"]})
        .bundle()
        .pipe(fs.createWriteStream("./app/static/scripts/js/main.js"));
});

gulp.task('del', function () {
    // Clean up the generated js files
    return del(['./app/static/scripts/js/*.js']);
});

gulp.task('default', ['del'], function () {
    // default task, run automatically when calling gulp
    gulp.start('transform');
    gulp.watch('./app/static/scripts/jsx/*.js', ['transform']);
});