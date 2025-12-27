import requests
import json
import re
from bs4 import BeautifulSoup

# URL test
test_url = "https://www.foody.vn/ha-noi/pizza-hut-xuan-thuy"

print(f"🔍 Đang test với URL: {test_url}\n")

# Tạo session với headers
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
    "Referer": "https://www.foody.vn/",
})

# Lấy HTML
response = session.get(test_url, timeout=15)
print(f"📊 Status code: {response.status_code}\n")

if response.status_code == 200:
    html = response.text
    
    # Tìm tất cả các pattern có thể
    patterns = [
        (r'var\s+initData\s*=\s*({.*?});', "var initData = {...}"),
        (r'window\.initData\s*=\s*({.*?});', "window.initData = {...}"),
        (r'initData\s*:\s*({.*?}),', "initData: {...}"),
        (r'"initData"\s*:\s*({.*?})', '"initData": {...}'),
    ]
    
    found = False
    for pattern, description in patterns:
        print(f"🔍 Đang thử pattern: {description}")
        match = re.search(pattern, html, re.DOTALL)
        
        if match:
            print(f"✅ Tìm thấy với pattern: {description}\n")
            json_str = match.group(1)
            
            # Lưu raw JSON string
            print("📝 Raw JSON string (100 ký tự đầu):")
            print(json_str[:100] + "...\n")
            
            try:
                data = json.loads(json_str)
                print("✅ Parse JSON thành công!\n")
                print("📊 Cấu trúc dữ liệu:")
                print(json.dumps(data, ensure_ascii=False, indent=2)[:500] + "...\n")
                
                # Lưu vào file
                with open("test_initdata_result.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print("💾 Đã lưu vào file: test_initdata_result.json")
                
                found = True
                break
            except json.JSONDecodeError as e:
                print(f"❌ Lỗi parse JSON: {e}\n")
        else:
            print(f"  ⚠️  Không tìm thấy\n")
    
    if not found:
        # Tìm tất cả thẻ script và in ra
        print("\n" + "="*60)
        print("🔍 Đang tìm kiếm tất cả các thẻ <script> chứa 'initData'...")
        soup = BeautifulSoup(html, 'html.parser')
        scripts = soup.find_all('script')
        
        for idx, script in enumerate(scripts, 1):
            script_content = script.string
            if script_content and 'initData' in script_content:
                print(f"\n📌 Script #{idx} chứa 'initData':")
                print(script_content[:300] + "...")
        
        # Lưu toàn bộ HTML để debug
        with open("test_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\n💾 Đã lưu toàn bộ HTML vào: test_page.html")
        print("   Bạn có thể mở file này và tìm kiếm 'initData' để xem cấu trúc thực tế.")
else:
    print(f"❌ Không thể lấy dữ liệu. Status code: {response.status_code}")

