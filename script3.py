import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- ตั้งค่าหน้าตาของเว็บแอปพลิเคชัน (Page Configuration) ---
st.set_page_config(page_title="Beverage Business Cost & Risk Analysis Tool", layout="wide",
                   page_icon="📊")  # type: ignore

# --- ตกแต่งการแสดงผลกล่อง Metric ด้วย Custom CSS ---
st.markdown("""
    <style>
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Beverage Business Cost & Risk Analysis Tool")

# --- SIDEBAR: ค่าใช้จ่ายคงที่รายเดือน (Fixed Costs) ---
st.sidebar.header("🏢 Monthly Fixed Costs")
rent = float(st.sidebar.number_input("Shop Rent ($/฿)", value=10000, step=500))
salaries = float(st.sidebar.number_input("Staff Salaries ($/฿)", value=15000, step=1000))
utilities = float(st.sidebar.number_input("Utilities & Internet ($/฿)", value=3000, step=500))
other_fixed = float(st.sidebar.number_input("Miscellaneous ($/฿)", value=2000, step=500))

# คำนวณรวมค่าใช้จ่ายคงที่ต่อเดือน
total_fixed_costs: float = rent + salaries + utilities + other_fixed

# --- TABS LAYOUT: แบ่งหน้าการทำงานเป็น 4 แท็บหลัก ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📦 1. Inventory & Raw Materials",
    "🥤 2. Menu Setup & Unit Costs",
    "📈 3. Break-Even Analysis",
    "⚠️ 4. Risk Simulation (What-If)"
])

# ==========================================
# TAB 1: ระบบจัดการสต็อกวัตถุดิบ (แยก 2 หมวดหมู่)
# ==========================================
with tab1:
    st.subheader("📦 Categorized Inventory Management")
    st.caption("Manage raw ingredients and packaging supplies separately for better inventory control.")

    # 1. หมวดหมู่วัตถุดิบหลัก (Raw Materials & Dairy)
    st.markdown("#### 🌾 Raw Materials & Dairy")
    if 'raw_data' not in st.session_state:
        st.session_state.raw_data = pd.DataFrame([
            {"Item Name": "Thai Tea Powder", "Pack Price": 150.0, "Quantity/Pack (g/ml)": 1000.0, "Current Stock": 5.0,
             "Unit": "Bag"},
            {"Item Name": "Green Tea Powder", "Pack Price": 180.0, "Quantity/Pack (g/ml)": 1000.0, "Current Stock": 3.0,
             "Unit": "Bag"},
            {"Item Name": "Coffee Beans", "Pack Price": 250.0, "Quantity/Pack (g/ml)": 500.0, "Current Stock": 4.0,
             "Unit": "Bag"},
            {"Item Name": "Condensed Milk", "Pack Price": 50.0, "Quantity/Pack (g/ml)": 2000.0, "Current Stock": 10.0,
             "Unit": "Can"},
            {"Item Name": "Fresh Milk", "Pack Price": 65.0, "Quantity/Pack (g/ml)": 1000.0, "Current Stock": 8.0,
             "Unit": "Carton"}
        ])

    edited_raw = st.data_editor(
        st.session_state.raw_data,
        num_rows="dynamic",
        use_container_width=True,
        key="raw_editor"
    )
    edited_raw["Unit Cost (per g/ml)"] = edited_raw["Pack Price"] / edited_raw["Quantity/Pack (g/ml)"]

    st.divider()

    # 2. หมวดหมู่บรรจุภัณฑ์ (Packaging Supplies)
    st.markdown("#### 🥤 Packaging Supplies")
    if 'pkg_data' not in st.session_state:
        st.session_state.pkg_data = pd.DataFrame([
            {"Item Name": "Plastic Cup", "Pack Price": 120.0, "Quantity/Pack (pcs)": 50.0, "Current Stock": 10.0,
             "Unit": "Sleeve"},
            {"Item Name": "Cup Lid", "Pack Price": 40.0, "Quantity/Pack (pcs)": 50.0, "Current Stock": 10.0,
             "Unit": "Sleeve"},
            {"Item Name": "Straw", "Pack Price": 25.0, "Quantity/Pack (pcs)": 100.0, "Current Stock": 5.0,
             "Unit": "Pack"},
            {"Item Name": "Takeaway Bag", "Pack Price": 35.0, "Quantity/Pack (pcs)": 100.0, "Current Stock": 5.0,
             "Unit": "Pack"}
        ])

    edited_pkg = st.data_editor(
        st.session_state.pkg_data,
        num_rows="dynamic",
        use_container_width=True,
        key="pkg_editor"
    )
    edited_pkg["Unit Cost (per pc)"] = edited_pkg["Pack Price"] / edited_pkg["Quantity/Pack (pcs)"]

    st.divider()

    # ระบบแจ้งเตือนสต็อกใกล้หมด (เช็ครวมทั้งสองตาราง)
    st.markdown("#### 🔔 Stock Level Alert")
    low_raw = edited_raw[edited_raw["Current Stock"] <= 3.0]
    low_pkg = edited_pkg[edited_pkg["Current Stock"] <= 3.0]

    if not low_raw.empty or not low_pkg.empty:
        low_items = low_raw["Item Name"].tolist() + low_pkg["Item Name"].tolist()
        st.warning(f"⚠️ Low Stock Warning: {len(low_items)} item(s) running low: " + ", ".join(low_items))
    else:
        st.success("✅ All stock levels are sufficient.")

# ==========================================
# TAB 2: ตั้งค่าเมนู เครื่องดื่ม และต้นทุน (Menu Setup)
# ==========================================
with tab2:
    st.subheader("Menu Pricing, Unit Costs & Sales Mix")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🟠 Thai Tea")
        price_thai = float(st.number_input("Selling Price", value=45.0, key="p_th"))
        cost_mat_thai = float(st.number_input("Ingredient Cost/Cup", value=12.0, key="cm_th"))
        cost_pkg_thai = float(st.number_input("Packaging Cost/Cup", value=4.0, key="cp_th"))
        share_thai = float(st.slider("Sales Share (%)", 0, 100, 50, key="s_th"))

    with col2:
        st.markdown("### 🟢 Green Tea")
        price_green = float(st.number_input("Selling Price", value=50.0, key="p_gr"))
        cost_mat_green = float(st.number_input("Ingredient Cost/Cup", value=15.0, key="cm_gr"))
        cost_pkg_green = float(st.number_input("Packaging Cost/Cup", value=4.0, key="cp_gr"))
        share_green = float(st.slider("Sales Share (%)", 0, 100, 30, key="s_gr"))

    with col3:
        st.markdown("### 🟤 Coffee")
        price_coffee = float(st.number_input("Selling Price", value=55.0, key="p_cf"))
        cost_mat_coffee = float(st.number_input("Ingredient Cost/Cup", value=18.0, key="cm_cf"))
        cost_pkg_coffee = float(st.number_input("Packaging Cost/Cup", value=4.0, key="cp_cf"))
        share_coffee = float(st.slider("Sales Share (%)", 0, 100, 20, key="s_cf"))

    total_share = share_thai + share_green + share_coffee
    if total_share != 100:
        st.error(f"⚠️ Total Sales Share must equal 100% (Current Total: {total_share:.0f}%)")

# ==========================================
# ส่วนคำนวณคณิตศาสตร์เบื้องหลัง (Core Calculation Logic)
# ==========================================
cost_thai = cost_mat_thai + cost_pkg_thai
cost_green = cost_mat_green + cost_pkg_green
cost_coffee = cost_mat_coffee + cost_pkg_coffee

w_th = share_thai / 100.0 if total_share > 0 else 0.0
w_gr = share_green / 100.0 if total_share > 0 else 0.0
w_cf = share_coffee / 100.0 if total_share > 0 else 0.0

avg_price: float = (price_thai * w_th) + (price_green * w_gr) + (price_coffee * w_cf)
avg_cost: float = (cost_thai * w_th) + (cost_green * w_gr) + (cost_coffee * w_cf)
avg_margin: float = avg_price - avg_cost

bep_month: float = (total_fixed_costs / avg_margin) if avg_margin > 0 else 0.0
bep_day: float = bep_month / 30.0

# ==========================================
# TAB 3: วิเคราะห์จุดคุ้มทุนและกราฟ (Break-Even Charts)
# ==========================================
with tab3:
    st.subheader("Key Performance Indicators (KPIs)")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Monthly Fixed Cost", f"${total_fixed_costs:,.0f}")
    m2.metric("Avg. Margin / Cup", f"${avg_margin:.2f}")
    m3.metric("Break-Even / Month", f"{bep_month:,.0f} cups")
    m4.metric("Break-Even / Day", f"{bep_day:,.1f} cups")

    st.divider()

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown("#### 🍩 Fixed Cost Breakdown")
        df_fixed = pd.DataFrame({
            "Category": ["Rent", "Salaries", "Utilities", "Misc"],
            "Amount": [rent, salaries, utilities, other_fixed]
        })
        fig_fixed = px.pie(df_fixed, values="Amount", names="Category", hole=0.4,
                           color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_fixed, use_container_width=True)

    with col_g2:
        st.markdown("#### 📈 Break-Even Analysis Chart")
        max_cups = int(bep_month * 2) + 100 if bep_month > 0 else 500
        cups = list(range(0, max_cups, 50))
        rev = [float(c * avg_price) for c in cups]
        vc = [float(c * avg_cost) for c in cups]
        tc = [v + total_fixed_costs for v in vc]

        fig_bep = go.Figure()
        fig_bep.add_trace(go.Scatter(x=cups, y=rev, mode='lines', name='Total Revenue', line=dict(color='green')))
        fig_bep.add_trace(go.Scatter(x=cups, y=tc, mode='lines', name='Total Cost', line=dict(color='red')))
        if bep_month > 0:
            fig_bep.add_vline(x=bep_month, line_dash="dash", line_color="blue", annotation_text="Break-Even Point")
        fig_bep.update_layout(xaxis_title="Monthly Volume (Cups)", yaxis_title="Amount ($/฿)")
        st.plotly_chart(fig_bep, use_container_width=True)

# ==========================================
# TAB 4: จำลองความเสี่ยงและการดาวน์โหลดรายงาน (What-If Analysis)
# ==========================================
with tab4:
    st.subheader("🧪 Risk Scenario Simulation (What-If Analysis)")

    sales_drop = float(st.slider("Simulated Sales Drop (%)", 0, 50, 10))
    cost_increase = float(st.slider("Simulated Ingredient Price Increase (%)", 0, 50, 5))

    new_avg_cost = avg_cost * (1.0 + (cost_increase / 100.0))
    new_avg_margin = avg_price - new_avg_cost
    new_bep_month: float = (total_fixed_costs / new_avg_margin) if new_avg_margin > 0 else 0.0

    st.warning(
        f"If ingredient costs increase by {cost_increase:.0f}%, the new break-even point will rise to **{new_bep_month:,.0f} cups/month** (previously {bep_month:,.0f} cups).")

    st.divider()
    df_export = pd.DataFrame({
        "Metric": ["Monthly Fixed Cost", "Weighted Avg Selling Price", "Weighted Avg Variable Cost",
                   "Break-Even Point (Monthly)", "Break-Even Point (Daily)"],
        "Value": [total_fixed_costs, avg_price, avg_cost, bep_month, bep_day]
    })
    csv = df_export.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Download Summary Report (CSV)", data=csv, file_name="business_analysis_report.csv",
                       mime="text/csv")