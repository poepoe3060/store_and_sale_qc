
{
    'name': 'R&P Quality Control',
    'version': '1.1',
    'category': 'QC/QC',
    'summary': 'QC Management',
    'description': """
    This module contains the qc management.
    """,
    'depends':  ['base','sale_internal', 'stock_internal','account'],
    'data': [
        'security/quality_control_security.xml',
        'security/ir.model.access.csv',
        'data/qc_sequence.xml',
        'views/sale_qc_view_form.xml',
        'views/store_qc_view_form.xml',
    ],

    'installable': True,
    'auto_install': False
}
