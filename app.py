import streamlit as st
import pandas as pd

# -------------------------------------------------------------------
# [สมมติข้อมูลผลลัพธ์จากโมเดลของคุณ]
# -------------------------------------------------------------------
# คลาสที่ทำนายได้สูงสุด: 'Moderate', 'Stable', หรือ 'Unstable'
predicted_class = 'Moderate' 

# ค่าความน่าจะเป็น (%) จากโมเดล
probabilities = {
    'Moderate': 97.73,
    'Stable': 2.27,
    'Unstable': 0.00
}
# -------------------------------------------------------------------

st.markdown("---")
st.subheader("📊 ผลการทำนายความมั่นคงทางการเงิน")

# 1. กำหนดข้อมูลการแปลภาษาไทย แถบสี และคำแนะนำ
status_config = {
    'Stable': {
        'title': 'ระดับความมั่นคงสูง (Stable)',
        'color': '#16a34a',       # เขียว
        'bg_color': '#f0fdf4',    # เขียวอ่อน
        'border_color': '#bbf7d0',
        'badge': '🟢 มั่นคง',
        'desc': 'สภาพคล่องทางการเงินแข็งแกร่ง มีภาระหนี้สินในระดับเหมาะสมและมีสัดส่วนเงินออมที่ดี'
    },
    'Moderate': {
        'title': 'ระดับปานกลาง (Moderate)',
        'color': '#d97706',       # ส้ม/เหลือง
        'bg_color': '#fffbeb',    # เหลืองอ่อน
        'border_color': '#fef3c7',
        'badge': '🟡 ปานกลาง',
        'desc': 'สภาพคล่องทางการเงินอยู่ในระดับปานกลาง ควรควบคุมการใช้จ่ายและเพิ่มสัดส่วนการออมฉุกเฉิน'
    },
    'Unstable': {
        'title': 'ระดับความเสี่ยงสูง (Unstable)',
        'color': '#dc2626',       # แดง
        'bg_color': '#fef2f2',    # แดงอ่อน
        'border_color': '#fecaca',
        'badge': '🔴 ไม่มั่นคง',
        'desc': 'มีความเสี่ยงทางการเงินสูง ควรปรับแผนรายจ่าย เร่งลดภาระหนี้สิน และสร้างเงินออมฉุกเฉิน'
    }
}

info = status_config[predicted_class]

# 2. แสดง Card สรุปผลการทำนายหลัก
st.markdown(f"""
    <div style="
        background-color: {info['bg_color']};
        border-left: 6px solid {info['color']};
        border-radius: 10px;
        padding: 18px 24px;
        margin-bottom: 25px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    ">
        <h3 style="color: {info['color']}; margin: 0 0 8px 0; font-size: 22px; font-weight: 700;">
            {info['badge']} — {info['title']}
        </h3>
        <p style="color: #374151; margin: 0; font-size: 15px; line-height: 1.6;">
            <strong>คำแนะนำ:</strong> {info['desc']}
        </p>
    </div>
""", unsafe_allow_html=True)

# 3. แสดงความน่าจะเป็นแบบ Visual (Progress Bars)
st.write("### 📈 สัดส่วนความน่าจะเป็นแต่ละระดับ")

label_map = {
    'Moderate': {'name': 'ปานกลาง (Moderate)', 'icon': '🟡'},
    'Stable': {'name': 'มั่นคง (Stable)', 'icon': '🟢'},
    'Unstable': {'name': 'ไม่มั่นคง (Unstable)', 'icon': '🔴'}
}

# สร้าง Container สำหรับจัดกลุ่ม Progress Bars ให้สวยงาม
with st.container():
    for key, prob_val in probabilities.items():
        col_text, col_bar, col_val = st.columns([3, 6, 1.5])
        
        with col_text:
            st.markdown(f"**{label_map[key]['icon']} {label_map[key]['name']}**")
        
        with col_bar:
            # st.progress รับค่าตั้งแต่ 0.0 ถึง 1.0
            st.progress(prob_val / 100.0)
            
        with col_val:
            st.markdown(f"**{prob_val:.2f}%**")
