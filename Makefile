SASS = pythonsd/sass
STATIC = pythonsd/static

compile-sass:
	-mkdir $(STATIC)/css 2>/dev/null
	sassc $(SASS)/pythonsd.scss $(STATIC)/css/pythonsd.css -s compressed
