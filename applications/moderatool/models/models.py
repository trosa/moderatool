from datetime import datetime

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('gae://mynamespace')             # connect to Google BigTable
    session.connect(request, response, db = db) # and store sessions and tickets there
    ### or use the following lines to store sessions in Memcache
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
else:                                         # else use a normal relational database
    db = DAL('postgres://moderatool:xx@localhost/moderatool')       # if not, use SQLite or other DB
## if no need for session
# session.forget()

Members = db.define_table(
        'members',
        Field('name',    'string', required=True, notnull=True),
        Field('profile', 'string', required=True, notnull=True),
        Field('warned',  'datetime', writable=False, readable=False, default=datetime.now()),
        Field('removed', 'datetime', writable=False, readable=False),
        Field('banned',  'boolean', writable=False, readable=False))

