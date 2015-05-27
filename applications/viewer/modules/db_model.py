#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gluon import Field

def get_model(db):
    '''db model based on imported dbf(s)
    - for each dbf repeat command
        db.define_table(<dbf-table-name>, Field(..), Field(..), singular=.., plural=.., format=..)
    - Field parameters: name, type, default, label - see example bellow
        type: 'string',length=NN | 'text' | 'integer' | 'date' | 'datetime', 'boolean',..
    - singular, plural: name of the table in natural language and singular/plural form
    - format: string template where for the row value %(<name>)s will be replaced with the value of field <name>
    '''

    db.define_table('codex',
            Field('autori', 'text', default='', label='Autoři'),
            Field('osoby', 'text', default='', label='Další osoby'),
            Field('nazev', 'text', default='', label='Název'),
            Field('podnazev', 'text', default='', label='Podnázev'),
            Field('klsl', 'text', default='', label='Klíčová slova'),
            Field('dt', 'text', default='', label='DT (System.třídění)'),
            Field('vydani', 'text', default='', label='Vydání'),
            Field('impresum', 'text', default='', label='Impresum'),
            Field('anotace', 'text', default='', label='Anotace'),
            singular="Kniha", plural="Knihy",
            format='%(nazev)s',
            )
    return db
