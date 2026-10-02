import streamlit as st
import pandas as pd
import joblib

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="Financial Stability Prediction AI",
    page_icon="💰",
    layout="wide"
)

st.title("💰 AI ทำนายความมั่นคงทางการเงินของครัวเรือน")
st.write("กรอกข้อมูลครัวเรือนทั้ง 18 รายการด้านล่างเพื่อทำนายระดับความมั่นคงทางการเงิน")

# โหลดโมเดล
@st.cache_resource
def load_model():
    # เปลี่ยนชื่อไฟล์ให้ตรงกับไฟล์โมเดลของคุณ เช่น model.pkl
    return joblib.load("models/models.pkcls")

try:
    model = load_model()
    st.success("โหลดโมเดลเรียบร้อยแล้ว!")
except Exception as e:
    st.error(f"ไม่สามารถโหลดโมเดลได้: {e}")
    st.info("กรุณาตรวจสอบว่ามีไฟล์ model.pkl อยู่ในโปรเจกต์")

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
        loan_type = "None"
        loan_amount_usd = 0.0
        loan_term_months = 0
        monthly_emi_usd = 0.0
        loan_interest_rate_pct = 0.0

st.markdown("---")

# ปุ่มกดทำนายผล
if st.button("🔍 ประมวลผลและทำนายความมั่นคงทางการเงิน", type="primary", use_container_width=True):
    # รวมข้อมูลทั้ง 18 คอลัมน์เป็น DataFrame
    input_data = pd.DataFrame([{
        'age': age,
        'gender': gender,
        'education_level': education_level,
        'employment_status': employment_status,
        'job_title': job_title,
        'monthly_income_usd': monthly_income_usd,
        'monthly_expenses_usd': monthly_expenses_usd,
        'savings_usd': savings_usd,
        'has_loan': has_loan,
        'loan_type': loan_type if has_loan == "Yes" else None,
        'loan_amount_usd': loan_amount_usd,
        'loan_term_months': loan_term_months,
        'monthly_emi_usd': monthly_emi_usd,
        'loan_interest_rate_pct': loan_interest_rate_pct,
        'debt_to_income_ratio': debt_to_income_ratio,
        'credit_score': credit_score,
        'savings_to_income_ratio': savings_to_income_ratio,
        'region': region
    }])
    
    st.write("### ข้อมูลที่นำเข้าเพื่อทำนาย:")
    st.dataframe(input_data)
    
    # ทำนายผลลัพธ์
    try:
        prediction = model.predict(input_data)[0]
        
        st.markdown("### 📊 ผลการทำนายความมั่นคงทางการเงิน:")
        if prediction == "Stable":
            st.success("🟢 **มั่นคง (Stable)** - ครัวเรือนนี้มีสถานะทางการเงินที่แข็งแกร่ง")
        elif prediction == "Moderate":
            st.warning("🟡 **ปานกลาง (Moderate)** - สภาพคล่องทางการเงินอยู่ในระดับปานกลาง ควรกุมภาระหนี้สิน")
        else:
            st.error("🔴 **ไม่มั่นคง (Unstable)** - มีความเสี่ยงทางการเงินสูง ควรปรับแผนรายจ่ายและหนี้สิน")
    except Exception as err:
        st.error(f"เกิดข้อผิดพลาดขณะทำนายผล: {err}")
        st.info("หมายเหตุ: ตรวจสอบว่าขั้นตอน Preprocessing / Encoding ข้อมูลในโมเดลตรงกับรูปแบบป้อนเข้า")
