from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
import json
from datetime import datetime
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
def offline(request):
    """Offline fallback view - shown when network is unavailable"""
    return render(request, 'qlthietbi/offline.html')

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
        operator_name = request.POST.get('operator_name', '').strip()
        start_time_str = request.POST.get('start_time', '')
        end_time_str = request.POST.get('end_time', '')
        device_status = request.POST.get('device_status', 'NORMAL')
        notes = request.POST.get('notes', '').strip()
        
        if not operator_name or not start_time_str or not end_time_str:
            messages.error(request, 'Vui lòng điền đầy đủ thông tin')
            return redirect('log_entry', qr_code=qr_code)
        
        try:
            # Parse datetime strings to datetime objects
            try:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                messages.error(request, 'Định dạng thời gian không hợp lệ')
                return redirect('log_entry', qr_code=qr_code)
            
            # Validate time order
            if end_time <= start_time:
                messages.error(request, 'Giờ tắt máy phải sau giờ nổ máy')
                return redirect('log_entry', qr_code=qr_code)
            
            log = OperationLog(
                device=device,
                device_unit=device_unit,
                operator_name=operator_name,
                start_time=start_time,
                end_time=end_time,
                device_status=device_status,
                notes=notes,
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

@require_http_methods(["POST"])
def api_log_entry(request, qr_code):
    """API endpoint for submitting operation logs (AJAX support for offline sync)"""
    try:
        device_unit = get_object_or_404(DeviceUnit, qr_code=qr_code)
        device = device_unit.device
        
        # Parse JSON body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {'success': False, 'message': 'Invalid JSON'},
                status=400
            )
        
        operator_name = data.get('operator_name', '').strip()
        start_time_str = data.get('start_time', '')
        end_time_str = data.get('end_time', '')
        device_status = data.get('device_status', 'NORMAL')
        notes = data.get('notes', '').strip()
        
        # Validation
        if not all([operator_name, start_time_str, end_time_str]):
            return JsonResponse(
                {'success': False, 'message': 'Vui lòng điền đầy đủ thông tin'},
                status=400
            )
        
        # Parse datetime strings
        try:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return JsonResponse(
                {'success': False, 'message': 'Định dạng thời gian không hợp lệ'},
                status=400
            )
        
        # Validate time order
        if end_time <= start_time:
            return JsonResponse(
                {'success': False, 'message': 'Giờ tắt máy phải sau giờ nổ máy'},
                status=400
            )
        
        # Create log
        log = OperationLog(
            device=device,
            device_unit=device_unit,
            operator_name=operator_name,
            start_time=start_time,
            end_time=end_time,
            device_status=device_status,
            notes=notes,
        )
        log.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Nhật ký vận hành đã được lưu thành công',
            'log_id': log.id,
            'duration': log.duration,
            'device_status': log.get_device_status_display(),
        })
    
    except Exception as e:
        return JsonResponse(
            {'success': False, 'message': f'Lỗi: {str(e)}'},
            status=500
        )

