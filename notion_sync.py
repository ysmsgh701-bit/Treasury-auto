import os
from notion_client import Client
from main import parse_borrowings, parse_financial_products
from dotenv import load_dotenv
import datetime

load_dotenv()

class NotionSync:
    def __init__(self):
        self.notion = Client(auth=os.getenv("NOTION_TOKEN"))
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        self.data_source_id = None
        self._get_data_source_id()

    def _get_data_source_id(self):
        if not self.database_id or "your_notion_database" in self.database_id:
            return
        try:
            db_info = self.notion.databases.retrieve(database_id=self.database_id)
            if "data_sources" in db_info and db_info["data_sources"]:
                self.data_source_id = db_info["data_sources"][0]["id"]
            else:
                # Fallback if structure is different
                print("Warning: No data sources found for this database.")
        except Exception as e:
            print(f"Error retrieving data source ID: {e}")

    def upsert_row(self, data):
        """
        data: dict with properties
        """
        if not self.data_source_id:
            print("Error: data_source_id is not set. Cannot query database.")
            return

        # Search for existing row with same Name (Bank + Account or Bank + Product)
        unique_name = f"[{data['category']}] {data['bank']} - {data.get('account_no') or data.get('product_name') or ''}"
        
        try:
            results = self.notion.data_sources.query(
                data_source_id=self.data_source_id,
                filter={
                    "property": "이름",
                    "title": {
                        "equals": unique_name
                    }
                }
            ).get("results")

            properties = {
                "이름": {"title": [{"text": {"content": unique_name}}]},
                "구분": {"select": {"name": data['category']}},
                "은행": {"select": {"name": data['bank']}},
                "금액": {"number": data['amount'] or 0},
                "이율": {"number": data['rate'] or 0},
                "통화": {"select": {"name": data.get('currency', 'KRW')}}
            }
            
            if data['maturity_date'] and isinstance(data['maturity_date'], (datetime.datetime, datetime.date)):
                date_val = data['maturity_date']
                if isinstance(date_val, datetime.datetime): date_val = date_val.date()
                properties["만기일"] = {"date": {"start": date_val.strftime("%Y-%m-%d")}}
            elif isinstance(data['maturity_date'], str) and data['maturity_date'] != "-":
                properties["만기일"] = {"date": {"start": data['maturity_date']}}

            if results:
                # Update existing
                page_id = results[0]["id"]
                self.notion.pages.update(page_id=page_id, properties=properties)
                print(f"Updated: {unique_name}")
            else:
                # Create new
                self.notion.pages.create(
                    parent={"database_id": self.database_id},
                    properties=properties
                )
                print(f"Created: {unique_name}")
        except Exception as e:
            print(f"Error syncing {unique_name}: {e}")

    def sync(self):
        if not self.database_id or "your_notion_database" in self.database_id:
            print("Notion Database ID is missing in .env")
            return
        
        if not self.data_source_id:
            print("Failed to identify Data Source ID for Notion Sync.")
            return

        print("--- Starting Notion Sync ---")
        
        # 1. Borrowings
        borrowings = parse_borrowings("borrowings.xlsx")
        for b in borrowings:
            b['category'] = "차입금"
            b['currency'] = "KRW" # Assume KRW for current borrowings.xlsx
            self.upsert_row(b)
            
        # 2. Financial Products
        products = parse_financial_products("financial_products.xlsx")
        for p in products:
            p['category'] = "금융상품"
            self.upsert_row(p)
            
        print("--- Notion Sync Completed ---")

if __name__ == "__main__":
    syncer = NotionSync()
    syncer.sync()
