import os

# ให้ Qt (ที่ Orange เรียกใช้) ทำงานแบบไม่มีหน้าจอบนเซิร์ฟเวอร์
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pickle
import numpy as np
import pandas as pd
import streamlit as st

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="ระบบวิเคราะห์ความมั่นคงทางการเงิน",
    page_icon="💰",
    layout="wide"
)

# Custom CSS ตกแต่งสไตล์เพิ่มเติม
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #1E293B;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #64748B;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }
    div[data-testid="stForm"] {
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

MODEL_PATH = "models/models.pkcls"

# โหลดโมเดลที่บันทึกจาก Orange (Save Model -> .pkcls)
@st.cache_resource
def load_model():
    import Orange  # noqa: F401
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

model = None
try:
    model = load_model()
except FileNotFoundError:
    st.error(f"❌ ไม่พบไฟล์โมเดลที่ {MODEL_PATH}")
    st.info("💡 กรุณาตรวจสอบว่ามีไฟล์ models.pkcls อยู่ในโฟลเดอร์ models ของโปรเจกต์")
except Exception as e:
    st.error(f"❌ ไม่สามารถโหลดโมเดลได้: {e}")

# Mappings จากภาษาไทย -> ค่าภาษาอังกฤษที่โมเดล Orange รู้จัก
GENDER_MAP = {"ชาย": "Male", "หญิง": "Female", "อื่นๆ": "Other"}
EDUCATION_MAP = {"มัธยมศึกษา": "High School", "ปริญญาตรี": "Bachelor", "ปริญญาโท": "Master", "ปริญญาเอก": "PhD", "อื่นๆ": "Other"}
EMPLOYMENT_MAP = {"ทำงานประจำ": "Employed", "ธุรกิจส่วนตัว / รับจ้างอิสระ": "Self-employed", "นักเรียน / นักศึกษา": "Student", "ว่างงาน": "Unemployed"}
JOB_MAP = {
    "พนักงานขาย": "Salesperson", "ครู / อาจารย์": "Teacher", "ผู้จัดการ": "Manager",
    "นักเรียน / นักศึกษา": "Student", "นักบัญชี": "Accountant", "แพทย์ / บุคลากรทางการแพทย์": "Doctor",
    "ว่างงาน": "Unemployed", "พนักงานขับรถ": "Driver", "วิศวกร": "Engineer"
}
REGION_MAP = {"เอเชีย": "Asia", "ยุโรป": "Europe", "อเมริกาเหนือ": "North America", "แอฟริกา": "Africa", "อื่นๆ": "Other"}
HAS_LOAN_MAP = {"ไม่มี": "No", "มี": "Yes"}
LOAN_TYPE_MAP = {"การศึกษา": "Education", "ธุรกิจ": "Business", "ยานพาหนะ": "Car", "ที่อยู่อาศัย": "Home"}

DEFAULT_SELECT = "กรุณากรอกข้อมูล"

def get_model_domain(m):
    return getattr(m, "original_domain", None) or m.domain

def build_orange_table(m, input_dict):
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
                unknown_values.append(f"{var.name} = {text}")
                row.append(np.nan)
        else:
            try:
                row.append(float(val))
            except (TypeError, ValueError):
                unknown_values.append(f"{var.name} = {val}")
                row.append(np.nan)

    table = Table.from_numpy(Domain(attrs), np.array([row], dtype=float))
    return table, missing_cols, unknown_values

# Header
st.markdown("<h1 class='main-title'>💰 AI ทำนายความมั่นคงทางการเงินของครัวเรือน</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>กรอกข้อมูลด้านล่างให้ครบถ้วนเพื่อประมวลผลและทำนายระดับความมั่นคงทางการเงิน</p>", unsafe_allow_html=True)

# ฟอร์มกรอกข้อมูลแบ่ง 3 คอลัมน์
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.subheader("👤 ข้อมูลทั่วไปและอาชีพ")
        age = st.number_input("1. อายุ (ปี)", min_value=18, max_value=100, value=None, placeholder="กรุณากรอกข้อมูล")
        gender_th = st.selectbox("2. เพศ", [DEFAULT_SELECT, "ชาย", "หญิง", "อื่นๆ"])
        education_th = st.selectbox("3. ระดับการศึกษา", [DEFAULT_SELECT, "มัธยมศึกษา", "ปริญญาตรี", "ปริญญาโท", "ปริญญาเอก", "อื่นๆ"])
        employment_th = st.selectbox("4. สถานะการทำงาน", [DEFAULT_SELECT, "ทำงานประจำ", "ธุรกิจส่วนตัว / รับจ้างอิสระ", "นักเรียน / นักศึกษา", "ว่างงาน"])
        job_th = st.selectbox("5. อาชีพ", [
            DEFAULT_SELECT, "พนักงานขาย", "ครู / อาจารย์", "ผู้จัดการ", "นักเรียน / นักศึกษา",
            "นักบัญชี", "แพทย์ / บุคลากรทางการแพทย์", "ว่างงาน", "พนักงานขับรถ", "วิศวกร"
        ])
        region_th = st.selectbox("6. ภูมิภาค", [DEFAULT_SELECT, "เอเชีย", "ยุโรป", "อเมริกาเหนือ", "แอฟริกา", "อื่นๆ"])

with col2:
    with st.container(border=True):
        st.subheader("💵 รายได้ รายจ่าย และเงินออม")
        monthly_income = st.number_input("7. รายได้ต่อเดือน (USD)", min_value=0.0, step=100.0, value=None, placeholder="กรุณากรอกข้อมูล")
        monthly_expenses = st.number_input("8. รายจ่ายต่อเดือน (USD)", min_value=0.0, step=50.0, value=None, placeholder="กรุณากรอกข้อมูล")
        savings = st.number_input("9. เงินออมสะสม (USD)", min_value=0.0, step=500.0, value=None, placeholder="กรุณากรอกข้อมูล")
        credit_score = st.number_input("10. คะแนนเครดิต (Credit Score 300-850)", min_value=300, max_value=850, step=1, value=None, placeholder="กรุณากรอกข้อมูล")
        savings_ratio = st.number_input("11. อัตราส่วนเงินออมต่อรายได้", min_value=0.0, max_value=10.0, step=0.1, value=None, placeholder="กรุณากรอกข้อมูล")
        dti_ratio = st.number_input("12. อัตราส่วนหนี้ต่อรายได้ (DTI %)", min_value=0.0, max_value=100.0, step=0.5, value=None, placeholder="กรุณากรอกข้อมูล")

with col3:
    with st.container(border=True):
        st.subheader("💳 ข้อมูลสินเชื่อและหนี้สิน")
        has_loan_th = st.selectbox("13. มีการกู้สินเชื่อหรือไม่", [DEFAULT_SELECT, "ไม่มี", "มี"])

        if has_loan_th == "มี":
            loan_type_th = st.selectbox("14. ประเภทสินเชื่อ", [DEFAULT_SELECT, "การศึกษา", "ธุรกิจ", "ยานพาหนะ", "ที่อยู่อาศัย"])
            loan_amount = st.number_input("15. จำนวนเงินกู้ (USD)", min_value=0.0, step=1000.0, value=None, placeholder="กรุณากรอกข้อมูล")
            loan_term = st.number_input("16. ระยะเวลากู้ (เดือน)", min_value=1, max_value=360, step=1, value=None, placeholder="กรุณากรอกข้อมูล")
            monthly_emi = st.number_input("17. ค่างวดผ่อนชำระต่อเดือน (USD)", min_value=0.0, step=50.0, value=None, placeholder="กรุณากรอกข้อมูล")
            loan_rate = st.number_input("18. อัตราดอกเบี้ย (%)", min_value=0.0, max_value=30.0, step=0.1, value=None, placeholder="กรุณากรอกข้อมูล")
        else:
            loan_type_th = DEFAULT_SELECT
            loan_amount = 0.0
            loan_term = 0
            monthly_emi = 0.0
            loan_rate = 0.0

st.markdown("<br>", unsafe_allow_html=True)

# ปุ่มทำนายผล
if st.button("🔍 ประมวลผลและทำนายความมั่นคงทางการเงิน", type="primary", use_container_width=True):
    # ตรวจสอบการกรอกข้อมูล
    required_selects = [gender_th, education_th, employment_th, job_th, region_th, has_loan_th]
    if has_loan_th == "มี":
        required_selects.append(loan_type_th)
    
    if DEFAULT_SELECT in required_selects or any(v is None for v in [age, monthly_income, monthly_expenses, savings, credit_score, savings_ratio, dti_ratio]):
        st.warning("⚠️ กรุณากรอกข้อมูลให้ครบถ้วนก่อนทำการประมวลผล")
    else:
        # แปลงค่าจาก TH -> EN เพื่อนำเข้า Model
        input_dict = {
            'age': age,
            'gender': GENDER_MAP.get(gender_th),
            'education_level': EDUCATION_MAP.get(education_th),
            'employment_status': EMPLOYMENT_MAP.get(employment_th),
            'job_title': JOB_MAP.get(job_th),
            'monthly_income_usd': monthly_income,
            'monthly_expenses_usd': monthly_expenses,
            'savings_usd': savings,
            'has_loan': HAS_LOAN_MAP.get(has_loan_th),
            'loan_type': LOAN_TYPE_MAP.get(loan_type_th) if has_loan_th == "มี" else None,
            'loan_amount_usd': loan_amount,
            'loan_term_months': loan_term,
            'monthly_emi_usd': monthly_emi,
            'loan_interest_rate_pct': loan_rate,
            'debt_to_income_ratio': dti_ratio,
            'credit_score': credit_score,
            'savings_to_income_ratio': savings_ratio,
            'region': REGION_MAP.get(region_th)
        }

        if model is None:
            st.error("ยังโหลดโมเดลไม่สำเร็จ จึงยังทำนายผลไม่ได้")
        else:
            try:
                table, missing_cols, unknown_values = build_orange_table(model, input_dict)

                values, probs = model(table, model.ValueProbs)
                class_var = get_model_domain(model).class_var
                prediction = class_var.values[int(values[0])]

                st.markdown("---")
                st.markdown("### 📊 ผลการทำนายความมั่นคงทางการเงิน")
                
                pred_lower = prediction.lower()
                if "unstable" in pred_lower:
                    st.error(f"🔴 **ไม่มั่นคง ({prediction})** — มีความเสี่ยงทางการเงินสูง ควรปรับแผนรายจ่ายและลดภาระหนี้สิน")
                elif "stable" in pred_lower:
                    st.success(f"🟢 **มั่นคง ({prediction})** — ครัวเรือนนี้มีสถานะทางการเงินที่แข็งแกร่งและปลอดภัย")
                else:
                    st.warning(f"🟡 **ปานกลาง ({prediction})** — สภาพคล่องทางการเงินอยู่ในระดับปานกลาง ควรควบคุมการใช้จ่าย")

                # ตารางแสดงความน่าจะเป็น
                prob_df = pd.DataFrame({
                    "ระดับความมั่นคง": list(class_var.values),
                    "ความน่าจะเป็น (%)": (probs[0] * 100).round(2)
                })
                st.write("#### ความน่าจะเป็นของแต่ละระดับ")
                st.dataframe(prob_df, hide_index=True, use_container_width=True)

            except Exception as err:
                st.error(f"เกิดข้อผิดพลาดขณะทำนายผล: {err}")
