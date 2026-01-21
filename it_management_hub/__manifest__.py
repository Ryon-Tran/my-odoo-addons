# -*- coding: utf-8 -*-
# Thông tin mô tả module it_management_hub
{
    'name': 'IT Management Hub',
    'version': '1.0.0',
    'summary': 'Quản trị hệ thống IT cho doanh nghiệp',
    'description': 'Mở rộng quản lý dự án với các trường DevOps, Domain, SSL, AI Analysis.',
    'author': 'Your Name',
    'website': 'https://yourcompany.com',
    'category': 'Project',
    'depends': ['project', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/it_project_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
