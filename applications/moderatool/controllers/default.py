# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

from datetime import datetime

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    members = db(Members.id>0).select(orderby=~Members.warned)
    for member in members:
        if member.warned:
            delta = datetime.now() - member.warned
            if delta.days >= 90:
                db(Members.id==member.id).delete()
                db.commit()
    form = SQLFORM(Members)
    if form.accepts(request.vars, session):
        session.flash = 'Membro adicionado com sucesso!'
        redirect(URL(request.application, 'default', 'index'))
    return dict(members=members, form=form)

def warn():
    member_id = int(request.vars['member_id'])
    member = Members[member_id]
    if member.warned:
        if member.removed:
            db(Members.id==member_id).update(banned=True)
            db.commit()
            session.flash = '%s DEVE SER BANIDO DA COMUNIDADE!'
        else:
            db(Members.id==member_id).update(warned=None, removed=datetime.now())
            db.commit()
            session.flash = '%s foi advertido novamente. Exclua-o da comunidade!' % member.name
    else:
        db(Members.id==member_id).update(warned=datetime.now())
        db.commit()
        session.flash = '%s foi advertido. Olho nele(a)!' % member.name
    redirect(URL(request.application, 'default', 'index'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()


