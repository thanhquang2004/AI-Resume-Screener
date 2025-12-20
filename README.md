# 🎯 AI Resume Screener & Job Fit System

**Hệ thống khai phá dữ liệu để sàng lọc hồ sơ và đánh giá mức độ phù hợp giữa Ứng viên (CV) và Tin tuyển dụng (JD).**

> Hệ thống đóng vai trò như một **AI Recruiter**, tự động phân tích CV và JD, tính toán **Điểm phù hợp (Matching Score)** và đưa ra gợi ý xếp hạng các công ty tiềm năng cho ứng viên.

---

## 🎯 Core Features

1. **CV Parsing**: Đọc và trích xuất thông tin từ PDF/DOCX
2. **JD Crawling**: Thu thập tin tuyển dụng từ ITViec, TopDev
3. **Skill Extraction**: NER để trích xuất skills, education, experience
4. **Semantic Matching**: Tính độ tương đồng CV-JD bằng TF-IDF + Cosine Similarity
5. **Company Ranking**: Xếp hạng danh sách công ty tiềm năng từ cao xuống thấp cho 1 CV
6. **Gap Analysis**: Phân tích skills còn thiếu

---

## 📁 Project Structure

```
AI-Resume-Screener/
├── src/
│   ├── crawlers/         # Web scraping JD từ các trang tuyển dụng
│   ├── parsers/          # Đọc và parse CV (PDF/DOCX)
│   ├── preprocessing/    # Làm sạch text, trích xuất skills
│   ├── models/           # Vectorization, Matching, Classification
│   ├── schemas/          # Pydantic data models
│   └── utils/            # Skill dictionary, helpers
├── api/                  # FastAPI application
├── tests/                # Unit tests
├── data/                 # Data storage
└── docs/                 # Documentation
```

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Run Demo

```bash
python demo.py
```

### 3. Start API Server

```bash
uvicorn api.main:app --reload
```

### 4. Access API Docs

Open http://localhost:8000/docs

---

## 📊 Data Mining Tasks

| Task                   | Kỹ thuật          | Mô tả                                               |
| ---------------------- | ----------------- | --------------------------------------------------- |
| Information Extraction | NER (spaCy)       | Trích xuất Skills, Education, Experience            |
| Text Vectorization     | TF-IDF            | Số hóa văn bản                                      |
| Semantic Matching      | Cosine Similarity | Tính độ tương đồng CV-JD                            |
| Classification         | Threshold-based   | Phân loại: Potential / Review Needed / Not Suitable |

---

## 📋 Classification Thresholds

| Category          | Score Range | Meaning                         |
| ----------------- | ----------- | ------------------------------- |
| **Potential**     | > 75%       | Ứng viên tiềm năng, nên xem xét |
| **Review Needed** | 50-75%      | Cần review thêm                 |
| **Not Suitable**  | < 50%       | Không phù hợp                   |

---

## 🔧 Pipeline Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Phase 1   │───▶│   Phase 2   │───▶│   Phase 3   │───▶│   Phase 4   │
│   Collect   │    │  Preprocess │    │   Model     │    │   Output    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      │                  │                  │                  │
      ▼                  ▼                  ▼                  ▼
  Crawl JDs          Clean text        TF-IDF           Ranked list
  Parse CVs          Extract skills    Cosine Sim       Gap analysis
                     Normalize         Classify         Score report
```

---

## 👥 Team Collaboration

Mọi người cùng làm, cùng hiểu toàn bộ pipeline:

| Tuần | Focus           | Tasks                         |
| ---- | --------------- | ----------------------------- |
| 1-2  | Data Collection | Crawl JDs + Parse CVs         |
| 3    | Preprocessing   | Clean text + Skill extraction |
| 4    | Modeling        | Vectorization + Matching      |
| 5    | Integration     | API + Testing                 |
| 6    | Final           | Report + Demo                 |

---

## 📝 License

Educational project for Data Mining course.
