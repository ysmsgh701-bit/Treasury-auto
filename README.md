# Treasury Auto (자금 운용 자동화 시스템)

이 프로젝트는 엑셀 파일(차입금 현황, 금융상품 현황)을 분석하여 만기일 및 이자 지급일을 자동으로 추적하고, 노션(Notion) 데이터베이스와 동기화하며 필요한 경우 알림을 보내는 시스템입니다.

## 주요 기능
- **엑셀 파싱**: `borrowings.xlsx` 및 `financial_products.xlsx` 파일에서 금융 데이터를 추출합니다.
- **노션 동기화**: 추출된 데이터를 노션 데이터베이스에 자동으로 업데이트합니다. (Notion API v3.0.0 대응)
- **알림 기능**: 만기일 및 이자 지급일 기준 D-Day 알림을 지원합니다. (Slack 등 확장 가능)

## 설치 방법
1. 저장소를 클론합니다.
2. 필요한 라이브러리를 설치합니다.
   ```bash
   pip install -r requirements.txt
   ```
3. `.env` 파일을 설정합니다. (제공된 `.env.example` 참고)
   - `NOTION_TOKEN`: 노션 API 통합 토큰
   - `NOTION_DATABASE_ID`: 노션 데이터베이스 ID
   - `SLACK_WEBHOOK_URL`: (선택) 슬랙 알림용 웹훅 URL

## 사용법
- 노션 동기화 실행:
  ```bash
  python notion_sync.py
  ```
- 만기 및 알림 체크:
  ```bash
  python main.py
  ```

## 주의사항
- 개인 금융 정보가 포함된 `.env` 파일과 `*.xlsx` 파일은 보안을 위해 `.gitignore`에 등록되어 있습니다.
