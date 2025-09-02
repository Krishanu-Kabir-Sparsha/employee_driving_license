# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class HrEmployeeDriving(models.Model):
    _inherit = 'hr.employee'
    
    # Basic Info
    has_driving_license = fields.Boolean(string='Has Driving License', groups="hr.group_hr_user")
    driving_license_number = fields.Char(string='License Number', groups="hr.group_hr_user")
    driving_license_type = fields.Selection([
        ('national', 'National License'),
        ('international', 'International License'),
        ('both', 'Both National & International')
    ], string='License Type', groups="hr.group_hr_user")
    
    # License Categories
    license_category_motorcycle = fields.Boolean(string='Motorcycle (A)', groups="hr.group_hr_user")
    license_category_car = fields.Boolean(string='Car (B)', groups="hr.group_hr_user")
    license_category_truck = fields.Boolean(string='Truck (C)', groups="hr.group_hr_user")
    license_category_bus = fields.Boolean(string='Bus (D)', groups="hr.group_hr_user")
    license_category_special = fields.Boolean(string='Special (E)', groups="hr.group_hr_user")
    license_categories_other = fields.Char(string='Other Categories', groups="hr.group_hr_user")
    
    # Dates
    driving_license_issue_date = fields.Date(string='Issue Date', groups="hr.group_hr_user")
    driving_license_expiry_date = fields.Date(string='Expiry Date', groups="hr.group_hr_user")
    driving_license_last_renewal = fields.Date(string='Last Renewal', groups="hr.group_hr_user")
    
    # Authority
    license_issuing_authority = fields.Char(string='Issuing Authority', groups="hr.group_hr_user")
    license_issuing_country = fields.Many2one('res.country', string='Issuing Country', groups="hr.group_hr_user")
    license_issuing_state = fields.Char(string='State/Province', groups="hr.group_hr_user")
    
    # International
    international_license_number = fields.Char(string='Intl. License Number', groups="hr.group_hr_user")
    international_license_issue_date = fields.Date(string='Intl. Issue Date', groups="hr.group_hr_user")
    international_license_expiry_date = fields.Date(string='Intl. Expiry Date', groups="hr.group_hr_user")
    
    # Authorization
    authorized_company_vehicle = fields.Boolean(string='Company Vehicle Auth', groups="hr.group_hr_user")
    vehicle_authorization_date = fields.Date(string='Auth Date', groups="hr.group_hr_user")
    preferred_vehicle_type = fields.Selection([
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('van', 'Van'),
        ('truck', 'Truck'),
        ('motorcycle', 'Motorcycle'),
        ('other', 'Other')
    ], string='Preferred Vehicle', groups="hr.group_hr_user")
    
    # Record
    traffic_violations_count = fields.Integer(string='Violations', groups="hr.group_hr_user", default=0)
    last_violation_date = fields.Date(string='Last Violation', groups="hr.group_hr_user")
    driving_points = fields.Integer(string='License Points', groups="hr.group_hr_user", default=0)
    clean_driving_record = fields.Boolean(string='Clean Record', compute='_compute_clean_driving_record', store=True, groups="hr.group_hr_user")
    
    # Insurance
    driving_insurance_policy = fields.Char(string='Insurance Policy', groups="hr.group_hr_user")
    driving_insurance_expiry = fields.Date(string='Insurance Expiry', groups="hr.group_hr_user")
    
    # Additional
    emergency_driver_contact = fields.Char(string='Emergency Contact', groups="hr.group_hr_user")
    driving_license_notes = fields.Text(string='Notes', groups="hr.group_hr_user")
    driving_license_attachment_ids = fields.Many2many('ir.attachment', 'employee_driving_attachment_rel', 'employee_id', 'attachment_id', string='Documents', groups="hr.group_hr_user")
    
    # Computed
    license_expiry_days = fields.Integer(string='Days to Expiry', compute='_compute_license_expiry_days', groups="hr.group_hr_user")
    license_status = fields.Selection([
        ('valid', 'Valid'),
        ('expiring_soon', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('not_applicable', 'N/A')
    ], string='Status', compute='_compute_license_status', store=True, groups="hr.group_hr_user")
    
    @api.depends('traffic_violations_count', 'last_violation_date')
    def _compute_clean_driving_record(self):
        for record in self:
            if record.traffic_violations_count == 0:
                record.clean_driving_record = True
            elif record.last_violation_date:
                three_years_ago = fields.Date.today() - timedelta(days=1095)
                record.clean_driving_record = record.last_violation_date < three_years_ago
            else:
                record.clean_driving_record = False
    
    @api.depends('driving_license_expiry_date')
    def _compute_license_expiry_days(self):
        today = fields.Date.today()
        for record in self:
            if record.driving_license_expiry_date:
                delta = record.driving_license_expiry_date - today
                record.license_expiry_days = delta.days
            else:
                record.license_expiry_days = 0
    
    @api.depends('has_driving_license', 'driving_license_expiry_date')
    def _compute_license_status(self):
        today = fields.Date.today()
        for record in self:
            if not record.has_driving_license:
                record.license_status = 'not_applicable'
            elif not record.driving_license_expiry_date:
                record.license_status = 'valid'
            elif record.driving_license_expiry_date < today:
                record.license_status = 'expired'
            elif record.driving_license_expiry_date <= today + timedelta(days=30):
                record.license_status = 'expiring_soon'
            else:
                record.license_status = 'valid'
    
    @api.constrains('driving_license_issue_date', 'driving_license_expiry_date')
    def _check_license_dates(self):
        for record in self:
            if record.driving_license_issue_date and record.driving_license_expiry_date:
                if record.driving_license_issue_date >= record.driving_license_expiry_date:
                    raise ValidationError(_("Expiry date must be after issue date."))
    
    @api.onchange('has_driving_license')
    def _onchange_has_driving_license(self):
        if not self.has_driving_license:
            self.driving_license_number = False
            self.driving_license_type = False
            self.authorized_company_vehicle = False
    
    def action_renew_license(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('License Renewal'),
                'message': _('Please update the license expiry date after renewal.'),
                'type': 'warning',
                'sticky': False,
            }
        }
    
    def action_view_license_details(self):
        self.ensure_one()
        return {
            'name': _('License Details'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'views': [(self.env.ref('employee_driving_license.view_employee_license_details_form').id, 'form')],
            'context': {'form_view_initial_mode': 'edit'},
        }