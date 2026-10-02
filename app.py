import streamlit as st
import pandas as pd
import numpy as np

# 1. ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(
    page_title="ระบบทำนายความมั่นคงทางการเงิน",
    page_icon="📊",
    layout="wide"
)

st.title("📊 ระบบทำนายความมั่นคงทางการเงินของครัวเรือน")

# 2. ฟอร์มรับข้อมูลนำเข้า (Inputs)
col1, col2 = st.columns(2)

with col1:
    gender = st.selectbox("1. เพศ", ["หญิง", "ชาย", "อื่นๆ"])
    education = st.selectbox("3. ระดับการศึกษา", ["ปริญญาตรี", "ต่ำกว่าปริญญาตรี", "สูงกว่าปริญญาตรี"])
    employment = st.selectbox("4. สถานะการทำงาน", ["นักเรียน / นักศึกษา", "ทำงานประจำ", "ว่างงาน", "ธุรกิจส่วนตัว"])
    job = st.selectbox("5. อาชีพ", ["นักเรียน / นักศึกษา", "พนักงานบริษัท", "ข้าราชการ", "ธุรกิจส่วนตัว"])
    region = st.selectbox("6. ภูมิภาค", ["เอเชีย", "ยุโรป", "อเมริกาเหนือ", "อื่นๆ"])

with col2:
    income = st.number_input("7. รายได้ต่อปี (USD)", value=10000.00, step=500.0)
    savings = st.number_input("9. เงินออมสะสม (USD)", value=30000.00, step=1000.0)
    credit_score = st.number_input("10. คะแนนเครดิต (Credit Score 300-850)", min_value=300, max_value=850, value=500)
    savings_ratio = st.number_input("11. อัตราส่วนเงินออมต่อรายได้ (%)", value=10.00, step=1.0)
    dti_ratio = st.number_input("12. อัตราส่วนหนี้ต่อรายได้ (DTI %)", value=10.00, step=1.0)

st.markdown("<br>", unsafe_allow_html=True)

# 3. ปุ่มประมวลผลทำนาย
if st.button("🔍 ประมวลผลและทำนายความมั่นคงทางการเงิน", use_container_width=True, type="primary"):
    
    # -------------------------------------------------------------------
    # [ส่วนเชื่อมต่อโมเดล ML] 
    # นำค่าที่ได้จาก Input เข้าโมเดลของคุณ เช่น:
    # probs = model.predict_proba(input_df)[0]
    # -------------------------------------------------------------------
    
    # ตัวอย่างการจำลองผลลัพธ์ความน่าจะเป็น (ตามรูปตัวอย่าง)
    classes = ['Moderate', 'Stable', 'Unstable']
    probabilities = [0.04, 0.00, 0.96]  # ค่าความน่าจะเป็น (4%, 0%, 96%)
    
    # ค้นหาคลาสที่มีค่าความน่าจะเป็นสูงสุด
    max_idx = np.argmax(probabilities)
    predicted_class = classes[max_idx]

    # 4. แสดงผลการทำนายหลัก (Header & Alert Message)
    st.subheader("📊 ผลการทำนายความมั่นคงทางการเงิน")
    
    if predicted_class == 'Unstable':
        st.error("🔴 **ไม่มั่นคง (Unstable)** — มีความเสี่ยงทางการเงินสูง ควรปรับแผนรายจ่ายและลดภาระหนี้สิน")
    elif predicted_class == 'Moderate':
        st.warning("🟡 **ปานกลาง (Moderate)** — มีความมั่นคงทางการเงินระดับปานกลาง ควรเพิ่มการออมฉุกเฉิน")
    else:
        st.success("🟢 **มั่นคง (Stable)** — สถานะทางการเงินมีความมั่นคงสูง")

    # 5. แสดงตารางระดับความน่าจะเป็น (แปลภาษาไทย)
    st.write("### ความน่าจะเป็นของแต่ละระดับ")
    
    # Dictionary แปลงคลาสภาษาอังกฤษ -> ภาษาไทย
    label_mapping = {
        'Moderate': 'ปานกลาง (Moderate)',
        'Stable': 'มั่นคง (Stable)',
        'Unstable': 'ไม่มั่นคง (Unstable)'
    }
    
    # สร้าง DataFrame สำหรับตาราง
    df_prob = pd.DataFrame({
        'ระดับความมั่นคง': [label_mapping[c] for c in classes],
        'ความน่าจะเป็น (%)': [int(p * 100) for p in probabilities]
    })
    
    # แสดงตารางภาษาไทย
    st.dataframe(
        df_prob, 
        use_container_width=True, 
        hide_index=True
    )
