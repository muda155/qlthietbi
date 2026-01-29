# Development Users Documentation

## Overview
This document contains all user accounts created for development and testing of the Digital Technical Logbook (Sổ Kỹ Thuật Số).

## User Accounts

### 1. Commander (Trưởng Ngành)
- **Username**: `truongnganh`
- **Password**: `123456`
- **Full Name**: Trưởng Ngành Kỹ Thuật
- **Email**: truongnganh@example.com
- **Group**: Commanders
- **Permissions**:
  - View all logs (Pending, Approved, Rejected)
  - Approve or Reject submitted logs
  - Access admin panel (if superuser)
  - Manage devices and units

### 2. Operator 1 (Nhân Viên)
- **Username**: `nhanvien1`
- **Password**: `123456`
- **Full Name**: Nguyễn Văn A
- **Email**: nv1@example.com
- **Group**: Operators
- **Permissions**:
  - Scan QR codes
  - Submit operation logs
  - View own logs and approved logs
  - Cannot approve/reject logs

### 3. Operator 2 (Nhân Viên)
- **Username**: `nhanvien2`
- **Password**: `123456`
- **Full Name**: Trần Thị B
- **Email**: nv2@example.com
- **Group**: Operators
- **Permissions**:
  - Scan QR codes
  - Submit operation logs
  - View own logs and approved logs
  - Cannot approve/reject logs

## User Groups

### Commanders
- **Role**: Trưởng Ngành (Department Head)
- **Capabilities**:
  - Full access to all features
  - Approve/Reject operation logs
  - Only approved logs update device running hours
  - View pending logs dashboard

### Operators
- **Role**: Nhân Viên (Staff/Worker)
- **Capabilities**:
  - Submit operation logs (auto status: PENDING)
  - View device information via QR scanning
  - Cannot approve their own logs
  - Logs must be approved by Commander

## Workflow

### Operator Workflow:
1. Login → `/accounts/login/`
2. Scan QR → `/quet-ma/`
3. Fill Log Form → `/ghi-nhat-ky/<qr_code>/`
4. Submit → Status: PENDING
5. Wait for Commander approval

### Commander Workflow:
1. Login → Dashboard shows "Cần duyệt" (Pending Approvals)
2. Review log details
3. Click "Duyệt" (Approve) → Device hours updated, Status: APPROVED
4. Or "Từ chối" (Reject) → Status: REJECTED with reason

## Sample Data

### Departments
- Ngành Máy (Machinery)
- Ngành Điện (Electrical)

### Devices
- **Máy Chính Trái** (Main Engine Left)
  - Unit 1: Động cơ Diesel (QR: `MAY-01`)
  - Unit 2: Hộp số (QR: `MAY-02`)

### Locations
- Hầm máy số 1 (Engine Room #1)

## Testing Scenarios

### Scenario 1: Submit and Approve Log
1. Login as `nhanvien1`
2. Navigate to `/thiet-bi/MAY-01/`
3. Click "Ghi nhật ký"
4. Fill in operation times
5. Submit (Status: PENDING)
6. Logout
7. Login as `truongnganh`
8. View pending log on Dashboard
9. Click "Duyệt" (Approve)
10. Verify device hours increased

### Scenario 2: Submit and Reject Log
1. Login as `nhanvien2`
2. Submit a log (Status: PENDING)
3. Logout
4. Login as `truongnganh`
5. Click "Từ chối" (Reject)
6. Enter reason: "Thời gian không chính xác"
7. Verify log status: REJECTED
8. Verify device hours NOT increased

## Security Notes

⚠️ **IMPORTANT**: All passwords are set to `123456` for development only.

**Before Production Deployment:**
1. Change all default passwords
2. Enforce strong password policy
3. Remove or disable development accounts
4. Create production user accounts with secure credentials
5. Enable HTTPS (already configured in `run_https.sh`)
6. Set `DEBUG = False` in settings.py
7. Configure proper `ALLOWED_HOSTS`

## Password Reset (Development Only)

To reset a user's password in development:

```bash
python manage.py shell
```

Then run:
```python
from django.contrib.auth.models import User
user = User.objects.get(username='nhanvien1')
user.set_password('newpassword123')
user.save()
```

## Creating New Users

Via Django Shell:
```python
from django.contrib.auth.models import User, Group

# Create Operator
operator_group = Group.objects.get(name='Operators')
user = User.objects.create_user('newoperator', 'email@example.com', 'password123')
user.first_name = "New"
user.last_name = "Operator"
user.save()
user.groups.add(operator_group)

# Create Commander
commander_group = Group.objects.get(name='Commanders')
user = User.objects.create_user('newcommander', 'email@example.com', 'password123')
user.first_name = "New"
user.last_name = "Commander"
user.save()
user.groups.add(commander_group)
```

## Admin Panel Access

Only superusers can access Django Admin Panel at `/admin/`.

To create a superuser:
```bash
python manage.py createsuperuser
```

---

**Last Updated**: 2026-01-29  
**Document Version**: 1.0
