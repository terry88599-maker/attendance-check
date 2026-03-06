import streamlit as st
import csv
import os
from datetime import datetime
import json
import pandas as pd
from streamlit_option_menu import option_menu

# 访问密码验证
def check_access():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 街舞考勤系统 - 登录")
        password = st.text_input("请输入访问密码", type="password")
        if st.button("登录", type="primary"):
            if password == "123456":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("密码错误，请重试")
        st.stop()

check_access()

# 页面配置 - 适配移动端（iPhone 13 Pro）
st.set_page_config(
    page_title="街舞考勤",
    page_icon="💃",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 全局样式 - 简洁版（适配移动端+电脑端）
st.markdown("""
<style>
/* 基础响应式设置 */
html, body, [class*="css"] {
    font-size: clamp(14px, 4vw, 16px);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 移动端适配 */
@media (max-width: 768px) {
    .mobile-col {flex-direction: column !important;}
    .mobile-btn {font-size: 18px !important; padding: 0.8rem 1rem !important;}
    .mobile-input {font-size: 18px !important; padding: 0.8rem !important;}
}

@media (min-width: 769px) {
    .mobile-col {flex-direction: row !important;}
}

/* 标题样式 */
h1 {font-size: clamp(22px, 5vw, 24px) !important; font-weight: 700 !important; color: white !important;}
h2 {font-size: clamp(18px, 4.5vw, 20px) !important; font-weight: 600 !important; color: white !important;}

/* 页面容器 */
div.block-container { 
    padding: 0.5rem 5% 2rem 5% !important;
    max-width: 100%;
    background-color: #0E1117;
}

/* 按钮样式 */
div.stButton > button { 
    width: 100%; 
    font-size: clamp(16px, 4vw, 18px) !important;
    padding: clamp(0.6rem, 3vw, 0.8rem) clamp(1rem, 4vw, 1.2rem) !important;
    border-radius: 12px !important;
    background-color: #262730 !important;
    color: white !important;
    border: 1px solid #4169E1 !important;
    margin-bottom: 0.5rem !important;
}
div.stButton > button[kind="primary"] {background-color: #4169E1 !important; border: none !important;}

/* 输入框/选择框样式 */
.stTextInput > div > div > input,
.stSelectbox > div > div > select {
    font-size: clamp(16px, 4vw, 18px) !important;
    background-color: #262730 !important;
    color: white !important;
    border: 1px solid #444 !important;
    border-radius: 12px !important;
    padding: clamp(0.6rem, 3vw, 0.8rem) !important;
}

/* 复选框样式 */
.stCheckbox > label {font-size: clamp(16px, 4vw, 18px) !important; color: white !important; padding: 0.5rem 0 !important;}

/* 信息框样式 */
.stInfo, .stSuccess, .stError {
    font-size: clamp(14px, 3.5vw, 15px) !important;
    padding: 1rem !important;
    border-radius: 12px !important;
    margin-bottom: 1rem !important;
}
.stSuccess {background-color: #1E3A2F !important; color: #4ADE80 !important; border: 1px solid #4ADE80 !important;}

/* 隐藏默认元素 */
#MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 基础配置（仅保留一个班级）
CSV_FILE = "dance_student_records.csv"
STUDENT_CONFIG_FILE = "dance_students.json"
CLASS_NAME = "少儿 Locking（周五）"  # 唯一班级名称
PRICE_PER_PERSON = 80

# 初始化数据文件（增强健壮性，强制覆盖旧配置）
def init_files():
    # 初始化考勤记录文件
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(["日期", "班级", "学生姓名", "是否到课"])
    
    # 强制初始化/重置学员配置文件（覆盖旧文件，确保班级名匹配）
    default_config = {
        CLASS_NAME: {
            "students": [
                "陆语晨", "吴浩宇", "金心悦", "黄彦祺", 
                "朱逸宸", "李俊昊", "侯夕妍", "詹宗瑜", 
                "蒿承越", "刘橙宣", "金昱阳"
            ],
            "color": "#4169E1"
        }
    }
    # 不管文件是否存在，都重新写入正确的配置（解决KeyError问题）
    with open(STUDENT_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=2)

def get_student_config():
    init_files()  # 每次获取配置前都确保文件是最新的
    with open(STUDENT_CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_student_config(config):
    with open(STUDENT_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# 删除单条考勤记录
def delete_record(date, student):
    records = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if not (row["日期"] == date and row["班级"] == CLASS_NAME and row["学生姓名"] == student):
                records.append(row)
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["日期", "班级", "学生姓名", "是否到课"])
        writer.writeheader()
        writer.writerows(records)

# 删除指定日期的全部考勤记录
def delete_batch_records(date_str):
    records = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if not (row["日期"] == date_str and row["班级"] == CLASS_NAME):
                records.append(row)
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["日期", "班级", "学生姓名", "是否到课"])
        writer.writeheader()
        writer.writerows(records)

# 导入考勤记录
def import_attendance_csv(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
        required_cols = ["日期", "班级", "学生姓名", "是否到课"]
        if not all(col in df.columns for col in required_cols):
            return False, "CSV列名错误！需包含：日期、班级、学生姓名、是否到课"
        df.to_csv(CSV_FILE, index=False, encoding='utf-8')
        return True, "考勤记录导入成功！"
    except Exception as e:
        return False, f"导入失败：{str(e)}"

# 导入学员信息
def import_student_json(uploaded_file):
    try:
        config = json.load(uploaded_file)
        if CLASS_NAME not in config:
            return False, f"JSON格式错误！需包含「{CLASS_NAME}」配置"
        save_student_config(config)
        return True, "学员信息导入成功！"
    except Exception as e:
        return False, f"导入失败：{str(e)}"

# 主逻辑执行
init_files()
config = get_student_config()
# 增加容错：即使配置读取异常，也能获取到正确的学员列表
students = config.get(CLASS_NAME, {}).get("students", [
    "陆语晨", "吴浩宇", "金心悦", "黄彦祺", 
    "朱逸宸", "李俊昊", "侯夕妍", "詹宗瑜", 
    "蒿承越", "刘橙宣", "金昱阳"
])

# ===================== 顶部导航栏（简化版） =====================
with st.container():
    page = option_menu(
        menu_title=None,
        options=["首页", "考勤", "学员", "统计", "追踪", "记录", "备份"],
        icons=["house", "pencil", "people", "bar-chart", "search", "trash", "cloud"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0.4rem !important", "background-color": "#1E1E1E", "border-radius": 10, "margin-bottom": "1rem", "border": "1px solid #333"},
            "icon": {"color": "#666", "font-size": "14px"},
            "nav-link": {"font-size": "13px", "text-align": "center", "margin": "0 2px", "--hover-color": "#4169E1", "padding": "8px 8px", "border-radius": "6px", "color": "#999"},
            "nav-link-selected": {"background-color": "#4169E1", "color": "white", "font-weight": "600"}
        }
    )

# ------------------- 1. 首页（简化版） -------------------
if page == "首页":
    st.title(f"🎉 {CLASS_NAME} 考勤系统")
    
    # 功能卡片（单列/双列自适应）
    st.markdown('<div class="mobile-col" style="display: flex; gap: 1rem; width: 100%;">', unsafe_allow_html=True)
    col1 = st.container()
    with col1:
        with st.container(border=True):
            st.markdown(f"""
            <div style="text-align: center; padding: 15px;">
                <div style="font-size: clamp(24px, 6vw, 28px); margin-bottom: 8px;">📝</div>
                <div style="font-weight: 600; color: #60A5FA; margin-bottom: 4px; font-size: clamp(16px, 4vw, 18px);">考勤录入</div>
                <div style="font-size: clamp(12px, 3vw, 13px); color: #888;">快速记录学员到课情况</div>
            </div>
            """, unsafe_allow_html=True)
            
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; padding: 15px;">
                <div style="font-size: clamp(24px, 6vw, 28px); margin-bottom: 8px;">👥</div>
                <div style="font-weight: 600; color: #60A5FA; margin-bottom: 4px; font-size: clamp(16px, 4vw, 18px);">学员管理</div>
                <div style="font-size: clamp(12px, 3vw, 13px); color: #888;">添加、修改、删除学员</div>
            </div>
            """, unsafe_allow_html=True)
            
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; padding: 15px;">
                <div style="font-size: clamp(24px, 6vw, 28px); margin-bottom: 8px;">📊</div>
                <div style="font-weight: 600; color: #60A5FA; margin-bottom: 4px; font-size: clamp(16px, 4vw, 18px);">月度统计</div>
                <div style="font-size: clamp(12px, 3vw, 13px); color: #888;">查看月度考勤报表</div>
            </div>
            """, unsafe_allow_html=True)
    
    col2 = st.container()
    with col2:
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; padding: 15px;">
                <div style="font-size: clamp(24px, 6vw, 28px); margin-bottom: 8px;">🔍</div>
                <div style="font-weight: 600; color: #60A5FA; margin-bottom: 4px; font-size: clamp(16px, 4vw, 18px);">学生追踪</div>
                <div style="font-size: clamp(12px, 3vw, 13px); color: #888;">查询个人考勤记录</div>
            </div>
            """, unsafe_allow_html=True)
            
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; padding: 15px;">
                <div style="font-size: clamp(24px, 6vw, 28px); margin-bottom: 8px;">🗑️</div>
                <div style="font-weight: 600; color: #60A5FA; margin-bottom: 4px; font-size: clamp(16px, 4vw, 18px);">记录管理</div>
                <div style="font-size: clamp(12px, 3vw, 13px); color: #888;">删除错误考勤记录</div>
            </div>
            """, unsafe_allow_html=True)
            
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; padding: 15px;">
                <div style="font-size: clamp(24px, 6vw, 28px); margin-bottom: 8px;">💾</div>
                <div style="font-weight: 600; color: #60A5FA; margin-bottom: 4px; font-size: clamp(16px, 4vw, 18px);">数据备份</div>
                <div style="font-size: clamp(12px, 3vw, 13px); color: #888;">导入导出数据文件</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.success("👆 请点击顶部导航选择功能")

# ------------------- 2. 考勤录入（简化版，仅一个班级） -------------------
elif page == "考勤":
    st.title(f"📝 {CLASS_NAME} 考勤录入")
    
    # 仅选择日期，无需选择班级
    selected_date = st.date_input("选择日期", datetime.now(), key="att_date")
    date_str = selected_date.strftime("%Y-%m-%d")
    
    st.markdown(f"**{CLASS_NAME}** 共 {len(students)} 人")
    st.markdown("---")
    
    # 修复：移除私有属性，改用自适应列数（移动端1列，电脑端2列）
    # 兼容所有Streamlit版本的写法
    cols = st.columns(2)  # 固定2列，移动端会自动堆叠
    
    attended_students = []
    for idx, name in enumerate(students):
        with cols[idx % 2]:
            if st.checkbox(name, key=f"stu_{name}"):
                attended_students.append(name)

    st.markdown("---")
    st.info(f"✅ 已到课：{len(attended_students)} 人 | ❌ 缺课：{len(students)-len(attended_students)} 人")

    if st.button("💾 保存考勤记录", type="primary"):
        delete_batch_records(date_str)
        rows = [[date_str, CLASS_NAME, s, "1" if s in attended_students else "0"] for s in students]
        with open(CSV_FILE, 'a', encoding='utf-8', newline='') as f:
            csv.writer(f).writerows(rows)
        st.success(f"✅ 保存成功！{CLASS_NAME} {date_str} 到课 {len(attended_students)} 人")

# ------------------- 3. 学员管理（简化版，仅一个班级） -------------------
elif page == "学员":
    st.title(f"👥 {CLASS_NAME} 学员管理")
    
    tab1, tab2, tab3 = st.tabs(["➕ 新增", "✏️ 改名", "🗑️ 删除"])
    
    with tab1:
        st.markdown("### 添加新学员")
        new_stu = st.text_input("学员姓名", key="add_stu", placeholder="请输入姓名")
        
        if st.button("➕ 添加学员", use_container_width=True):
            if new_stu.strip() and new_stu not in students:
                config[CLASS_NAME]["students"].append(new_stu)
                save_student_config(config)
                st.success(f"✅ 已添加「{new_stu}」到{CLASS_NAME}")
                st.rerun()
            elif new_stu in students:
                st.error(f"❌ {CLASS_NAME} 已有学员「{new_stu}」")
    
    with tab2:
        st.markdown("### 修改学员姓名")
        old_name = st.text_input("原姓名", key="edit_old", placeholder="输入要修改的姓名")
        new_name = st.text_input("新姓名", key="edit_new", placeholder="输入新姓名")
        
        if st.button("✏️ 确认修改", use_container_width=True):
            if old_name in students and new_name.strip():
                idx = students.index(old_name)
                config[CLASS_NAME]["students"][idx] = new_name
                save_student_config(config)
                st.success(f"✅ 已将「{old_name}」改为「{new_name}」")
                st.rerun()
            else:
                st.error("❌ 学员不存在或新姓名为空")
    
    with tab3:
        st.markdown(f"### {CLASS_NAME} 学员列表（共{len(students)}人）")
        if students:
            for name in students:
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.write(f"👤 {name}")
                with col_b:
                    if st.button("🗑️ 删除", key=f"del_{name}"):
                        config[CLASS_NAME]["students"].remove(name)
                        save_student_config(config)
                        st.rerun()
        else:
            st.info("该班级暂无学员")

# ------------------- 4. 月度统计（简化版，仅一个班级） -------------------
elif page == "统计":
    st.title(f"📊 {CLASS_NAME} 月度统计")
    
    year = st.text_input("年份", value=str(datetime.now().year), key="stat_year")
    month = st.text_input("月份", value=str(datetime.now().month), key="stat_month")
    
    if st.button("🔍 查询统计", type="primary", use_container_width=True):
        if year.isdigit() and month.isdigit():
            ym = f"{year}-{month.zfill(2)}"
            all_records = []
            if os.path.exists(CSV_FILE):
                with open(CSV_FILE, encoding='utf-8') as f:
                    all_records = [r for r in csv.DictReader(f) if r["日期"].startswith(ym) and r["班级"] == CLASS_NAME]
            
            ok_records = [r for r in all_records if r["是否到课"] == "1"]
            total = len(ok_records)
            
            # 统计卡片
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1E3A2F 0%, #2D5A3D 100%); 
                        padding: 25px; border-radius: 15px; text-align: center; 
                        margin: 20px 0; border: 1px solid #4ADE80;">
                <div style="font-size: clamp(12px, 3vw, 14px); color: #4ADE80; margin-bottom: 10px;">{ym} 月度总到课</div>
                <div style="font-size: clamp(36px, 10vw, 48px); font-weight: bold; color: #4ADE80; margin-bottom: 5px;">{total}</div>
                <div style="font-size: clamp(14px, 4vw, 16px); color: #4ADE80;">人次</div>
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #4ADE8055;">
                    <div style="font-size: clamp(12px, 3vw, 14px); color: #4ADE80AA;">课时费收入</div>
                    <div style="font-size: clamp(24px, 8vw, 32px); font-weight: bold; color: #FFD700;">¥{total*PRICE_PER_PERSON}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ------------------- 5. 学生追踪（简化版） -------------------
elif page == "追踪":
    st.title(f"🔍 {CLASS_NAME} 学生考勤追踪")
    
    selected_stu = st.selectbox("选择学生", students, key="track_stu")
    
    if st.button("🔍 查询记录", type="primary", use_container_width=True):
        records = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, encoding='utf-8') as f:
                records = [r for r in csv.DictReader(f) if r["学生姓名"] == selected_stu and r["班级"] == CLASS_NAME and r["是否到课"] == "1"]
        
        # 统计卡片
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1E2A4A 0%, #2D3A5A 100%); 
                    padding: 25px; border-radius: 15px; text-align: center; 
                    margin: 20px 0; border: 1px solid #4169E1;">
            <div style="font-size: clamp(14px, 4vw, 16px); color: #888; margin-bottom: 10px;">{selected_stu} 累计到课</div>
            <div style="font-size: clamp(40px, 10vw, 56px); font-weight: bold; color: #4169E1;">{len(records)}</div>
            <div style="font-size: clamp(14px, 4vw, 16px); color: #888;">次</div>
        </div>
        """, unsafe_allow_html=True)
        
        if records:
            st.markdown("### 详细记录")
            for r in sorted(records, key=lambda x: x['日期'], reverse=True):
                with st.container(border=True):
                    st.write(f"📅 {r['日期']} | 📍 {CLASS_NAME}")
        else:
            st.info("暂无考勤记录")

# ------------------- 6. 记录管理（简化版） -------------------
elif page == "记录":
    st.title(f"🗑️ {CLASS_NAME} 考勤记录管理")
    
    # 筛选条件（简化）
    date_filter = st.text_input("日期筛选（如：2026-03）", key="rec_date_filter")
    show_type = st.radio("显示类型", ["到课", "缺课", "全部"], index=0, horizontal=False, key="show_type")
    
    # 加载记录
    records = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["班级"] != CLASS_NAME:
                    continue
                if date_filter and not row["日期"].startswith(date_filter):
                    continue
                if show_type == "到课" and row["是否到课"] != "1":
                    continue
                if show_type == "缺课" and row["是否到课"] != "0":
                    continue
                records.append(row)
    
    st.info(f"📋 共找到 {len(records)} 条记录")
    
    if records:
        for idx, r in enumerate(sorted(records, key=lambda x: x['日期'], reverse=True)):
            with st.container(border=True):
                col1, col2 = st.columns([3, 2])
                with col1: 
                    st.write(f"📅 {r['日期']} | 👤 {r['学生姓名']}")
                with col2: 
                    if r["是否到课"] == "1":
                        st.markdown("<span style='color: #4ADE80;'>🟢 到课</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='color: #FF6B6B;'>🔴 缺课</span>", unsafe_allow_html=True)
                # 删除按钮
                if st.button("🗑️ 删除本条记录", key=f"del_rec_{idx}", use_container_width=True):
                    delete_record(r["日期"], r["学生姓名"])
                    st.success("已删除")
                    st.rerun()
    else:
        st.info("暂无符合条件的考勤记录")

# ------------------- 7. 数据备份（简化版） -------------------
elif page == "备份":
    st.title(f"💾 {CLASS_NAME} 数据备份与恢复")
    
    # 导出备份
    st.markdown("### 📤 导出数据")
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "rb") as f:
            st.download_button(
                label="📄 下载考勤记录 (CSV)",
                data=f,
                file_name=f"{CLASS_NAME}_考勤记录_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    if os.path.exists(STUDENT_CONFIG_FILE):
        with open(STUDENT_CONFIG_FILE, "rb") as f:
            st.download_button(
                label="👥 下载学员信息 (JSON)",
                data=f,
                file_name=f"{CLASS_NAME}_学员信息_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    st.markdown("---")
    
    # 导入恢复
    st.markdown("### 📥 导入数据")
    st.warning("⚠️ 警告：导入会覆盖现有数据，请先备份！")
    
    csv_file = st.file_uploader("上传考勤记录 CSV 文件", type=["csv"], key="import_csv")
    if st.button("📥 导入考勤记录", use_container_width=True):
        if csv_file:
            success, msg = import_attendance_csv(csv_file)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    
    json_file = st.file_uploader("上传学员信息 JSON 文件", type=["json"], key="import_json")
    if st.button("📥 导入学员信息", use_container_width=True):
        if json_file:
            success, msg = import_student_json(json_file)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
