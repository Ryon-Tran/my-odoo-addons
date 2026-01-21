# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import requests
import logging

_logger = logging.getLogger(__name__)

class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    # ==================== GITLAB & DEVOPS ====================
    it_gitlab_url = fields.Char(
        string='GitLab Repository',
        help='Đường dẫn tới repository GitLab của dự án'
    )
    
    it_gitlab_project_id = fields.Integer(
        string='GitLab Project ID',
        help='ID của project trên GitLab để call API'
    )
    
    it_pipeline_status = fields.Selection([
        ('success', 'Thành công'),
        ('failed', 'Thất bại'),
        ('running', 'Đang chạy'),
        ('pending', 'Chờ xử lý')
    ],
        string='Pipeline Status',
        default='pending',
        help='Trạng thái pipeline CI/CD của dự án'
    )
    
    it_last_pipeline_id = fields.Char(
        string='Last Pipeline ID',
        help='ID của pipeline gần nhất'
    )
    
    it_last_pipeline_url = fields.Char(
        string='Pipeline URL',
        help='Link trực tiếp đến pipeline trên GitLab'
    )
    
    it_last_deployment_date = fields.Datetime(
        string='Last Deployment',
        help='Thời điểm deploy gần nhất'
    )
    
    it_deployment_branch = fields.Char(
        string='Deployment Branch',
        default='main',
        help='Branch đang được deploy (main, staging, production)'
    )
    
    it_last_commit_message = fields.Text(
        string='Last Commit',
        help='Message của commit gần nhất'
    )
    
    it_deployment_author = fields.Char(
        string='Deploy Author',
        help='Người thực hiện deployment gần nhất'
    )
    
    # ==================== INFRASTRUCTURE ====================
    it_domain = fields.Char(
        string='Domain',
        help='Tên miền chính của hệ thống'
    )
    
    it_domain_aliases = fields.Text(
        string='Domain Aliases',
        help='Các domain phụ (mỗi domain một dòng)'
    )
    
    it_server_ip = fields.Char(
        string='Server IP',
        help='IP address của server'
    )
    
    it_hosting_provider = fields.Selection([
        ('aws', 'Amazon AWS'),
        ('gcp', 'Google Cloud'),
        ('azure', 'Microsoft Azure'),
        ('digitalocean', 'DigitalOcean'),
        ('vultr', 'Vultr'),
        ('vps', 'VPS/Custom'),
        ('other', 'Other')
    ],
        string='Hosting Provider',
        help='Nhà cung cấp hosting'
    )
    
    # ==================== SSL & SECURITY ====================
    it_ssl_status = fields.Selection([
        ('active', 'Đã kích hoạt'),
        ('expired', 'Hết hạn'),
        ('expiring_soon', 'Sắp hết hạn'),
        ('none', 'Chưa có')
    ],
        string='SSL Status',
        default='none',
        help='Trạng thái chứng chỉ SSL'
    )
    
    it_ssl_expiry_date = fields.Date(
        string='SSL Expiry Date',
        help='Ngày hết hạn SSL certificate'
    )
    
    it_ssl_issuer = fields.Char(
        string='SSL Issuer',
        default='Let\'s Encrypt',
        help='Nhà phát hành SSL (Let\'s Encrypt, Cloudflare, etc.)'
    )
    
    it_ssl_auto_renew = fields.Boolean(
        string='Auto Renew SSL',
        default=True,
        help='Tự động gia hạn SSL'
    )
    
    # ==================== CLOUDFLARE ====================
    it_cloudflare_zone_id = fields.Char(
        string='Cloudflare Zone ID',
        help='ID định danh Zone trên Cloudflare'
    )
    
    it_cloudflare_status = fields.Selection([
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('none', 'Not Using')
    ],
        string='Cloudflare Status',
        default='none'
    )
    
    it_cloudflare_plan = fields.Selection([
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('business', 'Business'),
        ('enterprise', 'Enterprise')
    ],
        string='Cloudflare Plan',
        default='free'
    )
    
    it_last_cache_purge = fields.Datetime(
        string='Last Cache Purge',
        help='Lần clear cache gần nhất'
    )
    
    # ==================== CHATWOOT & SUPPORT ====================
    it_chatwoot_website_token = fields.Char(
        string='Chatwoot Website Token',
        help='Token để nhúng widget chat vào website'
    )
    
    it_chatwoot_inbox_id = fields.Char(
        string='Chatwoot Inbox ID',
        help='ID của inbox trên Chatwoot'
    )
    
    it_chatwoot_dashboard_url = fields.Char(
        string='Chatwoot Dashboard',
        compute='_compute_chatwoot_dashboard',
        help='Link truy cập dashboard Chatwoot'
    )
    
    it_support_email = fields.Char(
        string='Support Email',
        help='Email hỗ trợ khách hàng'
    )
    
    it_total_support_tickets = fields.Integer(
        string='Total Support Tickets',
        compute='_compute_support_stats',
        help='Tổng số ticket từ Chatwoot'
    )
    
    it_open_support_tickets = fields.Integer(
        string='Open Tickets',
        compute='_compute_support_stats',
        help='Số ticket đang mở'
    )
    
    # ==================== AI ANALYSIS ====================
    it_ai_analysis = fields.Html(
        string='AI Analysis',
        help='Báo cáo phân tích từ Gemini AI qua n8n'
    )
    
    it_last_ai_analysis_date = fields.Datetime(
        string='Last AI Analysis',
        help='Thời điểm phân tích AI gần nhất'
    )
    
    it_ai_risk_level = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical')
    ],
        string='AI Risk Assessment',
        help='Đánh giá rủi ro từ AI'
    )
    
    # ==================== MONITORING & ALERTS ====================
    it_monitoring_enabled = fields.Boolean(
        string='Monitoring Enabled',
        default=False,
        help='Bật monitoring cho hệ thống'
    )
    
    it_uptime_percentage = fields.Float(
        string='Uptime %',
        digits=(5, 2),
        help='Tỷ lệ uptime của hệ thống'
    )
    
    it_last_downtime = fields.Datetime(
        string='Last Downtime',
        help='Lần downtime gần nhất'
    )
    
    it_alert_webhook_url = fields.Char(
        string='Alert Webhook',
        help='URL nhận alert khi có sự cố (Slack, Discord, Telegram)'
    )
    
    # ==================== TECHNICAL STACK ====================
    it_tech_stack = fields.Text(
        string='Tech Stack',
        help='Công nghệ sử dụng (Frontend, Backend, Database, etc.)'
    )
    
    it_framework = fields.Char(
        string='Framework',
        help='Framework chính (React, Vue, Laravel, Django, etc.)'
    )
    
    it_database = fields.Selection([
        ('postgresql', 'PostgreSQL'),
        ('mysql', 'MySQL'),
        ('mongodb', 'MongoDB'),
        ('redis', 'Redis'),
        ('sqlite', 'SQLite'),
        ('other', 'Other')
    ],
        string='Database',
        help='Database đang sử dụng'
    )
    
    it_server_type = fields.Selection([
        ('docker', 'Docker'),
        ('kubernetes', 'Kubernetes'),
        ('vm', 'Virtual Machine'),
        ('bare_metal', 'Bare Metal'),
        ('serverless', 'Serverless')
    ],
        string='Server Type',
        help='Loại server deployment'
    )
    
    # ==================== BACKUP & RECOVERY ====================
    it_backup_enabled = fields.Boolean(
        string='Backup Enabled',
        default=False
    )
    
    it_backup_frequency = fields.Selection([
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ],
        string='Backup Frequency',
        default='daily'
    )
    
    it_last_backup_date = fields.Datetime(
        string='Last Backup',
        help='Lần backup gần nhất'
    )
    
    it_backup_location = fields.Char(
        string='Backup Location',
        help='Nơi lưu trữ backup (S3, Google Drive, etc.)'
    )
    
    # ==================== COMPUTED FIELDS ====================
    @api.depends('it_chatwoot_inbox_id')
    def _compute_chatwoot_dashboard(self):
        for record in self:
            if record.it_chatwoot_inbox_id:
                # Giả sử bạn có base URL của Chatwoot
                base_url = self.env['ir.config_parameter'].sudo().get_param('chatwoot.base_url', '')
                record.it_chatwoot_dashboard_url = f"{base_url}/app/accounts/1/inbox/{record.it_chatwoot_inbox_id}"
            else:
                record.it_chatwoot_dashboard_url = False
    
    @api.depends('task_ids')
    def _compute_support_stats(self):
        for record in self:
            support_tasks = record.task_ids.filtered(
                lambda t: '[Support]' in t.name or '[Chatwoot]' in t.name
            )
            record.it_total_support_tickets = len(support_tasks)
            record.it_open_support_tickets = len(support_tasks.filtered(
                lambda t: t.stage_id.is_closed == False
            ))
    
    # ==================== AUTOMATED CHECKS ====================
    @api.model
    def _cron_check_ssl_expiry(self):
        """Scheduled action: Kiểm tra SSL sắp hết hạn"""
        projects = self.search([
            ('it_ssl_status', '=', 'active'),
            ('it_ssl_expiry_date', '!=', False)
        ])
        
        today = fields.Date.today()
        warning_days = 30  # Cảnh báo trước 30 ngày
        
        for project in projects:
            days_until_expiry = (project.it_ssl_expiry_date - today).days
            
            if days_until_expiry <= 0:
                project.it_ssl_status = 'expired'
                project.message_post(
                    body=_('⚠️ SSL Certificate has EXPIRED! Please renew immediately.'),
                    subject=_('SSL Expired: %s') % project.name
                )
            elif days_until_expiry <= warning_days:
                project.it_ssl_status = 'expiring_soon'
                project.message_post(
                    body=_('⚠️ SSL Certificate will expire in %d days.') % days_until_expiry,
                    subject=_('SSL Expiring Soon: %s') % project.name
                )
    
    @api.model
    def _cron_check_pipeline_status(self):
        """Scheduled action: Kiểm tra pipeline failed > 24h"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        projects = self.search([
            ('it_pipeline_status', '=', 'failed'),
            ('it_last_deployment_date', '<', cutoff_time)
        ])
        
        for project in projects:
            project.message_post(
                body=_('⚠️ Pipeline has been FAILED for more than 24 hours!'),
                subject=_('Pipeline Alert: %s') % project.name,
                subtype_xmlid='mail.mt_comment'
            )
    
    # ==================== ACTION METHODS ====================
    def action_open_gitlab(self):
        """Smart button: Mở GitLab repository"""
        self.ensure_one()
        if not self.it_gitlab_url:
            raise ValidationError(_('GitLab URL is not configured!'))
        return {
            'type': 'ir.actions.act_url',
            'url': self.it_gitlab_url,
            'target': 'new'
        }
    
    def action_open_domain(self):
        """Smart button: Mở website"""
        self.ensure_one()
        if not self.it_domain:
            raise ValidationError(_('Domain is not configured!'))
        url = self.it_domain if self.it_domain.startswith('http') else f'https://{self.it_domain}'
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new'
        }
    
    def action_open_chatwoot(self):
        """Smart button: Mở Chatwoot dashboard"""
        self.ensure_one()
        if not self.it_chatwoot_dashboard_url:
            raise ValidationError(_('Chatwoot is not configured!'))
        return {
            'type': 'ir.actions.act_url',
            'url': self.it_chatwoot_dashboard_url,
            'target': 'new'
        }
    
    def action_purge_cloudflare_cache(self):
        """Button action: Manual clear Cloudflare cache"""
        self.ensure_one()
        if not self.it_cloudflare_zone_id:
            raise ValidationError(_('Cloudflare Zone ID is not configured!'))
        
        # Trigger n8n webhook để clear cache
        n8n_webhook_url = self.env['ir.config_parameter'].sudo().get_param('n8n.cloudflare_webhook_url', '')
        if n8n_webhook_url:
            try:
                response = requests.post(n8n_webhook_url, json={
                    'zone_id': self.it_cloudflare_zone_id,
                    'project_name': self.name,
                    'trigger': 'manual'
                }, timeout=10)
                
                if response.status_code == 200:
                    self.it_last_cache_purge = fields.Datetime.now()
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Success'),
                            'message': _('Cloudflare cache cleared successfully!'),
                            'type': 'success',
                            'sticky': False,
                        }
                    }
            except Exception as e:
                _logger.error(f"Failed to purge Cloudflare cache: {str(e)}")
                raise ValidationError(_('Failed to clear cache: %s') % str(e))