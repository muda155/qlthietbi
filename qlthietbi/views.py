from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Device, DeviceUnit, OperationLog, Location

@require_http_methods(["GET"])
def dashboard(request):
    """Dashboard view - shows summary cards and recent logs"""
    normal_count = DeviceUnit.objects.filter(status='NORMAL').count()
    maintenance_count = DeviceUnit.objects.filter(status='MAINTENANCE').count()
    error_count = DeviceUnit.objects.filter(status='ERROR').count()
    
    recent_logs = OperationLog.objects.all().order_by('-start_time')[:10]
    
    context = {
        'normal_count': normal_count,
        'maintenance_count': maintenance_count,
        'error_count': error_count,
        'recent_logs': recent_logs,
    }
    return render(request, 'qlthietbi/dashboard.html', context)

@require_http_methods(["GET"])
def scan(request):
    """QR Scanner view - displays scanner interface"""
    return render(request, 'qlthietbi/scan.html')

@require_http_methods(["GET"])
def device_detail(request, qr_code):
    """Device detail view - shows device and units after QR scan"""
    device_unit = get_object_or_404(DeviceUnit, qr_code=qr_code)
    device = device_unit.device
    all_units = device.units.all()
    
    context = {
        'device': device,
        'device_unit': device_unit,
        'all_units': all_units,
    }
    return render(request, 'qlthietbi/device_detail.html', context)

@require_http_methods(["GET", "POST"])
def log_entry(request, qr_code):
    """Log entry form view - for recording operation logs"""
    device_unit = get_object_or_404(DeviceUnit, qr_code=qr_code)
    device = device_unit.device
    
    if request.method == 'POST':
        operator_name = request.POST.get('operator_name', '')
        start_time = request.POST.get('start_time', '')
        end_time = request.POST.get('end_time', '')
        
        if not operator_name or not start_time or not end_time:
            messages.error(request, 'Vui lòng điền đầy đủ thông tin')
            return redirect('log_entry', qr_code=qr_code)
        
        try:
            log = OperationLog(
                device=device,
                operator_name=operator_name,
                start_time=start_time,
                end_time=end_time,
            )
            log.save()
            messages.success(request, 'Nhật ký vận hành đã được lưu thành công')
            return redirect('device_detail', qr_code=qr_code)
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
            return redirect('log_entry', qr_code=qr_code)
    
    context = {
        'device': device,
        'device_unit': device_unit,
    }
    return render(request, 'qlthietbi/log_entry.html', context)

@require_http_methods(["GET"])
def history(request):
    """History view - displays all operation logs"""
    logs = OperationLog.objects.all().order_by('-start_time')
    
    context = {
        'logs': logs,
    }
    return render(request, 'qlthietbi/history.html', context)
