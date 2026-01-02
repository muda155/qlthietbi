from django.contrib import admin
from django.utils.html import format_html
from .models import Department, Location, Device, DeviceUnit, OperationLog

# Register your models here.
class DeviceUnitInline(admin.TabularInline):
    model = DeviceUnit
    extra = 1
    fields = ('name', 'qr_code', 'location', 'current_hours', 'status')
    readonly_fields = ('current_hours',)

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'total_system_hours')
    list_filter = ('department',)
    search_fields = ('name',)
    inlines = [DeviceUnitInline]

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class DeviceUnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'device', 'location', 'qr_code', 'status', 'current_hours', 'qr_image_preview')
    list_filter = ('status', 'device', 'location')
    search_fields = ('name', 'qr_code')
    readonly_fields = ('current_hours', 'qr_image_preview')
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('device', 'location', 'name', 'qr_code')
        }),
        ('Mã QR', {
            'fields': ('qr_image_preview', 'qr_image'),
            'description': 'Mã QR sẽ được tự động tạo khi lưu'
        }),
        ('Tham số hoạt động', {
            'fields': ('current_hours', 'maintenance_threshold', 'status')
        }),
    )
    
    def qr_image_preview(self, obj):
        if obj.qr_image:
            return format_html(
                '<img src="{}" width="200" height="200" />',
                obj.qr_image.url
            )
        return "Mã QR sẽ được tạo sau khi lưu lần đầu"
    qr_image_preview.short_description = "Xem trước mã QR"

class OperationLogAdmin(admin.ModelAdmin):
    list_display = ('device', 'operator_name', 'start_time', 'end_time', 'duration')
    list_filter = ('device', 'start_time')
    search_fields = ('operator_name', 'device__name')
    readonly_fields = ('duration',)
    fieldsets = (
        ('Thiết bị', {
            'fields': ('device',)
        }),
        ('Thông tin người vận hành', {
            'fields': ('operator_name',)
        }),
        ('Thời gian hoạt động', {
            'fields': ('start_time', 'end_time', 'duration')
        }),
    )

admin.site.register(Department, DepartmentAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(DeviceUnit, DeviceUnitAdmin)
admin.site.register(OperationLog, OperationLogAdmin)
