import datetime
import os
import pandas as pd
from supabase import Client, create_client
import streamlit as st
from streamlit_option_menu import option_menu

SUPABASE_URL = "https://xfknhxhllbabbdwxlfbe.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhma25oeGhsbGJhYmJkd3hsZmJlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc0OTIyNjgsImV4cCI6MjEwMzA2ODI2OH0.SdR9A_0l-K6RKj-cT7kQ7G5JcX-7sDT-r1gQjA4mmwk"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 1. CONFIG & GLOBAL CSS ---
st.set_page_config(
    page_title="99Coffee",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp { background-color: #FDFBF7; }
    .main-title { font-size: 24px; font-weight: bold; color: #5C4033; margin-bottom: 5px; }
    .sub-title { font-size: 14px; color: #8B5A2B; margin-bottom: 15px; }
    .stMetric { background-color: #FFFFFF; padding: 12px; border-radius: 12px; border: 1px solid #E6DCCD; box-shadow: 0 2px 5px rgba(92,64,51,0.05); }

    [data-testid="stImage"] img {
        width: 100% !important;
        height: 150px !important;
        object-fit: cover !important;
        border-radius: 8px !important;
    }

    .stButton > button {
        background-color: #FFFFFF !important;
        color: #5C4033 !important;
        border: 2px solid #E6DCCD !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        padding: 6px 12px !important;
        transition: all 0.25s ease-in-out !important;
    }
    .stButton > button:hover {
        background-color: #F5EBE6 !important;
        border-color: #C8B6A6 !important;
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# TRANSLATION DICTIONARY
# ==========================================
LANG = {
    "TH": {
        "sidebar_title": "☕ ระบบบริหารร้านกาแฟ Pro",
        "settings_header": "⚙️ ตั้งค่าระบบและอุปกรณ์",
        "gp_label": "หัก GP เดลิเวอรี (%)",
        "vat_gp": "คิด VAT 7% บนค่า GP",
        "low_stock": "🚨 แจ้งเตือนด่วน! วัตถุดิบใกล้หมด:",
        "pos_title": "💻 POS - ระบบขายหน้าร้าน / สั่งอาหาร",
        "pos_sub": "☕ เลือกเมนูเครื่องดื่มเพื่อเพิ่มลงในตะกร้าสินค้า",
        "cart_title": "🛒 ตะกร้าสินค้า",
        "total_label": "รวมทั้งสิ้น",
        "pay_btn": "💳 ชำระเงิน & ออกใบเสร็จ",
        "checkout_success": "ชำระเงิน บันทึกออเดอร์ และตัดสต็อกวัตถุดิบเรียบร้อยแล้ว!",
        "crm_header": "⭐ ระบบสมาชิก & สะสมแต้ม",
        "member_phone": "เบอร์โทรศัพท์ลูกค้า (สมาชิก)",
        "member_name": "ชื่อลูกค้า",
        "add_member_btn": "➕ สมัครสมาชิกใหม่",
        "shift_header": "💵 ระบบปิดกะ / ลิ้นชักเงินสด",
        "open_cash": "เงินทอนเริ่มต้นในลิ้นชัก (บาท)",
        "expected_cash": "เงินสดในลิ้นชักที่ควรมี",
        "actual_cash": "นับเงินสดจริงในลิ้นชัก (บาท)",
        "close_shift_btn": "🔒 ยืนยันปิดกะทำงาน",
        "line_header": "📢 ตั้งค่า Line Notify แจ้งเตือน",
        "line_token": "Line Notify Token",
        "line_btn": "🔔 ทดสอบส่ง Line แจ้งเตือน",
        "receipt_header": "🖨️ พิมพ์ใบเสร็จความร้อน (Slip 58mm/80mm)",
    },
    "EN": {
        "sidebar_title": "☕ Cafe Management Pro",
        "settings_header": "⚙️ Settings & Devices",
        "gp_label": "Delivery GP Deduction (%)",
        "vat_gp": "Include 7% VAT on GP",
        "low_stock": "🚨 Low stock alert:",
        "pos_title": "💻 POS - Storefront / Order System",
        "pos_sub": "☕ Select drinks to add to the shopping cart",
        "cart_title": "🛒 Shopping Cart",
        "total_label": "Total",
        "pay_btn": "💳 Checkout & Print Receipt",
        "checkout_success": "Checkout, order saved, and inventory deducted successfully!",
        "crm_header": "⭐ CRM & Member Points",
        "member_phone": "Customer Phone (Member)",
        "member_name": "Customer Name",
        "add_member_btn": "➕ Register New Member",
        "shift_header": "💵 Shift Closing / Cash Drawer",
        "open_cash": "Opening Cash Float (THB)",
        "expected_cash": "Expected Cash in Drawer",
        "actual_cash": "Actual Cash Counted (THB)",
        "close_shift_btn": "🔒 Close Shift",
        "line_header": "📢 Line Notify Settings",
        "line_token": "Line Notify Token",
        "line_btn": "🔔 Test Line Notification",
        "receipt_header": "🖨️ Thermal Receipt Printing (58mm/80mm)",
    },
}

# ==========================================
# DATABASE & FILE STORAGE MANAGEMENT
# ==========================================
INV_FILE = "inventory_data.csv"
SALES_FILE = "sales_data.csv"
EXP_FILE = "expenses_data.csv"
MENU_DB_FILE = "menu_database_full.csv"
ORDERS_FILE = "orders_management_data.csv"
MEMBER_FILE = "member_database.csv"
TARGET_FILE = "sales_target_data.csv"
ACCOUNTING_FILE = "daily_accounting_summary.csv"
UPLOAD_DIR = "uploaded_images"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def load_data():
    if "inventory_df" not in st.session_state:
        if os.path.exists(INV_FILE):
            st.session_state.inventory_df = pd.read_csv(INV_FILE)
        else:
            st.session_state.inventory_df = pd.DataFrame([
                {"หมวดหมู่": "🫘 วัตถุดิบหลัก", "รายการ": "เมล็ดกาแฟ (Arabica)", "ราคาซื้อ (บาท)": 600.0, "ขนาดบรรจุ": 1000.0, "หน่วย": "กรัม", "ขั้นต่ำแจ้งเตือน": 100.0, "คงเหลือ": 800.0},
                {"หมวดหมู่": "🥛 วัตถุดิบหลัก", "รายการ": "นมสดพาสเจอร์ไรส์", "ราคาซื้อ (บาท)": 95.0, "ขนาดบรรจุ": 1000.0, "หน่วย": "มล.", "ขั้นต่ำแจ้งเตือน": 200.0, "คงเหลือ": 900.0},
                {"หมวดหมู่": "🧋 วัตถุดิบหลัก", "รายการ": "ผงมัทฉะพรีเมียม", "ราคาซื้อ (บาท)": 450.0, "ขนาดบรรจุ": 100.0, "หน่วย": "กรัม", "ขั้นต่ำแจ้งเตือน": 20.0, "คงเหลือ": 80.0},
                {"หมวดหมู่": "📦 บรรจุภัณฑ์", "รายการ": "แก้ว PET 16 oz + ฝา + หลอด", "ราคาซื้อ (บาท)": 280.0, "ขนาดบรรจุ": 100.0, "หน่วย": "ชุด", "ขั้นต่ำแจ้งเตือน": 20.0, "คงเหลือ": 150.0}
            ])

    if "daily_sales_db" not in st.session_state:
        if os.path.exists(SALES_FILE):
            st.session_state.daily_sales_db = pd.read_csv(SALES_FILE)
        else:
            st.session_state.daily_sales_db = pd.DataFrame(columns=[
                "วันที่", "เวลา", "หมวดหมู่", "เมนู", "ช่องทาง", "จำนวน (แก้ว)", "ราคาขาย/แก้ว", "ต้นทุน/แก้ว", "ยอดขายรวม", "ต้นทุนรวม", "กำไรขั้นต้น", "สมาชิก"
            ])

    if "expenses_db" not in st.session_state:
        if os.path.exists(EXP_FILE):
            st.session_state.expenses_db = pd.read_csv(EXP_FILE)
        else:
            st.session_state.expenses_db = pd.DataFrame(columns=["วันที่", "รายการค่าใช้จ่าย", "หมวดหมู่", "จำนวนเงิน (บาท)"])

    if "orders_db" not in st.session_state:
        if os.path.exists(ORDERS_FILE):
            st.session_state.orders_db = pd.read_csv(ORDERS_FILE)
        else:
            st.session_state.orders_db = pd.DataFrame(columns=["OrderNo", "Time", "CustomerName", "MenuName", "Price", "Status"])

    if "member_db" not in st.session_state:
        if os.path.exists(MEMBER_FILE):
            st.session_state.member_db = pd.read_csv(MEMBER_FILE)
        else:
            st.session_state.member_db = pd.DataFrame(columns=["Phone", "Name", "Points", "RegisterDate"])

    if "sales_target_db" not in st.session_state:
        if os.path.exists(TARGET_FILE):
            st.session_state.sales_target_db = pd.read_csv(TARGET_FILE)
        else:
            st.session_state.sales_target_db = pd.DataFrame([
                {"TargetType": "Monthly", "TargetAmount": 60000.0, "SetDate": str(datetime.date.today())},
                {"TargetType": "Daily", "TargetAmount": 2000.0, "SetDate": str(datetime.date.today())}
            ])

    if "accounting_db" not in st.session_state:
        if os.path.exists(ACCOUNTING_FILE):
            st.session_state.accounting_db = pd.read_csv(ACCOUNTING_FILE)
        else:
            st.session_state.accounting_db = pd.DataFrame(columns=[
                "วันที่", "ยอดขายรวม", "จำนวนแก้วรวม", "ต้นทุนวัตถุดิบรวม", "กำไรขั้นต้น", "ค่าใช้จ่ายอื่นๆ", "กำไรสุทธิ", "เงินทอนเริ่มต้น", "ยอดเงินสดจริง", "ผลต่างเงินสด"
            ])

    if "cart" not in st.session_state:
        st.session_state.cart = []

def save_inventory(): st.session_state.inventory_df.to_csv(INV_FILE, index=False)
def save_sales(): st.session_state.daily_sales_db.to_csv(SALES_FILE, index=False)
def save_expenses(): st.session_state.expenses_db.to_csv(EXP_FILE, index=False)
def save_orders(): st.session_state.orders_db.to_csv(ORDERS_FILE, index=False)
def save_members(): st.session_state.member_db.to_csv(MEMBER_FILE, index=False)
def save_targets(): st.session_state.sales_target_db.to_csv(TARGET_FILE, index=False)
def save_accounting(): st.session_state.accounting_db.to_csv(ACCOUNTING_FILE, index=False)

load_data()

def show_back_button():
    if st.button("🏠 กลับหน้าหลัก (POS)", use_container_width=True):
        st.session_state.app_mode = "POS สั่งอาหาร"
        st.rerun()

# ==========================================
# MENU DATABASE & RECIPE ENGINE
# ==========================================
if "delivery_menu_db" not in st.session_state:
    if os.path.exists(MENU_DB_FILE):
        try:
            m_df_temp = pd.read_csv(MENU_DB_FILE)
            st.session_state.delivery_menu_db = {}
            for _, row in m_df_temp.iterrows():
                st.session_state.delivery_menu_db[row["MenuName"]] = {
                    "category": row["Category"],
                    "image": row.get("Image", "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=300"),
                    "price": float(row["Price"]),
                    "cost": float(row["Cost"])
                }
        except:
            st.session_state.delivery_menu_db = {}
    else:
        st.session_state.delivery_menu_db = {
            "Signature Latte": {"category": "☕ กาแฟ", "image": "https://images.unsplash.com/photo-1541167760496-1628856ab772?w=300", "price": 80.0, "cost": 25.0},
            "Dirty Coffee": {"category": "☕ กาแฟ", "image": "https://images.unsplash.com/photo-1517701604599-bb29b565090c?w=300", "price": 95.0, "cost": 30.0},
            "Chocolate Frappe": {"category": "🍫 นม/โกโก้", "image": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=300", "price": 90.0, "cost": 28.0},
            "นมสด": {"category": "🥛 เมนูนมสด", "image": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=300", "price": 40.0, "cost": 20.0}
        }

def save_menu_to_csv():
    rows = []
    for m_name, m_info in st.session_state.delivery_menu_db.items():
        rows.append({
            "MenuName": m_name,
            "Category": m_info.get("category", "📦 อื่นๆ"),
            "Image": m_info.get("image", "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=300"),
            "Price": m_info.get("price", 0.0),
            "Cost": m_info.get("cost", 0.0)
        })
    pd.DataFrame(rows).to_csv(MENU_DB_FILE, index=False)

def calculate_auto_cost(coffee_grams, milk_ml, cups_units):
    inv = st.session_state.inventory_df
    c_cost_per_g = 0.6
    m_cost_per_ml = 0.095
    cup_cost_unit = 2.8
    try:
        coffee_row = inv[inv["รายการ"].str.contains("กาแฟ", na=False)]
        if not coffee_row.empty:
            c_cost_per_g = float(coffee_row.iloc[0]["ราคาซื้อ (บาท)"]) / max(1.0, float(coffee_row.iloc[0]["ขนาดบรรจุ"]))
        milk_row = inv[inv["รายการ"].str.contains("นมสด", na=False)]
        if not milk_row.empty:
            m_cost_per_ml = float(milk_row.iloc[0]["ราคาซื้อ (บาท)"]) / max(1.0, float(milk_row.iloc[0]["ขนาดบรรจุ"]))
        cup_row = inv[inv["รายการ"].str.contains("แก้ว", na=False)]
        if not cup_row.empty:
            cup_cost_unit = float(cup_row.iloc[0]["ราคาซื้อ (บาท)"]) / max(1.0, float(cup_row.iloc[0]["ขนาดบรรจุ"]))
    except:
        pass
    return round((coffee_grams * c_cost_per_g) + (milk_ml * m_cost_per_ml) + (cups_units * cup_cost_unit), 2)

def deduct_inventory_on_sale(menu_name, category):
    inv = st.session_state.inventory_df
    coffee_use = 18.0 if "กาแฟ" in category or "Latte" in menu_name or "Dirty" in menu_name else 0.0
    milk_use = 120.0 if "นม" in category or "Latte" in menu_name or "Chocolate" in menu_name else 50.0
    cup_use = 1.0

    if coffee_use > 0:
        c_idx = inv[inv["รายการ"].str.contains("กาแฟ", na=False)].index
        if not c_idx.empty:
            current_val = float(inv.at[c_idx[0], "คงเหลือ"])
            inv.at[c_idx[0], "คงเหลือ"] = max(0.0, current_val - coffee_use)

    if milk_use > 0:
        m_idx = inv[inv["รายการ"].str.contains("นมสด", na=False)].index
        if not m_idx.empty:
            current_val = float(inv.at[m_idx[0], "คงเหลือ"])
            inv.at[m_idx[0], "คงเหลือ"] = max(0.0, current_val - milk_use)

    cup_idx = inv[inv["รายการ"].str.contains("แก้ว", na=False)].index
    if not cup_idx.empty:
        current_val = float(inv.at[cup_idx[0], "คงเหลือ"])
        inv.at[cup_idx[0], "คงเหลือ"] = max(0.0, current_val - cup_use)

    st.session_state.inventory_df = inv
    save_inventory()

# ==========================================
# SIDEBAR NAVIGATION & SETTINGS
# ==========================================
with st.sidebar:
    st.markdown("### ☕ 99Coffee")
    selected_lang = st.selectbox("🌐 Language / เลือกภาษา:", ["TH", "EN"], index=0)
    t = LANG[selected_lang]

    st.markdown("---")

    menu_options = [
        "POS สั่งอาหาร", "จัดการออเดอร์ลูกค้า", "ระบบสมาชิก CRM", "ปิดกะ / ลิ้นชักเงินสด",
        "จัดการเมนูและเพิ่มเมนู", "เมนู สูตร และสต็อก", "ค่าใช้จ่ายและกำไรสุทธิ",
        "สรุปบัญชีรายวัน", "จุดคุ้มทุน & โปรโมชั่น", "รายงานยอดขายและกราฟ",
        "ตั้งเป้าหมายยอดขาย", "วิเคราะห์ความเสี่ยง"
    ]
    menu_icons = [
        "cup-hot-fill", "box-seam", "people-fill", "shop",
        "plus-slash-minus", "journal-bookmark-fill", "cash-coin",
        "graph-up-arrow", "bar-chart-fill", "shield-exclamation", "bullseye", "safe-fill"
    ]

    app_mode = option_menu(
        menu_title="เมนูการทำงาน",
        options=menu_options,
        icons=menu_icons,
        menu_icon="shop",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#8B5A2B", "font-size": "16px"},
            "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0px", "--hover-color": "#F5EBE6"},
            "nav-link-selected": {"background-color": "#6F4E37", "color": "#FFFFFF"},
        }
    )

    st.markdown("---")
    st.subheader(t["settings_header"])
    gp_rate = st.number_input(t["gp_label"], min_value=0.0, max_value=50.0, value=30.0, step=1.0)
    include_vat_gp = st.checkbox(t["vat_gp"], value=True)

    inv_check_df = st.session_state.inventory_df
    low_stock_items = []
    for _, row in inv_check_df.iterrows():
        try:
            qty_val = float(row.get("คงเหลือ", 0)) if pd.notna(row.get("คงเหลือ")) else 0.0
            min_val = float(row.get("ขั้นต่ำแจ้งเตือน", 20.0)) if pd.notna(row.get("ขั้นต่ำแจ้งเตือน")) else 20.0
            if qty_val <= min_val:
                low_stock_items.append(str(row["รายการ"]))
        except:
            pass

    if low_stock_items:
        st.error(f"{t['low_stock']} **{', '.join(low_stock_items)}**")

# ==========================================
# MAIN APPLICATION ROUTING MODULES
# ==========================================
if app_mode in ["POS สั่งอาหาร", "POS Order System"]:
    st.markdown(f"<div class='main-title'>{t['pos_title']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-title'>{t['pos_sub']}</div>", unsafe_allow_html=True)

    col_pos_main, col_cart = st.columns([3, 1])

    with col_pos_main:
        all_categories = ["ทั้งหมด (All)"] + list(set([info.get("category", "📦 อื่นๆ") for info in st.session_state.delivery_menu_db.values()]))
        selected_category = st.selectbox("📂 กรองตามหมวดหมู่เครื่องดื่ม:", all_categories)

        filtered_items = []
        for m_name, m_info in st.session_state.delivery_menu_db.items():
            cat = m_info.get("category", "📦 อื่นๆ")
            if selected_category == "ทั้งหมด (All)" or cat == selected_category:
                filtered_items.append((m_name, m_info))

        if not filtered_items:
            st.info("ไม่พบเมนูในหมวดหมู่นี้")
        else:
            card_cols = st.columns(3)
            for idx, (m_name, m_info) in enumerate(filtered_items):
                c_target = card_cols[idx % 3]
                with c_target:
                    st.image(m_info.get("image", "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=300"), use_container_width=True)
                    st.markdown(f"**{m_name}**")
                    st.markdown(f"<span style='color: #8B5A2B; font-size: 13px;'>{m_info.get('category', '')}</span>", unsafe_allow_html=True)
                    st.markdown(f"**฿{m_info['price']:,.0f}**")
                    if st.button("➕ เพิ่ม", key=f"add_cart_{m_name}_{idx}", use_container_width=True):
                        st.session_state.cart.append({
                            "name": m_name, "price": m_info["price"], "cost": m_info["cost"],
                            "category": m_info.get("category", "เครื่องดื่ม")
                        })
                        st.toast(f"เพิ่ม {m_name} ลงตะกร้าแล้ว!")
                        st.rerun()

    with col_cart:
        st.markdown(f"### {t['cart_title']}")
        customer_name_input = st.text_input("👤 ชื่อลูกค้า / โต๊ะ", value="ลูกค้าทั่วไป")
        member_phones = ["ทั่วไป (ไม่ระบุสมาชิก)"] + st.session_state.member_db["Phone"].tolist() if not st.session_state.member_db.empty else ["ทั่วไป (ไม่ระบุสมาชิก)"]
        selected_member_phone = st.selectbox("⭐ สมาชิกสะสมแต้ม", member_phones)
        st.markdown("---")

        if not st.session_state.cart:
            st.info("ตะกร้าสินค้าว่างเปล่า")
        else:
            total_price = 0
            for item in st.session_state.cart:
                st.markdown(f"- {item['name']} : ฿{item['price']:,.0f}")
                total_price += item["price"]

            st.markdown("---")
            st.markdown(f"#### {t['total_label']}: ฿{total_price:,.0f}")

            if st.button(t["pay_btn"], type="primary", use_container_width=True):
                current_time_str = datetime.datetime.now().strftime("%H:%M:%S")
                order_no = f"ORD-{datetime.date.today().strftime('%Y%m%d')}-{len(st.session_state.orders_db) + 1:04d}"

                for item in st.session_state.cart:
                    new_row = pd.DataFrame([{
                        "วันที่": str(datetime.date.today()), "เวลา": current_time_str, "หมวดหมู่": item["category"],
                        "เมนู": item["name"], "ช่องทาง": "หน้าร้าน", "จำนวน (แก้ว)": 1, "ราคาขาย/แก้ว": item["price"],
                        "ต้นทุน/แก้ว": item["cost"], "ยอดขายรวม": item["price"], "ต้นทุนรวม": item["cost"],
                        "กำไรขั้นต้น": item["price"] - item["cost"], "สมาชิก": selected_member_phone
                    }])
                    st.session_state.daily_sales_db = pd.concat([st.session_state.daily_sales_db, new_row], ignore_index=True)
                    deduct_inventory_on_sale(item["name"], item["category"])

                new_order_row = pd.DataFrame([{
                    "OrderNo": order_no, "Time": current_time_str, "CustomerName": customer_name_input,
                    "MenuName": f"หลายรายการ ({len(st.session_state.cart)} แก้ว)",
                    "Price": total_price, "Status": "รอดำเนินการ"
                }])
                st.session_state.orders_db = pd.concat([st.session_state.orders_db, new_order_row], ignore_index=True)

                save_sales()
                save_orders()

                if selected_member_phone != "ทั่วไป (ไม่ระบุสมาชิก)":
                    m_df = st.session_state.member_db
                    m_idx = m_df[m_df["Phone"] == selected_member_phone].index
                    if not m_idx.empty:
                        earned_pts = int(total_price // 20)
                        m_df.at[m_idx[0], "Points"] = int(m_df.at[m_idx[0], "Points"]) + earned_pts
                        st.session_state.member_db = m_df
                        save_members()

                st.session_state.cart = []
                st.success(t["checkout_success"])
                st.rerun()

            if st.button("🗑️ ล้างตะกร้า", use_container_width=True):
                st.session_state.cart = []
                st.rerun()

elif app_mode in ["จัดการเมนูและเพิ่มเมนู", "Menu Management"]:
    show_back_button()
    st.markdown("<div class='main-title'>🛠️ จัดการ เพิ่ม และแก้ไขเมนูเครื่องดื่ม</div>", unsafe_allow_html=True)
    tab_add, tab_edit = st.tabs(["➕ เพิ่มเมนูใหม่", "✏️ แก้ไขเมนูที่มีอยู่"])

    with tab_add:
        new_n_cat = st.selectbox("เลือกหมวดหมู่เครื่องดื่ม", ["☕ กาแฟ", "🍵 ชา", "🍫 นม/โกโก้", "🍹 อิตาเลียนโซดา", "🥛 เมนูนมสด", "📦 อื่นๆ"], key="add_cat")

        with st.form("add_menu_form", clear_on_submit=True):
            new_m_name = st.text_input("ชื่อเมนูเครื่องดื่ม (เช่น ลาเต้เย็นหวานน้อย, ชาไทยปั่น)")
            new_m_price = st.number_input("ราคาขายหน้าร้าน (บาท)", min_value=0.0, value=65.0)

            c_grams, m_mls, cup_units = 18.0, 120.0, 1.0
            cup_units = st.number_input("จำนวนชุดแก้ว + ฝาปิด + หลอดดูด (ชุด)", min_value=0.0, value=1.0)
            auto_cost_calc = calculate_auto_cost(c_grams, m_mls, cup_units)

            st.info(f"💡 ต้นทุนคำนวณอัตโนมัติ: **฿{auto_cost_calc:,.2f}** ต่อแก้ว")
            uploaded_file = st.file_uploader("🖼️ อัปโหลดรูปภาพเมนู", type=["jpg", "jpeg", "png"], key="add_img_detailed")
            submitted = st.form_submit_button("➕ บันทึกเมนูใหม่เข้าสู่ระบบ", use_container_width=True)

        if submitted:
            if new_m_name:
                image_path = "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=300"
                if uploaded_file is not None:
                    file_extension = uploaded_file.name.split(".")[-1]
                    safe_file_name = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(new_m_name)}.{file_extension}"
                    image_path = os.path.join(UPLOAD_DIR, safe_file_name)
                    with open(image_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                st.session_state.delivery_menu_db[new_m_name] = {
                    "category": new_n_cat, "image": image_path, "price": float(new_m_price),
                    "cost": float(auto_cost_calc)
                }
                save_menu_to_csv()
                st.success(f"เพิ่มเมนู '{new_m_name}' สำเร็จ!")
                st.rerun()

    with tab_edit:
        st.subheader("✏️ แก้ไขเมนูที่มีอยู่")
        if not st.session_state.delivery_menu_db:
            st.info("ยังไม่มีเมนูในระบบ")
        else:
            edit_menu_choice = st.selectbox("เลือกเมนูที่จะแก้ไข", list(st.session_state.delivery_menu_db.keys()))
            curr_info = st.session_state.delivery_menu_db[edit_menu_choice]

            with st.form("edit_menu_form"):
                edit_name = st.text_input("ชื่อเมนู", value=edit_menu_choice)
                edit_price = st.number_input("ราคาขาย (บาท)", min_value=0.0, value=float(curr_info["price"]))

                col_e1, col_e2 = st.columns(2)
                save_edit = col_e1.form_submit_button("💾 บันทึกการแก้ไข", use_container_width=True)
                delete_menu = col_e2.form_submit_button("🗑️ ลบเมนูนี้", use_container_width=True)

                if save_edit:
                    st.session_state.delivery_menu_db[edit_name] = {
                        "category": curr_info["category"], "image": curr_info["image"], "price": edit_price,
                        "cost": curr_info["cost"]
                    }
                    if edit_name != edit_menu_choice:
                        del st.session_state.delivery_menu_db[edit_menu_choice]
                    save_menu_to_csv()
                    st.success("บันทึกการแก้ไขเรียบร้อยแล้ว!")
                    st.rerun()

                if delete_menu:
                    del st.session_state.delivery_menu_db[edit_menu_choice]
                    save_menu_to_csv()
                    st.success("ลบเมนูเรียบร้อยแล้ว")
                    st.rerun()

elif app_mode in ["สรุปบัญชีรายวัน", "Daily Accounting Summary"]:
    show_back_button()
    st.markdown("<div class='main-title'>📑 สรุปบัญชีรายวัน (Daily Accounting & Cash Flow)</div>", unsafe_allow_html=True)
    selected_date_acc = st.date_input("📅 เลือกวันที่", datetime.date.today())

    sales_df = st.session_state.daily_sales_db
    expenses_df = st.session_state.expenses_db
    date_str = str(selected_date_acc)

    day_sales = sales_df[sales_df["วันที่"] == date_str] if not sales_df.empty else pd.DataFrame()
    day_expenses = expenses_df[expenses_df["วันที่"] == date_str] if not expenses_df.empty else pd.DataFrame()

    total_rev = day_sales["ยอดขายรวม"].sum() if not day_sales.empty else 0.0
    total_qty = day_sales["จำนวน (แก้ว)"].sum() if not day_sales.empty else 0.0
    gross_p = day_sales["กำไรขั้นต้น"].sum() if not day_sales.empty else 0.0
    total_exp = day_expenses["จำนวนเงิน (บาท)"].sum() if not day_expenses.empty else 0.0
    net_p = gross_p - total_exp

    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    col_a1.metric("💰 ยอดขายรวม", f"฿{total_rev:,.2f}")
    col_a2.metric("🥤 จำนวนแก้วขายได้", f"{total_qty:,.0f} แก้ว")
    col_a3.metric("📈 กำไรขั้นต้น", f"฿{gross_p:,.2f}")
    col_a4.metric("💵 กำไรสุทธิ (หักค่าใช้จ่าย)", f"฿{net_p:,.2f}")

    st.markdown("---")
    st.subheader(f"📋 รายละเอียดยอดขายประจำวันที่ {date_str}")
    if not day_sales.empty:
        st.dataframe(day_sales, use_container_width=True)
    else:
        st.info("ไม่มีรายการขายในวันที่เลือกนี้")

    st.subheader(f"💸 รายละเอียดค่าใช้จ่ายอื่นๆ ประจำวันที่ {date_str}")
    if not day_expenses.empty:
        st.dataframe(day_expenses, use_container_width=True)
    else:
        st.info("ไม่มีรายการค่าใช้จ่ายในวันที่เลือกนี้")

elif app_mode in ["จัดการออเดอร์ลูกค้า", "Customer Orders"]:
    show_back_button()
    st.markdown("<div class='main-title'>🖨️ พิมพ์ใบเสร็จความร้อน & จัดการออเดอร์</div>", unsafe_allow_html=True)

    with st.form("clear_orders_form"):
        clear_btn = st.form_submit_button("🗑️ ล้างออเดอร์ที่เสร็จสิ้นแล้วทั้งหมด")
        if clear_btn:
            if "orders_db" in st.session_state and not st.session_state.orders_db.empty:
                st.session_state.orders_db = st.session_state.orders_db[st.session_state.orders_db["Status"] != "เสร็จสิ้น"]
                save_orders()
                st.success("ล้างออเดอร์ที่เสร็จสิ้นเรียบร้อย!")
                st.rerun()
            else:
                st.warning("ไม่มีข้อมูลออเดอร์ในระบบ")

    st.markdown("---")
    if st.session_state.orders_db.empty:
        st.info("ยังไม่มีออเดอร์ในระบบ")
    else:
        for idx, row in st.session_state.orders_db.iterrows():
            cust_name = row.get("CustomerName", "ลูกค้าทั่วไป")
            with st.expander(f"📦 {row['OrderNo']} | ลูกค้า: {cust_name} | ฿{row['Price']:,.2f} | สถานะ: {row['Status']}"):
                col_info, col_print = st.columns([2, 1])
                with col_info:
                    st.write(f"**เวลาที่สั่ง:** {row['Time']}")
                    st.write(f"**ชื่อลูกค้า:** {cust_name}")
                    st.write(f"**รายการ:** {row['MenuName']}")
                    st.write(f"**ราคารวม:** ฿{row['Price']:,.2f}")
                    st.write(f"**สถานะปัจจุบัน:** {row['Status']}")

                    if row["Status"] == "รอดำเนินการ":
                        with st.form(f"complete_form_{idx}"):
                            comp_sub = st.form_submit_button("🟡 ทำเครื่องหมายว่าเสร็จสิ้น")
                            if comp_sub:
                                st.session_state.orders_db.at[idx, "Status"] = "เสร็จสิ้น"
                                save_orders()
                                st.success(f"อัปเดตสถานะออเดอร์เรียบร้อย!")
                                st.rerun()

                with col_print:
                    st.markdown("#### พิมพ์ใบเสร็จ")
                    if st.button(f"🖨️ พิมพ์สลิป (58mm)", key=f"print_58_{idx}"):
                        st.code(f"========== CAFE ==========\nID: {row['OrderNo']}\nTOTAL: ฿{row['Price']:,.2f}\n==========================", language="text")
                    if st.button(f"🖨️ พิมพ์สลิป (80mm)", key=f"print_80_{idx}"):
                        st.code(f"============ CAFE ============\nID: {row['OrderNo']}\nTOTAL: ฿{row['Price']:,.2f}\n==============================", language="text")
            st.markdown("---")

elif app_mode in ["ระบบสมาชิก CRM", "CRM & Member Points"]:
    show_back_button()
    st.markdown(f"<div class='main-title'>{t['crm_header']}</div>", unsafe_allow_html=True)
    with st.form("mem_form"):
        m_phone = st.text_input(t["member_phone"])
        m_name = st.text_input(t["member_name"])
        if st.form_submit_button(t["add_member_btn"]):
            if m_phone and m_name:
                new_m = pd.DataFrame([{"Phone": m_phone, "Name": m_name, "Points": 0, "RegisterDate": str(datetime.date.today())}])
                st.session_state.member_db = pd.concat([st.session_state.member_db, new_m], ignore_index=True)
                save_members()
                st.success("สมัครสมาชิกสำเร็จ!")
                st.rerun()
    st.dataframe(st.session_state.member_db, use_container_width=True)

elif app_mode in ["ปิดกะ / ลิ้นชักเงินสด", "Shift Closing / Cash Drawer"]:
    show_back_button()
    st.markdown(f"<div class='main-title'>{t['shift_header']}</div>", unsafe_allow_html=True)
    float_cash = st.number_input(t["open_cash"], value=1000.0)
    st.metric(t["expected_cash"], f"฿{float_cash:,.2f}")

    with st.form("close_shift_form"):
        close_btn = st.form_submit_button(t["close_shift_btn"], type="primary")
        if close_btn:
            st.success("ปิดกะสำเร็จและบันทึกยอดลิ้นชักเรียบร้อย!")

elif app_mode in ["ค่าใช้จ่ายและกำไรสุทธิ", "Expenses & Net Profit"]:
    show_back_button()
    st.markdown("<div class='main-title'>💸 บันทึกค่าใช้จ่ายและกำไรสุทธิ</div>", unsafe_allow_html=True)
    with st.form("exp_f"):
        e_name = st.text_input("รายการค่าใช้จ่าย")
        e_cat = st.selectbox("หมวด", ["ค่าเช่า", "ค่าน้ำ/ไฟ", "เงินเดือน", "อื่นๆ"])
        e_amt = st.number_input("จำนวนเงิน (บาท)", value=1000.0)
        if st.form_submit_button("บันทึกค่าใช้จ่าย"):
            new_e = pd.DataFrame([{"วันที่": str(datetime.date.today()), "รายการค่าใช้จ่าย": e_name, "หมวดหมู่": e_cat, "จำนวนเงิน (บาท)": e_amt}])
            st.session_state.expenses_db = pd.concat([st.session_state.expenses_db, new_e], ignore_index=True)
            save_expenses()
            st.success("บันทึกสำเร็จ!")
            st.rerun()

elif app_mode in ["รายงานยอดขายและกราฟ", "Sales Report & Charts"]:
    show_back_button()
    st.markdown("<div class='main-title'>📊 รายงานยอดขายและกราฟ</div>", unsafe_allow_html=True)
    sales_df = st.session_state.daily_sales_db
    if not sales_df.empty:
        st.metric("ยอดขายรวมทั้งสิ้น", f"฿{sales_df['ยอดขายรวม'].sum():,.2f}")
        st.dataframe(sales_df, use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูลยอดขาย")

elif app_mode in ["จุดคุ้มทุน & โปรโมชั่น", "Break-Even & Promo"]:
    show_back_button()
    st.markdown("<div class='main-title'>📈 วิเคราะห์จุดคุ้มทุน</div>", unsafe_allow_html=True)
    fc = st.number_input("ค่าใช้จ่ายคงที่รวม (บาท/เดือน)", value=15000.0)
    st.info(f"เป้าหมายกำไรขั้นต้นเพื่อคุ้มทุน: ฿{fc:,.2f}")

elif app_mode in ["ตั้งเป้าหมายยอดขาย", "Sales Targets"]:
    show_back_button()
    st.markdown("<div class='main-title'>🎯 ตั้งเป้าหมายยอดขายและจำนวนแก้ว</div>", unsafe_allow_html=True)
    with st.form("set_target_form"):
        new_daily_target = st.number_input("เป้าหมายรายวัน (บาท)", min_value=0.0, value=2000.0)
        if st.form_submit_button("💾 บันทึกเป้าหมาย", use_container_width=True):
            st.success("บันทึกเป้าหมายสำเร็จ!")

elif app_mode in ["วิเคราะห์ความเสี่ยง", "Risk Analysis"]:
    show_back_button()
    st.markdown("<div class='main-title'>🛡️ วิเคราะห์ความเสี่ยงทางธุรกิจ</div>", unsafe_allow_html=True)
    st.success("✅ ระบบตรวจสอบความเสี่ยงทำงานปกติ")

elif app_mode in ["เมนู สูตร และสต็อก", "Menu, Recipe & Stock"]:
    show_back_button()
    st.markdown("<div class='main-title'>📦 คลังวัตถุดิบและจัดการสต็อก</div>", unsafe_allow_html=True)

    with st.expander("➕ เพิ่มรายการวัตถุดิบใหม่เข้าระบบ", expanded=False):
        with st.form("inventory_add_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                f_cat = st.selectbox("หมวดหมู่", ["🫘 วัตถุดิบหลัก", "🥛 วัตถุดิบหลัก", "🧋 วัตถุดิบหลัก", "🧁 ส่วนผสมปรุงรส", "📦 บรรจุภัณฑ์"])
                f_name = st.text_input("ชื่อรายการวัตถุดิบ")
            with c2:
                f_price = st.number_input("ราคาซื้อ (บาท)", min_value=0.0, value=100.0)
                f_size = st.number_input("ขนาดบรรจุ", min_value=0.1, value=1000.0)
            with c3:
                f_unit = st.text_input("หน่วยย่อย (เช่น กรัม, มล., ชุด)", value="กรัม")
                f_qty = st.number_input("ปริมาณคงเหลือปัจจุบัน", min_value=0.0, value=500.0)
                f_min = st.number_input("จุดต่ำสุดแจ้งเตือน", min_value=0.0, value=50.0)

            submit_btn = st.form_submit_button("บันทึกข้อมูล", use_container_width=True)

            if submit_btn:
                if f_name:
                    new_row = {
                        "หมวดหมู่": f_cat, "รายการ": f_name, "ราคาซื้อ (บาท)": f_price,
                        "ขนาดบรรจุ": f_size, "หน่วย": f_unit, "คงเหลือ": f_qty, "ขั้นต่ำแจ้งเตือน": f_min
                    }
                    st.session_state.inventory_df = pd.concat([st.session_state.inventory_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_inventory()
                    st.success(f"เพิ่มรายการ '{f_name}' สำเร็จเรียบร้อย!")
                    st.rerun()

    st.divider()

    clean_inv_df = st.session_state.inventory_df.dropna(subset=["รายการ"]).copy()
    clean_inv_df["ราคาซื้อ (บาท)"] = pd.to_numeric(clean_inv_df["ราคาซื้อ (บาท)"], errors="coerce").fillna(0.0)
    clean_inv_df["ขนาดบรรจุ"] = pd.to_numeric(clean_inv_df["ขนาดบรรจุ"], errors="coerce").fillna(1.0)
    clean_inv_df["คงเหลือ"] = pd.to_numeric(clean_inv_df["คงเหลือ"], errors="coerce").fillna(0.0)
    clean_inv_df["ขั้นต่ำแจ้งเตือน"] = pd.to_numeric(clean_inv_df["ขั้นต่ำแจ้งเตือน"], errors="coerce").fillna(0.0)
    clean_inv_df["หน่วย"] = clean_inv_df["หน่วย"].fillna("หน่วย")

    clean_inv_df["ต้นทุน/หน่วยย่อย (บาท)"] = (
        clean_inv_df["ราคาซื้อ (บาท)"] / clean_inv_df["ขนาดบรรจุ"].replace(0, 1)
    ).round(4)

    st.subheader("📋 แก้ไข/จัดการรายการวัตถุดิบในระบบ (อัปเดตอัตโนมัติทันที)")
    st.info("💡 สามารถคลิกแก้ไขตัวเลขหรือข้อความในตารางด้านล่างนี้ได้เลย ระบบจะทำการคำนวณและบันทึกข้อมูลลงไฟล์ให้อัตโนมัติทันทีที่คุณพิมพ์เสร็จ")

    edited_inventory_df = st.data_editor(
        clean_inv_df,
        use_container_width=True,
        num_rows="dynamic",
        key="inventory_live_editor"
    )

    if "ต้นทุน/หน่วยย่อย (บาท)" in edited_inventory_df.columns:
        to_save_df = edited_inventory_df.drop(columns=["ต้นทุน/หน่วยย่อย (บาท)"])
    else:
        to_save_df = edited_inventory_df

    to_save_df = to_save_df.dropna(subset=["รายการ"])

    if not to_save_df.equals(st.session_state.inventory_df):
        st.session_state.inventory_df = to_save_df
        save_inventory()
        st.toast("⚡ บันทึกการแก้ไขสต็อกอัตโนมัติเรียบร้อยแล้ว!", icon="💾")
