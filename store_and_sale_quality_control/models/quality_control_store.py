from odoo import api, fields, models, _, tools, Command
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, time



class QualityControlStore(models.Model):
    _name = "quality.control.store"
    _description = "Store Quality Control"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='QC Reference', required=True, copy=False, readonly=True, default='New')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')
    receipt_id = fields.Many2one('stock.picking', string='Receipt')
    qc_line_ids = fields.One2many('quality.control.store.line', 'qc_store_id', string='QC Store Lines')
    schedule_date = fields.Datetime(
        string='Scheduled Date',
        default=lambda self: datetime.now()
    )
    qc_note = fields.Text('QC Notes', tracking=True)
    test_person_id = fields.Many2one('hr.employee', string='Check Person', required=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('quality.control.store') or 'New'
        return super(QualityControlStore, self).create(vals)

    @api.onchange('purchase_order_id')
    def _onchange_purchase_order_id(self):
        self.receipt_id = None
        self.qc_line_ids = [Command.clear()]

    @api.onchange('receipt_id')
    def _onchange_receipt_id(self):
        if not self.receipt_id:
            self.qc_line_ids = [Command.clear()]
            return

        lines = []
        for move in self.receipt_id.move_ids_without_package:
            # Calculate total checked qty for this product from previous QC records
            prev_qcs = self.env['quality.control.store'].search([
                ('receipt_id', '=', self.receipt_id.id),
                ('id', '!=', self.id)
            ])

            # Sum previously checked quantities for this product
            prev_checked_qty = sum(
                line.complete_checked_qty
                for qc in prev_qcs
                for line in qc.qc_line_ids
                if line.product_id.id == move.product_id.id
            )

            remaining_qty = move.quantity - prev_checked_qty

            if remaining_qty > 0:
                lines.append(Command.create({
                    'product_id': move.product_id.id,
                    'quantity': remaining_qty,
                    'complete_checked_qty': 0.0,
                    'location_dest_id': move.location_dest_id.id,
                }))
        self.qc_line_ids = lines


class QualityControlStoreLines(models.Model):
    _name = "quality.control.store.line"
    _description = "Store Quality Control Line"

    qc_store_id = fields.Many2one('quality.control.store', string='QC Store')
    location_dest_id = fields.Many2one('stock.location', string='Location')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity')
    complete_checked_qty = fields.Float(string='Checked Qty')
