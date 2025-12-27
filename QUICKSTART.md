# 🍔 Food Detective - Hướng Dẫn Nhanh

## ⚡ Quick Start (Nhanh nhất)

```bash
# Chạy menu tương tác
python3 run.py
```

## 📝 Các bước chi tiết

### 1️⃣ Cài đặt thư viện
```bash
pip3 install beautifulsoup4 requests
```

### 2️⃣ Test với 1 URL
```bash
python3 test_initdata.py
```
Xem kết quả trong file: `test_initdata_result.json`

### 3️⃣ Chạy scrape cho tất cả URLs

**Option A: Script đơn giản**
```bash
python3 scrape_initdata.py
```

**Option B: Script nâng cao (Khuyên dùng)**
```bash
python3 scrape_initdata_advanced.py
```

Ưu điểm của Option B:
- ✅ Có checkpoint - dừng và resume bất cứ lúc nào
- ✅ Auto retry khi fail
- ✅ Progress bar chi tiết
- ✅ Ước tính thời gian còn lại

## 📊 Xem kết quả

```bash
# Xem số lượng nhà hàng đã scrape
wc -l restaurant_initdata.json

# Xem 20 dòng đầu
head -20 restaurant_initdata.json
```

## 🔧 Các file quan trọng

| File | Mô tả |
|------|-------|
| `final_result_link.json` | Danh sách 7581 links nhà hàng (input) |
| `restaurant_initdata.json` | Dữ liệu chi tiết đã scrape (output) |
| `checkpoint.json` | Checkpoint để resume |
| `scrape_errors.json` | Danh sách URLs bị lỗi |
| `test_initdata_result.json` | Kết quả test 1 URL |

## ⏸️ Dừng và Resume

Nếu đang chạy script nâng cao (`scrape_initdata_advanced.py`):

1. **Dừng**: Nhấn `Ctrl + C`
2. **Resume**: Chạy lại lệnh `python3 scrape_initdata_advanced.py`

Script sẽ tự động đọc checkpoint và tiếp tục từ chỗ dừng!

## 🎯 Dữ liệu nhận được

Mỗi nhà hàng có các thông tin:

```json
{
  "url": "https://www.foody.vn/ha-noi/pizza-hut-xuan-thuy",
  "initData": {
    "RestaurantID": 35998,
    "Name": "Pizza Hut - Xuân Thủy",
    "Address": "167 Xuân Thủy, P. Dịch Vọng Hậu",
    "City": "Hà Nội",
    "District": "Quận Cầu Giấy",
    "PriceMin": 40000,
    "PriceMax": 165000,
    "Latitude": 21.0363919,
    "Longtitude": 105.7839716,
    "TotalReview": 159,
    "TotalView": 24182,
    "AvgPointList": [...],
    "Cuisines": [...],
    ...
  }
}
```

### Các trường dữ liệu quan trọng:

**📍 Vị trí & Liên hệ:**
- `Name`, `Address`, `Phone`, `Website`
- `City`, `District`, `Area`
- `Latitude`, `Longtitude` (tọa độ GPS)

**💰 Giá cả:**
- `PriceMin`, `PriceMax`

**⭐ Đánh giá:**
- `TotalReview` - Số lượng review
- `TotalView` - Lượt xem
- `TotalFavourite` - Số người yêu thích
- `AvgPointList` - Điểm chi tiết (Vị trí, Không gian, Chất lượng, Phục vụ, Giá cả)

**🍽️ Ẩm thực:**
- `Cuisines` - Các loại ẩm thực (VD: Quốc tế, Việt Nam, Nhật Bản...)
- `Categories` - Danh mục (VD: Nhà hàng, Quán ăn, Cafe...)

**📸 Media:**
- `PictureModel` - Ảnh đại diện
- `TotalPictures` - Tổng số ảnh

## ⚙️ Tùy chỉnh

### Thay đổi delay (tránh bị block)
Mở file `scrape_initdata_advanced.py`, dòng 229:
```python
delay=1.0  # Đổi thành 2.0, 3.0 nếu bị block
```

### Thay đổi tần suất lưu checkpoint
Dòng 228:
```python
save_interval=50  # Đổi thành 10, 100, ...
```

## 🐛 Troubleshooting

### Lỗi: ModuleNotFoundError
```bash
pip3 install beautifulsoup4 requests
```

### Bị rate limit (429 error)
- Tăng delay lên 2-3 giây
- Chờ 5-10 phút rồi chạy lại

### Script bị crash
- Không sao! Chạy lại script nâng cao
- Checkpoint đã được lưu tự động

## ⏱️ Thời gian ước tính

Với 7581 URLs và delay 1 giây:
- **Thời gian tối thiểu**: ~2.1 giờ
- **Thời gian thực tế**: ~2.5-3 giờ (có retry, lỗi mạng...)

**💡 Mẹo**: Để máy chạy qua đêm!

## 📧 Support

Nếu gặp vấn đề:
1. Chạy test script: `python3 test_initdata.py`
2. Xem file `test_page.html` để debug
3. Check file `scrape_errors.json` để biết URL nào lỗi

---

**Made with ❤️ for Food Detective Project**

