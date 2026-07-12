# KIA Enquiry Analytics — FastAPI Backend

## Setup

```bash
cd d:\KIA\backend
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload --port 8000
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/enquiries/trend?group_by=day\|week` | GET | Enquiry counts grouped by day or ISO week |
| `/api/enquiries/customer-type` | GET | Individual vs. Corporate breakdown |
| `/api/enquiries/kpis` | GET | Summary KPI metrics |
| `/api/enquiries/data?page=1&page_size=25&search=&sort_by=&sort_order=asc&customer_type=` | GET | Paginated, searchable, filterable raw data |

## Notes

- The backend reads from `d:\KIA\data\master_clean.csv` on startup.
- CORS is configured for `http://localhost:5173` (Vite dev server).
