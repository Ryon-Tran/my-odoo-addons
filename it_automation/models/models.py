from odoo import models, fields, api
import requests

class ITServiceRequest(models.Model):
    _name = 'it.service.request'
    _description = 'IT Service Request'

    name = fields.Char(string="Tiêu đề", required=True)
    request_type = fields.Selection([
        ('onboarding', 'Nhân viên mới'),
        ('subdomain', 'Cấp Subdomain'),
        ('temp_access', 'Quyền tạm thời')
    ], string="Loại yêu cầu", default='onboarding')

    employee_name = fields.Char(string="Tên nhân viên")
    employee_email = fields.Char(string="Email")
    subdomain_name = fields.Char(string="Tên Subdomain")
    gitlab_project_id = fields.Char(string="GitLab Project ID")
    target_ip = fields.Char(string="Target IP")
    response_log = fields.Text(string="Response Log")
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('done', 'Hoàn thành')
    ], default='draft')

    def action_approve(self):
        # Link webhook từ n8n của bạn
        url = "http://localhost:5678/webhook/it-request"
        data = {
            "name": self.name,
            "type": self.request_type,
            "email": self.employee_email
        }
        try:
            requests.post(url, json=data)
            self.state = 'done'
        except:
            pass

    def action_approve_and_send(self):
        return self.action_approve()
