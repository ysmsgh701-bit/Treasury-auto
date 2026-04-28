import openpyxl
import datetime
import calendar
from notifier import Notifier
import os

def parse_borrowings(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb.active
        borrowings = []
        for row in sheet.iter_rows(min_row=6, values_only=True):
            bank = row[2]
            if bank == '계' or bank is None: continue
            try:
                item = {
                    'bank': bank,
                    'product_type': row[3],
                    'amount': row[5],
                    'rate': row[13],
                    'maturity_date': row[16],
                    'execution_date': row[15],
                    'account_no': row[4],
                    'currency': 'KRW' # Default for borrowings
                }
                borrowings.append(item)
            except: continue
        return borrowings
    except: return []

def parse_financial_products(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb.active
        products = []
        # Header is at row 1
        for row in sheet.iter_rows(min_row=2, values_only=True):
            bank = row[0]
            if bank is None: continue
            try:
                item = {
                    'bank': bank,
                    'product_name': row[1],
                    'type': row[2], # 수시/기간
                    'currency': row[3],
                    'amount': row[4],
                    'rate': row[5],
                    'maturity_date': row[7]
                }
                products.append(item)
            except: continue
        return products
    except: return []

def check_deadlines():
    notifier = Notifier()
    today = datetime.datetime.now().date()
    target_d_days = [30, 10, 3, 0]
    
    # 1. Check Borrowings
    borrowings = parse_borrowings("borrowings.xlsx")
    for b in borrowings:
        # Maturity
        if b['maturity_date'] and isinstance(b['maturity_date'], (datetime.datetime, datetime.date)):
            maturity = b['maturity_date']
            if isinstance(maturity, datetime.datetime): maturity = maturity.date()
            diff = (maturity - today).days
            if diff in target_d_days:
                notifier.notify_dday(f"차입금 만기 ({b['product_type']})", maturity.strftime("%Y-%m-%d"), f"D-{diff}" if diff > 0 else "D-Day", b['amount'] or 0, b['bank'])
        
        # Interest
        if b['execution_date'] and isinstance(b['execution_date'], (datetime.datetime, datetime.date)):
            exec_date = b['execution_date']
            if isinstance(exec_date, datetime.datetime): exec_date = exec_date.date()
            exec_day = exec_date.day
            next_m, next_y = (today.month + 1, today.year) if today.day > exec_day else (today.month, today.year)
            if next_m > 12: next_m, next_y = 1, next_y + 1
            _, last_day = calendar.monthrange(next_y, next_m)
            next_interest_date = datetime.date(next_y, next_m, min(exec_day, last_day))
            diff = (next_interest_date - today).days
            if diff in target_d_days:
                notifier.notify_dday("차입금 이자 지급일", next_interest_date.strftime("%Y-%m-%d"), f"D-{diff}" if diff > 0 else "D-Day", 0, b['bank'])

    # 2. Check Financial Products
    products = parse_financial_products("financial_products.xlsx")
    for p in products:
        if p['maturity_date'] and isinstance(p['maturity_date'], (datetime.datetime, datetime.date, str)):
            if p['maturity_date'] == "-": continue
            maturity = p['maturity_date']
            if isinstance(maturity, str):
                try: maturity = datetime.datetime.strptime(maturity, "%Y-%m-%d").date()
                except: continue
            elif isinstance(maturity, datetime.datetime): maturity = maturity.date()
            
            diff = (maturity - today).days
            if diff in target_d_days:
                amount_str = f"{p['amount']:,.0f} {p['currency']}"
                notifier.notify_dday(f"금융상품 만기 ({p['product_name']})", maturity.strftime("%Y-%m-%d"), f"D-{diff}" if diff > 0 else "D-Day", p['amount'], f"{p['bank']} ({p['currency']})")

if __name__ == "__main__":
    print(f"--- Running Treasury Auto Check ({datetime.datetime.now()}) ---")
    check_deadlines()
    print("--- Check Completed ---")
