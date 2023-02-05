// JavaScript requirements
import * as jquery from 'jquery';
import * as bootstrap from 'bootstrap';


// Import HTMX
// https://htmx.org/
// -------------------------------------------------------------------------
import * as htmx from 'htmx.org';


// CSS includes
import './sass/index.scss';


// Enable Bootstrap tooltips across the site
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
});
