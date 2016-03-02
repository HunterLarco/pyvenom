const gulp = require('gulp');
const sourcemaps = require('gulp-sourcemaps');
const sass = require('gulp-sass');
const fs = require('fs');
const csscomb = require('gulp-csscomb');
const autoprefixer = require('gulp-autoprefixer');

const settings = {
	src: {
		watchGlobPattern: './scss/**/*.scss',
		mainSassFile: './scss/main.scss'
	},
	dist: {
		mainSassDir: './venom/templates/resources/css'
	}
};

// Run default by default
gulp.task('default', ['sass', 'sass:watch']);

// $ gulp sass
gulp.task('sass', () => {
 // Start with the main sass file
 return gulp.src(settings.src.mainSassFile)
   .pipe(sourcemaps.init())
   // Run it through sass, compressed
   .pipe(sass().on('error', sass.logError))
   // .pipe(sourcemaps.write('./'))
   .pipe(autoprefixer())
   // Finally write it to the public directory
   .pipe(gulp.dest(settings.dist.mainSassDir));
});

// $ gulp sass:watch
gulp.task('sass:watch', () => {
 gulp.watch(settings.src.watchGlobPattern, ['sass']);
 gulp.watch(settings.src.watchGlobPattern, function (event) {
   if (event.path.indexOf('components') === -1) return;
   // [Using event.path for source and destination](https://github.com/gulpjs/gulp/issues/212)
   // Split the filename from the path.
   var filename = event.path.split('/');
   filename = filename[filename.length - 1];
   // For some reason it does need a base to work
   var base = event.path.replace(filename, '');

   gulp.src(event.path, { base: base })
     .pipe(csscomb())
     .pipe(gulp.dest( base ));
 });
});
