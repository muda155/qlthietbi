from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
import io
import qrcode

class Department(models.Model):
    name = models.CharField(max_length = 100, verbose_name = "Tên ngành")
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "1. Quản lý ngành"

class Device(models.Model):
    department = models.ForeignKey(Department, on_delete = models.CASCADE, verbose_name = "Thuộc ngành")
    name = models.CharField(max_length = 200, verbose_name="Tên thiết bị")
    description = models.TextField(blank = True, verbose_name = "Mô tả") 
    total_system_hours = models.FloatField(default = 0.0, verbose_name = "Tổng giờ tích luỹ")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "3. Hệ thống thiết bị (Cha)"
        verbose_name_plural = "3. Hệ thống thiết bị (Cha)"

class Location(models.Model):
    name = models.CharField(max_length = 100, verbose_name = "Tên vị trí/Khoang hầm")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "2. Danh mục vị trí"

class DeviceUnit(models.Model):
    STATUS_CHOICES = [
        ('NORMAL', 'Hoạt động bình thường'),
        ('MAINTENANCE','Bảo dưỡng'),
        ('ERROR', 'Lỗi')
    ]

    device = models.ForeignKey(Device, on_delete = models.CASCADE, related_name = 'units', verbose_name = "Thuộc Hệ thống")
    location = models.ForeignKey(Location, on_delete = models.SET_NULL, null = True, verbose_name = "Vị trí lắp đặt")
    name = models.CharField(max_length = 200, verbose_name = "Tên khối")
    qr_code = models.CharField(max_length = 50, unique = True, verbose_name = "Mã QR")
    qr_image = models.ImageField(upload_to='qr_codes/units/', blank=True, null=True, verbose_name="Mã QR")

    current_hours = models.FloatField(default = 0.0, verbose_name = "Giờ chạy")  
    maintenance_threshold = models.FloatField(default = 500.0, verbose_name = "Định mức bảo dưỡng")
    status = models.CharField(max_length  = 20, choices = STATUS_CHOICES, default = 'NORMAL', verbose_name = "Trạng thái")

    def generate_qr_code(self):
        """Generate QR code image from unit qr_code"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.qr_code)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        filename = f"unit_{self.id or 'new'}_{self.qr_code}.png"
        self.qr_image.save(filename, ContentFile(img_io.getvalue()), save=False)
    
    def save(self, *args, **kwargs):
        if not self.qr_image and self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "4. Khối chi tiết"
        verbose_name_plural = "4. Khối chi tiết"

class MaintenanceOrder(models.Model):
    """Maintenance and Repair Order Model"""
    
    # Priority Choices
    PRIORITY_CHOICES = [
        ('LOW', 'Thấp'),
        ('HIGH', 'Cao'),
        ('CRITICAL', 'Khẩn cấp')
    ]
    
    # Status Choices
    STATUS_CHOICES = [
        ('PENDING', 'Chờ duyệt'),
        ('APPROVED', 'Đã duyệt'),
        ('COMPLETED', 'Đã hoàn thành'),
        ('VERIFIED', 'Đã nghiệm thu'),
        ('CANCELLED', 'Đã hủy')
    ]
    
    device_unit = models.ForeignKey(DeviceUnit, on_delete=models.CASCADE, related_name='maintenance_orders', verbose_name="Khối thiết bị")
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maintenance_reports', verbose_name="Người báo cáo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian tạo")
    description = models.TextField(verbose_name="Mô tả sự cố")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='LOW', verbose_name="Mức độ ưu tiên")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Trạng thái")
    
    # Assignment fields
    assigned_to_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_maintenance', verbose_name="Giao cho (User)")
    assigned_to_name = models.CharField(max_length=100, blank=True, verbose_name="Giao cho (Tên)")
    
    solution = models.TextField(blank=True, verbose_name="Giải pháp sửa chữa")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian hoàn thành")
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        
        if not is_new:
            try:
                old_instance = MaintenanceOrder.objects.get(pk=self.pk)
                old_status = old_instance.status
            except MaintenanceOrder.DoesNotExist:
                pass
        
        # Auto-update device_unit status on creation (PENDING)
        if is_new and self.status == 'PENDING':
            if self.priority == 'CRITICAL':
                self.device_unit.status = 'ERROR'
            else:
                self.device_unit.status = 'MAINTENANCE'
            self.device_unit.save()
        
        # Reset device_unit status when verified
        if old_status != 'VERIFIED' and self.status == 'VERIFIED':
            self.device_unit.status = 'NORMAL'
            self.device_unit.save()
        
        # Auto-set completed_at when status changes to COMPLETED or VERIFIED
        if old_status not in ['COMPLETED', 'VERIFIED'] and self.status in ['COMPLETED', 'VERIFIED']:
            if not self.completed_at:
                self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def get_assigned_display_name(self):
        """Return assigned user's name or fallback to assigned_to_name"""
        if self.assigned_to_user:
            return self.assigned_to_user.get_full_name() or self.assigned_to_user.username
        return self.assigned_to_name or "Chưa phân công"
    
    def __str__(self):
        return f"Lệnh #{self.pk} - {self.device_unit.name} - {self.get_priority_display()}"
    
    class Meta:
        verbose_name = "6. Lệnh bảo dưỡng/Sửa chữa"
        verbose_name_plural = "6. Lệnh bảo dưỡng/Sửa chữa"
        ordering = ['-created_at']

class OperationLog(models.Model):
    # Device status choices - reported by operator
    DEVICE_STATUS_CHOICES = [
        ('NORMAL', 'Hoạt động bình thường (C1)'),
        ('MAINTENANCE', 'Cần bảo dưỡng (C2)'),
        ('ERROR', 'Hỏng hóc/Sự cố')
    ]

    # Approval Status Choices
    STATUS_CHOICES = [
        ('PENDING', 'Chờ duyệt'),
        ('APPROVED', 'Đã duyệt'),
        ('REJECTED', 'Từ chối')
    ]
    
    device = models.ForeignKey(Device, on_delete = models.CASCADE, verbose_name = "Chọn thiết bị")
    device_unit = models.ForeignKey(DeviceUnit, on_delete = models.CASCADE, null=True, blank=True, verbose_name = "Khối chi tiết")
    
    # Auth & Tracking
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logs_created', verbose_name="Người lập", null=True, blank=True)
    operator_name = models.CharField(max_length = 50, verbose_name = "Người thực hiện (Legacy)", blank=True, null=True)
    
    # Approval fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Trạng thái duyệt")
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='logs_verified', null=True, blank=True, verbose_name="Người duyệt")
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian duyệt")
    rejection_reason = models.TextField(blank=True, verbose_name="Lý do từ chối")

    start_time = models.DateTimeField(verbose_name = "Thời gian bật")
    end_time = models.DateTimeField(verbose_name = "Thời gian tắt")
    duration = models.FloatField(blank = True, null = True, verbose_name = "Giờ hoạt động (h)")
    device_status = models.CharField(max_length = 20, choices = DEVICE_STATUS_CHOICES, default = 'NORMAL', verbose_name = "Trạng thái thiết bị khi tắt máy")
    notes = models.TextField(blank = True, verbose_name = "Ghi chú/Mô tả vấn đề")
    
    def save(self, *args, **kwargs):
        # Calculate duration only if both times are set
        if self.start_time and self.end_time:
            diff = self.end_time - self.start_time
            # Only process if duration is positive
            if diff.total_seconds() > 0:
                self.duration = round(diff.total_seconds() / 3600, 2)
        
        # NOTE: We NO LONGER update device hours here.
        # That logic is moved to approve() method.
        
        super().save(*args, **kwargs)

    def approve(self, user):
        """Approve the log and update device hours"""
        if self.status == 'APPROVED':
            return # Already approved
            
        self.status = 'APPROVED'
        self.verified_by = user
        self.verified_at = timezone.now()
        
        # UPDATE DEVICE HOURS AND STATUS
        if self.duration and self.duration > 0:
            self.device.total_system_hours += self.duration
            self.device.save()
            
            # Update all units
            if self.device.pk:
                units = self.device.units.all()
                for unit in units:
                    unit.current_hours += self.duration
                    unit.status = self.device_status
                    unit.save()
        
        self.save()

    def reject(self, user, reason):
        """Reject the log"""
        self.status = 'REJECTED'
        self.verified_by = user
        self.verified_at = timezone.now()
        self.rejection_reason = reason
        self.save()

    def get_operator_display_name(self):
        """Return the operator's full name if available, otherwise username"""
        if self.created_by:
            return self.created_by.get_full_name() or self.created_by.username
        return self.operator_name or "Unknown"
    
    def __str__(self):
        return f"Log: {self.device.name} - {self.duration}h - {self.get_device_status_display()}"
    
    class Meta:
        verbose_name = "5. Nhật ký máy"
        verbose_name_plural = "5. Nhật ký máy"
        ordering = ['-start_time']

