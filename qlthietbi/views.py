from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Q
import json
from datetime import datetime
from .models import Device, DeviceUnit, OperationLog, Location, MaintenanceOrder

def is_commander(user):
    return user.groups.filter(name='Commanders').exists() or user.is_superuser

@login_required
@require_http_methods(["GET"])
def dashboard(request):
    """Dashboard view - shows summary cards and recent logs"""
    normal_count = DeviceUnit.objects.filter(status='NORMAL').count()
    maintenance_count = DeviceUnit.objects.filter(status='MAINTENANCE').count()
    error_count = DeviceUnit.objects.filter(status='ERROR').count()
    
    # Recent logs (Approved or created by me)
    recent_logs = OperationLog.objects.filter(status='APPROVED').order_by('-start_time')[:10]
    
    context = {
        'normal_count': normal_count,
        'maintenance_count': maintenance_count,
        'error_count': error_count,
        'recent_logs': recent_logs,
        'is_commander': is_commander(request.user),
    }

    # Commander specific context
    if is_commander(request.user):
        pending_logs = OperationLog.objects.filter(status='PENDING').order_by('start_time')
        context['pending_logs'] = pending_logs
        context['pending_count'] = pending_logs.count()

    return render(request, 'qlthietbi/dashboard.html', context)

@login_required
@require_http_methods(["GET"])
def scan(request):
    """QR Scanner view - displays scanner interface"""
    return render(request, 'qlthietbi/scan.html')

@require_http_methods(["GET"])
def offline(request):
    """Offline fallback view - shown when network is unavailable"""
    return render(request, 'qlthietbi/offline.html')

@login_required
@require_http_methods(["GET"])
def device_detail(request, qr_code):
    """Device detail view - shows device and units after QR scan"""
    device_unit = get_object_or_404(DeviceUnit, qr_code=qr_code)
    device = device_unit.device
    all_units = device.units.all()
    
    # Get active maintenance orders for this device_unit
    active_maintenance_orders = device_unit.maintenance_orders.exclude(
        status__in=['VERIFIED', 'CANCELLED']
    ).order_by('-created_at')
    
    context = {
        'device': device,
        'device_unit': device_unit,
        'all_units': all_units,
        'active_maintenance_orders': active_maintenance_orders,
        'is_commander': is_commander(request.user),
    }
    return render(request, 'qlthietbi/device_detail.html', context)

@login_required
@require_http_methods(["GET", "POST"])
def log_entry(request, qr_code):
    """Log entry form view - for recording operation logs"""
    device_unit = get_object_or_404(DeviceUnit, qr_code=qr_code)
    device = device_unit.device
    
    if request.method == 'POST':
        # Operator name is now automatic
        operator_name = request.user.get_full_name() or request.user.username
        
        start_time_str = request.POST.get('start_time', '')
        end_time_str = request.POST.get('end_time', '')
        device_status = request.POST.get('device_status', 'NORMAL')
        notes = request.POST.get('notes', '').strip()
        
        if not start_time_str or not end_time_str:
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
                operator_name=operator_name, # Legacy field
                created_by=request.user,     # New Auth field
                start_time=start_time,
                end_time=end_time,
                device_status=device_status,
                notes=notes,
                status='PENDING'             # Default status
            )
            log.save()
            messages.success(request, 'Nhật ký đã được gửi và đang chờ duyệt')
            return redirect('device_detail', qr_code=qr_code)
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
            return redirect('log_entry', qr_code=qr_code)
    
    context = {
        'device': device,
        'device_unit': device_unit,
    }
    return render(request, 'qlthietbi/log_entry.html', context)

@login_required
@require_http_methods(["GET"])
def history(request):
    """History view - displays all operation logs"""
    logs = OperationLog.objects.all().order_by('-start_time')
    
    context = {
        'logs': logs,
    }
    return render(request, 'qlthietbi/history.html', context)

@login_required
@require_http_methods(["POST"])
def approve_log(request, log_id):
    """Approve a log entry (Commander only)"""
    if not is_commander(request.user):
        return HttpResponseForbidden("Bạn không có quyền duyệt nhật ký")
        
    log = get_object_or_404(OperationLog, id=log_id)
    try:
        log.approve(request.user)
        messages.success(request, f"Đã duyệt nhật ký của {log.operator_name}")
    except Exception as e:
        messages.error(request, f"Lỗi: {str(e)}")
        
    return redirect('dashboard')

@login_required
@require_http_methods(["POST"])
def reject_log(request, log_id):
    """Reject a log entry (Commander only)"""
    if not is_commander(request.user):
        return HttpResponseForbidden("Bạn không có quyền từ chối nhật ký")
        
    log = get_object_or_404(OperationLog, id=log_id)
    reason = request.POST.get('reason', '').strip()
    
    try:
        log.reject(request.user, reason)
        messages.warning(request, f"Đã trả lại nhật ký của {log.operator_name}")
    except Exception as e:
        messages.error(request, f"Lỗi: {str(e)}")
        
    return redirect('dashboard')

@require_http_methods(["POST"])
def api_log_entry(request, qr_code):
    """API endpoint for submitting operation logs (AJAX support for offline sync)"""
    if not request.user.is_authenticated:
         return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=401)

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
        
        # Operator name is automatic
        operator_name = request.user.get_full_name() or request.user.username
        
        start_time_str = data.get('start_time', '')
        end_time_str = data.get('end_time', '')
        device_status = data.get('device_status', 'NORMAL')
        notes = data.get('notes', '').strip()
        
        # Validation
        if not all([start_time_str, end_time_str]):
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
            created_by=request.user,
            start_time=start_time,
            end_time=end_time,
            device_status=device_status,
            notes=notes,
            status='PENDING'
        )
        log.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Nhật ký đã được gửi và đang chờ duyệt',
            'log_id': log.id,
            'duration': log.duration,
            'device_status': log.get_device_status_display(),
        })
    
    except Exception as e:
        return JsonResponse(
            {'success': False, 'message': f'Lỗi: {str(e)}'},
            status=500
        )

# ========== MAINTENANCE VIEWS ==========

@login_required
@require_http_methods(["GET", "POST"])
def create_maintenance_order(request, qr_code):
    """Create maintenance order (Commanders only)"""
    if not is_commander(request.user):
        return HttpResponseForbidden("Chỉ Trưởng ngành mới có quyền tạo lệnh bảo dưỡng")
    
    device_unit = get_object_or_404(DeviceUnit, qr_code=qr_code)
    
    if request.method == 'POST':
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', 'LOW')
        
        if not description:
            messages.error(request, 'Vui lòng nhập mô tả sự cố')
            return redirect('create_maintenance', qr_code=qr_code)
        
        try:
            order = MaintenanceOrder(
                device_unit=device_unit,
                reported_by=request.user,
                description=description,
                priority=priority,
                status='PENDING'
            )
            order.save()
            messages.success(request, 'Đã tạo lệnh bảo dưỡng/sửa chữa')
            return redirect('device_detail', qr_code=qr_code)
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
            return redirect('create_maintenance', qr_code=qr_code)
    
    context = {
        'device_unit': device_unit,
        'device': device_unit.device,
    }
    return render(request, 'qlthietbi/maintenance_form.html', context)

@login_required
@require_http_methods(["GET"])
def maintenance_list(request):
    """List maintenance orders based on user role"""
    status_filter = request.GET.get('status', '')
    
    if is_commander(request.user):
        # Commanders see all orders
        orders = MaintenanceOrder.objects.all()
    else:
        # Workers see only orders assigned to them
        orders = MaintenanceOrder.objects.filter(assigned_to_user=request.user)
    
    # Apply status filter if provided
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Order by status priority (PENDING first) then by date
    status_order = {
        'PENDING': 1,
        'APPROVED': 2,
        'COMPLETED': 3,
        'VERIFIED': 4,
        'CANCELLED': 5
    }
    orders = sorted(orders, key=lambda x: (status_order.get(x.status, 999), -x.created_at.timestamp()))
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'is_commander': is_commander(request.user),
    }
    return render(request, 'qlthietbi/maintenance_list.html', context)

@login_required
@require_http_methods(["GET"])
def maintenance_detail(request, order_id):
    """View maintenance order details"""
    order = get_object_or_404(MaintenanceOrder, id=order_id)
    
    # Check permission: Commander or assigned worker
    if not is_commander(request.user) and order.assigned_to_user != request.user:
        return HttpResponseForbidden("Bạn không có quyền xem lệnh này")
    
    context = {
        'order': order,
        'is_commander': is_commander(request.user),
        'can_complete': order.assigned_to_user == request.user and order.status == 'APPROVED',
    }
    return render(request, 'qlthietbi/maintenance_detail.html', context)

@login_required
@require_http_methods(["GET", "POST"])
def update_maintenance_order(request, order_id):
    """Update maintenance order (Commanders only)"""
    if not is_commander(request.user):
        return HttpResponseForbidden("Chỉ Trưởng ngành mới có quyền cập nhật lệnh")
    
    order = get_object_or_404(MaintenanceOrder, id=order_id)
    
    if request.method == 'POST':
        try:
            order.status = request.POST.get('status', order.status)
            order.priority = request.POST.get('priority', order.priority)
            
            # Assignment
            assigned_user_id = request.POST.get('assigned_to_user', '')
            if assigned_user_id:
                from django.contrib.auth.models import User
                order.assigned_to_user = User.objects.get(id=assigned_user_id)
            else:
                order.assigned_to_user = None
            
            order.assigned_to_name = request.POST.get('assigned_to_name', '').strip()
            order.solution = request.POST.get('solution', '').strip()
            
            order.save()
            messages.success(request, 'Đã cập nhật lệnh bảo dưỡng')
            return redirect('maintenance_list')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
            return redirect('update_maintenance', order_id=order_id)
    
    # Get all users for assignment dropdown
    from django.contrib.auth.models import User
    users = User.objects.filter(is_active=True).order_by('username')
    
    context = {
        'order': order,
        'users': users,
    }
    return render(request, 'qlthietbi/maintenance_update.html', context)

@login_required
@require_http_methods(["POST"])
def complete_maintenance_order(request, order_id):
    """Mark maintenance order as completed (Assigned workers only)"""
    order = get_object_or_404(MaintenanceOrder, id=order_id)
    
    # Check permission: Must be assigned worker and status must be APPROVED
    if order.assigned_to_user != request.user:
        return HttpResponseForbidden("Bạn không được giao công việc này")
    
    if order.status != 'APPROVED':
        messages.error(request, 'Chỉ có thể hoàn thành lệnh đã được duyệt')
        return redirect('maintenance_detail', order_id=order_id)
    
    try:
        order.solution = request.POST.get('solution', '').strip()
        order.status = 'COMPLETED'
        order.completed_at = timezone.now()
        order.save()
        messages.success(request, 'Đã đánh dấu hoàn thành công việc')
        return redirect('maintenance_list')
    except Exception as e:
        messages.error(request, f'Lỗi: {str(e)}')
        return redirect('maintenance_detail', order_id=order_id)
