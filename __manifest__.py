# -*- coding: utf-8 -*-
{
    'name': 'Employee Driving License Info',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Add Driving License Information to Employee Private Information',
    'description': """
        Employee Driving License Management
        ====================================
        Adds driving license section to Private Information tab
    """,
    'author': 'Your Company',
    'depends': ['hr', 'ohrms_core', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_driving_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}