# PWA Quản Lý Thiết Bị (Device Management PWA)

## Project Structure
Created a Django-based Progressive Web App for military/industrial equipment management with Vietnamese UI.

### Directory Structure Created
```
qlthietbi/
├── templates/qlthietbi/
│   ├── base.html                 # ✅ Base template with fixed bottom nav bar
│   ├── dashboard.html            # ✅ Summary cards + Recent logs
│   ├── scan.html                 # ✅ QR scanner with manual input
│   ├── device_detail.html        # ✅ Device info & log button
│   ├── log_entry.html            # ✅ Form with validation & duration calculator
│   └── history.html              # ✅ All operation logs
├── static/
│   ├── css/                      # (Ready for future custom CSS)
│   └── js/                       # (Ready for future custom JS)
├── migrations/                   # Database migrations
├── views.py                      # ✅ 5 views created
├── urls.py                       # ✅ URL routing configured
├── models.py                     # ✅ Models with QR code generation
└── admin.py                      # ✅ Admin interface with QR display
```

## What Was Done

### 1. Created Base Template (`base.html`)
- ✅ Dark Mode theme (#0d1b2a background, #1b263b surface)
- ✅ Fixed bottom navigation bar with 3 items:
  - Bảng chỉ huy (Dashboard)
  - Quét mã (QR Scanner)
  - Lịch sử (History)
- ✅ Bootstrap 5 CSS via CDN
- ✅ FontAwesome Icons via CDN
- ✅ HTML5 QR Code Scanner library via CDN
- ✅ Custom CSS for Vietnamese military-style dark mode UI
- ✅ Touch-friendly buttons (min-height: 50px)
- ✅ Toast notification system for messages
- ✅ Semantic HTML5 structure

### 2. Created All 5 Templates

#### **dashboard.html** - Bảng chỉ huy
- 3 Summary cards showing device status:
  - Hoạt động tốt (Normal - Green, C1)
  - Cần bảo dưỡng (Maintenance - Yellow, C2)
  - Hỏng hóc (Error - Red)
- Recent logs section showing last 10 operation logs
- Click on logs to view device details

#### **scan.html** - Quét mã
- Real-time QR code scanner using html5-qrcode library
- Auto-redirect to device detail page on scan
- Manual QR code input form as fallback
- Camera permission request handling
- Success/error messages with visual feedback

#### **device_detail.html** - Chi tiết thiết bị
- Device system information (name, department, total hours)
- Current unit details (name, QR code, location, status)
- Status badges (C1 - Tốt, C2 - Bảo dưỡng, Hỏng)
- **"Ghi Nhật Ký"** button linking to log entry form
- List of all units in the device system
- Navigation breadcrumb

#### **log_entry.html** - Ghi Nhật Ký
- Form fields:
  - Người thực hiện (Operator name)
  - Giờ nổ máy (Start time) - datetime-local input
  - Giờ tắt máy (End time) - datetime-local input
- Real-time duration calculator (read-only display)
- Client-side validation:
  - Required field checks
  - End time > Start time validation
  - Error message: "Giờ tắt máy phải sau giờ nổ máy"
- Default datetime set to current time
- Smooth scrolling to errors
- Save/Cancel buttons

#### **history.html** - Lịch sử
- Complete list of all operation logs
- Displays per log:
  - Device name
  - Operator name
  - Start/end times (formatted: d/m H:i)
  - Total duration in hours
- "Xem chi tiết" button to navigate to device
- Empty state with CTA to start scanning
- Total log count display

### 3. Created Views (`views.py`)
Five main views implemented:
- ✅ **dashboard**: Shows 3 summary cards (normal, maintenance, error) + recent 10 logs
- ✅ **scan**: QR scanner interface page
- ✅ **device_detail**: Shows device info + "Ghi Nhật Ký" button
- ✅ **log_entry**: POST/GET form for recording operations with validation
- ✅ **history**: Shows all operation logs sorted by date

### 4. Created URLs (`urls.py`)
- ✅ Dashboard: `/` (root)
- ✅ QR Scanner: `/quet-ma/`
- ✅ Device Detail: `/thiet-bi/<qr_code>/`
- ✅ Log Entry Form: `/ghi-nhat-ky/<qr_code>/`
- ✅ History: `/lich-su/`

### 5. Updated Main URLs (`core/urls.py`)
- ✅ Included qlthietbi.urls in main project URLs
- ✅ Added media files serving for development (DEBUG mode)

### 6. Enhanced Admin Interface (`admin.py`)
- ✅ Registered all 5 models with custom ModelAdmin classes
- ✅ Added search, filters, fieldsets for better UX
- ✅ DeviceUnit inline editing on Device page
- ✅ **QR Code Preview in DeviceUnitAdmin:**
  - Shows 100x100 preview in list view
  - Shows 200x200 preview in detail view
  - One-click access for printing QR codes

### 7. QR Code Generation System (`models.py`)

#### **How QR Codes Work**
- Admin enters a **text code/identifier** (e.g., "PUMP-01", "ENGINE-MAIN") in the `qr_code` field
- Model auto-generates a PNG image encoding that text
- When scanned, QR decoder extracts the text → database lookup by `qr_code` field
- **No auto-generation from names** - only from manual `qr_code` text input

#### **DeviceUnit Model Updates**
- ✅ Added `qr_image` ImageField (stores generated QR PNG files)
- ✅ Added `generate_qr_code()` method:
  - Encodes the `qr_code` field text into PNG image
  - Saves as PNG to `media/qr_codes/units/`
  - Called automatically in `save()` if no image exists
- ✅ `qr_code` field remains CharField - admin enters text code manually

#### **QR Code Generation Details**
```python
# Uses qrcode library (pip install qrcode[pil])
# Encodes the qr_code field text value
# Configuration:
- version=1 (auto-sized)
- error_correction=ERROR_CORRECT_L
- box_size=10px per module
- border=4 modules
- Format: PNG
- Colors: Black on white
```

### 8. Media Configuration (`core/settings.py`)
- ✅ Added MEDIA_URL = '/media/'
- ✅ Added MEDIA_ROOT = BASE_DIR / 'media'
- ✅ Media files served in development via url patterns

### 9. Database Migrations
- ✅ Run `python manage.py makemigrations qlthietbi` to create migrations
- ✅ Run `python manage.py migrate` to apply changes

## Tech Stack
- **Framework**: Django 6.0 with Server-Side Rendering
- **CSS**: Bootstrap 5 (CDN) + Custom Deep Ocean Theme
- **Icons**: FontAwesome 6.4 (CDN)
- **JavaScript**: Vanilla ES6+ + html5-qrcode (CDN)
- **QR Generation**: qrcode library (pip install qrcode[pil])
- **Database**: SQLite3 (default Django)
- **UI Language**: Vietnamese (100%)

## Color Scheme - Deep Ocean Theme
**Optimized for ship/industrial environments with excellent readability:**

| Element | Color | Usage |
|---------|-------|-------|
| Body Background | `#0f172a` | Main page background |
| Text Primary | `#f1f5f9` | All body text |
| Card Background | `#1e293b` | Cards, surfaces |
| Border Color | `#334155` | Card borders, separators |
| Primary Accent | `#3b82f6` | Buttons, links, focus |
| Success | `#10b981` | Good status, success messages |
| Warning | `#f59e0b` | Maintenance, warnings |
| Danger | `#ef4444` | Error status |
| Text Muted | `#94a3b8` | Secondary text, hints |

## UI/UX Features
- **Deep Ocean Theme** optimized for ship/industrial environments
  - Dark Slate Blue body (#0f172a) reduces eye strain
  - Off-white text (#f1f5f9) for excellent readability
  - Lighter Slate cards (#1e293b) for visual contrast
  - Subtle grey borders (#334155) for clarity
- Fixed bottom navigation for mobile use
- Touch-friendly buttons (50px minimum height)
- Toast notifications for user feedback
- Semantic form layouts with Vietnamese labels
- Responsive Bootstrap 5 grid system
- Real-time form validation with clear error messages
- Breadcrumb navigation on detail pages
- Status badges with color coding (Green/Yellow/Red)
- Auto-focusing on errors with smooth scroll
- QR Code Preview in Admin: Easy access for printing

## User Flow
1. **Dashboard** → View summary and recent logs
2. **Scan QR** → Real-time QR camera or manual input
3. **Device Detail** → View device/unit info
4. **Log Entry** → Record operation with validation
5. **History** → Review all logs

## QR Code Workflow

### Generation (Admin)
1. Admin creates a DeviceUnit in `/admin/qlthietbi/deviceunit/`
2. Admin enters a unique **code/identifier** in the `qr_code` field (e.g., "PUMP-01", "ENGINE-A")
3. On save, the model auto-generates a QR code PNG representing that text code
4. PNG image saved to `media/qr_codes/units/` directory
5. Admin can view 200x200 preview and print the QR code

### Printing
1. Go to admin: `/admin/qlthietbi/deviceunit/`
2. Click on any DeviceUnit
3. View 200x200 QR code preview (encodes the qr_code field text)
4. Print page (Ctrl+P) or right-click image to save and print externally
5. Attach/label printed QR code on physical device

### Scanning & Lookup
1. Technician goes to "Quét mã" (`/quet-ma/`) page
2. Points camera at printed QR code
3. Camera decodes QR → extracts the text code (e.g., "PUMP-01")
4. Lookup: Finds DeviceUnit where `qr_code = "PUMP-01"`
5. Auto-redirects to `/thiet-bi/PUMP-01/` (device detail page)
6. Technician clicks "Ghi Nhật Ký" to log operation

### Data Flow
```
Admin Input (Text Code)
    ↓
QR Code Generation (Model.save())
    ↓
PNG Image Stored in Media
    ↓
Print & Attach to Device
    ↓
Scan with Camera
    ↓
Decode QR → Text Code
    ↓
Database Lookup (qr_code field)
    ↓
Device Details Page
```

## Directory Structure for QR Codes
```
media/
├── qr_codes/
│   └── units/            # DeviceUnit QR codes
│       └── unit_*.png
```

## Next Steps
1. Create `manifest.json` for PWA support
2. Create Service Worker for offline functionality
3. Add local storage handling for offline log submission
4. Create offline.html page
5. Add background sync for queued logs
6. Test on mobile devices and ship environment
7. Add print stylesheet for QR code printing

## Vietnamese Terminology Used
- **Bảng chỉ huy** = Dashboard
- **Quét mã** = QR Scanner
- **Lịch sử** = History
- **Ghi Nhật Ký** = Log Entry
- **Hoạt động tốt (C1)** = Good/Normal
- **Cần bảo dưỡng (C2)** = Maintenance Needed
- **Hỏng hóc** = Broken/Error
- **Giờ nổ máy** = Start time (engine on)
- **Giờ tắt máy** = End time (engine off)
- **Người thực hiện** = Operator name
- **Trạng thái kỹ thuật** = Technical status
- **Mã QR** = QR Code

## Notes
- All UI text is in Vietnamese as per requirements
- Using CDN for Bootstrap and html5-qrcode to avoid package management
- All templates responsive and mobile-first
- **Deep Ocean Theme** provides excellent readability in low-light ship environments
- Active navigation item highlighted with primary blue accent
- Form validation prevents bad data submission
- All datetime fields use HTML5 datetime-local input for mobile compatibility
- QR codes auto-generate on model save (no manual action needed)
- Media files accessible at `/media/` URL path

