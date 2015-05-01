SASS = pythonsd/sass
STATIC = pythonsd/static

compile-sass:
	sassc $(SASS)/pythonsd.scss $(STATIC)/css/pythonsd.css -s compressed
