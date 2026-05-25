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
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/175dIXwMzn3RronYPV3qt_LpjZjqhtYV1BcmM0UVWpII/edit"
        return client.open_by_url(spreadsheet_url).worksheet("เช็คชื่อรายวัน")
    except Exception as e:
        st.error(f"ระบบตรวจพบข้อผิดพลาดในการเชื่อมต่อ: {e}")
        return None

sheet = init_connection()

# --- 2. ฐานข้อมูลรายชื่อนักเรียนชั้น ป.3 ---
students_list = [
    {"num": 1, "name": "เด็กชายกิตติพัฒน์ เกตุตุ้ม"},
    {"num": 2, "name": "เด็กชายธนาธิป พ้นภัย"},
    {"num": 3, "name": "เด็กชายธีรเมท บุญมี"},
    {"num": 4, "name": "เด็กชายอธิพันธ์ ดาวสุข"},
    {"num": 5, "name": "เด็กหญิงจิราวรรณ ทองบริบูรณ์"},
    {"num": 6, "name": "เด็กหญิงนัฐชา ไมเจริญ"},
    {"num": 7, "name": "เด็กหญิงนิชญาดา แงวกุดเรือ"},
    {"num": 8, "name": "เด็กหญิงวราริน มะลิวัน"},
    {"num": 9, "name": "เด็กหญิงศิริวรรณ จุลลา"},
    {"num": 10, "name": "เด็กหญิงสุตราพันธุ์ พูลศิลป์"},
    {"num": 11, "name": "เด็กชายศักดิ์สิทธิ์ โหยหวน"},
    {"num": 12, "name": "เด็กชายเทพทัต เขตตลาด"}
]

# --- 3. ข้อมูลตารางสอน ป.3 ---
timetable = {
    0: ["ภาษาไทย", "วิทยาศาสตร์", "ศิลปะ", "ลดเวลาเรียน", "สุขศึกษา"],
    1: ["English", "คณิตศาสตร์", "การงาน", "สังคม", "แนะแนว"],
    2: ["ภาษาไทย", "English", "คณิตศาสตร์", "ลูกเสือ", "สังคม", "English"],
    3: ["ภาษาไทย", "English", "English", "วิทยาศาสตร์", "หน้าที่พลเมือง"],
    4: ["English", "คณิตศาสตร์", "ประวัติ", "ลดเวลาเรียน", "ชุมนุม"]
}

day_th_names = {0: "จันทร์", 1: "อังคาร", 2: "พุธ", 3: "พฤหัสบดี", 4: "ศุกร์", 5: "เสาร์", 6: "อาทิตย์"}

# --- 4. การจัดการหน้าตาเว็บแอปพลิเคชัน ---
st.set_page_config(page_title="ระบบบันทึกสถิติ ป.3", layout="centered")
st.title("📊 ระบบเช็คชื่อรายวันชั้น ป.3")
st.markdown("---")

selected_date = st.date_input("📅 เลือกวันที่ต้องการบันทึกสถิติ", datetime.date.today())

target_day = selected_date.strftime("%d")
target_day_int = str(int(target_day))
target_month = selected_date.strftime("%m")
target_month_int = str(int(target_month))

display_date_style = f"{target_day_int}/{target_month_int}/69"
st.info(f"🔍 ระบบกำลังล็อกเป้าหมายค้นหาคอลัมน์วันที่: **{display_date_style}**")

weekday_num = selected_date.weekday()

if weekday_num in timetable:
    st.markdown(f"📚 **ตารางสอนชั้น ป.3 ประจำวัน{day_th_names[weekday_num]}**")
    subjects_text = " ➡️ ".join(timetable[weekday_num])
    st.caption(subjects_text)
else:
    st.caption(f"📅 วัน{day_th_names.get(weekday_num, 'หยุด')} (ไม่มีกิจกรรมการเรียนการสอน)")

st.markdown("---")

st.subheader("👥 เลือกสถานะการมาเรียน (นักเรียน 12 คน)")
raw_attendance_input = {}

for student in students_list:
    col1, col2 = st.columns([3, 4])
    with col1:
        st.write(f"**เลขที่ {student['num']}** {student['name']}")
    with col2:
        choice = st.radio(
            f"สถานะของเลขที่ {student['num']}",
            ["มาเรียน", "ขาดเรียน", "ลาป่วย", "ลากิจ", "วันหยุด"],
            key=f"st_p3_radio_{student['num']}",
            horizontal=True,
            label_visibility="collapsed"
        )
        raw_attendance_input[student['num']] = choice

st.markdown("---")

if st.button("🚀 อัปเดตข้อมูลลงชีต ป.3 'เช็คชื่อรายวัน'", type="primary", use_container_width=True):
    final_upload_values = []
    for student in students_list:
        user_choice = raw_attendance_input[student['num']]
        if user_choice == "มาเรียน": status_code = "1"
        elif user_choice == "ขาดเรียน": status_code = "ข"
        elif user_choice == "ลาป่วย": status_code = "ป"
        elif user_choice == "ลากิจ": status_code = "ล"
        elif user_choice == "วันหยุด": status_code = "ห"
        final_upload_values.append(status_code)

    if sheet:
        with st.spinner("กำลังบันทึกข้อมูลลง Google Sheets..."):
            try:
                header_row = sheet.row_values(1)
                col_index = None
                
                pattern = f"^0?{target_day_int}/0?{target_month_int}/"
                
                for idx, cell_value in enumerate(header_row):
                    if re.search(pattern, str(cell_value).strip()):
                        col_index = idx + 1
                        break
                
                if col_index:
                    # ปรับปรุง: แก้ไขให้ระบุเฉพาะเลขพิกัดตรงๆ เพื่อตัดปัญหาความผิดพลาดของ gspread เวอร์ชันเก่า
                    # (แถวเริ่มต้น, คอลัมน์เริ่มต้น, แถวสิ้นสุด, คอลัมน์สิ้นสุด)
                    cell_list = sheet.range(2, col_index, 13, col_index)
                    
                    for i, code_val in enumerate(final_upload_values):
                        cell_list[i].value = code_val
                    
                    sheet.update_cells(cell_list, value_input_option="USER_ENTERED")
                    
                    st.success(f"🎉 บันทึกสถิตินักเรียน ป.3 ลงใน Google Sheets เรียบร้อยครบถ้วนทั้ง 12 คนแล้วครับ!")
                else:
                    st.error(f"❌ ไม่พบหัวคอลัมน์วันที่ตรงกับวันที่คุณเลือกในแผ่นชีต ป.3 กรุณาตรวจสอบว่าบนกูเกิลชีตแถวที่ 1 มีวันที่นี้อยู่หรือไม่")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการส่งข้อมูล: {e}")
    else:
        st.warning("⚠️ ไม่สามารถเชื่อมต่อ Google Sheets ได้ กรุณาตรวจสอบสิทธิ์เข้าถึง")
