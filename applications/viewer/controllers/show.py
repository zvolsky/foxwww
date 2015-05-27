# -*- coding: utf-8 -*-

def index():
    redirect(URL('table'))

def table():
    auth_prefix = 'auth_'    # hide authorizations tables
    len_prefix = len(auth_prefix)
    table = request.args
    if table not in filter(lambda candidate: candidate[:len_prefix]!=auth_prefix, dbu.tables):
        for table in dbu.tables:
            if table[:len_prefix]!=auth_prefix:
                break

    grid = SQLFORM.smartgrid(
            dbu[table]
            )

    return dict(grid=grid)
