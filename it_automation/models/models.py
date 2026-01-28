
# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)


class ITServiceRequest(models.Model):
    _name = 'it.service.request'
    _description = 'IT Service Request'
    _order = 'create_date desc'

    name = fields.Char(
        string="Tiêu đề",
        required=True
    )
    request_type = fields.Selection(
        [
            ('onboarding', 'Nhân viên mới'),
            ('subdomain', 'Cấp Subdomain'),
            ('temp_access', 'Quyền tạm thời'),
            ('clear_cache', 'Xóa Cache CDN (Cloudflare)'),
            ('reset_pwd', 'Cấp lại mật khẩu hệ thống'),
            ('offboarding', 'Thu hồi tài nguyên')
        ],
        string="Loại yêu cầu",
        default='onboarding',
        required=True
    )
    employee_name = fields.Char(string="Tên nhân viên")
    employee_email = fields.Char(string="Email")
    subdomain_name = fields.Char(string="Tên Subdomain")
    gitlab_project_id = fields.Char(string="GitLab Project ID")
    target_ip = fields.Char(string="Target IP")
    response_log = fields.Text(string="Response Log", readonly=True)
    duration = fields.Selection([
        ('1', '1 Giờ'),
        ('4', '4 Giờ'),
        ('8', '8 Giờ (1 Ca)'),
        ('24', '24 Giờ (1 Ngày)'),
        ('72', '72 Giờ (3 Ngày)'),
    ], string="Thời hạn cấp", default='1')
    state = fields.Selection(
        [
            ('draft', 'Nháp'),
            ('processing', 'Đang xử lý'),
            ('done', 'Hoàn thành'),
            ('failed', 'Thất bại')
        ],
        default='draft',
        string="Trạng thái",
        required=True
    )

    def action_approve_and_send(self):
        """
        Duyệt và gửi request đến n8n webhook
        """
        self.ensure_one()
        if self.state == 'processing':
            raise UserError('Yêu cầu này đang được xử lý, vui lòng không gửi lại!')

        # Validation
        if self.request_type in ['onboarding', 'temp_access', 'reset_pwd'] and not self.employee_email:
            raise UserError('Vui lòng nhập email nhân viên!')
        if self.request_type == 'subdomain' and not self.subdomain_name:
            raise UserError('Vui lòng nhập tên subdomain!')

        # Cập nhật trạng thái
        self.state = 'processing'

        # Lấy webhook_url từ System Parameters, nếu không có thì dùng mặc định
        webhook_url = self.env['ir.config_parameter'].sudo().get_param(
            'it_automation.webhook_url',
            'http://localhost:5678/webhook/it-request'
        )
        payload = {
            "request_id": self.id,
            "name": self.name,
            "type": self.request_type,
            "duration": self.duration if self.request_type == 'temp_access' else None,
            "email": self.employee_email,
            "employee_name": self.employee_name,
            "subdomain": self.subdomain_name,
            "created_by_id": self.create_uid.id,      
            "created_by_name": self.create_uid.name,  
            "target_ip": self.target_ip,
            "gitlab_project_id": self.gitlab_project_id
        }

        try:
            # Gửi request với timeout
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )

            # Log response
            log_message = (
                f"""
            ============================== IT Request Log ==============================
            Request Sent:
                URL         : {webhook_url}
                Status Code : {response.status_code}
                Response    : {response.text}
                Timestamp   : {fields.Datetime.now()}
            ==========================================================================="""
            )
            self.response_log = log_message

        except requests.exceptions.Timeout:
            self.state = 'failed'
            self.response_log = (
                f"Timeout khi gọi webhook\nTimestamp: {fields.Datetime.now()}"
            )
            raise UserError('Timeout: Không thể kết nối đến n8n webhook!')

        except requests.exceptions.ConnectionError:
            self.state = 'failed'
            self.response_log = (
                f"Connection Error\nTimestamp: {fields.Datetime.now()}"
            )
            raise UserError('Lỗi: Không thể kết nối đến n8n webhook. Kiểm tra xem n8n đã chạy chưa!')

        except Exception as e:
            self.state = 'failed'
            self.response_log = (
                f"Error: {str(e)}\nTimestamp: {fields.Datetime.now()}"
            )
            _logger.error(f"Error processing IT request {self.name}: {str(e)}")
            raise UserError(f'Đã xảy ra lỗi: {str(e)}')

        return True

    def action_reset_to_draft(self):
        """
        Reset về trạng thái nháp
        """
        self.state = 'draft'
        return True