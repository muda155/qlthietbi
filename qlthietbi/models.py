from django.db import models
from django.utils import timezone
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

class OperationLog(models.Model):
    # Device status choices - reported by operator
    DEVICE_STATUS_CHOICES = [
        ('NORMAL', 'Hoạt động bình thường (C1)'),
        ('MAINTENANCE', 'Cần bảo dưỡng (C2)'),
        ('ERROR', 'Hỏng hóc/Sự cố')
    ]
    
    device = models.ForeignKey(Device, on_delete = models.CASCADE, verbose_name = "Chọn thiết bị")
    device_unit = models.ForeignKey(DeviceUnit, on_delete = models.CASCADE, null=True, blank=True, verbose_name = "Khối chi tiết")
    operator_name = models.CharField(max_length = 50, verbose_name = "Người thực hiện")
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
                self.device.total_system_hours += self.duration
                self.device.save()
                
                # Update all units of this device with:
                # 1. Add operation hours
                # 2. Update status based on operator's report
                if self.device.pk:
                    units = self.device.units.all()
                    for unit in units:
                        # Add duration to each unit's current hours (for tracking)
                        unit.current_hours += self.duration
                        
                        # Update unit status from operator's report
                        unit.status = self.device_status
                        
                        unit.save()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Log: {self.device.name} - {self.duration}h - {self.get_device_status_display()}"
    
    class Meta:
        verbose_name = "5. Nhật ký máy"
        verbose_name_plural = "5. Nhật ký máy"
        ordering = ['-start_time']

