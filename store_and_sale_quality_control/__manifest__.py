
{
    'name': 'Quality Control for Sale and Store Team',
    'version': '1.0.0',
    'author': 'Poe Poe, R&P'
    'category': 'QC/QC',
    'summary': 'QC Management',
    'description': """
    This module contains the qc management.
    """,
    'depends':  ['base','sale', 'stock','account'],
    'data': [
        'security/quality_control_security.xml',
        'security/ir.model.access.csv',
        'data/qc_sequence.xml',
        'views/sale_qc_view_form.xml',
        'views/store_qc_view_form.xml',
    ],

    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
