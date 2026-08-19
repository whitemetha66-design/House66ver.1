import streamlit as st
import datetime
import pandas as pd
import os
from io import BytesIO

# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Cafe Management System 16 oz",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
    <style>
    .stApp { background-color: #FDFBF7; }
    .main-title { font-size: 24px; font-weight: bold; color: #5C4033; margin-bottom: 5px; }
    .sub-title { font-size: 14px; color: #8B5A2B; margin-bottom: 15px; }
    .stMetric { background-color: #FFFFFF; padding: 12px; border-radius: 12px; border: 1px solid #E6DCCD; box-shadow: 0 2px 5px rgba(92,64,51,0.05); }

    .stButton > button {
        background-color: #FFFFFF !important;
        color: #5C4033 !important;
        border: 2px solid #E6DCCD !important;
        border-radius: 14px !important;
        font-weight: bold !important;
        padding: 15px 10px !important;
        transition: all 0.25s ease-in-out !important;
        box-shadow: 0 4px 6px rgba(92, 64, 51, 0.04);
    }
    .stButton > button:hover {
        background-color: #F5EBE6 !important;
        color: #3B2F2F !important;
        border-color: #C8B6A6 !important;
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(92, 64, 51, 0.12);
    }
    .stButton > button[kind="primary"] {
        background-color: #6F4E37 !important;
        color: #FFFFFF !important;
        border-color: #5C4033 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# TRANSLATION DICTIONARY
# ==========================================
LANG = {
    "TH": {
        "sidebar_title": "☕ ระบบบริหารร้านกาแฟ",
        "nav_label": "เลือกภาษา / Language:",
        "menu_label": "เลือกเมนูการทำงาน:",
        "mode_1": "🥤 1. บันทึกออเดอร์ (POS)",
        "mode_2": "➕ 2. เมนู สูตร และสต็อก",
        "mode_3": "💸 3. ค่าใช้จ่ายและกำไรสุทธิ",
        "mode_4": "📊 4. รายงานยอดขายและกราฟ",
        "mode_5": "📈 5. จุดคุ้มทุนและโปรโมชั่น",
        "settings_header": "⚙️ ตั้งค่าระบบเดลิเวอรี",
        "gp_label": "หัก GP เดลิเวอรี (%)",
        "vat_gp": "คิด VAT 7% บนค่า GP",
        "low_stock": "🚨 แจ้งเตือนด่วน! วัตถุดิบใกล้หมด:",
        "manage_sys": "🛠️ จัดการข้อมูลระบบ",
        "adv_settings": "⚠️ ตั้งค่าขั้นสูง (รีเซ็ต / กู้คืน)",
        "reset_warn": "การรีเซ็ตจะล้างข้อมูลยอดขายและค่าใช้จ่ายทั้งหมด",
        "btn_reset": "🗑️ รีเซ็ตข้อมูลทั้งหมดเป็นค่าว่าง",
        "btn_restore": "🔄 กู้คืนสต็อกและข้อมูลตั้งต้น",
        "reset_success": "รีเซ็ตข้อมูลเรียบร้อย!",
        "restore_success": "กู้คืนระบบตั้งต้นสำเร็จ!",

        # POS Tab
        "pos_title": "🥤 บันทึกออเดอร์ (ระบบขายหน้าร้าน 16 oz)",
        "pos_sub": "☕ เลือกเมนูกาแฟและเครื่องดื่มเพื่อบันทึกการขายและตัดสต็อกอัตโนมัติ",
        "quick_menu": "✨ เมนูยอดฮิต (ปุ่มลัด):",
        "search_menu": "🔍 ค้นหาเมนูในหมวด",
        "no_menu": "❌ ไม่พบเมนูในเงื่อนไขนี้",
        "qty_label": "🔢 จำนวนแก้ว:",
        "channel_label": "ช่องทางขาย",
        "ch_front": "หน้าร้าน",
        "ch_delivery": "เดลิเวอรี",
        "pay_amount": "💰 ยอดที่ลูกค้าต้องชำระ:",
        "net_income": "💵 รายรับสุทธิหลังหัก GP:",
        "btn_order": "☕ ยืนยันการสั่งซื้อ & ตัดสต็อก",
        "order_success": "บันทึกออเดอร์เรียบร้อยแล้ว!",
        "recipe_title": "🧪 สูตรส่วนผสม",
        "cost_per_cup": "ต้นทุนวัตถุดิบรวมต่อแก้ว",
        "no_recipe": "ยังไม่ได้กำหนดสูตรสำหรับเมนูนี้",

        # Menu & Stock Tab
        "ms_title": "➕ จัดการเมนู, สูตรส่วนผสม และคลังวัตถุดิบ",
        "tab_m1": "📋 เพิ่มเมนู & จัดสูตร",
        "tab_m2": "📦 จัดการคลัง & เติมสต็อก",
        "tab_m3": "📊 ตารางราคา & GP",
        "add_menu_title": "1. เพิ่มเมนูใหม่",
        "new_m_name": "ชื่อเมนูใหม่",
        "new_m_cat": "หมวดหมู่สินค้า",
        "new_m_price": "ราคาขายหน้าร้าน (บาท)",
        "new_m_icon": "ไอคอนอีโมจิสำหรับเมนูนี้",
        "btn_add_menu": "➕ เพิ่มเมนูใหม่",
        "menu_added": "เพิ่มเมนูเรียบร้อยแล้ว!",
        "menu_exists": "มีเมนูนี้นานแล้วในระบบ",
        "enter_m_name": "กรุณากรอกชื่อเมนู",
        "recipe_header": "2. จัดสูตรส่วนผสม (16 oz)",
        "sel_cat": "เลือกหมวดหมู่",
        "sel_menu": "เลือกเมนู",
        "sel_ing": "เลือกวัตถุดิบจากคลัง:",
        "btn_save_recipe": "💾 บันทึกสูตรนี้",
        "recipe_saved": "บันทึกสูตรเรียบร้อย!",
        "refill_title": "📥 เติมสต็อกด่วน",
        "sel_material": "เลือกวัตถุดิบ",
        "add_amt": "จำนวนที่เพิ่ม",
        "buy_price": "ราคาซื้อ (บาท)",
        "btn_refill": "➕ เติมสต็อกเข้าคลัง",
        "refill_success": "✅ เติมสต็อกสำเร็จ!",
        "table_inv": "📋 ตารางสต็อกวัตถุดิบทั้งหมด",
        "dl_inv": "📥 ดาวน์โหลดสต็อกวัตถุดิบ",
        "table_menu_gp": "📋 ตารางรวมเมนู & วิเคราะห์ GP เดลิเวอรี",

        # Expenses Tab
        "exp_title": "💸 บันทึกค่าใช้จ่ายอื่นๆ & คำนวณกำไรสุทธิ (Net Profit)",
        "exp_sub": "บันทึกค่าใช้จ่ายคงที่ เช่น ค่าเช่าที่ ค่าไฟ ค่าจ้างพนักงาน เพื่อดูผลกำไรที่แท้จริงของร้าน",
        "add_exp_title": "➕ เพิ่มรายการค่าใช้จ่าย",
        "exp_date": "วันที่บันทึก",
        "exp_name": "รายการค่าใช้จ่าย",
        "exp_cat_lbl": "หมวดหมู่ค่าใช้จ่าย",
        "exp_amt": "จำนวนเงิน (บาท)",
        "btn_save_exp": "💾 บันทึกค่าใช้จ่าย",
        "exp_success": "บันทึกค่าใช้จ่ายสำเร็จ!",
        "exp_warn": "กรุณากรอกชื่อรายการค่าใช้จ่าย",
        "exp_history": "📋 ประวัติค่าใช้จ่ายทั้งหมด",
        "total_exp": "รวมค่าใช้จ่ายอื่นๆ ทั้งหมด",
        "dl_exp": "📥 ดาวน์โหลดรายงานค่าใช้จ่าย",
        "no_exp": "ยังไม่มีข้อมูลค่าใช้จ่ายอื่นๆ",
        "net_sum_title": "💰 สรุปกำไรสุทธิ (Net Profit Summary)",
        "total_sales": "ยอดขายรวมทั้งหมด",
        "total_gp_sum": "กำไรขั้นต้นรวม",
        "net_profit": "กำไรสุทธิ (หักค่าใช้จ่ายแล้ว)",

        # Sales Report Tab
        "rep_title": "📊 รายงานสรุปยอดขายและกราฟวิเคราะห์แนวโน้ม",
        "tot_qty_lbl": "จำนวนขายรวมทั้งหมด",
        "tot_rev_lbl": "ยอดขายรวม",
        "chart_daily": "📈 กราฟแสดงยอดขายแยกตามรายวัน",
        "chart_menu": "🥤 สัดส่วนยอดขายแยกตามเมนู",
        "history_sales": "📋 ประวัติการขายทั้งหมด",
        "dl_sales": "📥 ดาวน์โหลดรายงานยอดขาย",
        "no_sales": "ยังไม่มีข้อมูลการขายในระบบ กรุณาไปที่หน้า POS เพื่อบันทึกออเดอร์แรกครับ",

        # Break-even Tab
        "be_title": "📈 การวิเคราะห์จุดคุ้มทุน (Break-Even Analysis) & จำลองโปรโมชั่น",
        "be_sub": "คำนวณว่าร้านต้องขายให้ได้กี่แก้วจึงจะคุ้มทุนค่าใช้จ่ายคงที่ทั้งหมด",
        "fixed_cost": "📌 ค่าใช้จ่ายคงที่รวมทั้งหมด (Fixed Cost)",
        "contrib_margin": "☕ กำไรส่วนเกินเฉลี่ยต่อแก้ว (Contribution Margin)",
        "be_target": "🎯 **จุดคุ้มทุนของร้าน:** คุณต้องขายเครื่องดื่มเฉลี่ยรวมทุกเมนูให้ได้ประมาณ",
        "be_cups": "แก้ว จึงจะคุ้มทุนค่าใช้จ่ายทั้งหมด",
        "target_days": "ระยะเวลาเป้าหมาย (วัน)",
        "be_per_day": "📅 หมายความว่า ใน 1 เดือน คุณต้องขายให้ได้เฉลี่ยวันละประมาณ",
        "be_warn": "⚠️ กรุณาบันทึกค่าใช้จ่ายคงที่ (Tab 3) และกำหนดสูตรราคาต้นทุนให้เรียบร้อยก่อน ระบบจึงจะคำนวณจุดคุ้มทุนได้อย่างแม่นยำ"
    },
    "EN": {
        "sidebar_title": "☕ Cafe Management System",
        "nav_label": "Language / เลือกภาษา:",
        "menu_label": "Select Menu:",
        "mode_1": "🥤 1. Order POS",
        "mode_2": "➕ 2. Menu, Recipe & Stock",
        "mode_3": "💸 3. Expenses & Net Profit",
        "mode_4": "📊 4. Sales Report & Charts",
        "mode_5": "📈 5. Break-Even & Promo",
        "settings_header": "⚙️ Delivery Settings",
        "gp_rate": "Delivery GP Deduction (%)",
        "vat_gp": "Include 7% VAT on GP",
        "low_stock": "🚨 Low stock alert:",
        "manage_sys": "🛠️ System Data Management",
        "adv_settings": "⚠️ Advanced (Reset / Restore)",
        "reset_warn": "Resetting will clear all sales and expenses data.",
        "btn_reset": "🗑️ Reset All Data",
        "btn_restore": "🔄 Restore Default Stock & Data",
        "reset_success": "Data reset successfully!",
        "restore_success": "Default system restored successfully!",

        # POS Tab
        "pos_title": "🥤 POS Order System (16 oz)",
        "pos_sub": "☕ Select coffee & beverages to record sales and automatically deduct stock.",
        "quick_menu": "✨ Quick Menu Slots:",
        "search_menu": "🔍 Search menu in category",
        "no_menu": "❌ No menu found",
        "qty_label": "🔢 Quantity (Cups):",
        "channel_label": "Sales Channel",
        "ch_front": "Storefront",
        "ch_delivery": "Delivery",
        "pay_amount": "💰 Customer Total Payment:",
        "net_income": "💵 Net Income after GP:",
        "btn_order": "☕ Confirm Order & Deduct Stock",
        "order_success": "Order saved successfully!",
        "recipe_title": "🧪 Recipe Ingredients",
        "cost_per_cup": "Total Ingredient Cost per Cup",
        "no_recipe": "Recipe not defined for this menu yet.",

        # Menu & Stock Tab
        "ms_title": "➕ Manage Menu, Recipes & Inventory",
        "tab_m1": "📋 Add Menu & Recipes",
        "tab_m2": "📦 Manage Stock & Refill",
        "tab_m3": "📊 Price Table & GP",
        "add_menu_title": "1. Add New Menu",
        "new_m_name": "New Menu Name",
        "new_m_cat": "Category",
        "new_m_price": "Storefront Price (THB)",
        "new_m_icon": "Emoji Icon",
        "btn_add_menu": "➕ Add New Menu",
        "menu_added": "Menu added successfully!",
        "menu_exists": "Menu already exists in the system.",
        "enter_m_name": "Please enter a menu name.",
        "recipe_header": "2. Setup Recipe (16 oz)",
        "sel_cat": "Select Category",
        "sel_menu": "Select Menu",
        "sel_ing": "Select Ingredients from Stock:",
        "btn_save_recipe": "💾 Save Recipe",
        "recipe_saved": "Recipe saved successfully!",
        "refill_title": "📥 Quick Stock Refill",
        "sel_material": "Select Material",
        "add_amt": "Quantity to Add",
        "buy_price": "Purchase Price (THB)",
        "btn_refill": "➕ Refill Stock",
        "refill_success": "✅ Stock refilled successfully!",
        "table_inv": "📋 Complete Inventory Table",
        "dl_inv": "📥 Download Inventory Report",
        "table_menu_gp": "📋 Menu Table & Delivery GP Analysis",

        # Expenses Tab
        "exp_title": "💸 Expenses & Net Profit Calculation",
        "exp_sub": "Record fixed expenses such as rent, utilities, and wages to view real net profit.",
        "add_exp_title": "➕ Add Expense Item",
        "exp_date": "Date",
        "exp_name": "Expense Name",
        "exp_cat_lbl": "Category",
        "exp_amt": "Amount (THB)",
        "btn_save_exp": "💾 Save Expense",
        "exp_success": "Expense saved successfully!",
        "exp_warn": "Please enter an expense name.",
        "exp_history": "📋 Expense History",
        "total_exp": "Total Other Expenses",
        "dl_exp": "📥 Download Expense Report",
        "no_exp": "No expense data yet.",
        "net_sum_title": "💰 Net Profit Summary",
        "total_sales": "Total Sales",
        "total_gp_sum": "Total Gross Profit",
        "net_profit": "Net Profit (After Expenses)",

        # Sales Report Tab
        "rep_title": "📊 Sales Summary Report & Trend Charts",
        "tot_qty_lbl": "Total Cups Sold",
        "tot_rev_lbl": "Total Revenue",
        "chart_daily": "📈 Daily Sales Trend Chart",
        "chart_menu": "🥤 Sales Share by Menu",
        "history_sales": "📋 Complete Sales History",
        "dl_sales": "📥 Download Sales Report",
        "no_sales": "No sales data yet. Please go to POS to record your first order.",

        # Break-even Tab
        "be_title": "📈 Break-Even Analysis & Promotion Simulator",
        "be_sub": "Calculate how many cups you need to sell to cover all fixed expenses.",
        "fixed_cost": "📌 Total Fixed Cost",
        "contrib_margin": "☕ Average Contribution Margin per Cup",
        "be_target": "🎯 **Break-Even Point:** You need to sell approximately",
        "be_cups": "cups in total to cover all expenses.",
        "target_days": "Target Period (Days)",
        "be_per_day": "📅 This means you need to sell an average of about",
        "be_warn": "⚠️ Please record fixed costs (Tab 3) and setup recipe costs first to accurately calculate the break-even point."
    }
}


# ==========================================
# EXCEL CONVERTER FUNCTION
# ==========================================
def convert_df_to_excel(df):
    output = BytesIO()
    try:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        return output.getvalue(), "xlsx"
    except:
        return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig'), "csv"


# ==========================================
# PERSISTENT STORAGE (CSV FUNCTIONS)
# ==========================================
INV_FILE = "inventory_data.csv"
SALES_FILE = "sales_data.csv"
EXP_FILE = "expenses_data.csv"


def load_data():
    if "inventory_df" not in st.session_state:
        if os.path.exists(INV_FILE):
            st.session_state.inventory_df = pd.read_csv(INV_FILE)
        else:
            st.session_state.inventory_df = pd.DataFrame([
                {"หมวดหมู่": "🫘 วัตถุดิบหลัก", "รายการ": "เมล็ดกาแฟ (Arabica)", "ราคาซื้อ (บาท)": 600.0,
                 "ขนาดบรรจุ": 1000.0, "หน่วย": "กรัม"},
                {"หมวดหมู่": "🥛 วัตถุดิบหลัก", "รายการ": "นมสดพาสเจอร์ไรส์", "ราคาซื้อ (บาท)": 95.0,
                 "ขนาดบรรจุ": 1000.0, "หน่วย": "มล."},
                {"หมวดหมู่": "🍵 วัตถุดิบหลัก", "รายการ": "ผงมัทฉะพรีเมียม", "ราคาซื้อ (บาท)": 450.0, "ขนาดบรรจุ": 100.0,
                 "หน่วย": "กรัม"},
                {"หมวดหมู่": "🍵 วัตถุดิบหลัก", "รายการ": "ผงชาไทย", "ราคาซื้อ (บาท)": 140.0, "ขนาดบรรจุ": 400.0,
                 "หน่วย": "กรัม"},
                {"หมวดหมู่": "🍫 วัตถุดิบหลัก", "รายการ": "ผงโกโก้พรีเมียม", "ราคาซื้อ (บาท)": 180.0, "ขนาดบรรจุ": 500.0,
                 "หน่วย": "กรัม"},
                {"หมวดหมู่": "🧊 วัตถุดิบหลัก", "รายการ": "น้ำแข็ง / น้ำสะอาด", "ราคาซื้อ (บาท)": 50.0,
                 "ขนาดบรรจุ": 20000.0, "หน่วย": "กรัม"},
                {"หมวดหมู่": "🍯 ส่วนผสมปรุงรส", "รายการ": "นมข้นหวาน/นมข้นจืด", "ราคาซื้อ (บาท)": 55.0,
                 "ขนาดบรรจุ": 380.0, "หน่วย": "มล."},
                {"หมวดหมู่": "🥡 บรรจุภัณฑ์", "รายการ": "แก้ว PET 16 oz + ฝา + หลอด", "ราคาซื้อ (บาท)": 280.0,
                 "ขนาดบรรจุ": 100.0, "หน่วย": "ชุด"},
            ])

    if "daily_sales_db" not in st.session_state:
        if os.path.exists(SALES_FILE):
            st.session_state.daily_sales_db = pd.read_csv(SALES_FILE)
        else:
            st.session_state.daily_sales_db = pd.DataFrame(columns=[
                "วันที่", "เวลา", "หมวดหมู่", "เมนู", "ช่องทาง",
                "จำนวน (แก้ว)", "ราคาขาย/แก้ว", "ต้นทุน/แก้ว",
                "ยอดขายรวม", "ต้นทุนรวม", "กำไรขั้นต้น"
            ])

    if "expenses_db" not in st.session_state:
        if os.path.exists(EXP_FILE):
            st.session_state.expenses_db = pd.read_csv(EXP_FILE)
        else:
            st.session_state.expenses_db = pd.DataFrame(columns=[
                "วันที่", "รายการค่าใช้จ่าย", "หมวดหมู่", "จำนวนเงิน (บาท)"
            ])


def save_inventory():
    st.session_state.inventory_df.to_csv(INV_FILE, index=False)


def save_sales():
    st.session_state.daily_sales_db.to_csv(SALES_FILE, index=False)


def save_expenses():
    st.session_state.expenses_db.to_csv(EXP_FILE, index=False)


load_data()

# ==========================================
# INITIAL SESSION STATE (Menu & Recipes)
# ==========================================
if "delivery_menu_db" not in st.session_state:
    st.session_state.delivery_menu_db = {
        "เอสเพรสโซเย็น": {"category": "☕ กาแฟ", "icon": "☕", "price": 60.0, "cost": 18.50, "share": 25.0},
        "อเมริกาโนเย็น": {"category": "☕ กาแฟ", "icon": "🧊", "price": 55.0, "cost": 14.20, "share": 25.0},
        "ลาเต้เย็น": {"category": "☕ กาแฟ", "icon": "🥛", "price": 60.0, "cost": 19.80, "share": 15.0},
        "ชาไทยเย็น": {"category": "🧋 ชา", "icon": "🧋", "price": 45.0, "cost": 14.50, "share": 15.0},
        "มัทฉะลาเต้": {"category": "🧋 ชา", "icon": "🌿", "price": 75.0, "cost": 32.90, "share": 5.0},
        "โกโก้เย็น": {"category": "🍫 นม/โกโก้", "icon": "🍫", "price": 50.0, "cost": 17.20, "share": 10.0},
        "แดงมะนาวโซดา": {"category": "🍹 อิตาเลี่ยนโซดา", "icon": "🍹", "price": 40.0, "cost": 11.50, "share": 5.0},
    }

if "recipes_db" not in st.session_state:
    st.session_state.recipes_db = {
        "เอสเพรสโซเย็น": [
            {"รายการ": "เมล็ดกาแฟ (Arabica)", "ปริมาณ": 18.0, "wastage": 5.0},
            {"รายการ": "นมสดพาสเจอร์ไรส์", "ปริมาณ": 60.0, "wastage": 5.0},
            {"รายการ": "นมข้นหวาน/นมข้นจืด", "ปริมาณ": 30.0, "wastage": 0.0},
            {"รายการ": "น้ำแข็ง / น้ำสะอาด", "ปริมาณ": 150.0, "wastage": 5.0},
            {"รายการ": "แก้ว PET 16 oz + ฝา + หลอด", "ปริมาณ": 1.0, "wastage": 0.0}
        ],
        "อเมริกาโนเย็น": [
            {"รายการ": "เมล็ดกาแฟ (Arabica)", "ปริมาณ": 18.0, "wastage": 5.0},
            {"รายการ": "น้ำแข็ง / น้ำสะอาด", "ปริมาณ": 200.0, "wastage": 5.0},
            {"รายการ": "แก้ว PET 16 oz + ฝา + หลอด", "ปริมาณ": 1.0, "wastage": 0.0}
        ],
        "ชาไทยเย็น": [
            {"รายการ": "ผงชาไทย", "ปริมาณ": 15.0, "wastage": 5.0},
            {"รายการ": "นมสดพาสเจอร์ไรส์", "ปริมาณ": 60.0, "wastage": 5.0},
            {"รายการ": "นมข้นหวาน/นมข้นจืด", "ปริมาณ": 30.0, "wastage": 0.0},
            {"รายการ": "น้ำแข็ง / น้ำสะอาด", "ปริมาณ": 150.0, "wastage": 5.0},
            {"รายการ": "แก้ว PET 16 oz + ฝา + หลอด", "ปริมาณ": 1.0, "wastage": 0.0}
        ]
    }

for cat in ["☕ กาแฟ", "🧋 ชา", "🍫 นม/โกโก้", "🍹 อิตาเลี่ยนโซดา", "📦 อื่นๆ"]:
    if f"selected_menu_{cat}" not in st.session_state:
        st.session_state[f"selected_menu_{cat}"] = None


# ==========================================
# HELPER FUNCTIONS
# ==========================================
def get_flattened_menu_df() -> pd.DataFrame:
    rows = []
    menu_db = st.session_state.get("delivery_menu_db", {})
    for menu_name, menu_info in menu_db.items():
        if not isinstance(menu_info, dict): continue
        cat = menu_info.get("category", "📦 อื่นๆ")
        price_front = float(menu_info.get("price", 0.0))
        price_del = price_front + 20.0
        cost_val = float(menu_info.get("cost", 0.0))
        share_val = float(menu_info.get("share", 0.0))
        rows.append({
            "หมวดหมู่": cat, "เมนู": menu_name, "ขนาดแก้ว": "16 oz",
            "ราคาหน้าร้าน": price_front, "ราคา Delivery": price_del,
            "ต้นทุนแปรผัน": cost_val, "สัดส่วนขาย (%)": share_val
        })
    return pd.DataFrame(rows)


def get_all_categories() -> list:
    cats = set()
    menu_db = st.session_state.get("delivery_menu_db", {})
    for m_info in menu_db.values():
        if isinstance(m_info, dict): cats.add(str(m_info.get("category", "📦 อื่นๆ")))
    return sorted(list(cats))


# ==========================================
# SIDEBAR NAVIGATION & SETTINGS
# ==========================================
st.sidebar.title("☕ Cafe Management")

# Language Selector
selected_lang = st.sidebar.selectbox("🌐 Language / เลือกภาษา:", ["TH", "EN"], index=0)
t = LANG[selected_lang]

st.sidebar.markdown("---")

app_mode = st.sidebar.radio(
    t["menu_label"],
    [
        t["mode_1"],
        t["mode_2"],
        t["mode_3"],
        t["mode_4"],
        t["mode_5"]
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader(t["settings_header"])
gp_rate = st.sidebar.number_input(t["gp_label"], min_value=0.0, max_value=50.0, value=30.0, step=1.0)
include_vat_gp = st.sidebar.checkbox(t["vat_gp"], value=True)
effective_gp_pct = gp_rate * 1.07 if include_vat_gp else gp_rate

# Low stock alert
inv_check_df = st.session_state.inventory_df
low_stock_items = [row["รายการ"] for idx, row in inv_check_df.iterrows() if float(row["ขนาดบรรจุ"]) <= 20.0]
if low_stock_items:
    st.sidebar.error(f"{t['low_stock']} **{', '.join(low_stock_items)}**")

# ==========================================
# RESET & RESTORE SYSTEM
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader(t["manage_sys"])

with st.sidebar.expander(t["adv_settings"]):
    st.warning(t["reset_warn"])

    if st.button(t["btn_reset"], use_container_width=True):
        st.session_state.daily_sales_db = pd.DataFrame(columns=[
            "วันที่", "เวลา", "หมวดหมู่", "เมนู", "ช่องทาง",
            "จำนวน (แก้ว)", "ราคาขาย/แก้ว", "ต้นทุน/แก้ว",
            "ยอดขายรวม", "ต้นทุนรวม", "กำไรขั้นต้น"
        ])
        st.session_state.expenses_db = pd.DataFrame(columns=[
            "วันที่", "รายการค่าใช้จ่าย", "หมวดหมู่", "จำนวนเงิน (บาท)"
        ])
        if os.path.exists(SALES_FILE): os.remove(SALES_FILE)
        if os.path.exists(EXP_FILE): os.remove(EXP_FILE)
        st.success(t["reset_success"])
        st.rerun()

    if st.button(t["btn_restore"], use_container_width=True):
        if os.path.exists(INV_FILE): os.remove(INV_FILE)
        if os.path.exists(SALES_FILE): os.remove(SALES_FILE)
        if os.path.exists(EXP_FILE): os.remove(EXP_FILE)
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success(t["restore_success"])
        st.rerun()

# ==========================================
# MAIN ROUTING (5 TABS)
# ==========================================

# ------------------------------------------
# TAB 1: บันทึกออเดอร์ (POS)
# ------------------------------------------
if app_mode == t["mode_1"]:
    st.markdown(f"<div class='main-title'>{t['pos_title']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-title'>{t['pos_sub']}</div>", unsafe_allow_html=True)

    st.markdown(t["quick_menu"])
    q_cols = st.columns(4)
    quick_menus = ["เอสเพรสโซเย็น", "อเมริกาโนเย็น", "ชาไทยเย็น", "โกโก้เย็น"]


    def quick_order_action(m_name):
        menu_db = st.session_state.delivery_menu_db
        if m_name in menu_db:
            m_info = menu_db[m_name]
            cat_n = m_info.get("category", "📦 อื่นๆ")
            price_v = m_info["price"]
            cost_v = m_info["cost"]
            current_time_str = datetime.datetime.now().strftime("%H:%M:%S")

            new_row = pd.DataFrame([{
                "วันที่": str(datetime.date.today()), "เวลา": current_time_str, "หมวดหมู่": cat_n,
                "เมนู": f"{m_name} (16 oz)", "ช่องทาง": t["ch_front"], "จำนวน (แก้ว)": 1,
                "ราคาขาย/แก้ว": price_v, "ต้นทุน/แก้ว": cost_v, "ยอดขายรวม": price_v,
                "ต้นทุนรวม": cost_v, "กำไรขั้นต้น": price_v - cost_v
            }])
            st.session_state.daily_sales_db = pd.concat([st.session_state.daily_sales_db, new_row], ignore_index=True)
            save_sales()

            if m_name in st.session_state.recipes_db:
                inv_df = st.session_state.inventory_df
                for ing in st.session_state.recipes_db[m_name]:
                    ing_name = ing["รายการ"]
                    ing_qty = ing["ปริมาณ"] * (1 + ing["wastage"] / 100.0)
                    m_idx = inv_df[inv_df["รายการ"] == ing_name].index
                    if not m_idx.empty:
                        r_idx = m_idx[0]
                        inv_df.at[r_idx, "ขนาดบรรจุ"] = max(0.0, float(inv_df.at[r_idx, "ขนาดบรรจุ"]) - ing_qty)
                st.session_state.inventory_df = inv_df
                save_inventory()

            st.toast(f"🤎 Quick Order: {m_name} Success!")
            st.rerun()


    for i, qm in enumerate(quick_menus):
        if qm in st.session_state.delivery_menu_db:
            icon_str = st.session_state.delivery_menu_db[qm].get("icon", "☕")
            p_val = st.session_state.delivery_menu_db[qm]["price"]
            if q_cols[i].button(f"{icon_str}  {qm}\n({p_val:,.0f} ฿)", use_container_width=True, key=f"quick_btn_{qm}"):
                quick_order_action(qm)

    st.markdown("---")
    categories = get_all_categories()
    if categories:
        category_tabs = st.tabs([cat for cat in categories])
        for idx, cat_name in enumerate(categories):
            with category_tabs[idx]:
                search_query = st.text_input(f"{t['search_menu']} {cat_name}...", placeholder="Search...",
                                             key=f"search_{cat_name}")
                filtered_menus = []
                menu_db = st.session_state.delivery_menu_db
                for m_name, m_info in menu_db.items():
                    if m_info.get("category", "📦 อื่นๆ") != cat_name: continue
                    if search_query.strip() and search_query.strip().lower() not in m_name.lower(): continue
                    filtered_menus.append(m_name)

                if not filtered_menus:
                    st.warning(t["no_menu"])
                else:
                    cols = st.columns(3)
                    for i, m_name in enumerate(filtered_menus):
                        col_target = cols[i % 3]
                        m_info = menu_db[m_name]
                        item_icon = m_info.get("icon", "☕")
                        p_val = m_info.get("price", 0)

                        is_selected = (st.session_state[f"selected_menu_{cat_name}"] == m_name)
                        btn_label = f"{item_icon}  {m_name}\n{p_val:,.0f} ฿ (16 oz)"
                        btn_type = "primary" if is_selected else "secondary"

                        if col_target.button(btn_label, key=f"btn_menu_{cat_name}_{m_name}", type=btn_type,
                                             use_container_width=True):
                            st.session_state[f"selected_menu_{cat_name}"] = m_name
                            st.rerun()

                    current_sel = st.session_state[f"selected_menu_{cat_name}"]
                    if current_sel not in filtered_menus:
                        current_sel = filtered_menus[0]
                        st.session_state[f"selected_menu_{cat_name}"] = current_sel

                    if current_sel:
                        st.markdown("---")
                        menu_data = menu_db[current_sel]
                        base_price = menu_data["price"]
                        selected_icon = menu_data.get("icon", "☕")
                        unit_cost_val = float(menu_data.get("cost", 0.0))

                        col_info1, col_info2 = st.columns([1, 2])
                        with col_info1:
                            st.markdown(f"### {selected_icon} {current_sel}")
                            target_qty = st.number_input(t["qty_label"], min_value=1, value=1, step=1,
                                                         key=f"qty_mult_{cat_name}")
                            channel = st.radio(t["channel_label"], [t["ch_front"], t["ch_delivery"]], horizontal=True,
                                               key=f"channel_{cat_name}")

                            sale_price_to_customer = base_price if channel == t["ch_front"] else (base_price + 20.0)
                            net_income_per_cup = sale_price_to_customer * (1 - effective_gp_pct / 100) if channel == t[
                                "ch_delivery"] else sale_price_to_customer

                            total_batch_sales = sale_price_to_customer * target_qty
                            total_batch_net_income = net_income_per_cup * target_qty
                            total_batch_cost = unit_cost_val * target_qty
                            total_batch_profit = total_batch_net_income - total_batch_cost

                            st.info(f"{t['pay_amount']} `{sale_price_to_customer:,.2f}` THB")
                            if channel == t["ch_delivery"]:
                                st.write(f"{t['net_income']} `{total_batch_net_income:,.2f}` THB")

                            if st.button(t["btn_order"], type="primary", use_container_width=True,
                                         key=f"btn_save_order_{cat_name}"):
                                full_menu_name_str = f"{current_sel} (16 oz)"
                                current_time_str = datetime.datetime.now().strftime("%H:%M:%S")

                                new_row = pd.DataFrame([{
                                    "วันที่": str(datetime.date.today()), "เวลา": current_time_str,
                                    "หมวดหมู่": cat_name,
                                    "เมนู": full_menu_name_str, "ช่องทาง": channel, "จำนวน (แก้ว)": target_qty,
                                    "ราคาขาย/แก้ว": sale_price_to_customer, "ต้นทุน/แก้ว": unit_cost_val,
                                    "ยอดขายรวม": total_batch_sales, "ต้นทุนรวม": total_batch_cost,
                                    "กำไรขั้นต้น": total_batch_profit
                                }])
                                st.session_state.daily_sales_db = pd.concat([st.session_state.daily_sales_db, new_row],
                                                                            ignore_index=True)
                                save_sales()

                                if current_sel in st.session_state.recipes_db:
                                    inv_df = st.session_state.inventory_df
                                    for ing in st.session_state.recipes_db[current_sel]:
                                        ing_name = ing["รายการ"]
                                        ing_qty_needed = ing["ปริมาณ"] * (1 + ing["wastage"] / 100.0) * target_qty
                                        match_idx = inv_df[inv_df["รายการ"] == ing_name].index
                                        if not match_idx.empty:
                                            idx_row = match_idx[0]
                                            inv_df.at[idx_row, "ขนาดบรรจุ"] = max(0.0, float(
                                                inv_df.at[idx_row, "ขนาดบรรจุ"]) - ing_qty_needed)
                                    st.session_state.inventory_df = inv_df
                                    save_inventory()

                                st.success(t["order_success"])
                                st.rerun()

                        with col_info2:
                            st.subheader(f"{t['recipe_title']}: {current_sel} (16 oz)")
                            current_recipe = st.session_state.recipes_db.get(current_sel, [])
                            if current_recipe:
                                st.dataframe(pd.DataFrame(current_recipe), use_container_width=True, hide_index=True)
                                st.metric(t["cost_per_cup"], f"{unit_cost_val:.2f} THB")
                            else:
                                st.warning(t["no_recipe"])

# ------------------------------------------
# TAB 2: เมนู & สูตร & สต็อก
# ------------------------------------------
elif app_mode == t["mode_2"]:
    st.markdown(f"<div class='main-title'>{t['ms_title']}</div>", unsafe_allow_html=True)

    sub_tab1, sub_tab2, sub_tab3 = st.tabs([t["tab_m1"], t["tab_m2"], t["tab_m3"]])

    with sub_tab1:
        st.subheader(t["add_menu_title"])
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            new_menu_name = st.text_input(t["new_m_name"], placeholder="e.g. Iced Mocha")
        with col_m2:
            new_menu_cat = st.selectbox(t["new_m_cat"],
                                        options=["☕ กาแฟ", "🧋 ชา", "🍫 นม/โกโก้", "🍹 อิตาเลี่ยนโซดา", "📦 อื่นๆ"],
                                        key="new_cat_t2")
        with col_m3:
            new_menu_price = st.number_input(t["new_m_price"], min_value=0.0, value=50.0, step=5.0)
        new_menu_icon = st.text_input(t["new_m_icon"], value="☕")

        if st.button(t["btn_add_menu"], use_container_width=True):
            if new_menu_name.strip():
                if new_menu_name not in st.session_state.delivery_menu_db:
                    st.session_state.delivery_menu_db[new_menu_name] = {
                        "category": new_menu_cat, "icon": new_menu_icon, "price": new_menu_price, "cost": 0.0,
                        "share": 5.0
                    }
                    st.success(t["menu_added"])
                    st.rerun()
                else:
                    st.error(t["menu_exists"])
            else:
                st.warning(t["enter_m_name"])

        st.markdown("---")
        st.subheader(t["recipe_header"])
        all_cats = get_all_categories()
        if all_cats:
            col_cat_sel, col_menu_sel = st.columns(2)
            with col_cat_sel:
                recipe_cat_target = st.selectbox(t["sel_cat"], options=all_cats, key="recipe_cat_target")

            filtered_menus_for_recipe = [m_name for m_name, m_info in st.session_state.delivery_menu_db.items() if
                                         m_info.get("category", "📦 อื่นๆ") == recipe_cat_target]

            with col_menu_sel:
                recipe_menu_target = st.selectbox(t["sel_menu"], options=filtered_menus_for_recipe,
                                                  key="recipe_m_target") if filtered_menus_for_recipe else None

            if recipe_menu_target:
                current_recipe = st.session_state.recipes_db.get(recipe_menu_target, [])
                df_inv = st.session_state.inventory_df.copy()
                df_inv["ต้นทุนต่อหน่วย"] = df_inv["ราคาซื้อ (บาท)"] / df_inv["ขนาดบรรจุ"]

                default_items = [item["รายการ"] for item in current_recipe if
                                 item["รายการ"] in df_inv["รายการ"].tolist()]
                selected_items = st.multiselect(t["sel_ing"], options=df_inv["รายการ"].tolist(), default=default_items,
                                                key=f"ms_tab2_{recipe_menu_target}")

                total_recipe_cost = 0.0
                new_recipe_data = []

                if selected_items:
                    recipe_dict = {item["รายการ"]: item for item in current_recipe}
                    for item in selected_items:
                        item_info = df_inv[df_inv["รายการ"] == item].iloc[0]
                        prev_qty = recipe_dict[item]["ปริมาณ"] if item in recipe_dict else 10.0
                        prev_wastage = recipe_dict[item]["wastage"] if item in recipe_dict else 5.0

                        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                        c1.write(f"**{item}**")
                        qty = c2.number_input("Qty", min_value=0.0, value=float(prev_qty),
                                              key=f"q_t2_{recipe_menu_target}_{item}")
                        wastage = c3.number_input("Wastage %", min_value=0.0, value=float(prev_wastage),
                                                  key=f"w_t2_{recipe_menu_target}_{item}")

                        item_cost = qty * (1 + wastage / 100.0) * item_info["ต้นทุนต่อหน่วย"]
                        total_recipe_cost += item_cost
                        c4.write(f"{item_cost:.2f} ฿")
                        new_recipe_data.append({"รายการ": item, "ปริมาณ": qty, "wastage": wastage})

                if st.button(t["btn_save_recipe"], type="primary", key=f"btn_save_t2_{recipe_menu_target}"):
                    st.session_state.recipes_db[recipe_menu_target] = new_recipe_data
                    st.session_state.delivery_menu_db[recipe_menu_target]["cost"] = round(total_recipe_cost, 2)
                    st.success(t["recipe_saved"])
                    st.rerun()

    with sub_tab2:
        st.subheader(t["refill_title"])
        inv_list = st.session_state.inventory_df["รายการ"].tolist()
        col_ref1, col_ref2, col_ref3 = st.columns([3, 2, 2])
        with col_ref1:
            refill_item = st.selectbox(t["sel_material"], options=inv_list, key="refill_item_sel")

        current_row = st.session_state.inventory_df[st.session_state.inventory_df["รายการ"] == refill_item].iloc[0]
        curr_unit = current_row["หน่วย"]
        curr_qty = current_row["ขนาดบรรจุ"]

        with col_ref2:
            add_amount = st.number_input(f"{t['add_amt']} ({curr_unit})", min_value=0.0, value=float(curr_qty),
                                         step=1.0, key="refill_amount_input")
        with col_ref3:
            new_price = st.number_input(t["buy_price"], min_value=0.0, value=float(current_row["ราคาซื้อ (บาท)"]),
                                        step=5.0, key="refill_price_input")

        if st.button(t["btn_refill"], type="primary", use_container_width=True):
            idx_target = st.session_state.inventory_df[st.session_state.inventory_df["รายการ"] == refill_item].index[0]
            old_val = float(st.session_state.inventory_df.at[idx_target, "ขนาดบรรจุ"])
            st.session_state.inventory_df.at[idx_target, "ขนาดบรรจุ"] = old_val + add_amount
            st.session_state.inventory_df.at[idx_target, "ราคาซื้อ (บาท)"] = new_price
            save_inventory()
            st.success(t["refill_success"])
            st.rerun()

        st.markdown("---")
        st.subheader(t["table_inv"])
        edited_inv = st.data_editor(st.session_state.inventory_df, num_rows="dynamic", use_container_width=True,
                                    key="inv_editor")
        if not edited_inv.equals(st.session_state.inventory_df):
            st.session_state.inventory_df = edited_inv
            save_inventory()

        inv_data_bytes, inv_ext = convert_df_to_excel(st.session_state.inventory_df)
        st.download_button(
            label=f"{t['dl_inv']} ({inv_ext.upper()})",
            data=inv_data_bytes,
            file_name=f"inventory_report.{inv_ext}",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if inv_ext == "xlsx" else "text/csv"
        )

    with sub_tab3:
        st.subheader(t["table_menu_gp"])
        menu_df = get_flattened_menu_df()
        gp_factor = 1 - (effective_gp_pct / 100)
        menu_df["รายรับหลังหัก GP"] = menu_df["ราคา Delivery"] * gp_factor
        menu_df["กำไรหน้าร้าน/แก้ว"] = menu_df["ราคาหน้าร้าน"] - menu_df["ต้นทุนแปรผัน"]
        menu_df["กำไร Delivery/แก้ว"] = menu_df["รายรับหลังหัก GP"] - menu_df["ต้นทุนแปรผัน"]
        display_df = menu_df[
            ["หมวดหมู่", "เมนู", "ขนาดแก้ว", "ราคาหน้าร้าน", "ราคา Delivery", "ต้นทุนแปรผัน", "กำไรหน้าร้าน/แก้ว",
             "กำไร Delivery/แก้ว"]].copy()
        st.dataframe(display_df, use_container_width=True, hide_index=True)

# ------------------------------------------
# TAB 3: ค่าใช้จ่าย & กำไรสุทธิ
# ------------------------------------------
elif app_mode == t["mode_3"]:
    st.markdown(f"<div class='main-title'>{t['exp_title']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-title'>{t['exp_sub']}</div>", unsafe_allow_html=True)

    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        st.subheader(t["add_exp_title"])
        exp_date = st.date_input(t["exp_date"], datetime.date.today(), key="exp_date_input")
        exp_name = st.text_input(t["exp_name"], placeholder="e.g. Monthly Rent")
        exp_cat = st.selectbox(t["exp_cat_lbl"], ["Rent", "Utilities", "Staff Salaries", "Marketing", "Miscellaneous"],
                               key="exp_cat_input")
        exp_amount = st.number_input(t["exp_amt"], min_value=0.0, value=1000.0, step=100.0, key="exp_amt_input")

        if st.button(t["btn_save_exp"], type="primary", use_container_width=True):
            if exp_name.strip():
                new_exp = pd.DataFrame([{
                    "วันที่": str(exp_date), "รายการค่าใช้จ่าย": exp_name, "หมวดหมู่": exp_cat,
                    "จำนวนเงิน (บาท)": exp_amount
                }])
                st.session_state.expenses_db = pd.concat([st.session_state.expenses_db, new_exp], ignore_index=True)
                save_expenses()
                st.success(t["exp_success"])
                st.rerun()
            else:
                st.warning(t["exp_warn"])

    with col_ex2:
        st.subheader(t["exp_history"])
        df_exp = st.session_state.expenses_db
        if not df_exp.empty:
            st.dataframe(df_exp, use_container_width=True, hide_index=True)
            total_exp = df_exp["จำนวนเงิน (บาท)"].sum()
            st.metric(t["total_exp"], f"{total_exp:,.2f} THB")

            exp_data_bytes, exp_ext = convert_df_to_excel(df_exp)
            st.download_button(
                label=f"{t['dl_exp']} ({exp_ext.upper()})",
                data=exp_data_bytes,
                file_name=f"expenses_report.{exp_ext}",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if exp_ext == "xlsx" else "text/csv"
            )
        else:
            st.info(t["no_exp"])

    st.markdown("---")
    st.subheader(t["net_sum_title"])
    total_sales_all = st.session_state.daily_sales_db[
        "ยอดขายรวม"].sum() if not st.session_state.daily_sales_db.empty else 0.0
    total_cogs_all = st.session_state.daily_sales_db[
        "ต้นทุนรวม"].sum() if not st.session_state.daily_sales_db.empty else 0.0
    gross_profit_all = st.session_state.daily_sales_db[
        "กำไรขั้นต้น"].sum() if not st.session_state.daily_sales_db.empty else 0.0
    total_expenses = st.session_state.expenses_db[
        "จำนวนเงิน (บาท)"].sum() if not st.session_state.expenses_db.empty else 0.0
    net_profit_all = gross_profit_all - total_expenses

    np1, np2, np3 = st.columns(3)
    np1.metric(t["total_sales"], f"{total_sales_all:,.2f} ฿")
    np2.metric(t["total_gp_sum"], f"{gross_profit_all:,.2f} ฿")
    np3.metric(t["net_profit"], f"{net_profit_all:,.2f} ฿", delta=f"{net_profit_all:,.2f} ฿")

# ------------------------------------------
# TAB 4: รายงานยอดขาย & กราฟ
# ------------------------------------------
elif app_mode == t["mode_4"]:
    st.markdown(f"<div class='main-title'>{t['rep_title']}</div>", unsafe_allow_html=True)
    df_sales = st.session_state.daily_sales_db.copy()

    if not df_sales.empty:
        tot_qty = df_sales["จำนวน (แก้ว)"].sum()
        tot_rev = df_sales["ยอดขายรวม"].sum()
        tot_profit = df_sales["กำไรขั้นต้น"].sum()

        s1, s2, s3 = st.columns(3)
        s1.metric(t["tot_qty_lbl"], f"{tot_qty:,} Cups")
        s2.metric(t["tot_rev_lbl"], f"{tot_rev:,.2f} THB")
        s3.metric(t["total_gp_sum"], f"{tot_profit:,.2f} THB")

        st.markdown("---")
        st.subheader(t["chart_daily"])
        daily_trend = df_sales.groupby("วันที่")[["ยอดขายรวม", "กำไรขั้นต้น"]].sum().reset_index()
        daily_trend["วันที่"] = pd.to_datetime(daily_trend["วันที่"])
        daily_trend = daily_trend.sort_values("วันที่")
        st.line_chart(daily_trend.set_index("วันที่"))

        st.markdown("---")
        st.subheader(t["chart_menu"])
        menu_trend = df_sales.groupby("เมนู")["จำนวน (แก้ว)"].sum().reset_index()
        if not menu_trend.empty:
            st.bar_chart(menu_trend.set_index("เมนู"))

        st.markdown("---")
        st.subheader(t["history_sales"])
        st.dataframe(df_sales, use_container_width=True, hide_index=True)

        sales_data_bytes, sales_ext = convert_df_to_excel(df_sales)
        st.download_button(
            label=f"{t['dl_sales']} ({sales_ext.upper()})",
            data=sales_data_bytes,
            file_name=f"sales_report.{sales_ext}",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if sales_ext == "xlsx" else "text/csv"
        )
    else:
        st.info(t["no_sales"])

# ------------------------------------------
# TAB 5: จุดคุ้มทุน & โปรโมชั่น
# ------------------------------------------
elif app_mode == t["mode_5"]:
    st.markdown(f"<div class='main-title'>{t['be_title']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-title'>{t['be_sub']}</div>", unsafe_allow_html=True)

    total_fixed_cost = st.session_state.expenses_db[
        "จำนวนเงิน (บาท)"].sum() if not st.session_state.expenses_db.empty else 0.0

    col_be1, col_be2 = st.columns(2)
    with col_be1:
        st.metric(t["fixed_cost"], f"{total_fixed_cost:,.2f} THB")

    menu_df_calc = get_flattened_menu_df()
    if not menu_df_calc.empty:
        avg_price_est = menu_df_calc["ราคาหน้าร้าน"].mean()
        avg_cost_est = menu_df_calc["ต้นทุนแปรผัน"].mean()
        avg_margin = avg_price_est - avg_cost_est

        with col_be2:
            st.metric(t["contrib_margin"], f"{avg_margin:,.2f} THB/cup")

        st.markdown("---")
        if avg_margin > 0 and total_fixed_cost > 0:
            breakeven_cups = total_fixed_cost / avg_margin
            st.success(f"{t['be_target']} **{int(breakeven_cups) + 1:,}** {t['be_cups']}")

            days_target = st.slider(t["target_days"], min_value=1, max_value=30, value=30)
            cups_per_day = (breakeven_cups / days_target)
            st.info(f"{t['be_per_day']} **{cups_per_day:.1f} cups/day**")
        else:
            st.warning(t["be_warn"])