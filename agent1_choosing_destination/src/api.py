from flask import Flask, request, jsonify
import requests
import torch
import pickle
import os
import logging
from together import Together 
from model import TripMindEncoder
from database import get_provinces_stats, agent_1_output
from flask_cors import CORS # Thêm dòng này
from extract_name_from_query import extract_city_from_query

# CONFIG
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TripMind-Gateway")

app = Flask(__name__)
CORS(app) # Thêm dòng này để cho phép giao diện HTML gọi vào API
MODEL = None
WORD2IDX = None
ASSETS = None
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
PROVINCE_STATS = None

AGENT_2_URL = "http://localhost:8000/ranking"
AGENT_3_URL = "http://localhost:9000/optimize"

TOGETHER_CLIENT = Together(api_key="tgp_v1_UW0sLE3au_46TXWs51t_g7VNODLRjPFzb8BTVPMn9yQ")

def load_system():
    global MODEL, ASSETS, WORD2IDX, PROVINCE_STATS
    try:
        logger.info(f"Khởi tạo hệ thống trên thiết bị: {DEVICE}...")
        weights_path = "/Users/trannguyenmyanh/Documents/TripMind/agent1_choosing_destination/weights"
        
        with open(os.path.join(weights_path, "assets.pkl"), "rb") as f:
            ASSETS = pickle.load(f)
        
        WORD2IDX = ASSETS['word2idx']
        vocab_size = ASSETS['vocab_size']
        num_categories = len(ASSETS['cat_encoder'].classes_)
        
        MODEL = TripMindEncoder(
            vocab_size=vocab_size,
            num_categories=num_categories,
            d_model=128,   
            nhead=8,
            num_layers=4   
        ).to(DEVICE)
        
        weights_file = os.path.join(weights_path, "encoder_weights.pth")
        state_dict = torch.load(weights_file, map_location=DEVICE)
        MODEL.load_state_dict(state_dict)
        MODEL.eval()
        
        PROVINCE_STATS = get_provinces_stats()
        
        logger.info("Hệ thống Gateway tích hợp 4 Agent đã sẵn sàng!")
        
    except Exception as e:
        logger.error(f"Lỗi khởi động hệ thống: {str(e)}")
        raise e

def generate_storytelling(itinerary_data, user_query):
    # Kiểm tra an toàn trước khi lặp
    if not itinerary_data or not isinstance(itinerary_data, list):
        return "Tôi đã tìm thấy một số địa điểm thú vị cho bạn, nhưng đang gặp chút vấn đề khi sắp xếp lộ trình. Hãy kiểm tra danh sách bên dưới nhé!"

    try:
        places_summary = ""
        for i, p in enumerate(itinerary_data, 1):
            # Dùng dict.get() với giá trị mặc định để tránh KeyError
            name = p.get('name', 'Địa điểm không tên')
            score_pct = round(p.get('final_score', 0) * 100, 1)
            places_summary += f"{i}. {name} (Độ hài lòng: {score_pct}%)\n"
            
            reviews = p.get('reviews', [])
            if reviews and len(reviews) > 0:
                places_summary += f"   - Review: {reviews[0][:150]}...\n"

        prompt = f"""
                Bạn là chuyên gia tư vấn du lịch của TripMind.
                Khi người dùng hỏi: "{user_query}"

                Chúng tôi đã tìm ra và tối ưu lộ trình di chuyển cho 5 địa điểm tuyệt vời nhất:
                {places_summary}

                Hãy viết một đoạn phản hồi ngắn gọn (khoảng 150-200 từ), thân thiện để chào mừng người dùng.
                Yêu cầu:
                - Không đưa ra phần giải thích hay suy luận của bạn.
                - Chỉ đưa ra phần trả lời, không đưa ra những nội dung dẫn dắt/ giới thiệu vấn đề.
                - Giải thích rằng lộ trình đã được sắp xếp theo thứ tự di chuyển tối ưu nhất.
                - Nhấn mạnh vào chất lượng dịch vụ dựa trên điểm số hài lòng.
                - Trình bày bằng tiếng Việt, giọng văn chuyên nghiệp nhưng gần gũi.
                """

        response = TOGETHER_CLIENT.chat.completions.create(
            model="ServiceNow-AI/Apriel-1.6-15b-Thinker",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Agent 4 LLM Error: {e}")
        return "Chúc bạn có một hành trình tuyệt vời với lộ trình di chuyển tối ưu mà chúng tôi đã chuẩn bị!"

@app.route('/api/v1/recommend', methods=['POST'])
def recommend_places():
    try:
        data = request.get_json()
        query = data.get('query')
        province_id = data.get('province_id')

        if not query:
            return jsonify({"success": False, "error": "Missing query"}), 400

        # Nếu frontend không gửi → tự extract
        if province_id is None:
            province_id = extract_city_from_query(query)
            logger.info(f"Extracted province_id={province_id} from query")
        
        p_id_str = str(province_id).zfill(2) 
        trip_type = data.get('trip_type', 'any')
        n_places = min(int(data.get('n_places', 5)), 10)
        
        # --- Step 1: AGENT 1 (Recall) ---
        candidates = agent_1_output(
            user_query=query, model=MODEL, word2idx=WORD2IDX, assets=ASSETS,
            device=DEVICE, province_id=p_id_str, trip_type=trip_type,
            n_places=5, max_reviews_per_place=5
        )
        
        if not candidates:
            return jsonify({"success": True, "data": [], "message": "Không tìm thấy kết quả"}), 200

        # --- Step 2: AGENT 2 (Sentiment Ranking) ---
        ranked_places = candidates
        try:
            res2 = requests.post(AGENT_2_URL, json=candidates, timeout=10)
            if res2.status_code == 200:
                ranked_places = res2.json()
        except Exception as e:
            logger.warning(f"Agent 2 connection failed: {e}")

        top_candidates = ranked_places[:n_places]

        # --- Step 3: AGENT 3 (Route Optimization) ---
        final_itinerary = top_candidates # Mặc định nếu Agent 3 lỗi
        try:
            res3 = requests.post(AGENT_3_URL, json=top_candidates, timeout=10)
            if res3.status_code == 200:
                optimized_ids = res3.json()
                
                # Logic Re-hydration: Khôi phục object từ danh sách ID của Agent 3
                if isinstance(optimized_ids, list) and len(optimized_ids) > 0:
                    # Tạo dictionary để tìm kiếm nhanh theo ID
                    lookup = {str(p['id']): p for p in top_candidates}
                    # Sắp xếp lại dựa trên thứ tự ID mà Agent 3 trả về
                    final_itinerary = [lookup[str(idx)] for idx in optimized_ids if str(idx) in lookup]
        except Exception as e:
            logger.warning(f"Agent 3 fail: {e}, using default order.")

        # --- Step 4: AGENT 4 (Together.ai Storytelling) ---
        logger.info("Đang khởi tạo Agent 4 để tổng hợp câu trả lời...")
        ai_message = generate_storytelling(final_itinerary, query)

        return jsonify({
            "success": True,
            "recommendation_text": ai_message,
            "data": final_itinerary,           
            "metadata": {
                "province_id": p_id_str,
                "status": "Success",
                "agents_active": 4
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Pipeline Error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Khối này bây giờ sẽ không còn bị SyntaxError nữa vì try bên trên đã được đóng
@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "device": str(DEVICE),
        "agents": {"A2": AGENT_2_URL, "A3": AGENT_3_URL}
    }), 200

if __name__ == "__main__":
    load_system()
    app.run(host='0.0.0.0', port=5000, debug=False)
