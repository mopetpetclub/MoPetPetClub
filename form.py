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
    if pet_type == "喵喵！ 🐱（暫不開放！）":
        st.warning("呢度暫時未開貓貓申請，敬請期待～ 🐱💕")
        return 
    breeds = {
        "汪汪！ 🐶": ["拉布拉多", "柴柴", "可卡", "柯基", "其他"],
        "喵喵！ 🐱（暫不開放！）": []
    }

    pet_idx = ["汪汪🐶", "喵喵🐱"]
    breed = st.selectbox(f"✨ 選擇您家{pet_idx}嘅品種：", breeds[pet_type])
    if breed == "其他":
        breed = st.text_input("請輸入 Pet Pet 嘅品種：")

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
            "⚙️ 請選擇您的自付方案：",
            [*deductible_rate_map.keys()],
            key="deductible_rate",
            help = "🍀 綠意款係最高級，🌸 櫻花款喺中級，🎉 戰鼓款喺普通款\n" \
                   "\n 例如：如果係普通款，手術費喺MOP 1000，自付額大嘅係 MOP 200；如果係最高級，自付額大嘅係 MOP 100"
        )

        reimbursement_option = st.selectbox(
            "⚙️ 請選擇您的自付方案：",
            [*reimbursement_rate_map.keys()],
            key="reimbursement_rate",
            help = "🌻 向陽款係最高級, ❄️ 冰晶款喺中級, 🍁 楓葉款普通款\n" \
                   "\n 例如：如果係普通款，手術費喺MOP 1000，自付額大嘅喺 MOP 100，咁最後賠償係 MOP 630\n" \
                   "\n 例如：如果係最高級款，手術費喺MOP 1000，自付額大嘅喺 MOP 100，咁最後賠償係 MOP 810"
        )
    else:
        deductible_option = st.selectbox(
            "⚙️ 請選擇您的自付方案：",
            [*deductible_rate_map.keys()],
            key="deductible_rate",
            help = "🍀 綠意款係最高級，🌸 櫻花款喺中級，🎉 戰鼓款喺普通款\n" \
                   "\n 如果係普通款，手術費喺MOP 1000，自付額大嘅係 MOP 200；如果係最高級，自付額大嘅係 MOP 100"
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
        help = '越長嘅會員期，手續費越少，12個月直接免會員費！',
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
            f"🎉 恭喜你，{pet_name}嘅{term}個月預計會員費已生成：\n\n"
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
    if pet_type == "喵喵！ 🐱（暫不開放！）":
        st.warning("呢度暫時未開貓貓申請，敬請期待～ 🐱💕")
        return 
    breeds = {
        "汪汪！ 🐶": ["拉布拉多", "柴柴", "可卡", "柯基", "其他"],
        "喵喵！ 🐱（暫不開放！）": []
    }

    pet_idx = ["汪汪🐶", "喵喵🐱"]
    breed = st.selectbox(f"✨ 選擇您家{pet_idx}嘅品種：", breeds[pet_type])
    if breed == "其他":
        breed = st.text_input("請輸入 Pet Pet 嘅品種：")

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
            "⚙️ 請選擇您的自付方案：",
            [*deductible_rate_map.keys()],
            key="deductible_rate",
            help = "🍀 綠意款係最高級，🌸 櫻花款喺中級，🎉 戰鼓款喺普通款\n" \
                   "\n 例如：如果係普通款，手術費喺MOP 1000，自付額大嘅係 MOP 200；如果係最高級，自付額大嘅係 MOP 100"
        )

        reimbursement_option = st.selectbox(
            "⚙️ 請選擇您的自付方案：",
            [*reimbursement_rate_map.keys()],
            key="reimbursement_rate",
            help = "🌻 向陽款係最高級, ❄️ 冰晶款喺中級, 🍁 楓葉款普通款\n" \
                   "\n 例如：如果係普通款，手術費喺MOP 1000，自付額大嘅喺 MOP 100，咁最後賠償係 MOP 630\n" \
                   "\n 例如：如果係最高級款，手術費喺MOP 1000，自付額大嘅喺 MOP 100，咁最後賠償係 MOP 810"
        )
    else:
        deductible_option = st.selectbox(
            "⚙️ 請選擇您的自付方案：",
            [*deductible_rate_map.keys()],
            key="deductible_rate",
            help = "🍀 綠意款係最高級，🌸 櫻花款喺中級，🎉 戰鼓款喺普通款\n" \
                   "\n 如果係普通款，手術費喺MOP 1000，自付額大嘅係 MOP 200；如果係最高級，自付額大嘅係 MOP 100"
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
        help = '越長嘅會員期，手續費越少，12個月直接免會員費！',
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
            f"🎉 恭喜你，{pet_name}嘅{term}個月預計會員費已生成：\n\n"
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
        with open("application.db", "rb") as f:
            st.download_button(
                "📥 下载 application.db",
                data=f.read(),
                file_name="application.db",
                mime="application/octet-stream",
            )
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
        return

    if plan_type == "🍁 公立舒心組":
        render_public_plan(plan_type)
    else:
        render_private_plan(plan_type) 


if __name__ == "__main__":
    run_form()
