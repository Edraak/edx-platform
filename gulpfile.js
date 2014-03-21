// Include gulp
var gulp = require('gulp');

// Include Our Plugins
var sass = require('gulp-sass');
var uglify = require('gulp-uglify');
var concat = require('gulp-concat');
var rename = require('gulp-rename');

// Compile Our Sass
gulp.task('sass', function() {
    gulp.src('./cms/static/sass/*.scss')
        .pipe(sass())
        .pipe(gulp.dest('./'));
});

// Watch Files For Changes
gulp.task('watch', function() {
    gulp.watch('./scss/*.scss', ['sass']);
});

// Default Task
gulp.task('default', ['sass', 'watch']);
