# QuizApe

Simple Django-based survey site

Use the Django Admin to create a survey. Supports the following question
types:

* Boolean
* Star rating 1-5
* Numeric range
* Free-form text
* Drop-down selection

Survey questions can be grouped by pages. A cookie is set when someone has
taken a survey so they can return to the survey.

The Django Admin has basic reports showing the survey results, including SVG
graphs.


# Setup / Configuration

You'll need to add your own configuration for a SECRET_KEY. See the README in
QuizeApe/local_settings to learn how to set that up.

You'll also want to replace `static/img/home_logo.png` and
`static/img/logo_50.png` with logos more appropriate to your own site. A less
lazy developer would have made this configurable, but well, I'm not a less
lazy developer.


# But... what about?

This was a (mostly) quick one-off I needed to solve a problem. If it helps
you, great! I don't expect much to change from here on in unless I end up
needing a survey for a client that I can't do with what is here.

Feel free to DM me on Twitter if you get stuck or you find a problem.
