# -*- coding: utf-8 -*-
{
    'name': "IT Automation Service",
    'summary': "Tự động hóa IT và quản lý dịch vụ hỗ trợ kỹ thuật",
    'version': '1.0',
    'category': 'IT Support',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'installable': True,
    'application': True,  
    'auto_install': False,
}