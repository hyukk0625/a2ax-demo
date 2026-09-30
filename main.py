from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import hashlib

app = FastAPI()

# 프론트엔드(Vercel)에서 백엔드 API에 차단 없이 접속할 수 있도록 CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    budget: int
    category: str = "hotel"
    location: str = "강남"

@app.post("/api/negotiate")
def run_negotiation(req: SearchRequest):
    # 판매자 에이전트 데이터
    sellers = [
        {"name": "신라호텔 에이전트", "price": 170000, "benefits": ["레이트 체크아웃 1시간", "무료 음료 쿠폰"]},
        {"name": "하얏트호텔 에이전트", "price": 153000, "benefits": ["레이트 체크아웃 1시간", "무료 음료 쿠폰"]}
    ]
    
    best_deal = None
    for s in sellers:
        if s["price"] <= req.budget:
            if best_deal is None or s["price"] < best_deal["price"]:
                best_deal = s
    
    if best_deal:
        # 스마트 계약 해시 및 에스크로 수수료 계산
        contract_raw = f"{best_deal['name']}-{best_deal['price']}-{time.time()}"
        contract_id = "0x" + hashlib.sha256(contract_raw.encode()).hexdigest()[:12]
        fee = int(best_deal['price'] * 0.02)
        payout = best_deal['price'] - fee
        
        return {
            "success": True,
            "contract_id": contract_id,
            "seller": best_deal['name'],
            "price": best_deal['price'],
            "benefits": best_deal['benefits'],
            "fee": fee,
            "payout": payout,
            "message": "A2A 협상 및 에스크로 계약 체결 완료"
        }
    else:
        return {
            "success": False,
            "message": "예산 범위 내 조건에 맞는 에이전트 제안이 없습니다."
        }
        