import datetime

from flask import Flask
from flask import g
from flask import redirect
from flask import request
from flask import session
from flask import url_for, abort, render_template, flash
from functools import wraps
from hashlib import md5
from peewee import *

# config - aside from our database, the rest is for use by Flask
DEBUG = True
SECRET_KEY = 'whatisthis'

# create a flask application - this ``app`` object will be used to handle
# inbound requests, routing them to the proper 'view' functions, etc
app = Flask(__name__)
app.config.from_object(__name__)

# create a peewee database instance -- our models will use this database to
# persist information
database = PostgresqlDatabase('user_story_manager')

# model definitions -- the standard "pattern" is to define a base model class
# that specifies which database to use.  then, any subclasses will automatically
# use the correct storage. for more information, see:
# http://charlesleifer.com/docs/peewee/peewee/models.html#model-api-smells-like-django


class BaseModel(Model):
    class Meta:
        database = database


class UserStory(BaseModel):
    story_title = CharField()
    user_story = TextField()
    acceptance_criteria = TextField()
    business_value = IntegerField()
    estimation = FloatField()
    status = CharField()


# simple utility function to create tables
def create_tables():
    database.connect()
    database.create_tables([UserStory])


# Request handlers -- these two hooks are provided by flask and we will use them
# to create and tear down a database connection on each request.
@app.before_request
def before_request():
    g.db = database
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


# views -- these are the actual mappings of url to view function
@app.route('/')
def homepage():
    return list_all_user_stories()


@app.route('/list/')
def list_all_user_stories():
    record_list = UserStory.select()
    print(record_list)
    return render_template('list.html', records=record_list)


@app.route('/story/', methods=['GET', 'POST'])
def add_user_story():
    if (request.method == "POST" and request.form["story_title"] and request.form["user_story"] and
            request.form["acceptance_criteria"] and request.form["business_value"] and request.form["estimation"] and
            request.form["status"]):
        UserStory.create(story_title=request.form["story_title"], user_story=request.form["user_story"],
                         acceptance_criteria=request.form["acceptance_criteria"],
                         business_value=request.form["business_value"], estimation=request.form["estimation"],
                         status=request.form["status"])
        return redirect('/list/')
    else:
        return render_template('form.html')


@app.route('/delete/', methods=['GET'])
def delete_user_story():
    UserStory.delete().where(UserStory.id == request.args.get("story_id")).execute()
    return redirect('/list/')


# allow running from the command line
if __name__ == '__main__':
    app.run()
