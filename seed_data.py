from django.contrib.auth.models import User, Group
from qlthietbi.models import Department, Device, DeviceUnit, Location

def run():
    print("🌱 Seeding data...")

    # 1. Create Groups
    commander_group, _ = Group.objects.get_or_create(name='Commanders')
    operator_group, _ = Group.objects.get_or_create(name='Operators')
    print("✅ Created Groups")

    # 2. Create Users
    # Commander
    if not User.objects.filter(username='truongnganh').exists():
        u = User.objects.create_user('truongnganh', 'truongnganh@example.com', '123456')
        u.first_name = "Trưởng Ngành"
        u.last_name = "Kỹ Thuật"
        u.save()
        u.groups.add(commander_group)
        print("✅ Created User: truongnganh (Pass: 123456)")

    # Operator 1
    if not User.objects.filter(username='nhanvien1').exists():
        u = User.objects.create_user('nhanvien1', 'nv1@example.com', '123456')
        u.first_name = "Nguyễn Văn"
        u.last_name = "A"
        u.save()
        u.groups.add(operator_group)
        print("✅ Created User: nhanvien1 (Pass: 123456)")

    # Operator 2
    if not User.objects.filter(username='nhanvien2').exists():
        u = User.objects.create_user('nhanvien2', 'nv2@example.com', '123456')
        u.first_name = "Trần Thị"
        u.last_name = "B"
        u.save()
        u.groups.add(operator_group)
        print("✅ Created User: nhanvien2 (Pass: 123456)")

    # 3. Create Departments
    dept_may, _ = Department.objects.get_or_create(name='Ngành Máy')
    dept_dien, _ = Department.objects.get_or_create(name='Ngành Điện')

    # 4. Create Locations
    loc_ham, _ = Location.objects.get_or_create(name='Hầm máy số 1')
    
    # 5. Create Devices & Units
    # Device 1
    dev1, _ = Device.objects.get_or_create(
        department=dept_may,
        name='Máy Chính Trái',
        defaults={'description': 'MTU 4000 Series'}
    )
    
    # Unit 1.1
    DeviceUnit.objects.get_or_create(
        device=dev1,
        qr_code='MAY-01',
        defaults={
            'name': 'Động cơ Diesel',
            'location': loc_ham,
            'maintenance_threshold': 500
        }
    )
    
    # Unit 1.2
    DeviceUnit.objects.get_or_create(
        device=dev1,
        qr_code='MAY-02',
        defaults={
            'name': 'Hộp số',
            'location': loc_ham,
            'maintenance_threshold': 1000
        }
    )
    
    print("✅ Created Sample Data: Departments, Devices, Units")
    print("🎉 Done! Ready to login.")
