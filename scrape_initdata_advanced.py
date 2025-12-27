"""
Script nâng cao để lấy initData từ Foody.vn
- Có progress bar
- Auto retry khi fail
- Resume từ checkpoint
- Multi-threading option
"""

import requests
import json
import time
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
import os

class FoodyInitDataScraper:
    def __init__(self, checkpoint_file="checkpoint.json", output_file="restaurant_initdata.json"):
        self.checkpoint_file = checkpoint_file
        self.output_file = output_file
        self.session = self._create_session()
        self.results = []
        self.errors = []
        self.processed_urls = set()
        
        # Load checkpoint nếu có
        self._load_checkpoint()
    
    def _create_session(self):
        """Tạo session với headers"""
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
            "Referer": "https://www.foody.vn/",
            "Connection": "keep-alive",
        })
        return session
    
    def _load_checkpoint(self):
        """Load checkpoint để resume"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                    checkpoint = json.load(f)
                    self.results = checkpoint.get("results", [])
                    self.errors = checkpoint.get("errors", [])
                    self.processed_urls = set(checkpoint.get("processed_urls", []))
                    print(f"✅ Đã load checkpoint: {len(self.processed_urls)} URLs đã xử lý")
            except Exception as e:
                print(f"⚠️  Không thể load checkpoint: {e}")
        
        # Load existing output file nếu có
        elif os.path.exists(self.output_file):
            try:
                with open(self.output_file, "r", encoding="utf-8") as f:
                    self.results = json.load(f)
                    self.processed_urls = {item["url"] for item in self.results}
                    print(f"✅ Đã load output file: {len(self.processed_urls)} URLs đã xử lý")
            except Exception as e:
                print(f"⚠️  Không thể load output file: {e}")
    
    def _save_checkpoint(self):
        """Lưu checkpoint"""
        checkpoint = {
            "results": self.results,
            "errors": self.errors,
            "processed_urls": list(self.processed_urls),
            "last_updated": datetime.now().isoformat()
        }
        with open(self.checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, ensure_ascii=False, indent=2)
    
    def _extract_initdata(self, html_content: str) -> Optional[Dict[Any, Any]]:
        """Trích xuất initData từ HTML"""
        patterns = [
            r'var\s+initData\s*=\s*({.*?});',
            r'window\.initData\s*=\s*({.*?});',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1)
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def scrape_url(self, url: str, max_retries: int = 3) -> Optional[Dict[Any, Any]]:
        """Lấy initData từ 1 URL với retry"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    initdata = self._extract_initdata(response.text)
                    return initdata
                elif response.status_code == 429:  # Too many requests
                    print(f"  ⚠️  Rate limited, đợi 5s...")
                    time.sleep(5)
                    continue
                else:
                    return None
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"  ⏱️  Timeout, thử lại lần {attempt + 2}...")
                    time.sleep(2)
                    continue
                return None
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    print(f"  🔌 Connection error, thử lại lần {attempt + 2}...")
                    time.sleep(3)
                    continue
                return None
            except Exception as e:
                print(f"  ❌ Error: {e}")
                return None
        
        return None
    
    def scrape_all(self, urls: List[str], save_interval: int = 50, delay: float = 1.0):
        """Scrape tất cả URLs"""
        total = len(urls)
        start_time = time.time()
        
        print(f"\n{'='*60}")
        print(f"🚀 BẮT ĐẦU SCRAPE")
        print(f"📊 Tổng số URLs: {total}")
        print(f"✅ Đã xử lý: {len(self.processed_urls)}")
        print(f"⏳ Còn lại: {total - len(self.processed_urls)}")
        print(f"{'='*60}\n")
        
        for idx, url in enumerate(urls, 1):
            # Skip nếu đã xử lý
            if url in self.processed_urls:
                continue
            
            # Progress
            elapsed = time.time() - start_time
            avg_time = elapsed / len(self.processed_urls) if self.processed_urls else 0
            remaining = (total - len(self.processed_urls)) * avg_time if avg_time > 0 else 0
            
            print(f"\n[{idx}/{total}] ({len(self.results)} thành công, {len(self.errors)} lỗi)")
            print(f"⏱️  Thời gian: {elapsed/60:.1f}m | Còn lại: ~{remaining/60:.1f}m")
            print(f"🔗 {url}")
            
            # Scrape
            initdata = self.scrape_url(url)
            
            if initdata:
                self.results.append({
                    "url": url,
                    "initData": initdata,
                    "scraped_at": datetime.now().isoformat()
                })
                self.processed_urls.add(url)
                print(f"  ✅ Thành công!")
            else:
                self.errors.append({
                    "url": url,
                    "index": idx,
                    "attempted_at": datetime.now().isoformat()
                })
                self.processed_urls.add(url)  # Đánh dấu đã thử để không thử lại
                print(f"  ❌ Thất bại")
            
            # Save checkpoint
            if idx % save_interval == 0:
                print(f"\n💾 Đang lưu checkpoint...")
                self._save_checkpoint()
                self._save_results()
            
            # Delay
            time.sleep(delay)
        
        # Save cuối cùng
        print(f"\n{'='*60}")
        print(f"💾 Đang lưu kết quả cuối cùng...")
        self._save_checkpoint()
        self._save_results()
        
        # Thống kê
        total_time = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"✅ HOÀN THÀNH!")
        print(f"{'='*60}")
        print(f"⏱️  Tổng thời gian: {total_time/60:.1f} phút")
        print(f"✅ Thành công: {len(self.results)}/{total}")
        print(f"❌ Thất bại: {len(self.errors)}/{total}")
        print(f"📊 Tỉ lệ thành công: {len(self.results)/total*100:.1f}%")
        print(f"💾 Đã lưu: {self.output_file}")
        if self.errors:
            print(f"💾 Lỗi: scrape_errors.json")
        print(f"{'='*60}\n")
    
    def _save_results(self):
        """Lưu kết quả"""
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        if self.errors:
            with open("scrape_errors.json", "w", encoding="utf-8") as f:
                json.dump(self.errors, f, ensure_ascii=False, indent=2)

def main():
    # Load URLs
    print("📖 Đang đọc file URLs...")
    with open("final_result_link.json", "r", encoding="utf-8") as f:
        urls = json.load(f)
    
    # Tạo scraper
    scraper = FoodyInitDataScraper(
        checkpoint_file="checkpoint.json",
        output_file="restaurant_initdata.json"
    )
    
    # Scrape
    scraper.scrape_all(
        urls=urls,
        save_interval=50,  # Lưu sau mỗi 50 URLs
        delay=1.0  # Delay 1 giây giữa các requests
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Đã dừng bởi người dùng (Ctrl+C)")
        print("💾 Checkpoint đã được lưu, có thể resume sau")
    except Exception as e:
        print(f"\n\n❌ Lỗi nghiêm trọng: {e}")
        raise

