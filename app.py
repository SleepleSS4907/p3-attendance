import streamlit as st
import pandas as pd
import datetime
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. ตั้งค่าการเชื่อมต่อ Google Sheets (เวอร์ชันสำหรับคลาวด์ออนไลน์) ---
def init_connection():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # 🎯 ปรับปรุงใหม่: เปลี่ยนมาใช้การอ่านคีย์จากระบบ Secrets บนออนไลน์เพื่อความปลอดภัยสูงสุด
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            # สำรองไว้กรณีคุณครูยังต้องการกดทดสอบบนเครื่องคอมพิวเตอร์ตัวเองก่อน
            creds = ServiceAccountCredentials.from_json_keyfile_name("your-credentials.json", scope)
            
        client = gspread.authorize(creds)
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/175dIXwMzn3RronYPV3qt_LpjZjqhtYV1BcmM0UVWpII/edit"
        return client.open_by_url(spreadsheet_url).worksheet("เช็คชื่อรายวัน")
    except Exception as e:
        return None

sheet = init_connection()

# --- 2. ฐานข้อมูลรายชื่อนักเรียนชั้น ป.3 ---
students_list = [
    {"เลขที่": 1, "ชื่อ": "เด็กชายกิตติพัฒน์ เกตุตุ้ม"},
    {"เลขที่": 2, "ชื่อ": "เด็กชายธนาธิป พ้นภัย"},
    {"เลขที่": 3, "ชื่อ": "เด็กชายธีรเมท บุญมี"},
    {"เลขที่": 4, "ชื่อ": "เด็กชายอธิพันธ์ ดาวสุข"},
    {"เลขที่": 5, "ชื่อ": "เด็กหญิงจิราวรรณ"},
    {"เลขที่": 6, "ชื่อ": "เด็กหญิงนัฐชา"},
    {"เลขที่": 7, "ชื่อ": "เด็กหญิงนิชญาดา"},
    {"เลขที่": 8, "ชื่อ": "เด็กหญิงวราริน วงค์แปง"},
    {"เลขที่": 9, "ชื่อ": "เด็กหญิงศิริวรรณ"},
    {"เลขที่": 10, "ชื่อ": "เด็กหญิงสุตราพันธ์"},
    {"เลขที่": 11, "ชื่อ": "เด็กชายศักดิ์สิทธิ์ โหยหวน"},
    {"เลขที่": 12, "ชื่อ": "เด็กชายเทพทัต เขตตลาด"}
]

# --- 3. ข้อมูลตารางสอน ป.3 ---
timetable = {
    "Monday": ["ภาษาไทย (ครูณัฐวุฒิ)", "วิทยาศาสตร์ (ครูณัฐวุฒิ)", "ศิลปะ (ครูณัฐวุฒิ)", "ลดเวลาเรียน (ครูณัฐวุฒิ)", "สุขศึกษา (ครูทวีศักดิ์)"],
    "Tuesday": ["English (ครูจุรีพร)", "คณิตศาสตร์ (ครูณัฐวุฒิ)", "การงาน (ครูณัฐวุฒิ)", "สังคม (ครูณัฐวุฒิ)", "แนะแนว (ครูณัฐวุฒิ)"],
    "Wednesday": ["ภาษาไทย (ครูณัฐวุฒิ)", "English (ครูจุรีพร)", "คณิตศาสตร์ (ครูณัฐวุฒิ)", "ลูกเสือ (ครูณัฐวุฒิ)", "สังคม (ครูณัฐวุฒิ)", "English (ครูณัฐวุฒิ)"],
    "Thursday": ["ภาษาไทย (ครูณัฐวุฒิ)", "English (ครูจุรีพร)", "English (ครูจุรีพร)", "วิทยาศาสตร์ (ครูณัฐวุฒิ)", "หน้าที่พลเมือง (ครูณัฐวุฒิ)"],
    "Friday": ["English (ครูจุรีพร)", "คณิตศาสตร์ (ครูณัฐวุฒิ)", "ประวัติ (ครูณัฐวุฒิ)", "ลดเวลาเรียน (ครูณัฐวุฒิ)", "ชุมนุม (ครูณัฐวุฒิ)"]
}

# --- 4. การจัดการหน้าตาเว็บแอป ---
st.set_page_config(page_title="ระบบบันทึกสถิติ ป.3", layout="centered")
st.title("📊 ระบบเช็คชื่อรายวันชั้น ป.3")
st.markdown("---")

selected_date = st.date_input("📅 เลือกวันที่ต้องการบันทึกสถิติ", datetime.date.today())

target_day = selected_date.strftime("%d")
target_month = selected_date.strftime("%m")
display_date_style = f"{target_day}/{target_month}/69"

st.info(f"🔍 ระบบกำลังล็อกเป้าหมายค้นหาคอลัมน์วันที่: **{display_date_style}**")

day_name = selected_date.strftime("%A")
if day_name in timetable:
    st.markdown(f"📚 **ตารางสอนประจำวัน {day_name}**")
    subjects_text = " ➡️ ".join(timetable[day_name])
    st.caption(subjects_text)
else:
    st.caption("📅 วันหยุดสุดสัปดาห์ (ไม่มีกิจกรรมการเรียนการสอน)")

st.markdown("---")

st.subheader("👥 เลือกสถานะการมาเรียน")
raw_attendance_input = {}

for student in students_list:
    col1, col2 = st.columns([3, 4])
    with col1:
        st.write(f"**เลขที่ {student['เลขที่']}** {student['ชื่อ']}")
    with col2:
        choice = st.radio(
            f"สถานะของเลขที่ {student['เลขที่']}",
            ["มาเรียน", "ขาดเรียน", "ลาป่วย", "ลากิจ", "วันหยุด"],
            key=f"st_{student['เลขที่']}",
            horizontal=True,
            label_visibility="collapsed"
        )
        raw_attendance_input[student['เลขที่']] = choice

st.markdown("---")

if st.button("🚀 อัปเดตข้อมูลลงชีต 'เช็คชื่อรายวัน'", type="primary", use_container_width=True):
    final_upload_values = []
    for student in students_list:
        user_choice = raw_attendance_input[student['เลขที่']]
        if user_choice == "มาเรียน": status_code = "1"
        elif user_choice == "ขาดเรียน": status_code = "ข"
        elif user_choice == "ลาป่วย": status_code = "ป"
        elif user_choice == "ลากิจ": status_code = "ล"
        elif user_choice == "วันหยุด": status_code = "ห"
        final_upload_values.append(status_code)

    if sheet:
        try:
            header_row = sheet.row_values(1)
            col_index = None
            
            # ใช้การค้นหาแบบตรวจจับตัวเลข วัน/เดือน เพื่อความแม่นยำสูงสุด
            pattern = f"^{target_day}/{target_month}/"
            
            for idx, cell_value in enumerate(header_row):
                if re.search(pattern, str(cell_value).strip()):
                    col_index = idx + 1
                    break
            
            if col_index:
                for idx, code_val in enumerate(final_upload_values):
                    row_index = idx + 2
                    sheet.update_cell(row_index, col_index, code_val)
                st.success(f"🎉 บันทึกข้อมูลลงในช่องวันที่คอลัมน์ลำดับที่ {col_index} ({display_date_style}) เรียบร้อยครบทั้ง 12 คนครับ!")
            else:
                st.error(f"❌ ไม่พบหัวคอลัมน์ที่ขึ้นต้นด้วยวันที่ '{target_day}/{target_month}/' ในแถวที่ 1 ของ Google Sheets")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการเข้าถึงข้อมูล: {e}")
    else:
        st.warning("⚠️ โปรแกรมรันในโหมดจำลอง (กรุณาตรวจสอบการตั้งค่า Secrets หลังบ้านของระบบ Streamlit Cloud ครับ)")