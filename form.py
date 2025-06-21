import streamlit as st
import time
import datetime
import qrcode
import sqlite3
import os
import pandas as pd
from logic import save_application, init_db, db_path, is_existing_chip, premium_calculation_private_dog, premium_calculation_public_dog
from streamlit.runtime.scriptrunner.script_runner import RerunException, RerunData

def rerun():
    raise RerunException(RerunData())

def show_db_contents(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * From application", conn)
    conn.close()
    st.markdown("### 📊 檢視目前所有申請紀錄")
    st.dataframe(df)

def run_form():
    # 1. 兼容拿 query-params（只用 st.query_params 足矣）
    params = st.query_params

    # 2. 提取 secret_code
    raw = params.get("veryveryverysecretcode", None)
    if isinstance(raw, list):
        secret_code = raw[0]
    else:
        secret_code = raw

    # 3. Debug 输出
    # st.write("🔍 Debug — Query Params:", params)
    # st.write("🔑 Debug — secret_code:", secret_code)

    # 4. 初始化数据库
    init_db(db_path)

    # 5. 管理员模式
    if secret_code == "kaiwaho":
        st.success("🔑 管理员模式生效")
        show_db_contents(db_path)
        if st.button("🔄 重置資料庫"):
            os.remove(db_path)
            init_db(db_path)
            st.success("✅ 已重置資料庫")
        with open(db_path, "rb") as f:
            st.download_button("📥 下載 application.db", f.read(), "application.db")
        return



    col1, col2 = st.columns([2, 1])
    col1.markdown("## 🐾 挑選 Pet Pet 嘅照顧方式 ")
    plan_type = col2.selectbox(
        "照顧方式：",
        ["請先選擇…", "🍁 公立舒心組", "🛡️ 私家無憂組"],
        key="plan_type"
    )
    if plan_type == "請先選擇…":
        st.info("📌 請先從上方下拉框選擇方案類型")
        st.caption("注：")
        st.caption("• 🍁 公立舒心組：只享用公立政府獸醫的專屬優惠")
        st.caption("• 🛡️ 私家無憂組：享有公立政府獸醫 100% 優惠，還有私立獸醫額外福利")
        return
    pet_type = st.radio("請問你嘅Pet Pet喺？", ["汪汪！ 🐶", "喵喵！ 🐱（暫不開放！）"], key = 'pet_type') 

    if pet_type == "汪汪！ 🐶":
        render_dog_plan(plan_type, pet_type)
    else:
        render_cat_plan(plan_type, pet_type)

# 多選勾選框函式
def multi_checkbox(options: dict[str, str], cols: int = 2) -> list[str]:
    selected = []
    col_objs = st.columns(cols)
    for i, (opt, hint) in enumerate(options.items()):
        c = col_objs[i % cols]
        with c:
            checked = st.checkbox(f"✨ {opt}", key=f"chk_{opt}")
            st.caption(hint)
            if checked:
                selected.append(opt)
    return selected

# 主表單
def render_dog_plan(plan_type, pet_type):
    st.markdown("# 🐶🐱 摸Pet Pet Club 申請表 🐾")
    st.write("🐾 嘿！歡迎加入 **摸Pet Pet Club** 🎉，下面填返你同你 Pet Pet 嘅資料啦！")

    owner = st.text_input("👤 Pet爸Pet媽，請輸入您嘅名：", placeholder="例：大佬")
    pet_name = st.text_input("🐾 Pet Pet的小名：", placeholder="例：豆豆")

    chipped = st.text_input("🔖 Pet Pet嘅晶片號碼：（無就填NA）")
    if chipped and is_existing_chip(chipped, db_path):
        st.warning("⚠️ 呢嗰晶片已經存在喇，試下填另一個先～")
    phone = st.text_input("📞 聯絡電話（必填）", placeholder="例：63212345")
    email = st.text_input("✉️ 電郵地址（必填）", placeholder="例：abc@xxx.com")
    wechat_id = st.text_input("💬 Wechat ID（建議）")
    
    st.markdown("### 🐥 基本資訊")
    pet_sex = st.radio("Pet Pet 嘅性別？", ['男仔', '女仔']) 
    breeds = {
        "汪汪！ 🐶":  [
                    "1. 博美犬", "2. 約克夏㹴", "3. 比熊犬", "4. 貴賓犬（泰迪犬）", "5. 雪納瑞", "6. 柴犬", "7. 法國鬥牛犬", "8. 巴哥犬", "9. 金毛尋回犬", "10. 拉布拉多尋回犬",
                    "11. 雪橇犬（哈士奇）", "12. 馬爾濟斯犬", "13. 喜樂蒂牧羊犬", "14. 邊境牧羊犬", "15. 臘腸犬", "16. 北京犬", "17. 西施犬", "18. 英國鬥牛犬", "19. 德國牧羊犬", "20. 柯基犬",
                    "21. 吉娃娃", "22. 巴仙吉犬", "23. 迷你杜賓犬", "24. 羅威納犬", "25. 牛頭㹴", "26. 美國可卡犬", "27. 英國可卡犬", "28. 大白熊犬", "29. 斗牛獒犬", "30. 大丹犬",
                    "31. 松獅犬", "32. 比特犬", "33. 阿拉斯加雪橇犬", "34. 萊卡犬", "35. 比利時瑪連萊犬", "36. 古代英國牧羊犬", "37. 波士頓㹴", "38. 威爾斯㹴", "39. 拉薩犬", "40. 波音達犬",
                    "41. 萨摩耶犬", "42. 中亞牧羊犬", "43. 西藏獒犬", "44. 阿富汗獵犬", "45. 葡萄牙水犬", "46. 布偶犬", "47. 芬蘭拉普杭犬", "48. 捷克狼犬", "49. 俄羅斯獵狼犬", "50. 蘇俄獵狼犬",
                    "51. 墨西哥無毛犬", "52. 西班牙獵犬", "53. 義大利靈緹", "54. 鬆獅犬", "55. 法老王犬", "56. 狒狒犬（沙皮犬）", "57. 獒犬", "58. 瑞士白牧羊犬", "59. 蘇格蘭牧羊犬", "60. 澳大利亞牧羊犬",
                    "61. 澳洲絲毛㹴", "62. 黑俄羅斯㹴", "63. 哈瓦那犬", "64. 波利犬", "65. 巴吉度獵犬", "66. 挪威糜犬", "67. 芬蘭狐狸犬", "68. 愛爾蘭雪達犬", "69. 愛爾蘭獵狼犬", "70. 丹迪丁蒙㹴",
                    "71. 史賓格獵犬", "72. 布列塔尼獵犬", "73. 萊卡犬", "74. 德國剛毛指示犬", "75. 德國短毛指示犬", "76. 紐芬蘭犬", "77. 愛斯基摩犬", "78. 博比犬", "79. 克倫伯獵犬", "80. 可蒙犬",
                    "81. 小型雪納瑞", "82. 愛爾蘭㹴", "83. 萊州紅犬", "84. 荷蘭毛獵犬", "85. 西藏獵犬", "86. 卡斯羅犬", "87. 小獵兔犬", "88. 英國獵狐犬", "89. 西班牙加納利犬", "90. 赫瑞亞犬",
                    "91. 巴森吉犬", "92. 阿金廷杜告犬", "93. 蘭伯格犬", "94. 西高地白㹴", "95. 蘇格蘭㹴", "96. 捲毛獵犬", "97. 義大利指示犬", "98. 瑞典狐狸犬", "99. 泰國脊背犬", "100. 格雷伊獵犬",
                    "101. 其他"
                ],
    }

    neuter = st.radio(f"Pet Pet 絕育了嗎？：", ["是", "否"], key = 'neuter')
    pet_idx = ["汪汪🐶", "喵喵🐱"]
    breed = st.selectbox(f"✨ 選擇您家{pet_idx}嘅品種：", breeds)
    if breed == "101. 其他":
        breed = st.text_input("請輸入 Pet Pet 嘅品種：")
    
    color = st.color_picker("🖌️ 選擇標記顏色", "#FF0000")
    st.write(f"你選擇的顏色是：**{color}**")
    st.markdown(
        f"<div style='width:100px;height:30px;background-color:{color}; border:1px solid #000'></div>",
        unsafe_allow_html=True
    )



    dob = st.date_input(
        "🎂 Pet Pet 嘅出生日期：",
        min_value=datetime.date(1990,1,1),
        max_value=datetime.date.today(),
        key="dob"
    )
    today = datetime.date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    st.write(f"🐥 Pet Pet而家：**{age}** 歲囉！")
    weight_input = st.text_input("⚖️ Pet Pet體重（kg）：", placeholder="例：5.2")

    q1 = st.radio(
        "① 過去90天內，您的寵物是否曾因意外或患病接受或需要接受治療？",
        ["Yes/是", "No/否"],
        key="q1"
    )
    # 如果第1題選 Yes，就顯示詳情欄
    medical_history = ""
    if q1 == "Yes/是":
        medical_history = st.text_area(
            "請提供病歷詳情（診斷、治療建議…等）",
            key="medical_history"
        )

    q2 = st.radio(
        "② 若第①題為「Yes」，您的寵物現在是否仍在接受觀察/治療？",
        ["Yes/是", "No/否"],
        key="q2"
    )
    q3 = st.radio(
        "③ 您的寵物是否曾接受任何手術（除絕育外）？",
        ["Yes/是", "No/否"],
        key="q3"
    )
    q4 = st.radio(
        "④ 過去5年內，您的寵物是否有攻擊傾向或咬傷他人/動物？",
        ["Yes/是", "No/否"],
        key="q4"
    )
    q5 = st.radio(
        "⑤ 您的寵物是否有任何身體缺陷或殘疾？",
        ["Yes/是", "No/否"],
        key="q5"
    )

    
    try:
        weight = float(weight_input)
        weight_valid = True
    except ValueError:
        weight_valid = False
        
    st.markdown("### 📝 選擇需要的福利 (可多選)")
    cover_options = {"診金": "常規診療、門診費用補助，我哋預每個月一次基本既門診費同複診費！",
                    "狂犬病預防疫苗（每劑）": "預每年一針！",
                    "DHPPiL 五合一": "預每年一針！",
                    "冠狀病毒疫苗": "預每年一針！",
                    "萊姆病疫苗": "預每年一針！",
                    "犬咳（Bordetella）": "預每年一針！"}

    covered = multi_checkbox(cover_options, cols = 1)
    cover_consultation   = "診金" in covered
    cover_rabies_vax     = "狂犬病預防疫苗（每劑）" in covered
    cover_dhppil         = "DHPPiL 五合一"       in covered
    cover_corona_vax     = "冠狀病毒疫苗"        in covered
    cover_lyme_vax       = "萊姆病疫苗"          in covered
    cover_bordetella     = "犬咳（Bordetella）"   in covered

    st.markdown("### 🌟 選擇方案")
    deductible_rate_map = {
        "請選擇…": None,
        "🍀 綠意款": 0.10,
        "🌸 櫻花款": 0.15,
        "🎉 戰鼓款": 0.20,
    }
    reimbursement_rate_map = {
        "請選擇…": None,
        "🍁 楓葉款 - 70%": 0.70,      
        "❄️ 冰晶款 - 80%": 0.80,
        "🌻 向陽款 - 90%": 0.90
    }
    deductible_option = st.selectbox(
            "⚙️ 請選擇您的免賠比例：",
            [*deductible_rate_map.keys()],
            key="deductible_rate",
            help = "🍀 綠意款係最高級，🌸 櫻花款喺中級，🎉 戰鼓款喺普通款\n" \
                   "\n 如果係普通款，手術費喺MOP 1000，自付額大嘅係 MOP 200；如果係最高級，自付額大嘅係 MOP 100"
        )

    reimbursement_option = st.selectbox(
            "🛎 請選擇您的理賠比例：",
            [*reimbursement_rate_map.keys()],
            key="reimbursement_rate",
        )
    
    deductible_rate = deductible_rate_map[deductible_option]
    reimbursement_rate = reimbursement_rate_map[reimbursement_option]

    term = st.selectbox(
        "⏰ 繳費期數（選一個最適合你哋）：", 
        [3, 6, 12], 
        format_func=lambda x: {
        3: "小季輕付（每 3 個月）",
        6: "半載悠遊（每 6 個月）",
        12: "全年安心（每 12 個月）"
        }[x],
        help = '越長嘅會員期，手續費越少，12個月直接免會員費！',
        key="term"
    )
    if deductible_rate is None or reimbursement_rate is None:
        st.info("請先選擇「自付方案」與「理賠方案」！")
    else:
        if plan_type == "🍁 公立舒心組":
            total_monthly_premium, extra_premium, total_extra_premium = premium_calculation_public_dog(
                weight=weight,
                age=age,
                term=term,
                deductible_rate=deductible_rate,
                reimbursement_rate=reimbursement_rate,
                cover_consultation=cover_consultation,
                cover_rabies_vax=cover_rabies_vax,
                cover_dhppil=cover_dhppil,
                cover_corona_vax=cover_corona_vax,
                cover_lyme_vax=cover_lyme_vax,
                cover_bordetella=cover_bordetella,
            )
            monthly_premium = total_monthly_premium/term
        else:
            total_monthly_premium, extra_premium, total_extra_premium = premium_calculation_private_dog(
                weight=weight,
                age=age,
                term=term,
                deductible_rate=deductible_rate,
                reimbursement_rate=reimbursement_rate,
                cover_consultation=cover_consultation,
                cover_rabies_vax=cover_rabies_vax,
                cover_dhppil=cover_dhppil,
                cover_corona_vax=cover_corona_vax,
                cover_lyme_vax=cover_lyme_vax,
                cover_bordetella=cover_bordetella,
            )
            monthly_premium = total_monthly_premium/term

    effective_date = st.date_input(
        "會員生效日期：",
        min_value = datetime.date.today(),
        max_value = datetime.date(2030, 12, 31),
        key = 'effective_date'
    )

    submitted = st.button("💌 立即送出，成為俱樂部一員，保護Pet Pet")
    comment = st.text_area("💬 其他留言或建議（選填）", help="留下您對 Club 嘅想法、建議都好 😊")
    if submitted:
        errors = []

        # 1. 基本文本输入
        if not owner:
            errors.append("👤 Pet Pet主人姓名")
        if not pet_name:
            errors.append("🐾 Pet Pet名字")
        if not chipped:
            errors.append("🔖 晶片號碼")
        if not phone:
            errors.append("📞 聯絡電話")
        if not email or '@' not in email:
            errors.append("✉️ 有效電郵地址")
        if not wechat_id:
            errors.append("💬 Wechat ID（雖然可選，但建議填寫）")

        # 2. 性别 & 絕育
        if pet_sex not in ['男仔', '女仔']:
            errors.append("⚥ 請選擇 Pet Pet 嘅性別")
        if neuter not in ['是', '否']:
            errors.append("🔪 請選擇 Pet Pet 是否絕育")

        # 3. 品種
        if not breed:
            errors.append("🐶🐱 Pet Pet 品種")

        # 4. 體重
        if not weight_input or not weight_valid:
            errors.append("⚖️ 請輸入有效嘅體重（例如 5.2）")

        # 5. 問卷 q1–q5
        if q1 not in ["Yes/是", "No/否"]:
            errors.append("① 過去90天內治療狀況")
        if q1 == "Yes/是" and not medical_history:
            errors.append("請提供病歷詳情（第①題選 Yes 時必填）")
        for idx, q in enumerate([q2, q3, q4, q5], start=2):
            if q not in ["Yes/是", "No/否"]:
                errors.append(f"第 {idx} 題問卷未填或格式錯誤")

        # 6. 標記顏色
        if not color:
            errors.append("🖌️ 請選擇一個標記顏色")

        # 7. 生效日期
        if not effective_date:
            errors.append("⏳ 請選擇會員生效日期")

        # 8. 保單方案 & 費率選擇
        if plan_type not in ["🍁 公立舒心組", "🛡️ 私家無憂組"]:
            errors.append("🌟 請選擇「照顧方式」")
        if deductible_option not in deductible_rate_map or deductible_rate is None:
            errors.append("⚙️ 請選擇免賠比例")
        if reimbursement_option not in reimbursement_rate_map or reimbursement_rate is None:
            errors.append("🛎 請選擇理賠比例")
        if term not in [3,6,12]:
            errors.append("⏰ 請選擇繳費期數")

        # 最后如果有错误，一次性报出来
        if errors:
            st.error("😿 以下欄位需補充或修正：")
            for e in errors:
                st.markdown(f"- {e}")
            return
        age = int(age)
        record = {
            "owner": owner,
            "wechat_id": wechat_id,
            "phone": phone,
            "email": email,

            "pet_name": pet_name,
            "pet_type": pet_type,
            "pet_sex": pet_sex,
            "chipped": chipped,
            "neuter": neuter,
            "breed": breed,
            "age": age,
            "weight": weight_input,
            "color": color,
            "q1": q1,
            "q2": q2,
            "q3": q3,
            "q4": q4,
            "q5": q5,
            "medical_history": medical_history,

            "plan_type": plan_type,
            "covered": ";".join(covered),
            "deductible_rate": deductible_rate,
            "reimbursement_rate": reimbursement_rate,
            "term": term,
            "monthly_premium": monthly_premium,
            "total_monthly_premium": total_monthly_premium,
            "monthly_extra": extra_premium,
            "total_extra": total_extra_premium,
            "effective_date": effective_date,
            "cover_consultation":    1 if "診金" in covered else 0,
            "cover_rabies_vax":      1 if "狂犬病預防疫苗" in covered else 0,
            "cover_dhppil":          1 if "DHPPiL 五合一" in covered else 0,
            "cover_corona_vax":      1 if "冠狀病毒疫苗" in covered else 0,
            "cover_lyme_vax":        1 if "萊姆病疫苗" in covered else 0,
            "cover_bordetella":      1 if "犬咳（Bordetella）" in covered else 0,

            "comment": comment,
            
        }
        save_application(record, db_path)
        placeholder = st.empty()
        for i in range(3,-1,-1):
            placeholder.markdown(f"⏳ 檔案儲存中… {i}")
            time.sleep(1)

        st.success(
            f"🎉 恭喜你，{pet_name}嘅{term}個月預計會員費已生成：\n\n"
            f"- **總金額：** MOP {total_monthly_premium:.2f} 元\n"
            f"- **每月額外：** MOP {extra_premium:.2f} 元\n"
            f"- **手續費總額：** MOP {total_extra_premium:.2f} 元\n\n"
            "感謝你嘅支持，期待同你同Pet Pet 一齊玩樂！💕"
        )
        placeholder = st.empty()
    st.write("🛠 Version: 2025-06-18-1")
    st.markdown("---")
    st.markdown("### 📱 掃描加摸Pet Pet Club 專員")
    # st.image("qrcode.png", use_column_width=True)

def render_cat_plan(plan_type, pet_type):
    st.markdown("# 🐶🐱 摸Pet Pet Club 申請表 🐾")
    st.write("🐾 嘿！歡迎加入 **摸Pet Pet Club** 🎉，下面填返你同你 Pet Pet 嘅資料啦！")

    owner = st.text_input("👤 Pet爸Pet媽，請輸入您嘅名：", placeholder="例：大佬")
    pet_name = st.text_input("🐾 Pet Pet的小名：", placeholder="例：小白")

    chipped = st.text_input("🔖 Pet Pet嘅晶片號碼：（無就填NA）")
    if chipped and is_existing_chip(chipped, db_path):
        st.warning("⚠️ 呢嗰晶片已經存在喇，試下填另一個先～")
    phone = st.text_input("📞 聯絡電話（必填）", placeholder="例：63212345")
    email = st.text_input("✉️ 電郵地址（必填）", placeholder="例：abc@xxx.com")
    wechat_id = st.text_input("💬 Wechat ID（建議）")
    
    st.markdown("### 🐥 基本資訊")
    pet_sex = st.radio("Pet Pet 嘅性別？", ['男仔', '女仔']) 
    breeds = {
        "喵喵！ 🐱": [
                    "1. 家貓（米克斯 / 土貓）",
                    "2. 英國短毛貓",
                    "3. 蘇格蘭摺耳貓",
                    "4. 美國短毛貓",
                    "5. 布偶貓",
                    "6. 波斯貓",
                    "7. 短毛異國貓（加菲貓）",
                    "8. 暹羅貓",
                    "9. 緬因貓",
                    "10. 奧西貓（Ocicat）",
                    "11. 阿比西尼亞貓",
                    "12. 挪威森林貓",
                    "13. 土耳其安哥拉貓",
                    "14. 土耳其梵貓",
                    "15. 孟加拉貓",
                    "16. 紐伯里貓（Nebelung）",
                    "17. 柯尼斯卷毛貓",
                    "18. 德文卷毛貓",
                    "19. 東方短毛貓",
                    "20. 芒奇金貓（短腿貓）",
                    "21. 巴厘貓",
                    "22. 拉帕姆貓（LaPerm）",
                    "23. 巴曼貓（Sacred Birman）",
                    "24. 喜馬拉雅貓",
                    "25. 加州閃電貓（California Spangled）",
                    "26. 新加坡貓（Singapura）",
                    "27. 沙凡納貓（Savannah）",
                    "28. 雪鞋貓（Snowshoe）",
                    "29. 索馬里貓（Somali）",
                    "30. 彼得禿貓（Peterbald）",
                    "31. 東奇尼貓（Tonkinese）",
                    "32. 日本短尾貓",
                    "33. 馬恩島貓（Manx）",
                    "34. 塞爾凱克卷毛貓（Selkirk Rex）",
                    "35. 斯芬克斯貓（無毛貓）",
                    "36. 捲耳貓（American Curl）",
                    "37. 美國硬毛貓",
                    "38. 美國環尾貓（American Ringtail）",
                    "39. 澳洲霧貓（Australian Mist）",
                    "40. 波米拉貓（Burmilla）",
                    "41. 克里米亞貓（Korat）",
                    "42. 哈瓦那棕貓",
                    "43. 高地摺耳貓（Highland Fold）",
                    "44. 高地長毛貓（Highland Straight）",
                    "45. 英國長毛貓",
                    "46. 烏克蘭 Levkoy",
                    "47. 阿拉伯貓",
                    "48. 俄羅斯藍貓",
                    "49. 寇達貓（Khao Manee）",
                    "50. 沙特阿拉伯貓",
                    "51. 泰國貓（Thai）",
                    "52. 愛琴海貓",
                    "53. 馬耳他藍貓",
                    "54. 阿納托利亞貓",
                    "55. 奧西羅貓（Ashera）",
                    "56. 美洲豹貓（Chausie）",
                    "57. 烏拉圭貓",
                    "58. 猶太貓（Yiddish Cat）",
                    "59. 白俄羅斯貓",
                    "60. 俾斯麥貓",
                    "61. 波斯長毛貓",
                    "62. 迷你豹貓（Mini Leopard）",
                    "63. 北美林貓（Bobcat Hybrid）",
                    "64. 猩紅虎紋貓（Red Tabby）",
                    "65. 黑足貓（Black-footed Cat）",
                    "66. 沙漠貓（Sand Cat）",
                    "67. 非洲野貓（African Wildcat）",
                    "68. 歐洲野貓（European Wildcat）",
                    "69. 安哥拉長毛貓",
                    "70. 碧眼白貓（Odd-eyed White）",
                    "71. 金吉拉貓",
                    "72. 金絲貓",
                    "73. 火焰點色貓（Flame Point）",
                    "74. 紅虎斑貓",
                    "75. 烏雲灰貓",
                    "76. 長毛虎斑貓",
                    "77. 黑白貓",
                    "78. 龍貓貓（特殊命名混種）",
                    "79. 雪豹貓",
                    "80. 幽靈貓（Ghost Tabby）",
                    "81. 墨水斑點貓（Inkspot Cat）",
                    "82. 馬卡貓（Macaw Cat）",
                    "83. 彩虹貓（Rainbow Cat）",
                    "84. 智利藍貓",
                    "85. 冰島灰貓",
                    "86. 墨西哥短毛貓",
                    "87. 墨西哥長毛貓",
                    "88. 多明尼加貓",
                    "89. 拉丁虎紋貓",
                    "90. 希臘藍貓",
                    "91. 非洲短毛貓",
                    "92. 貓仙（傳說品種）",
                    "93. 迷你家貓（Mini Cat）",
                    "94. 白虎斑貓",
                    "95. 燈籠貓（Lantern Cat）",
                    "96. 洛可可貓（Rococo Cat）",
                    "97. 冰藍貓",
                    "98. 曼切斯特貓",
                    "99. 沙丘貓",
                    "100. 翡翠貓（Emerald Cat）",
                    "101. 其他"
    ]
    }
    neuter = st.radio(f"Pet Pet 絕育了嗎？：", ["是", "否"], key = 'neuter')
    pet_idx = ["汪汪🐶", "喵喵🐱"]
    breed = st.selectbox(f"✨ 選擇您家{pet_idx}嘅品種：", breeds)
    if breed == "101. 其他":
        breed = st.text_input("請輸入 Pet Pet 嘅品種：")
    
    color = st.color_picker("🖌️ 選擇標記顏色", "#FF0000")
    st.write(f"你選擇的顏色是：**{color}**")
    st.markdown(
        f"<div style='width:100px;height:30px;background-color:{color}; border:1px solid #000'></div>",
        unsafe_allow_html=True
    )


    dob = st.date_input(
        "🎂 Pet Pet 嘅出生日期：",
        min_value=datetime.date(1990,1,1),
        max_value=datetime.date.today(),
        key="dob"
    )
    today = datetime.date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    st.write(f"🐥 Pet Pet而家：**{age}** 歲囉！")
    weight_input = st.text_input("⚖️ Pet Pet體重（kg）：", placeholder="例：5.2")

    q1 = st.radio(
        "① 過去90天內，您的寵物是否曾因意外或患病接受或需要接受治療？",
        ["Yes/是", "No/否"],
        key="q1"
    )
    # 如果第1題選 Yes，就顯示詳情欄
    medical_history = ""
    if q1 == "Yes/是":
        medical_history = st.text_area(
            "請提供病歷詳情（診斷、治療建議…等）",
            key="medical_history"
        )

    q2 = st.radio(
        "② 若第①題為「Yes」，您的寵物現在是否仍在接受觀察/治療？",
        ["Yes/是", "No/否"],
        key="q2"
    )
    q3 = st.radio(
        "③ 您的寵物是否曾接受任何手術（除絕育外）？",
        ["Yes/是", "No/否"],
        key="q3"
    )
    q4 = st.radio(
        "④ 過去5年內，您的寵物是否有攻擊傾向或咬傷他人/動物？",
        ["Yes/是", "No/否"],
        key="q4"
    )
    q5 = st.radio(
        "⑤ 您的寵物是否有任何身體缺陷或殘疾？",
        ["Yes/是", "No/否"],
        key="q5"
    )

    
    try:
        weight = float(weight_input)
        weight_valid = True
    except ValueError:
        weight_valid = False
        
    st.markdown("### 📝 選擇需要的福利 (可多選)")
    cover_options = {"診金": "常規診療、門診費用補助，我哋預每個月一次基本既門診費同複診費！",
                    "狂犬病預防疫苗（每劑）": "預每年一針！",
                    "FCRVP 三合一": "預每年一針！",
                    "FeLV 貓白血病": "預每年一針！",
                    "（披衣菌）": "預每年一針！",
                    "呼吸道感染（Bordetella）": "預每年一針！"}

    covered = multi_checkbox(cover_options, cols = 1)
    cover_consultation   = "診金" in covered
    cover_rabies_vax     = "狂犬病預防疫苗（每劑）" in covered
    cover_fcrvp          = "FCRVP 三合一"       in covered
    cover_felv           = "貓白血病"        in covered
    cover_Chlamydia      = "（披衣菌） "          in covered
    cover_bordetella     = "呼吸道感染（Bordetella）"   in covered

    st.markdown("### 🌟 選擇方案")
    deductible_rate_map = {
        "請選擇…": None,
        "🍀 綠意款": 0.10,
        "🌸 櫻花款": 0.15,
        "🎉 戰鼓款": 0.20,
    }
    reimbursement_rate_map = {
        "請選擇…": None,
        "🍁 楓葉款 - 70%": 0.70,      
        "❄️ 冰晶款 - 80%": 0.80,
        "🌻 向陽款 - 90%": 0.90
    }
    deductible_option = st.selectbox(
            "⚙️ 請選擇您的免賠比例：",
            [*deductible_rate_map.keys()],
            key="deductible_rate",
            help = "🍀 綠意款係最高級，🌸 櫻花款喺中級，🎉 戰鼓款喺普通款\n" \
                   "\n 如果係普通款，手術費喺MOP 1000，自付額大嘅係 MOP 200；如果係最高級，自付額大嘅係 MOP 100"
        )

    reimbursement_option = st.selectbox(
            "🛎 請選擇您的理賠比例：",
            [*reimbursement_rate_map.keys()],
            key="reimbursement_rate",
        )
    
    deductible_rate = deductible_rate_map[deductible_option]
    reimbursement_rate = reimbursement_rate_map[reimbursement_option]

    term = st.selectbox(
        "⏰ 繳費期數（選一個最適合你哋）：", 
        [3, 6, 12], 
        format_func=lambda x: {
        3: "小季輕付（每 3 個月）",
        6: "半載悠遊（每 6 個月）",
        12: "全年安心（每 12 個月）"
        }[x],
        help = '越長嘅會員期，手續費越少，12個月直接免會員費！',
        key="term"
    )
    if deductible_rate is None or reimbursement_rate is None:
        st.info("請先選擇「自付方案」與「理賠方案」！")
    else:
        if plan_type == "🍁 公立舒心組":
            total_monthly_premium, extra_premium, total_extra_premium = premium_calculation_public_dog(
                weight=weight,
                age=age,
                term=term,
                deductible_rate=deductible_rate,
                reimbursement_rate=reimbursement_rate,
                cover_consultation=cover_consultation,
                cover_rabies_vax=cover_rabies_vax,
                cover_fcrvp=cover_fcrvp,
                cover_felv=cover_felv,
                cover_Chlamydia=cover_Chlamydia,
                cover_bordetella=cover_bordetella,
            )
            monthly_premium = total_monthly_premium/term
        else:
            total_monthly_premium, extra_premium, total_extra_premium = premium_calculation_private_dog(
                weight=weight,
                age=age,
                term=term,
                deductible_rate=deductible_rate,
                reimbursement_rate=reimbursement_rate,
                cover_consultation=cover_consultation,
                cover_rabies_vax=cover_rabies_vax,
                cover_fcrvp=cover_fcrvp,
                cover_felv=cover_felv,
                cover_Chlamydia=cover_Chlamydia,
                cover_bordetella=cover_bordetella,
            )
            monthly_premium = total_monthly_premium/term

    effective_date = st.date_input(
        "會員生效日期：",
        min_value = datetime.date.today(),
        max_value = datetime.date(2030, 12, 31),
        key = 'effective_date'
    )

    submitted = st.button("💌 立即送出，成為俱樂部一員，保護Pet Pet")
    comment = st.text_area("💬 其他留言或建議（選填）", help="留下您對 Club 嘅想法、建議都好 😊")
    if submitted:
        errors = []

        # 1. 基本文本输入
        if not owner:
            errors.append("👤 Pet Pet主人姓名")
        if not pet_name:
            errors.append("🐾 Pet Pet名字")
        if not chipped:
            errors.append("🔖 晶片號碼")
        if not phone:
            errors.append("📞 聯絡電話")
        if not email or '@' not in email:
            errors.append("✉️ 有效電郵地址")
        if not wechat_id:
            errors.append("💬 Wechat ID（雖然可選，但建議填寫）")

        # 2. 性别 & 絕育
        if pet_sex not in ['男仔', '女仔']:
            errors.append("⚥ 請選擇 Pet Pet 嘅性別")
        if neuter not in ['是', '否']:
            errors.append("🔪 請選擇 Pet Pet 是否絕育")

        # 3. 品種
        if not breed:
            errors.append("🐶🐱 Pet Pet 品種")

        # 4. 體重
        if not weight_input or not weight_valid:
            errors.append("⚖️ 請輸入有效嘅體重（例如 5.2）")

        # 5. 問卷 q1–q5
        if q1 not in ["Yes/是", "No/否"]:
            errors.append("① 過去90天內治療狀況")
        if q1 == "Yes/是" and not medical_history:
            errors.append("請提供病歷詳情（第①題選 Yes 時必填）")
        for idx, q in enumerate([q2, q3, q4, q5], start=2):
            if q not in ["Yes/是", "No/否"]:
                errors.append(f"第 {idx} 題問卷未填或格式錯誤")

        # 6. 標記顏色
        if not color:
            errors.append("🖌️ 請選擇一個標記顏色")

        # 7. 生效日期
        if not effective_date:
            errors.append("⏳ 請選擇會員生效日期")

        # 8. 保單方案 & 費率選擇
        if plan_type not in ["🍁 公立舒心組", "🛡️ 私家無憂組"]:
            errors.append("🌟 請選擇「照顧方式」")
        if deductible_option not in deductible_rate_map or deductible_rate is None:
            errors.append("⚙️ 請選擇免賠比例")
        if reimbursement_option not in reimbursement_rate_map or reimbursement_rate is None:
            errors.append("🛎 請選擇理賠比例")
        if term not in [3,6,12]:
            errors.append("⏰ 請選擇繳費期數")

        # 最后如果有错误，一次性报出来
        if errors:
            st.error("😿 以下欄位需補充或修正：")
            for e in errors:
                st.markdown(f"- {e}")
            return
        age = int(age)
        record = {
            "owner": owner,
            "wechat_id": wechat_id,
            "phone": phone,
            "email": email,

            "pet_name": pet_name,
            "pet_type": pet_type,
            "pet_sex": pet_sex,
            "chipped": chipped,
            "neuter": neuter,
            "breed": breed,
            "age": age,
            "weight": weight_input,
            "color": color,
            "q1": q1,
            "q2": q2,
            "q3": q3,
            "q4": q4,
            "q5": q5,
            "medical_history": medical_history,

            "plan_type": plan_type,
            "covered": ";".join(covered),
            "deductible_rate": deductible_rate,
            "reimbursement_rate": reimbursement_rate,
            "term": term,
            "monthly_premium": monthly_premium,
            "total_monthly_premium": total_monthly_premium,
            "monthly_extra": extra_premium,
            "total_extra": total_extra_premium,
            "effective_date": effective_date,
            "cover_consultation":    1 if "診金" in covered else 0,
            "cover_rabies_vax":      1 if "狂犬病預防疫苗" in covered else 0,
            "cover_dhppil":          1 if "DHPPiL 五合一" in covered else 0,
            "cover_corona_vax":      1 if "冠狀病毒疫苗" in covered else 0,
            "cover_lyme_vax":        1 if "萊姆病疫苗" in covered else 0,
            "cover_bordetella":      1 if "犬咳（Bordetella）" in covered else 0,

            "comment": comment,
            
        }
        save_application(record, db_path)
        placeholder = st.empty()
        for i in range(3,-1,-1):
            placeholder.markdown(f"⏳ 檔案儲存中… {i}")
            time.sleep(1)

        st.success(
            f"🎉 恭喜你，{pet_name}嘅{term}個月預計會員費已生成：\n\n"
            f"- **總金額：** MOP {total_monthly_premium:.2f} 元\n"
            f"- **每月額外：** MOP {extra_premium:.2f} 元\n"
            f"- **手續費總額：** MOP {total_extra_premium:.2f} 元\n\n"
            "感謝你嘅支持，期待同你同Pet Pet 一齊玩樂！💕"
        )
        placeholder = st.empty()
    st.write("🛠 Version: 2025-06-18-1")
    st.markdown("---")
    st.markdown("### 📱 掃描加摸Pet Pet Club 專員")
    # st.image("qrcode.png", use_column_width=True)



if __name__ == "__main__":
    run_form()
