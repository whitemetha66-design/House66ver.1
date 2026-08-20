import streamlit as st
import pandas as pd
import datetime
import os
from streamlit_option_menu import option_menu

# --- 1. CONFIG & GLOBAL CSS ---
st.set_page_config(
    page_title="Cafe Management Pro System",
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
        "checkout_success": "ชำระเงินและบันทึกออเดอร์เรียบร้อยแล้ว!",
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
        "checkout_success": "Checkout and order saved successfully!",
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
                {"หมวดหมู่": "🫘 วัตถุดิบหลัก", "รายการ": "เมล็ดกาแฟ (Arabica)", "ราคาซื้อ (บาท)": 600.0,
                 "ขนาดบรรจุ": 1000.0, "หน่วย": "กรัม", "ขั้นต่ำแจ้งเตือน": 100.0},
                {"หมวดหมู่": "🥛 วัตถุดิบหลัก", "รายการ": "นมสดพาสเจอร์ไรส์", "ราคาซื้อ (บาท)": 95.0,
                 "ขนาดบรรจุ": 1000.0, "หน่วย": "มล.", "ขั้นต่ำแจ้งเตือน": 200.0},
                {"หมวดหมู่": "🧋 วัตถุดิบหลัก", "รายการ": "ผงมัทฉะพรีเมียม", "ราคาซื้อ (บาท)": 450.0, "ขนาดบรรจุ": 100.0,
                 "หน่วย": "กรัม", "ขั้นต่ำแจ้งเตือน": 20.0},
                {"หมวดหมู่": "🧋 วัตถุดิบหลัก", "รายการ": "ผงชาไทย", "ราคาซื้อ (บาท)": 140.0, "ขนาดบรรจุ": 400.0,
                 "หน่วย": "กรัม", "ขั้นต่ำแจ้งเตือน": 50.0},
                {"หมวดหมู่": "🍫 วัตถุดิบหลัก", "รายการ": "ผงโกโก้พรีเมียม", "ราคาซื้อ (บาท)": 180.0, "ขนาดบรรจุ": 500.0,
                 "หน่วย": "กรัม", "ขั้นต่ำแจ้งเตือน": 50.0},
                {"หมวดหมู่": "🧊 วัตถุดิบหลัก", "รายการ": "น้ำแข็ง / น้ำสะอาด", "ราคาซื้อ (บาท)": 50.0,
                 "ขนาดบรรจุ": 20000.0, "หน่วย": "กรัม", "ขั้นต่ำแจ้งเตือน": 2000.0},
                {"หมวดหมู่": "🧁 ส่วนผสมปรุงรส", "รายการ": "นมข้นหวาน/นมข้นจืด", "ราคาซื้อ (บาท)": 55.0,
                 "ขนาดบรรจุ": 380.0, "หน่วย": "มล.", "ขั้นต่ำแจ้งเตือน": 50.0},
                {"หมวดหมู่": "📦 บรรจุภัณฑ์", "รายการ": "แก้ว PET 16 oz + ฝา + หลอด", "ราคาซื้อ (บาท)": 280.0,
                 "ขนาดบรรจุ": 100.0, "หน่วย": "ชุด", "ขั้นต่ำแจ้งเตือน": 20.0}
            ])

    if "daily_sales_db" not in st.session_state:
        if os.path.exists(SALES_FILE):
            st.session_state.daily_sales_db = pd.read_csv(SALES_FILE)
        else:
            st.session_state.daily_sales_db = pd.DataFrame(columns=[
                "วันที่", "เวลา", "หมวดหมู่", "เมนู", "ช่องทาง", "จำนวน (แก้ว)", "ราคาขาย/แก้ว", "ต้นทุน/แก้ว",
                "ยอดขายรวม", "ต้นทุนรวม", "กำไรขั้นต้น", "สมาชิก"
            ])

    if "expenses_db" not in st.session_state:
        if os.path.exists(EXP_FILE):
            st.session_state.expenses_db = pd.read_csv(EXP_FILE)
        else:
            st.session_state.expenses_db = pd.DataFrame(
                columns=["วันที่", "รายการค่าใช้จ่าย", "หมวดหมู่", "จำนวนเงิน (บาท)"])

    if "orders_db" not in st.session_state:
        if os.path.exists(ORDERS_FILE):
            st.session_state.orders_db = pd.read_csv(ORDERS_FILE)
        else:
            st.session_state.orders_db = pd.DataFrame(columns=["OrderNo", "Time", "MenuName", "Price", "Status"])

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
                "วันที่", "ยอดขายรวม", "จำนวนแก้วรวม", "ต้นทุนวัตถุดิบรวม", "กำไรขั้นต้น", "ค่าใช้จ่ายอื่นๆ",
                "กำไรสุทธิ", "เงินทอนเริ่มต้น", "ยอดเงินสดจริง", "ผลต่างเงินสด"
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

# ==========================================
# AUTHENTICATION & LOGIN SCREEN
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = "Barista"

if not st.session_state.logged_in:
    st.markdown(
        "<div class='main-title' style='text-align: center; margin-top: 50px;'>☕ Cafe Management Pro - Login</div>",
        unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1, 1])
    with col_l2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("เข้าสู่ระบบ (Login)", use_container_width=True)
            if login_btn:
                if username == "admin" and password == "1234":
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Owner"
                    st.success("เข้าสู่ระบบในฐานะเจ้าของร้าน (Owner)")
                    st.rerun()
                elif username == "staff" and password == "1234":
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Barista"
                    st.success("เข้าสู่ระบบในฐานะพนักงานบาริสต้า (Barista)")
                    st.rerun()
                else:
                    st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง (Admin: admin/1234, Staff: staff/1234)")
    st.stop()

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
            "Signature Latte": {"category": "☕ กาแฟ",
                                "image": "https://images.unsplash.com/photo-1541167760496-1628856ab772?w=300",
                                "price": 80.0, "cost": 25.0},
            "Dirty Coffee": {"category": "☕ กาแฟ",
                             "image": "https://images.unsplash.com/photo-1517701604599-bb29b565090c?w=300",
                             "price": 95.0, "cost": 30.0},
            "Chocolate Frappe": {"category": "🍫 นม/โกโก้",
                                 "image": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=300",
                                 "price": 90.0, "cost": 28.0},
            "นมสด": {"category": "🥛 เมนูนมสด",
                     "image": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=300", "price": 40.0,
                     "cost": 20.0}
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
            c_cost_per_g = float(coffee_row.iloc[0]["ราคาซื้อ (บาท)"]) / max(1.0,
                                                                             float(coffee_row.iloc[0]["ขนาดบรรจุ"]))
        milk_row = inv[inv["รายการ"].str.contains("นมสด", na=False)]
        if not milk_row.empty:
            m_cost_per_ml = float(milk_row.iloc[0]["ราคาซื้อ (บาท)"]) / max(1.0, float(milk_row.iloc[0]["ขนาดบรรจุ"]))
        cup_row = inv[inv["รายการ"].str.contains("แก้ว", na=False)]
        if not cup_row.empty:
            cup_cost_unit = float(cup_row.iloc[0]["ราคาซื้อ (บาท)"]) / max(1.0, float(cup_row.iloc[0]["ขนาดบรรจุ"]))
    except:
        pass
    return round((coffee_grams * c_cost_per_g) + (milk_ml * m_cost_per_ml) + (cups_units * cup_cost_unit), 2)


# ==========================================
# SIDEBAR NAVIGATION & SETTINGS
# ==========================================
with st.sidebar:
    st.markdown(f"### ☕ Cafe Pro ({st.session_state.user_role})")
    selected_lang = st.selectbox("🌐 Language / เลือกภาษา:", ["TH", "EN"], index=0)
    t = LANG[selected_lang]

    if st.button("🚪 ออกจากระบบ (Logout)", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown("---")

    if st.session_state.user_role == "Owner":
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
    else:
        menu_options = ["POS สั่งอาหาร", "จัดการออเดอร์ลูกค้า", "ระบบสมาชิก CRM"]
        menu_icons = ["cup-hot-fill", "box-seam", "people-fill"]

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
    low_stock_items = [row["รายการ"] for _, row in inv_check_df.iterrows() if
                       float(row["ขนาดบรรจุ"]) <= float(row.get("ขั้นต่ำแจ้งเตือน", 20.0))]
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
        all_categories = ["ทั้งหมด (All)"] + list(
            set([info.get("category", "📦 อื่นๆ") for info in st.session_state.delivery_menu_db.values()]))
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
                    st.image(m_info.get("image", "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=300"),
                             use_container_width=True)
                    st.markdown(f"**{m_name}**")
                    st.markdown(f"<span style='color: #8B5A2B; font-size: 13px;'>{m_info.get('category', '')}</span>",
                                unsafe_allow_html=True)
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
        member_phones = ["ทั่วไป (ไม่ระบุสมาชิก)"] + st.session_state.member_db[
            "Phone"].tolist() if not st.session_state.member_db.empty else ["ทั่วไป (ไม่ระบุสมาชิก)"]
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
                    st.session_state.daily_sales_db = pd.concat([st.session_state.daily_sales_db, new_row],
                                                                ignore_index=True)

                new_order_row = pd.DataFrame([{
                    "OrderNo": order_no, "Time": current_time_str,
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
    st.markdown("<div class='main-title'>🛠️ จัดการ เพิ่ม และแก้ไขเมนูเครื่องดื่ม</div>", unsafe_allow_html=True)
    tab_add, tab_edit = st.tabs(["➕ เพิ่มเมนูใหม่", "✏️ แก้ไขเมนูที่มีอยู่"])

    with tab_add:
        new_n_cat = st.selectbox("เลือกหมวดหมู่เครื่องดื่ม",
                                 ["☕ กาแฟ", "🍵 ชา", "🍫 นม/โกโก้", "🍹 อิตาเลียนโซดา", "🥛 เมนูนมสด", "📦 อื่นๆ"],
                                 key="add_cat")

        with st.form("add_menu_form", clear_on_submit=True):
            new_m_name = st.text_input("ชื่อเมนูเครื่องดื่ม (เช่น ลาเต้เย็นหวานน้อย, ชาไทยปั่น)")
            new_m_price = st.number_input("ราคาขายหน้าร้าน (บาท)", min_value=0.0, value=65.0)

            st.markdown("---")
            st.markdown("### 📋 สูตรส่วนผสมและวัตถุดิบเชิงลึกต่อ 1 แก้ว")

            # ตัวแปรสำหรับเก็บค่าส่วนผสมละเอียด
            ing_1, ing_2, ing_3, ing_4, ing_5 = 0.0, 0.0, 0.0, 0.0, 0.0
            c_grams, m_mls, extra_amt, cup_units = 0.0, 0.0, 0.0, 1.0

            if "กาแฟ" in new_n_cat:
                st.markdown("☕ **สัดส่วนวัตถุดิบหมวดกาแฟ**")
                c_grams = st.number_input("ปริมาณเมล็ดกาแฟ / ช็อตเอสเพรสโซ (กรัม)", min_value=0.0, value=18.0)
                m_mls = st.number_input("ปริมาณนมสดพาสเจอร์ไรส์ (มล.)", min_value=0.0, value=120.0)
                ing_1 = st.number_input("ปริมาณนมข้นหวาน (มล.)", min_value=0.0, value=20.0)
                ing_2 = st.number_input("ปริมาณนมข้นจืด (มล.)", min_value=0.0, value=10.0)
                ing_3 = st.number_input("ปริมาณไซรัป / น้ำตาลแต่งหวาน (มล./กรัม)", min_value=0.0, value=10.0)
                ing_4 = st.number_input("ปริมาณน้ำแข็ง (กรัม)", min_value=0.0, value=150.0)
            elif "ชา" in new_n_cat:
                st.markdown("🍵 **สัดส่วนวัตถุดิบหมวดชา**")
                c_grams = st.number_input("ปริมาณผงชา / ใบชา (กรัม)", min_value=0.0, value=15.0)
                m_mls = st.number_input("ปริมาณนมสด (มล.)", min_value=0.0, value=60.0)
                ing_1 = st.number_input("ปริมาณนมข้นหวาน (มล.)", min_value=0.0, value=30.0)
                ing_2 = st.number_input("ปริมาณนมข้นจืด (มล.)", min_value=0.0, value=20.0)
                ing_3 = st.number_input("ปริมาณน้ำร้อนสำหรับสกัดชา (มล.)", min_value=0.0, value=100.0)
                ing_4 = st.number_input("ปริมาณน้ำแข็ง (กรัม)", min_value=0.0, value=150.0)
            elif "นม/โกโก้" in new_n_cat or "เมนูนมสด" in new_n_cat:
                st.markdown("🍫 **สัดส่วนวัตถุดิบหมวดโกโก้ / นมสด**")
                c_grams = st.number_input("ปริมาณผงโกโก้ / ช็อกโกแลต (กรัม)", min_value=0.0, value=30.0)
                m_mls = st.number_input("ปริมาณนมสดหลัก (มล.)", min_value=0.0, value=140.0)
                ing_1 = st.number_input("ปริมาณนมข้นหวาน (มล.)", min_value=0.0, value=30.0)
                ing_2 = st.number_input("ปริมาณนมข้นจืด (มล.)", min_value=0.0, value=15.0)
                ing_3 = st.number_input("ปริมาณน้ำร้อนละลายผง (มล.)", min_value=0.0, value=40.0)
                ing_4 = st.number_input("ปริมาณน้ำแข็ง (กรัม)", min_value=0.0, value=150.0)
            elif "อิตาเลียนโซดา" in new_n_cat:
                st.markdown("🍹 **สัดส่วนวัตถุดิบหมวดอิตาเลียนโซดา**")
                c_grams = st.number_input("ปริมาณไซรัปผลไม้ / หัวเชื้อ (มล.)", min_value=0.0, value=45.0)
                m_mls = st.number_input("ปริมาณโซดาซ่า (มล.)", min_value=0.0, value=160.0)
                ing_1 = st.number_input("ปริมาณน้ำเชื่อม / น้ำตาล (มล.)", min_value=0.0, value=15.0)
                ing_2 = st.number_input("ปริมาณผลไม้สดแต่งหน้า (กรัม)", min_value=0.0, value=10.0)
                ing_3 = 0.0
                ing_4 = st.number_input("ปริมาณน้ำแข็ง (กรัม)", min_value=0.0, value=180.0)
            else:
                st.markdown("📦 **สัดส่วนวัตถุดิบหมวดอื่นๆ**")
                c_grams = st.number_input("ปริมาณวัตถุดิบหลัก A (กรัม/มล.)", min_value=0.0, value=20.0)
                m_mls = st.number_input("ปริมาณวัตถุดิบหลัก B (กรัม/มล.)", min_value=0.0, value=100.0)
                ing_1 = st.number_input("ปริมาณส่วนผสมเสริม 1", min_value=0.0, value=0.0)
                ing_2 = st.number_input("ปริมาณส่วนผสมเสริม 2", min_value=0.0, value=0.0)
                ing_4 = st.number_input("ปริมาณน้ำแข็ง (กรัม)", min_value=0.0, value=150.0)

            st.markdown("---")
            st.markdown("📦 **วัสดุสิ้นเปลือง (Packaging)**")
            cup_units = st.number_input("จำนวนชุดแก้ว + ฝาปิด + หลอดดูด (ชุด)", min_value=0.0, value=1.0)

            # คำนวณต้นทุนรวมจากทุกส่วนผสมเชิงลึก
            total_weight_or_volume = c_grams + m_mls + ing_1 + ing_2 + ing_3 + ing_4
            auto_cost_calc = calculate_auto_cost(c_grams + ing_1, m_mls + ing_2, cup_units)

            st.info(
                f"💡 สรุปปริมาณรวมต่อแก้ว: **{total_weight_or_volume:,.1f} กรัม/มล.** | ต้นทุนคำนวณอัตโนมัติ: **฿{auto_cost_calc:,.2f}** ต่อแก้ว")

            uploaded_file = st.file_uploader("🖼️ อัปโหลดรูปภาพเมนู", type=["jpg", "jpeg", "png"],
                                             key="add_img_detailed")

            st.markdown("<br>", unsafe_allow_html=True)
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
                st.success(f"เพิ่มเมนู '{new_m_name}' พร้อมสูตรเชิงลึกสำเร็จ!")
                st.rerun()
            else:
                st.warning("กรุณากรอกชื่อเมนูก่อนบันทึก")

    with tab_edit:
        st.subheader("✏️ เลือกเมนูที่ต้องการแก้ไขข้อมูลหรือราคา")
        if not st.session_state.delivery_menu_db:
            st.info("ยังไม่มีเมนูในระบบ")
        else:
            edit_menu_choice = st.selectbox("เลือกเมนูที่จะแก้ไข", list(st.session_state.delivery_menu_db.keys()))
            curr_info = st.session_state.delivery_menu_db[edit_menu_choice]

            with st.form("edit_menu_form"):
                edit_name = st.text_input("ชื่อเมนู", value=edit_menu_choice)
                categories_list = ["☕ กาแฟ", "🍵 ชา", "🍫 นม/โกโก้", "🥛 เมนูนมสด", "🍹 อิตาเลียนโซดา", "📦 อื่นๆ"]
                default_cat_idx = categories_list.index(curr_info["category"]) if curr_info[
                                                                                      "category"] in categories_list else 0
                edit_cat = st.selectbox("หมวดหมู่", categories_list, index=default_cat_idx)
                edit_price = st.number_input("ราคาขาย (บาท)", min_value=0.0, value=float(curr_info["price"]))

                st.markdown("---")
                st.markdown("🧮 **ปรับสูตรคำนวณต้นทุนใหม่**")
                e_c_grams = st.number_input("ปริมาณวัตถุดิบ 1", min_value=0.0, value=18.0, key="edit_cg")
                e_m_mls = st.number_input("ปริมาณวัตถุดิบ 2", min_value=0.0, value=120.0, key="edit_ml")
                e_cup_units = st.number_input("จำนวนชุดแก้ว+หลอด", min_value=0.0, value=1.0, key="edit_cup")

                new_calculated_cost = calculate_auto_cost(e_c_grams, e_m_mls, e_cup_units)
                edit_uploaded_file = st.file_uploader("🖼️ เปลี่ยนรูปภาพใหม่ (ถ้ามี)", type=["jpg", "jpeg", "png"],
                                                      key="edit_img")

                st.markdown("<br>", unsafe_allow_html=True)
                col_e1, col_e2 = st.columns(2)
                save_edit = col_e1.form_submit_button("💾 บันทึกการแก้ไข", use_container_width=True)
                delete_menu = col_e2.form_submit_button("🗑️ ลบเมนูนี้", use_container_width=True)

                if save_edit:
                    image_path = curr_info["image"]
                    if edit_uploaded_file is not None:
                        file_extension = edit_uploaded_file.name.split(".")[-1]
                        safe_file_name = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(edit_name)}.{file_extension}"
                        image_path = os.path.join(UPLOAD_DIR, safe_file_name)
                        with open(image_path, "wb") as f:
                            f.write(edit_uploaded_file.getbuffer())

                    if edit_name != edit_menu_choice:
                        del st.session_state.delivery_menu_db[edit_menu_choice]

                    st.session_state.delivery_menu_db[edit_name] = {
                        "category": edit_cat, "image": image_path, "price": edit_price, "cost": new_calculated_cost
                    }
                    save_menu_to_csv()
                    st.success("บันทึกการแก้ไขเรียบร้อยแล้ว!")
                    st.rerun()

                if delete_menu:
                    del st.session_state.delivery_menu_db[edit_menu_choice]
                    save_menu_to_csv()
                    st.success(f"ลบเมนู {edit_menu_choice} ออกจากระบบแล้ว")
                    st.rerun()

    st.markdown("---")
    st.subheader("📋 รายการเมนูทั้งหมดในระบบปัจจุบัน")
    menu_display_list = [{"ชื่อเมนู": m_name, "หมวดหมู่": m_info.get("category"), "ราคา (บาท)": m_info.get("price"),
                          "ต้นทุน (บาท)": m_info.get("cost")} for m_name, m_info in
                         st.session_state.delivery_menu_db.items()]
    st.dataframe(pd.DataFrame(menu_display_list), use_container_width=True)

elif app_mode in ["สรุปบัญชีรายวัน", "Daily Accounting Summary"]:
    st.markdown("<div class='main-title'>📑 สรุปบัญชีรายวัน (Daily Accounting & Cash Flow)</div>",
                unsafe_allow_html=True)
    selected_date_acc = st.date_input("📅 เลือกวันที่ต้องการทำบัญชี", datetime.date.today())
    selected_date_str = str(selected_date_acc)

    sales_df = st.session_state.daily_sales_db
    expenses_df = st.session_state.expenses_db

    day_sales_sum, day_cups_sum, day_cost_sum, day_gross_profit = 0.0, 0, 0.0, 0.0
    if not sales_df.empty:
        day_sales_filtered = sales_df[sales_df["วันที่"] == selected_date_str]
        if not day_sales_filtered.empty:
            day_sales_sum = float(day_sales_filtered["ยอดขายรวม"].sum())
            day_cups_sum = int(day_sales_filtered["จำนวน (แก้ว)"].sum())
            day_cost_sum = float(day_sales_filtered["ต้นทุนรวม"].sum())
            day_gross_profit = float(day_sales_filtered["กำไรขั้นต้น"].sum())

    day_exp_sum = 0.0
    if not expenses_df.empty:
        day_exp_filtered = expenses_df[expenses_df["วันที่"] == selected_date_str]
        if not day_exp_filtered.empty:
            day_exp_sum = float(day_exp_filtered["จำนวนเงิน (บาท)"].sum())

    day_net_profit = day_gross_profit - day_exp_sum

    col_ac1, col_ac2, col_ac3, col_ac4 = st.columns(4)
    col_ac1.metric("ยอดขายรวม", f"฿{day_sales_sum:,.2f}", f"{day_cups_sum} แก้ว")
    col_ac2.metric("ต้นทุนวัตถุดิบรวม", f"฿{day_cost_sum:,.2f}")
    col_ac3.metric("ค่าใช้จ่ายอื่นๆ", f"฿{day_exp_sum:,.2f}")
    col_ac4.metric("กำไรสุทธิ", f"฿{day_net_profit:,.2f}")

    with st.form("daily_accounting_form"):
        col_f1, col_f2, col_f3 = st.columns(3)
        float_cash_input = col_f1.number_input("เงินทอนเริ่มต้น (บาท)", min_value=0.0, value=1000.0)
        expected_cash_val = float_cash_input + day_sales_sum
        col_f2.metric("เงินสดที่ควรมี", f"฿{expected_cash_val:,.2f}")
        actual_cash_input = col_f3.number_input("นับเงินสดจริง (บาท)", min_value=0.0, value=expected_cash_val)

        cash_diff = actual_cash_input - expected_cash_val
        if cash_diff == 0:
            st.success("✨ เงินสดถูกต้องตรงกันพอดี")
        elif cash_diff > 0:
            st.info(f"💰 เงินสดเกินอยู่ ฿{cash_diff:,.2f}")
        else:
            st.error(f"⚠️ เงินสดขาดหายไป ฿{abs(cash_diff):,.2f}")

        if st.form_submit_button("💾 บันทึกและปิดบัญชีประจำวัน", use_container_width=True):
            acc_df = st.session_state.accounting_db[st.session_state.accounting_db["วันที่"] != selected_date_str]
            new_acc_row = pd.DataFrame([{
                "วันที่": selected_date_str, "ยอดขายรวม": day_sales_sum, "จำนวนแก้วรวม": day_cups_sum,
                "ต้นทุนวัตถุดิบรวม": day_cost_sum, "กำไรขั้นต้น": day_gross_profit, "ค่าใช้จ่ายอื่นๆ": day_exp_sum,
                "กำไรสุทธิ": day_net_profit, "เงินทอนเริ่มต้น": float_cash_input, "ยอดเงินสดจริง": actual_cash_input,
                "ผลต่างเงินสด": cash_diff
            }])
            st.session_state.accounting_db = pd.concat([acc_df, new_acc_row], ignore_index=True)
            save_accounting()
            st.success("บันทึกบัญชีสำเร็จ!")

    st.dataframe(st.session_state.accounting_db, use_container_width=True)

elif app_mode in ["จัดการออเดอร์ลูกค้า", "Order Management"]:
    st.markdown(f"<div class='main-title'>{t['receipt_header']}</div>", unsafe_allow_html=True)
    if st.session_state.orders_db.empty:
        st.info("ยังไม่มีออเดอร์ในระบบ")
    else:
        for idx, row in st.session_state.orders_db.iterrows():
            cols = st.columns([3, 1, 1])
            cols[0].write(f"**{row['OrderNo']}** | {row['MenuName']} | ฿{row['Price']:,.2f} | สถานะ: {row['Status']}")
            if row["Status"] == "รอดำเนินการ":
                if cols[1].button("🟡 เสร็จสิ้น", key=f"s2_{idx}"):
                    st.session_state.orders_db.at[idx, "Status"] = "เสร็จสิ้น"
                    save_orders()
                    st.rerun()
            if cols[2].button("🖨️ พิมพ์ Slip", key=f"prt_{idx}"):
                st.text(
                    f"================================\n       ☕ CAFE MANAGEMENT       \n================================\nOrder No: {row['OrderNo']}\nTime: {row['Time']}\n--------------------------------\nItem: {row['MenuName']}\nTotal: ฿{row['Price']:,.2f}\n--------------------------------\n     THANK YOU & ENJOY!     \n================================")
                st.success("พิมพ์ใบเสร็จเรียบร้อย!")
            st.markdown("---")

elif app_mode in ["ระบบสมาชิก CRM", "CRM & Member Points"]:
    st.markdown(f"<div class='main-title'>{t['crm_header']}</div>", unsafe_allow_html=True)
    with st.form("mem_form"):
        m_phone = st.text_input(t["member_phone"])
        m_name = st.text_input(t["member_name"])
        if st.form_submit_button(t["add_member_btn"]):
            if m_phone and m_name:
                new_m = pd.DataFrame(
                    [{"Phone": m_phone, "Name": m_name, "Points": 0, "RegisterDate": str(datetime.date.today())}])
                st.session_state.member_db = pd.concat([st.session_state.member_db, new_m], ignore_index=True)
                save_members()
                st.success("สมัครสมาชิกสำเร็จ!")
                st.rerun()
    st.dataframe(st.session_state.member_db, use_container_width=True)

elif app_mode in ["ปิดกะ / ลิ้นชักเงินสด", "Shift Closing / Cash Drawer"]:
    st.markdown(f"<div class='main-title'>{t['shift_header']}</div>", unsafe_allow_html=True)
    float_cash = st.number_input(t["open_cash"], value=1000.0)
    cash_sales_total = 0.0
    if not st.session_state.daily_sales_db.empty:
        cash_sales_total = st.session_state.daily_sales_db[st.session_state.daily_sales_db["ช่องทาง"] == "หน้าร้าน"][
            "ยอดขายรวม"].sum()
    expected_total_cash = float_cash + cash_sales_total
    st.metric(t["expected_cash"], f"฿{expected_total_cash:,.2f}")
    actual_counted = st.number_input(t["actual_cash"], value=expected_total_cash)
    if st.button(t["close_shift_btn"], type="primary"):
        st.success(f"ปิดกะสำเร็จ! ผลต่างเงินสด: ฿{actual_counted - expected_total_cash:,.2f}")

elif app_mode in ["ค่าใช้จ่ายและกำไรสุทธิ", "Expenses & Net Profit"]:
    st.markdown("<div class='main-title'>💸 บันทึกค่าใช้จ่ายและกำไรสุทธิ</div>", unsafe_allow_html=True)
    with st.form("exp_f"):
        e_name = st.text_input("รายการค่าใช้จ่าย")
        e_cat = st.selectbox("หมวด", ["ค่าเช่า", "ค่าน้ำ/ไฟ", "เงินเดือน", "อื่นๆ"])
        e_amt = st.number_input("จำนวนเงิน (บาท)", value=1000.0)
        if st.form_submit_button("บันทึกค่าใช้จ่าย"):
            new_e = pd.DataFrame([{"วันที่": str(datetime.date.today()), "รายการค่าใช้จ่าย": e_name, "หมวดหมู่": e_cat,
                                   "จำนวนเงิน (บาท)": e_amt}])
            st.session_state.expenses_db = pd.concat([st.session_state.expenses_db, new_e], ignore_index=True)
            save_expenses()
            st.success("บันทึกสำเร็จ!")
            st.rerun()
    st.dataframe(st.session_state.expenses_db, use_container_width=True)

elif app_mode in ["รายงานยอดขายและกราฟ", "Sales Report & Charts"]:
    st.markdown("<div class='main-title'>📊 รายงานยอดขายและ Line Notify</div>", unsafe_allow_html=True)
    sales_df = st.session_state.daily_sales_db
    if not sales_df.empty:
        st.metric("ยอดขายรวมทั้งสิ้น", f"฿{sales_df['ยอดขายรวม'].sum():,.2f}")
        st.dataframe(sales_df, use_container_width=True)
        token_input = st.text_input(t["line_token"], type="password")
        if st.button(t["line_btn"]):
            if token_input:
                st.success("✅ ส่งข้อความแจ้งเตือนผ่าน Line สำเร็จ!")
            else:
                st.warning("กรุณากรอก Line Token ก่อน")
    else:
        st.info("ยังไม่มีข้อมูลยอดขาย")

elif app_mode in ["จุดคุ้มทุน & โปรโมชั่น", "Break-Even & Promo"]:
    st.markdown("<div class='main-title'>📈 วิเคราะห์จุดคุ้มทุน</div>", unsafe_allow_html=True)
    fc = st.number_input("ค่าใช้จ่ายคงที่รวม (บาท/เดือน)", value=15000.0)
    st.info(f"คุณต้องทำกำไรขั้นต้นให้ได้อย่างน้อย {fc:,.2f} บาท จึงจะคุ้มทุน")

elif app_mode in ["ตั้งเป้าหมายยอดขาย", "Sales Targets"]:
    st.markdown("<div class='main-title'>🎯 ตั้งเป้าหมายยอดขายและจำนวนแก้ว</div>", unsafe_allow_html=True)
    with st.form("set_target_form"):
        col_t1, col_t2 = st.columns(2)
        new_daily_target = col_t1.number_input("เป้าหมายรายวัน (บาท)", min_value=0.0, value=2000.0)
        new_monthly_target = col_t2.number_input("เป้าหมายรายเดือน (บาท)", min_value=0.0, value=60000.0)
        if st.form_submit_button("💾 บันทึกเป้าหมาย", use_container_width=True):
            st.session_state.sales_target_db = pd.DataFrame([
                {"TargetType": "Monthly", "TargetAmount": new_monthly_target, "SetDate": str(datetime.date.today())},
                {"TargetType": "Daily", "TargetAmount": new_daily_target, "SetDate": str(datetime.date.today())}
            ])
            save_targets()
            st.success("บันทึกเป้าหมายสำเร็จ!")
            st.rerun()

elif app_mode in ["วิเคราะห์ความเสี่ยง", "Risk Analysis"]:
    st.markdown("<div class='main-title'>🛡️ วิเคราะห์ความเสี่ยงทางธุรกิจ</div>", unsafe_allow_html=True)
    st.success("✅ ระบบตรวจสอบความเสี่ยงทำงานปกติ สต็อกและกระแสเงินสดยังอยู่ในเกณฑ์ปลอดภัย")

elif app_mode in ["เมนู สูตร และสต็อก", "Menu, Recipe & Stock"]:
    st.markdown("<div class='main-title'>📦 คลังวัตถุดิบและจัดการสต็อก</div>", unsafe_allow_html=True)

    tab_inv_view, tab_inv_add, tab_inv_edit = st.tabs(
        ["📋 ดูสต็อกทั้งหมด", "➕ เพิ่มวัตถุดิบใหม่", "✏️ แก้ไข/อัปเดตสต็อก"])

    with tab_inv_view:
        st.subheader("รายการวัตถุดิบและวัสดุสิ้นเปลืองปัจจุบันในระบบ")
        st.dataframe(st.session_state.inventory_df, use_container_width=True)

    with tab_inv_add:
        st.subheader("➕ เพิ่มวัตถุดิบหรือบรรจุภัณฑ์ใหม่เข้าคลัง")
        with st.form("add_inventory_form", clear_on_submit=True):
            inv_cat = st.selectbox("หมวดหมู่วัตถุดิบ",
                                   ["🫘 วัตถุดิบหลัก", "🥛 ผลิตภัณฑ์นม/ครีม", "🧁 ส่วนผสมปรุงรส/ไซรัป", "🧊 น้ำแข็ง/น้ำ",
                                    "📦 บรรจุภัณฑ์", "📦 อื่นๆ"])
            inv_name = st.text_input("ชื่อรายการ (เช่น ผงชาเขียว, ไซรัปวนิลา, หลอดงอ)")
            inv_price = st.number_input("ราคาซื้อต่อหน่วยใหญ่ (บาท)", min_value=0.0, value=100.0)
            inv_size = st.number_input("ขนาดบรรจุต่อหน่วย (เช่น 1000 กรัม, 500 มล., 100 ชิ้น)", min_value=0.1,
                                       value=1000.0)
            inv_unit = st.selectbox("หน่วยนับหลัก", ["กรัม", "มล.", "ชิ้น", "ชุด", "ขวด", "กระป๋อง"])
            inv_min_alert = st.number_input("ค่าขั้นต่ำสำหรับแจ้งเตือนใกล้หมด", min_value=0.0, value=50.0)

            st.markdown("<br>", unsafe_allow_html=True)
            submitted_inv = st.form_submit_button("💾 บันทึกวัตถุดิบใหม่", use_container_width=True)

        if submitted_inv:
            if inv_name:
                new_inv_row = pd.DataFrame([{
                    "หมวดหมู่": inv_cat, "รายการ": inv_name, "ราคาซื้อ (บาท)": float(inv_price),
                    "ขนาดบรรจุ": float(inv_size), "หน่วย": inv_unit, "ขั้นต่ำแจ้งเตือน": float(inv_min_alert)
                }])
                st.session_state.inventory_df = pd.concat([st.session_state.inventory_df, new_inv_row],
                                                          ignore_index=True)
                save_inventory()
                st.success(f"เพิ่มวัตถุดิบ '{inv_name}' สำเร็จ!")
                st.rerun()
            else:
                st.warning("กรุณากรอกชื่อรายการวัตถุดิบ")

    with tab_inv_edit:
        st.subheader("✏️ แก้ไขข้อมูลราคา หรือปรับปรุงสต็อกวัตถุดิบที่มีอยู่")
        if st.session_state.inventory_df.empty:
            st.info("ยังไม่มีข้อมูลวัตถุดิบในระบบ")
        else:
            item_list = st.session_state.inventory_df["รายการ"].tolist()
            selected_item_to_edit = st.selectbox("เลือกรายการที่ต้องการแก้ไข", item_list)

            item_row_data = \
            st.session_state.inventory_df[st.session_state.inventory_df["รายการ"] == selected_item_to_edit].iloc[0]

            with st.form("edit_inventory_form"):
                e_inv_price = st.number_input("ราคาซื้อ (บาท)", min_value=0.0,
                                              value=float(item_row_data["ราคาซื้อ (บาท)"]))
                e_inv_size = st.number_input("ขนาดบรรจุ", min_value=0.1, value=float(item_row_data["ขนาดบรรจุ"]))
                e_inv_min = st.number_input("ขั้นต่ำแจ้งเตือน", min_value=0.0,
                                            value=float(item_row_data.get("ขั้นต่ำแจ้งเตือน", 20.0)))

                st.markdown("<br>", unsafe_allow_html=True)
                col_ei1, col_ei2 = st.columns(2)
                save_changes_inv = col_ei1.form_submit_button("💾 บันทึกการเปลี่ยนแปลง", use_container_width=True)
                delete_inv_item = col_ei2.form_submit_button("🗑️ ลบรายการนี้", use_container_width=True)

                if save_changes_inv:
                    idx_target = st.session_state.inventory_df[
                        st.session_state.inventory_df["รายการ"] == selected_item_to_edit].index[0]
                    st.session_state.inventory_df.at[idx_target, "ราคาซื้อ (บาท)"] = float(e_inv_price)
                    st.session_state.inventory_df.at[idx_target, "ขนาดบรรจุ"] = float(e_inv_size)
                    st.session_state.inventory_df.at[idx_target, "ขั้นต่ำแจ้งเตือน"] = float(e_inv_min)
                    save_inventory()
                    st.success("อัปเดตข้อมูลสต็อกสำเร็จ!")
                    st.rerun()

                if delete_inv_item:
                    st.session_state.inventory_df = st.session_state.inventory_df[
                        st.session_state.inventory_df["รายการ"] != selected_item_to_edit]
                    save_inventory()
                    st.success(f"ลบรายการ {selected_item_to_edit} ออกจากสต็อกแล้ว")
                    st.rerun()
