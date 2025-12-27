#!/usr/bin/env python3
"""
🍔 Food Detective - Restaurant Data Scraper
Quick Start Script
"""

import sys
import os

def print_menu():
    print("\n" + "="*60)
    print("🍔 FOOD DETECTIVE - RESTAURANT DATA SCRAPER")
    print("="*60)
    print("\n📋 MENU:")
    print("  1. Test với 1 URL mẫu (nhanh)")
    print("  2. Scrape đơn giản (script cơ bản)")
    print("  3. Scrape nâng cao (có checkpoint, retry, progress)")
    print("  4. Xem thống kê dữ liệu hiện có")
    print("  5. Thoát")
    print("\n" + "="*60)

def check_dependencies():
    """Kiểm tra các thư viện cần thiết"""
    try:
        import requests
        import bs4
        return True
    except ImportError:
        print("\n❌ Chưa cài đặt đủ thư viện!")
        print("\n📦 Chạy lệnh sau để cài đặt:")
        print("   pip3 install beautifulsoup4 requests")
        return False

def show_stats():
    """Hiển thị thống kê dữ liệu"""
    import json
    
    print("\n" + "="*60)
    print("📊 THỐNG KÊ DỮ LIỆU")
    print("="*60)
    
    # Check links file
    if os.path.exists("final_result_link.json"):
        with open("final_result_link.json", "r") as f:
            links = json.load(f)
        print(f"\n📎 Tổng số links: {len(links)}")
    else:
        print(f"\n❌ Chưa có file final_result_link.json")
    
    # Check results file
    if os.path.exists("restaurant_initdata.json"):
        with open("restaurant_initdata.json", "r") as f:
            results = json.load(f)
        print(f"✅ Đã scrape: {len(results)} nhà hàng")
        
        if results:
            print(f"\n📍 Nhà hàng mới nhất:")
            latest = results[-1]
            if "initData" in latest:
                data = latest["initData"]
                print(f"   - Tên: {data.get('Name', 'N/A')}")
                print(f"   - Địa chỉ: {data.get('Address', 'N/A')}")
                print(f"   - Giá: {data.get('PriceMin', 0):,.0f} - {data.get('PriceMax', 0):,.0f} VNĐ")
                print(f"   - Reviews: {data.get('TotalReview', 0)}")
    else:
        print(f"❌ Chưa có dữ liệu scraped")
    
    # Check checkpoint
    if os.path.exists("checkpoint.json"):
        with open("checkpoint.json", "r") as f:
            checkpoint = json.load(f)
        processed = len(checkpoint.get("processed_urls", []))
        print(f"\n💾 Checkpoint: {processed} URLs đã xử lý")
    
    # Check errors
    if os.path.exists("scrape_errors.json"):
        with open("scrape_errors.json", "r") as f:
            errors = json.load(f)
        print(f"❌ Lỗi: {len(errors)} URLs")
    
    print("\n" + "="*60)

def run_script(script_name):
    """Chạy một script Python"""
    os.system(f"python3 {script_name}")

def main():
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    while True:
        print_menu()
        choice = input("\n👉 Chọn (1-5): ").strip()
        
        if choice == "1":
            print("\n🔍 Đang chạy test script...")
            run_script("test_initdata.py")
            input("\n⏸️  Nhấn Enter để tiếp tục...")
        
        elif choice == "2":
            print("\n⚠️  Script này sẽ scrape TẤT CẢ URLs (có thể mất 2-3 giờ)")
            confirm = input("Tiếp tục? (y/n): ").strip().lower()
            if confirm == 'y':
                print("\n🚀 Đang chạy scrape đơn giản...")
                run_script("scrape_initdata.py")
            input("\n⏸️  Nhấn Enter để tiếp tục...")
        
        elif choice == "3":
            print("\n⚠️  Script này sẽ scrape TẤT CẢ URLs (có thể mất 2-3 giờ)")
            print("✅ Có thể dừng (Ctrl+C) và resume sau")
            confirm = input("Tiếp tục? (y/n): ").strip().lower()
            if confirm == 'y':
                print("\n🚀 Đang chạy scrape nâng cao...")
                run_script("scrape_initdata_advanced.py")
            input("\n⏸️  Nhấn Enter để tiếp tục...")
        
        elif choice == "4":
            show_stats()
            input("\n⏸️  Nhấn Enter để tiếp tục...")
        
        elif choice == "5":
            print("\n👋 Tạm biệt!")
            break
        
        else:
            print("\n❌ Lựa chọn không hợp lệ!")
            input("\n⏸️  Nhấn Enter để thử lại...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Đã thoát!")

