#!/usr/bin/env python3
"""
Demo script - Hiển thị cách sử dụng các scripts
"""

import json
import os

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def main():
    print_header("🍔 FOOD DETECTIVE - DEMO & EXAMPLES")
    
    # 1. Thống kê dữ liệu hiện có
    print("📊 1. THỐNG KÊ DỮ LIỆU HIỆN CÓ")
    print("-" * 70)
    
    if os.path.exists("final_result_link.json"):
        with open("final_result_link.json", "r") as f:
            links = json.load(f)
        print(f"✅ Tổng số links nhà hàng: {len(links):,}")
        print(f"   - File: final_result_link.json")
        print(f"   - Ví dụ: {links[0]}")
    
    if os.path.exists("test_initdata_result.json"):
        with open("test_initdata_result.json", "r") as f:
            data = json.load(f)
        print(f"\n✅ Dữ liệu test đã có:")
        print(f"   - Nhà hàng: {data.get('Name', 'N/A')}")
        print(f"   - Địa chỉ: {data.get('Address', 'N/A')}")
        print(f"   - Giá: {data.get('PriceMin', 0):,} - {data.get('PriceMax', 0):,} VNĐ")
        print(f"   - Điểm đánh giá:")
        for rating in data.get('AvgPointList', [])[:3]:
            print(f"     • {rating['Label']}: {rating['Point']}/10")
    
    # 2. Cấu trúc project
    print_header("📁 2. CẤU TRÚC PROJECT")
    
    files_info = {
        "Scripts chính": [
            ("test_initdata.py", "Test với 1 URL để xem cấu trúc dữ liệu"),
            ("scrape_initdata.py", "Scrape đơn giản - không có checkpoint"),
            ("scrape_initdata_advanced.py", "Scrape nâng cao - có checkpoint, retry"),
            ("run.py", "Menu tương tác để chọn script"),
            ("scrape_foody.py", "Script gốc để lấy list URLs"),
        ],
        "Documentation": [
            ("README.md", "Hướng dẫn chi tiết và đầy đủ"),
            ("QUICKSTART.md", "Hướng dẫn nhanh để bắt đầu"),
        ],
        "Data Files": [
            ("final_result_link.json", "7,579 links nhà hàng (INPUT)"),
            ("restaurant_initdata.json", "Dữ liệu chi tiết đã scrape (OUTPUT)"),
            ("test_initdata_result.json", "Kết quả test mẫu"),
            ("checkpoint.json", "Checkpoint để resume"),
            ("scrape_errors.json", "Danh sách URLs bị lỗi"),
        ]
    }
    
    for category, files in files_info.items():
        print(f"📦 {category}:")
        for filename, description in files:
            status = "✅" if os.path.exists(filename) else "⭕"
            print(f"   {status} {filename:30s} - {description}")
        print()
    
    # 3. Ví dụ sử dụng
    print_header("💡 3. VÍ DỤ SỬ DỤNG")
    
    examples = [
        ("Test nhanh với 1 URL", "python3 test_initdata.py"),
        ("Xem menu tương tác", "python3 run.py"),
        ("Scrape ALL (nâng cao)", "python3 scrape_initdata_advanced.py"),
        ("Xem kết quả", "head -50 restaurant_initdata.json"),
        ("Đếm số nhà hàng", "grep '\"url\"' restaurant_initdata.json | wc -l"),
    ]
    
    for idx, (desc, cmd) in enumerate(examples, 1):
        print(f"{idx}. {desc}:")
        print(f"   $ {cmd}\n")
    
    # 4. Dữ liệu có được
    print_header("🎯 4. DỮ LIỆU SẼ CÓ ĐƯỢC")
    
    fields = {
        "Thông tin cơ bản": ["RestaurantID", "Name", "Address", "Phone", "Website"],
        "Vị trí": ["City", "District", "Area", "Latitude", "Longtitude"],
        "Giá cả": ["PriceMin", "PriceMax"],
        "Đánh giá": ["TotalReview", "TotalView", "TotalFavourite", "AvgPointList"],
        "Phân loại": ["Cuisines", "Categories"],
        "Media": ["PictureModel", "TotalPictures"],
    }
    
    for category, field_list in fields.items():
        print(f"📌 {category}:")
        print(f"   {', '.join(field_list)}\n")
    
    # 5. Workflow khuyến nghị
    print_header("🚀 5. WORKFLOW KHUYẾN NGHỊ")
    
    steps = [
        "Cài đặt dependencies: pip3 install beautifulsoup4 requests",
        "Test với 1 URL: python3 test_initdata.py",
        "Xem kết quả test: cat test_initdata_result.json",
        "Chạy scrape nâng cao: python3 scrape_initdata_advanced.py",
        "Để máy chạy (2-3 giờ) hoặc Ctrl+C để dừng",
        "Resume nếu bị dừng: chạy lại bước 4",
        "Xem kết quả: cat restaurant_initdata.json",
    ]
    
    for idx, step in enumerate(steps, 1):
        print(f"   {idx}. {step}")
    
    # 6. Tips
    print_header("💡 6. TIPS & TRICKS")
    
    tips = [
        "✅ Script nâng cao tự động lưu checkpoint mỗi 50 URLs",
        "✅ Có thể dừng (Ctrl+C) và resume bất cứ lúc nào",
        "✅ Auto retry khi bị lỗi mạng",
        "✅ Delay 1s giữa các request để tránh bị block",
        "⚠️  Nếu bị rate limit, tăng delay lên 2-3s",
        "⚠️  Tổng thời gian: ~2-3 giờ cho 7,579 URLs",
        "💡 Nên để máy chạy qua đêm",
        "💡 Kiểm tra checkpoint.json để biết progress",
    ]
    
    for tip in tips:
        print(f"   {tip}")
    
    print("\n" + "="*70)
    print("✨ Sẵn sàng để bắt đầu!")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

