# -*- coding: utf-8 -*-
{
    'name': 'Electoral Roll',
    'version': '1.0.0',
    'category': 'Custom',
    'summary': 'Electoral Roll module',
    'description': """
        Electoral Roll Module
        ==================

        Add your description here.
    """,
    'author': 'Solaria Builder',
    'depends': ['base', 'contacts'],
    'data': [
        'security/permissions.json',
        'config/views/electoral_roll_views.json',
        'config/menu.json',
    ],
    'installable': True,
    'application': True,
}
