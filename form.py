import streamlit as st
import time
import datetime
import qrcode
import os
from logic import save_application, init_db, db_path, is_existing_chip, premium_calculation_private, premium_calculation_public
from streamlit.runtime.scriptrunner.script_runner import RerunException, RerunData

def rerun():
    raise RerunException(RerunData())

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
def render_plan(plan_type):
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
    pet_type = st.radio("請問你嘅Pet Pet喺？", ["汪汪！ 🐶", "喵喵！ 🐱（暫不開放！）"]) 
    pet_sex = st.radio("Pet Pet 嘅性別？", ['男仔', '女仔']) 
    if pet_type == "喵喵！ 🐱（暫不開放！）":
        st.warning("呢度暫時未開貓貓申請，敬請期待～ 🐱💕")
        return 
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
                    "91. 巴森吉犬", "92. 阿金廷杜告犬", "93. 蘭伯格犬", "94. 西高地白㹴", "95. 蘇格蘭㹴", "96. 捲毛獵犬", "97. 義大利指示犬", "98. 瑞典狐狸犬", "99. 泰國脊背犬", "100. 格雷伊獵犬"
                ],
        "喵喵！ 🐱（暫不開放！）": []
    }
    neuter = st.radio(f"Pet Pet 絕育了嗎？：", ["是", "否"], key = 'neuter')
    pet_idx = ["汪汪🐶", "喵喵🐱"]
    breed = st.selectbox(f"✨ 選擇您家{pet_idx}嘅品種：", breeds[pet_type])
    if breed == "其他":
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
        "🌻 向陽款 - 90%": 0.90,
        "❄️ 冰晶款 - 80%": 0.80,
        "🍁 楓葉款 - 70%": 0.70
    }
    if pet_type == "汪汪！ 🐶":
        deductible_option = st.selectbox(
            "⚙️ 請選擇您的免賠比例：",
            [*deductible_rate_map.keys()],
            key="deductible_rate",
            help = "🍀 綠意款係最高級，🌸 櫻花款喺中級，🎉 戰鼓款喺普通款\n" \
                   "\n 例如：如果係普通款，手術費喺MOP 1000，自付額大嘅係 MOP 200；如果係最高級，自付額大嘅係 MOP 100"
        )

        reimbursement_option = st.selectbox(
            "🛎 請選擇您的理賠比例：",
            [*reimbursement_rate_map.keys()],
            key="reimbursement_rate",
            help = "🌻 向陽款係最高級, ❄️ 冰晶款喺中級, 🍁 楓葉款普通款\n" \
                   "\n 例如：如果係普通款，手術費喺MOP 1000，自付額大嘅喺 MOP 100，咁最後賠償係 MOP 630\n" \
                   "\n 例如：如果係最高級款，手術費喺MOP 1000，自付額大嘅喺 MOP 100，咁最後賠償係 MOP 810"
        )
    else:
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
            total_monthly_premium, extra_premium, total_extra_premium = premium_calculation_public(
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
            total_monthly_premium, extra_premium, total_extra_premium = premium_calculation_private(
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
        # 驗證必填
        errors = []
        if not owner:    errors.append("👤 Pet Pet主人姓名")
        if not pet_name: errors.append("🐾 Pet Pet名字")
        if not breed:    errors.append("🐾 Pet Pet品種")
        if not phone:    errors.append("📞 聯絡電話")
        if not email or '@' not in email: errors.append("✉️ 有效電郵")
        if not chipped:  errors.append("🔖 晶片號碼")
        if not weight_valid:
            errors.append("🐾 體重（請輸入有效數字，例如 5.2）")
        if deductible_option == "請選擇…" or reimbursement_option == "請選擇…":
            errors.append("要選方案呀！")
        if errors:
            st.error("😿 以下欄位需補充：")
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

def run_form():
    # 1. 先拿到 query-params
    try:
        params = st.query_params
    except AttributeError:
        params = st.experimental_get_query_params()

    # 兼容旧的 "admin" 参数
    raw = params.get("veryveryverysecretcode", [None])
    secret_code = raw[0] if isinstance(raw, list) else raw

    # 2. 管理员模式：判断密码
    if secret_code == "kaiwaho":
        st.success("🔑 管理员模式生效")
        if st.button("🔄 重置資料庫"):
            if os.path.exists(db_path):
                os.remove(db_path)
            init_db(db_path)
            st.success("✅ 已清空並重新初始化 application.db")
        
        # —— 下载数据库按钮 —— 
        with open(db_path, "rb") as f:
            st.download_button(
                "📥 下載 application.db",
                data=f.read(),
                file_name="application.db",
                mime="application/octet-stream",
            )
        return

        return  # 阻止后续普通表单显示


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

    render_plan(plan_type)

if __name__ == "__main__":
    run_form()
