SASS = pythonsd/sass
STATIC = pythonsd/static

compile-sass:
	mkdir -p $(STATIC)
	sassc $(SASS)/pythonsd.scss $(STATIC)/css/pythonsd.css -s compressed
