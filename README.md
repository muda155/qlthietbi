# Sổ Kỹ Thuật Số - Technical Log Book PWA

A **Progressive Web App (PWA)** for managing equipment operation logs in Vietnamese. Built with Django, Bootstrap 5, and designed for ship/industrial environments.

> 🇻🇳 **100% Vietnamese UI** | 📱 **Mobile-First PWA** | 🔐 **Offline Support** | 🌙 **Dark Mode**

---

## 📋 Features

- ✅ **QR Code Scanning** - Real-time camera QR scanning or manual input
- ✅ **Operation Logging** - Record device status, operator info, and runtime hours
- ✅ **Device Dashboard** - Summary cards showing device health (3 statuses)
- ✅ **Status Tracking** - Operator-reported device conditions (Normal/Maintenance/Error)
- ✅ **Offline Support** - Works without internet, syncs when online
- ✅ **PWA Installation** - Install as app on iOS Safari, Android Chrome
- ✅ **Dark Mode** - Deep ocean theme optimized for ship environments
- ✅ **Responsive Design** - Touch-friendly UI with large buttons (50px min)
- ✅ **Form Validation** - Real-time validation with Vietnamese error messages

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Django 6.0+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/qlthietbi.git
cd qlthietbi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create admin user (optional)
python manage.py createsuperuser

# Start server
python manage.py runserver 0.0.0.0:8000
```

Visit: `http://localhost:8000`

Admin panel: `http://localhost:8000/admin`

---

## 📱 Usage

### For Operators

1. **Dashboard** (`/`) - View equipment status overview
2. **Scan QR** (`/scan/`) - Scan equipment codes
3. **Log Entry** (`/log-entry/`) - Record operation details and status
4. **History** (`/history/`) - View past operation logs

### For Administrators

1. Access admin panel: `/admin/`
2. Create equipment categories (Departments)
3. Create equipment systems (Devices)
4. Create equipment units with QR codes
5. View/manage operation logs

---

## 🏗️ Project Structure

```
qlthietbi/
├── models.py                 # Database models (Device, DeviceUnit, OperationLog)
├── views.py                  # 5 main views (dashboard, scan, device_detail, log_entry, history)
├── urls.py                   # URL routing
├── admin.py                  # Admin interface with QR code preview
├── templates/qlthietbi/
│   ├── base.html             # Base template + fixed bottom nav
│   ├── dashboard.html        # Summary cards + recent logs
│   ├── scan.html             # QR scanner interface
│   ├── device_detail.html    # Equipment details page
│   ├── log_entry.html        # Operation log form
│   ├── history.html          # All logs list
│   └── offline.html          # Offline fallback page
├── static/
│   ├── manifest.json         # PWA manifest
│   └── serviceworker.js      # Service worker for offline support
└── migrations/               # Database migrations
```

---

## 🎨 Design

### Color Scheme (Deep Ocean Theme)
| Element | Color | Usage |
|---------|-------|-------|
| Background | `#0f172a` | Main page |
| Surface | `#1e293b` | Cards |
| Text | `#f1f5f9` | Body text |
| Primary | `#3b82f6` | Buttons, links |
| Success | `#10b981` | Good status (C1) |
| Warning | `#f59e0b` | Maintenance (C2) |
| Error | `#ef4444` | Error status |

### Device Status Codes
- **C1 (Tốt)** - Normal operation (Green)
- **C2 (Bảo dưỡng)** - Needs maintenance (Yellow)
- **Error** - Broken/Failed (Red)

---

## 💾 Database Models

### Device (Equipment System)
- Department
- Name
- Description
- Total accumulated hours

### DeviceUnit (Equipment Unit)
- Device (FK)
- Name
- Location
- QR Code
- Current hours
- Maintenance threshold
- Status (NORMAL/MAINTENANCE/ERROR)
- QR code image

### OperationLog (Operation Record)
- Device (FK)
- DeviceUnit (FK)
- Operator name
- Start/End time
- Duration (hours)
- Device status (reported by operator)
- Notes/Comments

---

## 🔄 Operation Log Flow

```
1. Operator scans QR code
   ↓
2. Device details page appears
   ↓
3. Click "Ghi Nhật Ký" (Log Entry)
   ↓
4. Fill form (operator, times, status, notes)
   ↓
5. Server calculates duration
   ↓
6. Device unit status updates from operator report
   ↓
7. Redirect to device details
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 6.0 (Python) |
| **Frontend** | HTML5, Bootstrap 5, Vanilla JS |
| **Icons** | FontAwesome 6.4 |
| **QR Scanning** | html5-qrcode |
| **QR Generation** | qrcode library |
| **Database** | SQLite3 |
| **Styling** | Custom CSS + Bootstrap 5 |

---

## 🌐 PWA Configuration

### manifest.json
- App name: "Sổ Kỹ Thuật Số" (Technical Log Book)
- Standalone display mode
- Offline support with shortcuts
- Maskable icons for adaptive icons

### Service Worker
- **Network-first strategy**: Try network, fallback to cache
- **Offline page**: Returns offline.html when no cached version
- **Auto-updates**: Caches successful responses
- **Background sync**: Ready for log syncing when online

### Installation on iPad
1. Open in Safari
2. Tap **Share** button (↑)
3. Tap **"Add to Home Screen"**
4. Confirm name and tap **"Add"**

---

## 📝 Vietnamese Terminology

| Term | English |
|------|---------|
| Bảng chỉ huy | Dashboard |
| Quét mã | QR Scanner |
| Lịch sử | History |
| Ghi Nhật Ký | Log Entry |
| Hoạt động tốt | Good/Normal |
| Cần bảo dưỡng | Needs Maintenance |
| Hỏng hóc | Broken/Error |
| Giờ nổ máy | Start time |
| Giờ tắt máy | End time |
| Người thực hiện | Operator name |
| Trạng thái | Status |

---

## 🔧 Configuration

### Django Settings (core/settings.py)
```python
# Media files (for QR codes)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Installed apps
INSTALLED_APPS = [
    'qlthietbi',
    # ... other apps
]
```

---

## 🚨 Common Issues

### QR Scanner not working
- Check camera permissions in browser settings
- Ensure HTTPS or localhost (some browsers require secure context)
- Try different browser (Chrome recommended for Android)

### PWA not installing
- Only Safari on iOS supports PWA installation (Apple limitation)
- Use Chrome/Edge on Android for full PWA support
- Ensure manifest.json is properly linked in base.html

### Service worker not updating
- Clear browser cache: DevTools → Application → Clear storage
- Unregister old service worker manually if needed

---

## 📄 License

[Add your license here]

---

## 👨‍💻 Contributors

- [Your Name]

---

## 📞 Support

For issues or feature requests, please open an issue on GitHub.

---

**Made for Vietnamese Military/Industrial Equipment Management** 🚢⚙️

