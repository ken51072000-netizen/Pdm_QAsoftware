# 設備頻譜分析報告比對系統

比對人工顧問與軟體系統所產出的設備頻譜分析 PDF 報告，重點針對三個欄位進行差異分析：
- **設備閾值/健康度**
- **診斷說明**
- **改善建議**

## 技術架構

| 層次 | 技術 |
|---|---|
| 前端 | React + Vite + TypeScript + Tailwind CSS |
| 後端 | Python FastAPI |
| PDF 擷取 | pdfplumber |
| AI 結構化解析 | Claude API (claude-sonnet-4-6) |
| 差異比對 | diff-match-patch |

## 快速開始

### 後端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 設定 API 金鑰
cp .env.example .env
# 編輯 .env，填入您的 ANTHROPIC_API_KEY

# 啟動開發伺服器
uvicorn backend.main:app --reload
```

後端運行於 http://localhost:8000

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端運行於 http://localhost:5173

## 使用方式

1. 開啟瀏覽器至 http://localhost:5173
2. 分別上傳人工顧問報告 PDF（左側）與軟體系統報告 PDF（右側）
3. 點擊「開始比對」
4. 系統會使用 AI 自動擷取三個關鍵欄位並進行差異分析
5. 查看各欄位的相似度、差異標示（紅色=人工顧問獨有、綠色=軟體系統獨有）
6. 展開「原始完整文字」區塊可查看 PDF 擷取的完整原始文字

## API 端點

| 方法 | 路徑 | 說明 |
|---|---|---|
| POST | `/api/upload` | 上傳兩份 PDF，回傳 session_id |
| POST | `/api/compare` | 執行 AI 解析與差異比對 |
| GET | `/api/compare/{session_id}` | 取得已完成的比對結果 |
| GET | `/api/health` | 健康狀態檢查 |

## 注意事項

- 僅支援可擷取文字的 PDF（不支援掃描影像 PDF）
- 需要有效的 Anthropic API 金鑰
- 大型 PDF（>50 頁）會自動擷取關鍵頁面
