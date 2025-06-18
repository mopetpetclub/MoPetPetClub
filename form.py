import streamlit as st
import time
import datetime
import qrcode
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
def render_public_plan(plan_type):
    st.markdown("# 🐶🐱 摸Pet Pet Club 申請表 🐾")
    st.write("🐾 嘿！歡迎加入 **摸Pet Pet Club** 🎉，來為您家毛寶貝選擇最貼心的福利吧！")

    owner = st.text_input("👤 毛爸毛媽，請輸入您的大名：")
    pet_name = st.text_input("🐾 毛孩的小名：")

    chipped = st.text_input("🔖 毛孩的晶片號碼：（如果沒有，請填寫NA）")
    if chipped and is_existing_chip(chipped, db_path):
        st.warning("⚠️ 晶片號已存在，請輸入不同的號碼")
    phone = st.text_input("📞 聯絡電話（必填）")
    email = st.text_input("✉️ 電郵地址（必填）")
    wechat_id = st.text_input("💬 Wechat ID（建議）")
    
    st.markdown("### 🐥 基本資訊")
    pet_type = st.radio("請問您的寶貝是？", ["汪汪！ 🐶", "喵喵！ 🐱（暫不開放！）"])  
    if pet_type == "喵喵！ 🐱（暫不開放！）":
        st.warning("暫不適用")
        return 
    breeds = {
        "汪汪！ 🐶": ["拉布拉多", "柴柴", "可卡", "柯基", "其他"],
        "喵喵！ 🐱（暫不開放！）": []
    }

    pet_idx = ["汪汪🐶", "喵喵🐱"]
    breed = st.selectbox(f"✨ 選擇您家{pet_idx}的品種：", breeds[pet_type])
    if breed == "其他":
        breed = st.text_input("請輸入您的寶貝特殊品種：")

    dob = st.date_input(
        "🎂 請選擇寶貝的出生日期：",
        min_value=datetime.date(1990,1,1),
        max_value=datetime.date.today(),
        key="dob"
    )
    today = datetime.date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    st.write(f"🐥 寶貝年齡：**{age}** 歲")
    weight_input = st.text_input("🐥 寶貝體重（kg）：", placeholder="例：5.2")
    try:
        weight = float(weight_input)
        weight_valid = True
    except ValueError:
        weight_valid = False
        
    st.markdown("### 📝 選擇需要的福利 (可多選)")
    cover_options = {"診金": "常規診療、門診費用補助",
                    "狂犬病預防疫苗（每劑）": "每年一針",
                    "DHPPiL 五合一": "每年一針",
                    "冠狀病毒疫苗": "每年一針",
                    "萊姆病疫苗": "每年一針",
                    "犬咳（Bordetella）": "每年一針"}

    covered = multi_checkbox(cover_options, cols = 3)
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
            "⚙️ 請選擇您的自付方案：",
            [*deductible_rate_map.keys()],
            key="deductible_rate",
        )

        reimbursement_option = st.selectbox(
            "⚙️ 請選擇您的自付方案：",
            [*reimbursement_rate_map.keys()],
            key="reimbursement_rate",
        )
    else:
        deductible_option = st.selectbox(
            "⚙️ 請選擇您的自付方案：",
            [*deductible_rate_map.keys()],
            key="deductible_rate",
        )

        reimbursement_option = st.selectbox(
            "⚙️ 請選擇您的自付方案：",
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
        help = '會員期',
        key="term"
    )
    if deductible_rate is None or reimbursement_rate is None:
        st.info("請先選擇「自付方案」與「理賠方案」！")
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

    submitted = st.button("💌 立即送出，成為俱樂部一員，保護寶貝")
    comment = st.text_area("💬 其他留言或建議（選填）", help="留下您對 Club 嘅想法、建議都好 😊")
    if submitted:
        # 驗證必填
        errors = []
        if not owner:    errors.append("👤 主人姓名")
        if not pet_name: errors.append("🐾 寶貝名字")
        if not breed:    errors.append("🐾 寶貝品種")
        if not phone:    errors.append("📞 聯絡電話")
        if not email or '@' not in email: errors.append("✉️ 有效電郵")
        if not chipped:  errors.append("🔖 晶片號碼")
        if not weight_valid:
            errors.append("🐾 體重（請輸入有效數字，例如 5.2）")
        if deductible_option == "請選擇…" or reimbursement_option == "請選擇…":
            errors.append("請先選擇「自付方案」與「理賠方案」！")
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
            "chipped": chipped,
            "breed": breed,
            "age": age,
            "weight": weight_input,

            "plan_type": plan_type,
            "covered": ";".join(covered),
            "deductible_rate": deductible_rate,
            "reimbursement_rate": reimbursement_rate,
            "term": term,
            "monthly_premium": monthly_premium,
            "total_monthly_premium": total_monthly_premium,
            "monthly_extra": extra_premium,
            "total_extra": total_extra_premium,
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
            f"🎉 恭喜你，{pet_name}的{term}個月預計會員費已生成：\n\n"
            f"- **總金額：** MOP {total_monthly_premium:.2f} 元\n"
            f"- **每月額外：** MOP {extra_premium:.2f} 元\n"
            f"- **手續費總額：** MOP {total_extra_premium:.2f} 元\n\n"
            "感謝你嘅支持，期待同你同毛孩一齊玩樂！💕"
        )
        placeholder = st.empty()
    st.markdown("---")
    st.markdown("### 📱 掃描加摸Pet Pet Club 專員")
    # st.image("qrcode.png", use_column_width=True)

def render_private_plan(plan_type):
    st.markdown("# 🐶🐱 摸Pet Pet Club 申請表 🐾")
    st.write("🐾 嘿！歡迎加入 **摸Pet Pet Club** 🎉，來為您家毛寶貝選擇最貼心的福利吧！")

    owner = st.text_input("👤 毛爸毛媽，請輸入您的大名：")
    pet_name = st.text_input("🐾 毛孩的小名：")

    chipped = st.text_input("🔖 毛孩的晶片號碼：（如果沒有，請填寫NA）")
    if chipped and is_existing_chip(chipped, db_path):
        st.warning("⚠️ 晶片號已存在，請輸入不同的號碼")
    phone = st.text_input("📞 聯絡電話（必填）")
    email = st.text_input("✉️ 電郵地址（必填）")
    wechat_id = st.text_input("💬 Wechat ID（建議）")
    
    st.markdown("### 🐥 基本資訊")
    pet_type = st.radio("請問您的寶貝是？", ["汪汪！ 🐶", "喵喵！ 🐱（暫不開放！）"])  
    if pet_type == "喵喵！ 🐱（暫不開放！）":
        st.warning("暫不適用")
        return 
    breeds = {
        "汪汪！ 🐶": ["拉布拉多", "柴柴", "可卡", "柯基", "其他"],
        "喵喵！ 🐱（暫不開放！）": []
    }

    pet_idx = ["汪汪🐶", "喵喵🐱"]
    breed = st.selectbox(f"✨ 選擇您家{pet_idx}的品種：", breeds[pet_type])
    if breed == "其他":
        breed = st.text_input("請輸入您的寶貝特殊品種：")

    dob = st.date_input(
        "🎂 請選擇寶貝的出生日期：",
        min_value=datetime.date(1990,1,1),
        max_value=datetime.date.today(),
        key="dob"
    )
    today = datetime.date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    st.write(f"🐥 寶貝年齡：**{age}** 歲")
    weight_input = st.text_input("🐥 寶貝體重（kg）：", placeholder="例：5.2")
    try:
        weight = float(weight_input)
        weight_valid = True
    except ValueError:
        weight_valid = False
        
    st.markdown("### 📝 選擇需要的福利 (可多選)")
    cover_options = {"診金": "常規診療、門診費用補助",
                    "狂犬病預防疫苗（每劑）": "每年一針",
                    "DHPPiL 五合一": "每年一針",
                    "冠狀病毒疫苗": "每年一針",
                    "萊姆病疫苗": "每年一針",
                    "犬咳（Bordetella）": "每年一針"}

    covered = multi_checkbox(cover_options, cols = 3)
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
            "⚙️ 請選擇您的自付方案：",
            [*deductible_rate_map.keys()],
            key="deductible_rate",
        )

        reimbursement_option = st.selectbox(
            "⚙️ 請選擇您的自付方案：",
            [*reimbursement_rate_map.keys()],
            key="reimbursement_rate",
        )
    else:
        deductible_option = st.selectbox(
            "⚙️ 請選擇您的自付方案：",
            [*deductible_rate_map.keys()],
            key="deductible_rate",
        )

        reimbursement_option = st.selectbox(
            "⚙️ 請選擇您的自付方案：",
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
        help = '會員期',
        key="term"
    )
    if deductible_rate is None or reimbursement_rate is None:
        st.info("請先選擇「自付方案」與「理賠方案」！")
    else:
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

    submitted = st.button("💌 立即送出，成為俱樂部一員，保護寶貝")
    comment = st.text_area("💬 其他留言或建議（選填）", help="留下您對 Club 嘅想法、建議都好 😊")
    if submitted:
        # 驗證必填
        errors = []
        if not owner:    errors.append("👤 主人姓名")
        if not pet_name: errors.append("🐾 寶貝名字")
        if not breed:    errors.append("🐾 寶貝品種")
        if not phone:    errors.append("📞 聯絡電話")
        if not email or '@' not in email: errors.append("✉️ 有效電郵")
        if not chipped:  errors.append("🔖 晶片號碼")
        if not weight_valid:
            errors.append("🐾 體重（請輸入有效數字，例如 5.2）")
        if deductible_option == "請選擇…" or reimbursement_option == "請選擇…":
            errors.append("請先選擇「自付方案」與「理賠方案」！")
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
            "chipped": chipped,
            "breed": breed,
            "age": age,
            "weight": weight_input,

            "plan_type": plan_type,
            "covered": ";".join(covered),
            "deductible_rate": deductible_rate,
            "reimbursement_rate": reimbursement_rate,
            "term": term,
            "monthly_premium": monthly_premium,
            "total_monthly_premium": total_monthly_premium,
            "monthly_extra": extra_premium,
            "total_extra": total_extra_premium,
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
            f"🎉 已成功儲存！{pet_name}的{term}個月預計會員費已生成：\n\n"
            f"- **總金額：** MOP {total_monthly_premium:.2f} 元\n"
            f"- **每月額外：** MOP {extra_premium:.2f} 元\n"
            f"- **手續費總額：** MOP {total_extra_premium:.2f} 元\n\n"
            "感謝你嘅支持，期待同你同毛孩一齊玩樂！💕"
        )
        placeholder = st.empty()
    st.markdown("---")
    st.markdown("### 📱 掃描加摸Pet Pet Club 專員")
    # st.image("qrcode.png", use_column_width=True)

def run_form():
    init_db(db_path)

    plan_type = st.selectbox(
        "請選擇方案：",
        ["請先選擇…", "公立方案", "全方位方案"],
        key="plan_type"
    )

    # 如果還是佔位，就顯示提示並結束 run_form
    if plan_type == "請先選擇…":
        st.info("ℹ️ 請先選擇上面的方案，才能繼續填寫表單喔！")
        return

    if plan_type == "公立方案":
        render_public_plan(plan_type)
    else:
        render_private_plan(plan_type)