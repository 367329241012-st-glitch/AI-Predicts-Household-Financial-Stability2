import os

# ให้ Qt (ที่ Orange เรียกใช้) ทำงานแบบไม่มีหน้าจอบนเซิร์ฟเวอร์
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pickle

import numpy as np
import pandas as pd
import streamlit as st

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="Financial Stability Prediction AI",
    page_icon="💰",
    layout="wide"
)

st.title("💰 AI ทำนายความมั่นคงทางการเงินของครัวเรือน")
st.write("กรอกข้อมูลด้านล่างเพื่อทำนายระดับความมั่นคงทางการเงิน")

MODEL_PATH = "models/models.pkcls"


# โหลดโมเดลที่บันทึกจาก Orange (Save Model -> .pkcls)
@st.cache_resource
def load_model():
    import Orange  # noqa: F401  ต้อง import ก่อนเพื่อให้ pickle รู้จักคลาสของ Orange
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


model = None
try:
    model = load_model()
    st.success("โหลดโมเดลเรียบร้อยแล้ว!")
except FileNotFoundError:
    st.error(f"ไม่พบไฟล์โมเดลที่ {MODEL_PATH}")
    st.info("กรุณาตรวจสอบว่ามีไฟล์ models.pkcls อยู่ในโฟลเดอร์ models ของโปรเจกต์")
except Exception as e:
    st.error(f"ไม่สามารถโหลดโมเดลได้: {e}")


def get_model_domain(m):
    """โดเมนข้อมูลดิบที่ใช้ตอนเทรน (ก่อนผ่าน preprocessing ของ Orange)"""
    return getattr(m, "original_domain", None) or m.domain


def build_orange_table(m, input_dict):
    """แปลงข้อมูลที่กรอกให้เป็น Orange Table ตามคอลัมน์ที่โมเดลใช้ตอนเทรน"""
    from Orange.data import Domain, Table

    attrs = get_model_domain(m).attributes
    row = []
    missing_cols = []
    unknown_values = []

    for var in attrs:
        val = input_dict.get(var.name)

        if val is None or (isinstance(val, float) and np.isnan(val)):
            if var.name not in input_dict:
                missing_cols.append(var.name)
            row.append(np.nan)
            continue

        if var.is_discrete:
            text = str(val)
            if text in var.values:
                row.append(float(var.values.index(text)))
            else:
                unknown_values.append(f"{var.name} = {text} (ค่าที่โมเดลรู้จัก: {', '.join(var.values)})")
                row.append(np.nan)
        else:
            try:
                row.append(float(val))
            except (TypeError, ValueError):
                unknown_values.append(f"{var.name} = {val} (ต้องเป็นตัวเลข)")
                row.append(np.nan)

    table = Table.from_numpy(Domain(attrs), np.array([row], dtype=float))
    return table, missing_cols, unknown_values


st.markdown("---")

# แบ่งการกรอกข้อมูลเป็น 3 ส่วน
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("👤 ข้อมูลทั่วไปและอาชีพ")
    age = st.number_input("1. อายุ (Age)", min_value=18, max_value=100, value=35)
    gender = st.selectbox("2. เพศ (Gender)", ["Female", "Male", "Other"])
    education_level = st.selectbox("3. ระดับการศึกษา (Education Level)", ["High School", "Bachelor", "Master", "PhD", "Other"])
    employment_status = st.selectbox("4. สถานะการทำงาน (Employment Status)", ["Employed", "Self-employed", "Student", "Unemployed"])
    job_title = st.selectbox("5. อาชีพ (Job Title)", [
        "Salesperson", "Teacher", "Manager", "Student",
        "Accountant", "Doctor", "Unemployed", "Driver", "Engineer"
    ])
    region = st.selectbox("18. ภูมิภาค (Region)", ["Asia", "Europe", "North America", "Africa", "Other"])

with col2:
    st.subheader("💵 รายได้ รายจ่าย และเงินออม")
    monthly_income_usd = st.number_input("6. รายได้ต่อเดือน (USD)", min_value=0.0, value=3500.0, step=100.0)
    monthly_expenses_usd = st.number_input("7. รายจ่ายต่อเดือน (USD)", min_value=0.0, value=1500.0, step=50.0)
    savings_usd = st.number_input("8. เงินออมสะสม (USD)", min_value=0.0, value=10000.0, step=500.0)
    credit_score = st.slider("16. คะแนนเครดิต (Credit Score)", min_value=300, max_value=850, value=650)
    savings_to_income_ratio = st.number_input("17. อัตราส่วนเงินออมต่อรายได้", min_value=0.0, max_value=10.0, value=2.5, step=0.1)
    debt_to_income_ratio = st.number_input("15. อัตราส่วนหนี้ต่อรายได้ (DTI %)", min_value=0.0, max_value=100.0, value=15.0, step=0.5)

with col3:
    st.subheader("💳 ข้อมูลสินเชื่อและหนี้สิน")
    has_loan = st.selectbox("9. มีการกู้สินเชื่อหรือไม่ (Has Loan)", ["No", "Yes"])

    if has_loan == "Yes":
        loan_type = st.selectbox("10. ประเภทสินเชื่อ (Loan Type)", ["Education", "Business", "Car", "Home"])
        loan_amount_usd = st.number_input("11. จำนวนเงินกู้ (USD)", min_value=0.0, value=50000.0, step=1000.0)
        loan_term_months = st.number_input("12. ระยะเวลากู้ (เดือน)", min_value=1, max_value=360, value=36)
        monthly_emi_usd = st.number_input("13. ค่างวดผ่อนชำระต่อเดือน (USD)", min_value=0.0, value=1200.0, step=50.0)
        loan_interest_rate_pct = st.number_input("14. อัตราดอกเบี้ย (%)", min_value=0.0, max_value=30.0, value=5.5, step=0.1)
    else:
        loan_type = None
        loan_amount_usd = 0.0
        loan_term_months = 0
        monthly_emi_usd = 0.0
        loan_interest_rate_pct = 0.0

st.markdown("---")

# ปุ่มกดทำนายผล
if st.button("🔍 ประมวลผลและทำนายความมั่นคงทางการเงิน", type="primary", use_container_width=True):
    # รวมข้อมูลทั้ง 18 รายการ
    input_dict = {
        'age': age,
        'gender': gender,
        'education_level': education_level,
        'employment_status': employment_status,
        'job_title': job_title,
        'monthly_income_usd': monthly_income_usd,
        'monthly_expenses_usd': monthly_expenses_usd,
        'savings_usd': savings_usd,
        'has_loan': has_loan,
        'loan_type': loan_type,
        'loan_amount_usd': loan_amount_usd,
        'loan_term_months': loan_term_months,
        'monthly_emi_usd': monthly_emi_usd,
        'loan_interest_rate_pct': loan_interest_rate_pct,
        'debt_to_income_ratio': debt_to_income_ratio,
        'credit_score': credit_score,
        'savings_to_income_ratio': savings_to_income_ratio,
        'region': region
    }

    st.write("### ข้อมูลที่นำเข้าเพื่อทำนาย:")
    st.dataframe(pd.DataFrame([input_dict]))

    if model is None:
        st.error("ยังโหลดโมเดลไม่สำเร็จ จึงยังทำนายผลไม่ได้")
    else:
        try:
            table, missing_cols, unknown_values = build_orange_table(model, input_dict)

            if missing_cols:
                st.warning("คอลัมน์ที่โมเดลต้องการแต่ไม่มีในฟอร์ม: " + ", ".join(missing_cols))
            if unknown_values:
                st.warning("ค่าที่โมเดลไม่รู้จัก (ถือเป็นค่าว่าง):\n\n- " + "\n- ".join(unknown_values))

            values, probs = model(table, model.ValueProbs)
            class_var = get_model_domain(model).class_var
            prediction = class_var.values[int(values[0])]

            st.markdown("### 📊 ผลการทำนายความมั่นคงทางการเงิน:")
            pred_lower = prediction.lower()
            if "unstable" in pred_lower:
                st.error(f"🔴 **ไม่มั่นคง ({prediction})** - มีความเสี่ยงทางการเงินสูง ควรปรับแผนรายจ่ายและหนี้สิน")
            elif "stable" in pred_lower:
                st.success(f"🟢 **มั่นคง ({prediction})** - ครัวเรือนนี้มีสถานะทางการเงินที่แข็งแกร่ง")
            else:
                st.warning(f"🟡 **ปานกลาง ({prediction})** - สภาพคล่องทางการเงินอยู่ในระดับปานกลาง ควรควบคุมภาระหนี้สิน")

            prob_df = pd.DataFrame({
                "ระดับ": list(class_var.values),
                "ความน่าจะเป็น (%)": (probs[0] * 100).round(2)
            })
            st.write("#### ความน่าจะเป็นของแต่ละระดับ")
            st.dataframe(prob_df, hide_index=True, use_container_width=True)

        except Exception as err:
            st.error(f"เกิดข้อผิดพลาดขณะทำนายผล: {err}")

# แสดงคอลัมน์ที่โมเดลใช้ เพื่อเช็กว่าชื่อตรงกับฟอร์ม
if model is not None:
    with st.expander("🔧 ข้อมูลโมเดล (สำหรับตรวจสอบ)"):
        domain = get_model_domain(model)
        info = []
        for var in domain.attributes:
            info.append({
                "คอลัมน์": var.name,
                "ชนิด": "ตัวเลือก" if var.is_discrete else "ตัวเลข",
                "ค่าที่รู้จัก": ", ".join(var.values) if var.is_discrete else "-"
            })
        st.dataframe(pd.DataFrame(info), hide_index=True, use_container_width=True)
        if domain.class_var is not None:
            st.write(f"ตัวแปรเป้าหมาย: **{domain.class_var.name}** → {', '.join(domain.class_var.values)}")
