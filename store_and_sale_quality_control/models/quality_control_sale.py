from odoo import api, fields, models, _, tools, Command
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, time


class QualityControlSale(models.Model):
    _name = "quality.control.sale"
    _description = "Sale Quality Control"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='QC Reference', required=True, copy=False, readonly=True, default='New')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    invoice_id = fields.Many2one('account.move', string='Account Move')
    invoice_domain_ids = fields.Many2many('account.move', compute='_compute_invoice_domain', store=False)
    qc_sale_line_ids = fields.One2many('quality.control.sale.line', 'qc_sale_id', string='QC Store Lines')
    schedule_date = fields.Datetime(
        string='Scheduled Date',
        default=lambda self: datetime.now()
    )
    qc_note = fields.Text('QC Notes', tracking=True)
    test_person_id = fields.Many2one('hr.employee', string='Check Person', required=True)

    @api.onchange('sale_order_id')
    def _compute_invoice_domain(self):
        for rec in self:
            rec.invoice_domain_ids = self.env['account.move'].search([
                ('invoice_origin', '=', rec.sale_order_id.name),
                ('state','=', 'posted'), ('move_type', '=', 'out_invoice')
            ])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('quality.control.sale') or 'New'
        return super(QualityControlSale, self).create(vals)

    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        self.invoice_id = None
        self.qc_sale_line_ids = [Command.clear()]

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        if not self.invoice_id:
            self.qc_sale_line_ids = [Command.clear()]
            return

        lines = []
        for move_line in self.invoice_id.invoice_line_ids:
            if move_line.product_id and move_line.quantity:
                lines.append(Command.create({
                    'product_id': move_line.product_id.id,
                    'quantity': move_line.quantity,
                    'already_checked': False,
                }))
        self.qc_sale_line_ids = lines

    def write(self, values):
        for rec in self:
            changes = []
            for field, val in values.items():
                if field not in rec._fields:
                    continue
                old = rec[field]
                new = val
                if rec._fields[field].type == 'many2one':
                    old = old.display_name if old else ''
                    new = rec.env[rec._fields[field].comodel_name].browse(val).display_name if val else ''
                if old != new:
                    changes.append(f"{field}: {old} → {new}")
            if changes:
                rec.message_post(body="Updated Fields:" + "<br/>".join(changes), subtype_xmlid="mail.mt_note")
        return super().write(values)


class QualityControlSaleLines(models.Model):
    _name = "quality.control.sale.line"
    _description = "Store Quality Control Line"

    qc_sale_id = fields.Many2one('quality.control.sale', string='QC Store')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity')
    already_checked = fields.Boolean(string='Checked', required=True)

    def write(self, vals):
        for line in self:
            changes = []
            for field, val in vals.items():
                if field not in line._fields:
                    continue
                old = line[field]
                new = val
                if line._fields[field].type == 'many2one':
                    old = old.display_name if old else ''
                    new = line.env[line._fields[field].comodel_name].browse(val).display_name if val else ''
                if old != new:
                    changes.append(f"{field}: {old} → {new}")
            if changes and line.qc_sale_id:
                message = "QC Line Updated:" + "<br/>".join(changes)
                line.qc_sale_id.message_post(body=message, subtype_xmlid="mail.mt_note")
        return super().write(vals)


