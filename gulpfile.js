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
    browserify("./project/static/scripts/jsx/main.js")
        .transform("babelify", {presets: ["stage-2", "react"]})
        .bundle()
        .pipe(fs.createWriteStream("./project/static/scripts/js/main.js"));
});

gulp.task('del', function () {
    // Clean up the generated js files
    return del(['./project/static/scripts/js/*.js']);
});

gulp.task('default', ['del'], function () {
    // default task, run automatically when calling gulp
    gulp.start('transform');
    gulp.watch('./project/static/scripts/jsx/*.js', ['transform']);
});