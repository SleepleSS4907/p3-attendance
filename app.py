import streamlit as st
import pandas as pd
import datetime
import re
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. ตั้งค่าการเชื่อมต่อ Google Sheets ---
def init_connection():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if os.path.exists("your-credentials.json"):
            creds = ServiceAccountCredentials.from_json_keyfile_name("your-credentials.json", scope)
        elif "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            return None
        client = gspread.authorize(creds)
        # ลิงก์ Google Sheet สำหรับ ชั้น ป.3
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/175dIXwMzn3RronYPV3qt_LpjZjqhtYV1BcmM0UVWpII/edit"
        return client.open_by_url(spreadsheet_url).worksheet("เช็คชื่อรายวัน")
    except Exception as e:
        st.error(f"ระบบตรวจพบข้อผิดพลาดในการเชื่อมต่อ: {e}")
        return None

sheet = init_connection()

# --- 2. ฐานข้อมูลรายชื่อนักเรียนชั้น ป.3 ---
students_list = [
    {"เลขที่": 1, "ชื่อ": "เด็กชายกฤษดา นามบุตร"},
    {"เลขที่": 2, "ชื่อ": "เด็กชายชัยภัทร ยอดพรม"},
    {"เลขที่": 3, "ชื่อ": "เด็กชายณัฐชนนท์ บุญเนตร"},
    {"เลขที่": 4, "ชื่อ": "เด็กชายธนวัฒน์ ศรีสะอาด"},
    {"เลขที่": 5, "ชื่อ": "เด็กชายนิติศาสตร์ ผาจวง"},
    {"เลขที่": 6, "ชื่อ": "เด็กชายนิพัทธ์ ร่อนแก้ว"},
    {"เลขที่": 7, "ชื่อ": "เด็กชายปัณณวิชญ์ ขวัญสุข"},
    {"เลขที่": 8, "ชื่อ": "เด็กชายพงศกร เจริญยิ่ง"},
    {"เลขที่": 9, "ชื่อ": "เด็กชายพัสกร ศรีงาม"},
    {"เลขที่": 10, "ชื่อ": "เด็กชายภาคิน คุ้มวงษ์"},
    {"เลขที่": 11, "ชื่อ": "เด็กชายภูริภัทร เสนอใจ"},
    {"เลขที่": 12, "ชื่อ": "เด็กชายเมธาสิทธิ์ เสนอใจ"},
    {"เลขที่": 13, "ชื่อ": "เด็กหญิงจริยา คุ้มวงษ์"},
    {"เลขที่": 14, "ชื่อ": "เด็กหญิงชลิตา วงษ์คำ"},
    {"เลขที่": 15, "ชื่อ": "เด็กหญิงญาณิศา ไกรพาน"},
    {"เลขที่": 16, "ชื่อ": "เด็กหญิงฐานิตา ยอดรักษ์"},
    {"เลขที่": 17, "ชื่อ": "เด็กหญิงณัฏฐ์ชญา ทิมจันทร์"},
    {"เลขที่": 18, "ชื่อ": "เด็กหญิงดวงกมล หล่อเลิศ"},
    {"เลขที่": 19, "ชื่อ": "เด็กหญิงทักษพร เอี่ยมยิ่ง"},
    {"เลขที่": 20, "ชื่อ": "เด็กหญิงปดิวรัดา นาสมใจ"},
    {"เลขที่": 21, "ชื่อ": "เด็กหญิงพิยดา เอี่ยมยิ่ง"},
    {"เลขที่": 22, "ชื่อ": "เด็กหญิงวรัญญา ขวัญสุข"}
]

# --- 3. ข้อมูลตารางสอน ป.3 ---
timetable = {
    "Monday": ["ภาษาไทย", "วิทยาศาสตร์", "ศิลปะ", "ลดเวลาเรียน", "สุขศึกษา"],
    "Tuesday": ["English", "คณิตศาสตร์", "การงาน", "สังคม", "แนะแนว"],
    "Wednesday": ["ภาษาไทย", "English", "คณิตศาสตร์", "ลูกเสือ", "สังคม", "English"],
    "Thursday": ["ภาษาไทย", "English", "English", "วิทยาศาสตร์", "หน้าที่พลเมือง"],
    "Friday": ["English", "คณิตศาสตร์", "ประวัติ", "ลดเวลาเรียน", "ชุมนุม"]
}

# --- 4. การจัดการหน้าตาเว็บแอปพลิเคชัน ---
st.set_page_config(page_title="ระบบบันทึกสถิติ ป.3", layout="centered")
st.title("📊 ระบบเช็คชื่อรายวันชั้น ป.3")
st.markdown("---")

selected_date = st.date_input("📅 เลือกวันที่ต้องการบันทึกสถิติ", datetime.date.today())

target_day = selected_date.strftime("%d")
target_day_int = str(int(target_day))
target_month = selected_date.strftime("%m")
target_month_int = str(int(target_month))

display_date_style = f"{target_day}/{target_month}/69"
st.info(f"🔍 ระบบกำลังล็อกเป้าหมายค้นหาคอลัมน์วันที่: **{display_date_style}**")

day_name = selected_date.strftime("%A")
if day_name in timetable:
    st.markdown(f"📚 **ตารางสอนชั้น ป.3 ประจำวัน {day_name}**")
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
            key=f"st_p3_{student['เลขที่']}",
            horizontal=True,
            label_visibility="collapsed"
        )
        raw_attendance_input[student['เลขที่']] = choice

st.markdown("---")

if st.button("🚀 อัปเดตข้อมูลลงชีต ป.3 'เช็คชื่อรายวัน'", type="primary", use_container_width=True):
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
            
            # ใช้ระบบค้นหาแบบยืดหยุ่น รองรับทั้ง 25/05/69, 25/5/69, 25/05/2569
            pattern = f"^0?{target_day_int}/0?{target_month_int}/"
            
            for idx, cell_value in enumerate(header_row):
                if re.search(pattern, str(cell_value).strip()):
                    col_index = idx + 1
                    break
            
            if col_index:
                for idx, code_val in enumerate(final_upload_values):
                    row_index = idx + 2
                    sheet.update_cell(row_index, col_index, code_val)
                st.success(f"🎉 บันทึกสถิตินักเรียน ป.3 ลงใน Google Sheets เรียบร้อยครบถ้วนทั้ง 22 คนแล้วครับ!")
            else:
                st.error(f"❌ ไม่พบหัวคอลัมน์วันที่ที่ตรงกับ '{display_date_style}' ในแผ่นชีต ป.3 กรุณาตรวจสอบแถวที่ 1 ใน Sheets ครับ")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการเข้าถึงข้อมูล: {e}")
    else:
        st.warning("⚠️ ไม่สามารถเชื่อมต่อ Google Sheets ได้")
