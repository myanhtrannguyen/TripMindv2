import requests
import json
import time
import re
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any

# Tạo session với headers
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
    "Referer": "https://www.foody.vn/",
    "Connection": "keep-alive",
})

def extract_initdata(html_content: str) -> Optional[Dict[Any, Any]]:
    """
    Trích xuất initData từ HTML content
    initData thường nằm trong thẻ script với format: var initData = {...}
    """
    try:
        # Tìm pattern var initData = {...}
        pattern = r'var\s+initData\s*=\s*({.*?});'
        match = re.search(pattern, html_content, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            # Parse JSON
            data = json.loads(json_str)
            return data
        
        # Thử pattern khác: window.initData = {...}
        pattern2 = r'window\.initData\s*=\s*({.*?});'
        match2 = re.search(pattern2, html_content, re.DOTALL)
        
        if match2:
            json_str = match2.group(1)
            data = json.loads(json_str)
            return data
            
        return None
    except json.JSONDecodeError as e:
        print(f"  ❌ Lỗi parse JSON: {e}")
        return None
    except Exception as e:
        print(f"  ❌ Lỗi: {e}")
        return None

def scrape_restaurant_initdata(url: str) -> Optional[Dict[Any, Any]]:
    """
    Lấy initData từ một trang nhà hàng
    """
    try:
        response = session.get(url, timeout=15)
        
        if response.status_code != 200:
            print(f"  ❌ Status code: {response.status_code}")
            return None
        
        # Trích xuất initData từ HTML
        initdata = extract_initdata(response.text)
        
        if initdata:
            print(f"  ✅ Đã lấy được initData")
            return initdata
        else:
            print(f"  ⚠️  Không tìm thấy initData")
            return None
            
    except requests.exceptions.Timeout:
        print(f"  ❌ Timeout")
        return None
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Connection Error")
        return None
    except Exception as e:
        print(f"  ❌ Lỗi: {e}")
        return None

def main():
    # Đọc file links
    print("📖 Đọc file final_result_link.json...")
    with open("final_result_link.json", "r", encoding="utf-8") as f:
        urls = json.load(f)
    
    print(f"📊 Tổng số links: {len(urls)}")
    
    # Kết quả
    results = []
    errors = []
    
    # Xử lý từng URL
    for idx, url in enumerate(urls, 1):
        print(f"\n[{idx}/{len(urls)}] {url}")
        
        initdata = scrape_restaurant_initdata(url)
        
        if initdata:
            results.append({
                "url": url,
                "initData": initdata
            })
            
            # Lưu kết quả sau mỗi 50 items
            if idx % 50 == 0:
                print(f"\n💾 Lưu kết quả tạm thời... ({len(results)} items)")
                with open("restaurant_initdata.json", "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
        else:
            errors.append({
                "url": url,
                "index": idx
            })
        
        # Delay để tránh bị block
        time.sleep(1)
    
    # Lưu kết quả cuối cùng
    print(f"\n\n{'='*60}")
    print(f"✅ HOÀN THÀNH!")
    print(f"📊 Thành công: {len(results)}/{len(urls)}")
    print(f"❌ Thất bại: {len(errors)}/{len(urls)}")
    
    with open("restaurant_initdata.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"💾 Đã lưu: restaurant_initdata.json")
    
    if errors:
        with open("scrape_errors.json", "w", encoding="utf-8") as f:
            json.dump(errors, f, ensure_ascii=False, indent=2)
        print(f"💾 Đã lưu lỗi: scrape_errors.json")

if __name__ == "__main__":
    main()

