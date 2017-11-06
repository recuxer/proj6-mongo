"""
Flask web app connects to Mongo database.
Keep a simple list of dated memoranda.

Representation conventions for dates: 
   - We use Arrow objects when we want to manipulate dates, but for all
     storage in database, in session or g objects, or anything else that
     needs a text representation, we use ISO date strings.  These sort in the
     order as arrow date objects, and they are easy to convert to and from
     arrow date objects.  (For display on screen, we use the 'humanize' filter
     below.) A time zone offset will 
   - User input/output is in local (to the server) time.  
"""

import flask
from flask import g
from flask import render_template
from flask import request
from flask import url_for
from flask import flash
import db
import logging
import sys

# Date handling 
import arrow   
from dateutil import tz  # For interpreting local times

# Config Args
import config

#if statement is to allow config variables in tests of db.py
if __name__ == "__main__":
    CONFIG = config.configuration()
else:
    CONFIG = config.configuration(proxied=True)

# Globals
app = flask.Flask(__name__)
app.secret_key = CONFIG.SECRET_KEY


###########
# Pages
###

@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    g.memos = db.getmemos()
    for memo in g.memos: 
        app.logger.debug("Memo: " + str(memo))
    return flask.render_template('index.html')

@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('page_not_found.html',
                                 badurl=request.base_url,
                                 linkback=url_for("index")), 404

##########
# form handlers
###

@app.route("/create", methods=["POST"])
def create():
    app.logger.debug("Create")
    
    #form variables called before concat for error checking
    memo = flask.request.form["memo"]
    date = flask.request.form["date"]
    time = flask.request.form["time"]
    
    #if user didn't enter required fields
    if not memo or not date or not time:
        error = "memo not created. date, time, and memo field can't be empty!"
        flash(error)
    else:
        cur_datetime = date + ' ' + time
        db.enterinDB(memo, cur_datetime)
    return flask.redirect(flask.url_for("index"))

@app.route("/remove", methods=["POST"])
def remove():
    app.logger.debug("Remove")
    datetime = flask.request.form["removememo"]
    db.removefromDB(datetime)
    return flask.redirect(flask.url_for("index")) 

#################
#
# Functions used within the templates
#
#################

@app.template_filter( 'humanize' )
def humanize_arrow_date( date ):
    """
    Date is internal UTC ISO format string.
    Output should be "today", "yesterday", "in 5 days", etc.
    Arrow will try to humanize down to the minute, so we
    need to catch 'today' as a special case. 
    """
    try:
        then = arrow.get(date).to('local')
        now = arrow.utcnow().to('local')
        if then.date() == now.date():
            human = "Today"
        else: 
            human = then.humanize(now)
            if human == "in a day":
                human = "Tomorrow"
    except: 
        human = date
    return human


if __name__ == "__main__":
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT,host="0.0.0.0")
