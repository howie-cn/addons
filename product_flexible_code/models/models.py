# -*- coding: utf-8 -*-

from openerp.exceptions import Warning
from openerp import models, fields, api

import logging
_logger = logging.getLogger(name=__name__)

class stockCategory(models.Model):

    _name = 'stock.category'
    _description = u'the product category for flexible code generation'

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'
    _rec_name = 'complete_name'

    parent_left = fields.Integer('Left Parent', index=True)
    parent_right = fields.Integer('Right Parent', index=True)

    name = fields.Char(
        string='Name',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help=False,
        size=50,
    )

    code = fields.Char(
        string='Code',
        required=True,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
    )

    description = fields.Text(
        string='Description',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
    )

    is_end = fields.Boolean(
        string='Is End ?',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )

    sequence = fields.Many2one(
        string='Sequence',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='ir.sequence',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )

    digits = fields.Integer(
        string=u'此分类产品流水码位数',
        required=False,
        readonly=False,
        index=False,
        default=4,
        help=False
    )

    parent_id = fields.Many2one(
        string='Parent Category',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='stock.category',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )

    product_description_template = fields.Char(
        string=u'此分类产品描述规则',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=256,
    )

    product_description_sample = fields.Char(
        string=u'此分类产品描述实例',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=256,
    )

    account_category = fields.Many2one(
        string=u'此分类产品默认会计类别',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='product.category',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )

    production_efficiency = fields.Float(
        string=u'此分类产品默认生产效率',
        required=False,
        readonly=False,
        index=False,
        default=1.0,
        digits=(1, 3),
        help=False
    )

    complete_name = fields.Char(
        string='Category Name',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help=False,
        size=50,
        compute='_compute_name'
    )

    @api.one
    @api.depends('name')
    def _compute_name(self):
        name = self.name
        current = self
        while current.parent_id:
            current = current.parent_id
            name = '%s/%s' % (current.name, name)

        self.complete_name = name

    complete_code = fields.Char(
        string='Code Prefix',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help=False,
        size=50,
        store=True,
        compute='_compute_code'
    )

    @api.one
    @api.depends('code')
    def _compute_code(self):
        code = self.code
        current = self
        while current.parent_id:
            current = current.parent_id
            code = '%s%s' % (current.code, code)

        self.complete_code = code

    @api.multi
    def name_get(self):
        return [(cat.id, cat.complete_name) for cat in self]

    @api.model
    def _create_sequence(self, vals):
        seq = {
            'name': vals['name'],
            'implementation': 'no_gap',
            'prefix': vals['code'],
            'padding': vals['digits'],
            'number_increment': 1,
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        return self.env['ir.sequence'].create(seq)

    @api.model
    def create(self, values):

        if values.get('is_end') and values['is_end']:
            values.update({'sequence': self.sudo()._create_sequence(values).id})

        result = super(stockCategory, self).create(values)

        return result

    @api.multi
    def write(self, values):
        seq_vals = {}

        if values.get('code'):
            seq_vals.update({'prefix': values['code']})

        if values.get('name'):
            seq_vals.update({'name': values['name']})

        if values.get('digits'):
            seq_vals.update({'padding': values['digits']})

        _logger.info(seq_vals)
        self.sequence.write(seq_vals)

        result = super(stockCategory, self).write(values)

        return result

    @api.multi
    def unlink(self):
        product_tempates = self.env['product.template'].search_count([('stock_category', 'in', [self.id])])

        if product_tempates:
            raise Warning('You can not delete this category, as it has been referenced with product')

        result = super(stockCategory, self).unlink()

        return result


class productTemplate(models.Model):
    _inherit = 'product.template'

    stock_category = fields.Many2one(
         string='Stock Category',
         required=False,
         readonly=False,
         index=False,
         default=None,
         help=False,
         comodel_name='stock.category',
         domain=[('is_end', '=', True)],
         context={},
         ondelete='cascade',
         auto_join=False
    )

    product_description_template = fields.Char(
        string='Product Description Template',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        related="stock_category.product_description_template"
    )

    product_description_sample = fields.Char(
        string='Product Description Sample',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        related="stock_category.product_description_sample"
    )

    code_prefix = fields.Char(
        string='Code Prefix',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        related="stock_category.complete_code"
    )

    production_efficiency = fields.Float(
        string='Production Efficiency',
        required=False,
        readonly=False,
        index=False,
        help=False
    )

    similar_products = fields.One2many(
        string='Similar Products',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='product.template',
        inverse_name='parent_product',
        domain=[],
        context={},
        auto_join=False,
        limit=10
    )

    parent_product = fields.Many2one(
        string='Parent Product',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        comodel_name='product.template',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )

    @api.onchange('stock_category')
    def _onchange_stock_category(self):
        _logger.info(self.stock_category.production_efficiency)
        self.production_efficiency = self.stock_category.production_efficiency

        if self.stock_category.account_category:
            self.categ_id = self.stock_category.account_category

    @api.onchange('description')
    def _onchange_description(self):
        desc_string = self.description
        if not isinstance(desc_string, basestring):
            return False
        import re
        decs_list = re.split(ur"[;,\s，。；：]\s*", desc_string)
        domain = []

        for i in desc_list:
            t = ('description', 'ilike', '%s' % i)
            # domain.append('|')
            domain.append(t)

        for x in range(len(domain) - 1):
            domain.insert(0, '|')

        _logger.info(domain)

        self.similar_products = self.search(domain)


class productProduct(models.Model):

    _inherit = 'product.product'

    renew_code = fields.Boolean(
        string='New Code',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False
    )

    @api.model
    def create(self, values):
        product = super(productProduct, self).create(values)
        _logger.info('product temples')
        _logger.info(product.product_tmpl_id.default_code)
        if product.stock_category:
            product.button_renew_code()
        return product

    @api.one
    def button_renew_code(self):
        if self.stock_category:
            sequence = self.stock_category.sequence
            if self.stock_category.parent_id:
                prefix = self.stock_category.parent_id.complete_code
                code = '%s%s' % (prefix, sequence.next_by_id(sequence.id))
            else:
                code = '%s' % (sequence.next_by_id(sequence.id))

            self.default_code = code


class mrpBOM(models.Model):
    _inherit = 'mrp.bom'

    product_efficiency = fields.Float(
        related='product_tmpl_id.production_efficiency',
        readonly=True
    )

class mrpBOMLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_efficiency = fields.Float(
        related='product_id.production_efficiency',
        readonly=True
    )