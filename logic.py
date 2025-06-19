import sqlite3
import os
import pandas as pd
import numpy as np

db_path = os.path.join(os.path.dirname(__file__), "application.db")

def init_db(db_path=db_path):
    os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS application (
        id                     INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at             DATETIME DEFAULT CURRENT_TIMESTAMP,
        owner                  TEXT    NOT NULL DEFAULT '',
        wechat_id              TEXT    NOT NULL DEFAULT '',
        phone                  TEXT    NOT NULL DEFAULT '',
        email                  TEXT    NOT NULL DEFAULT '',
        pet_name               TEXT    NOT NULL DEFAULT '',
        pet_type               TEXT    NOT NULL DEFAULT '',
        chipped                TEXT    NOT NULL DEFAULT '',
        breed                  TEXT    NOT NULL DEFAULT '',
        age                    INTEGER NOT NULL DEFAULT 0,
        pet_sex                TEXT    NOT NULL DEFAULT '',
        weight                 TEXT    NOT NULL DEFAULT '',
        color                  TEXT    NOT NULL DEFAULT '',
        neuter                 TEXT    NOT NULL DEFAULT '',
        q1                     TEXT    NOT NULL DEFAULT '',
        q2                     TEXT    NOT NULL DEFAULT '',
        q3                     TEXT    NOT NULL DEFAULT '',
        q4                     TEXT    NOT NULL DEFAULT '',
        q5                     TEXT    NOT NULL DEFAULT '',
        medical_history        TEXT    NOT NULL DEFAULT '',
        effective_date         DATE    NOT NULL DEFAULT CURRENT_DATE,
        plan_type              TEXT    NOT NULL DEFAULT '',
        covered                TEXT    NOT NULL DEFAULT '',
        deductible_rate        REAL    NOT NULL DEFAULT 0.0,
        reimbursement_rate     REAL    NOT NULL DEFAULT 0.0,
        term                   INTEGER NOT NULL DEFAULT 12,
        monthly_premium        REAL    NOT NULL DEFAULT 0.0,
        total_monthly_premium  REAL    NOT NULL DEFAULT 0.0,
        monthly_extra          REAL    NOT NULL DEFAULT 0.0,
        total_extra            REAL    NOT NULL DEFAULT 0.0,
        comment                TEXT    NOT NULL DEFAULT '',
        cover_consultation     INTEGER NOT NULL DEFAULT 0,
        cover_rabies_vax       INTEGER NOT NULL DEFAULT 0,
        cover_dhppil           INTEGER NOT NULL DEFAULT 0,
        cover_corona_vax       INTEGER NOT NULL DEFAULT 0,
        cover_lyme_vax         INTEGER NOT NULL DEFAULT 0,
        cover_bordetella       INTEGER NOT NULL DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

def save_application(record: dict, db_path=db_path):
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 看這隻 chip 是否已存在
    c.execute("SELECT id FROM application WHERE chipped = ?", (record['chipped'],))
    row = c.fetchone()

    # 一定要跟上面 CREATE TABLE 的欄位順序一模一樣
    params = (
        record['owner'],
        record['wechat_id'],
        record['phone'],
        record['email'],
        record['pet_name'],
        record['pet_type'],
        record['pet_sex'],
        record['chipped'],
        record['breed'],
        record['age'],
        record['weight'],
        record['color'],
        record['neuter'],
        record['q1'],
        record['q2'],
        record['q3'],
        record['q4'],
        record['q5'],
        record['medical_history'],
        record['plan_type'],
        record['covered'],
        record['deductible_rate'],
        record['reimbursement_rate'],
        record['term'],
        record['monthly_premium'],
        record['total_monthly_premium'],
        record['monthly_extra'],
        record['total_extra'],
        record['effective_date'],
        record['comment'],
        record.get('cover_consultation', 0),
        record.get('cover_rabies_vax', 0),
        record.get('cover_dhppil', 0),
        record.get('cover_corona_vax', 0),
        record.get('cover_lyme_vax', 0),
        record.get('cover_bordetella', 0),
    )

    if row:
        # UPDATE
        sql = """
        UPDATE application SET
            owner                 = ?,
            wechat_id             = ?,
            phone                 = ?,
            email                 = ?,
            pet_name              = ?,
            pet_type              = ?,
            pet_sex               = ?,
            chipped               = ?,
            nueter                = ?,
            breed                 = ?,
            color                 = ?,
            age                   = ?,
            q1                    = ?,
            q2                    = ?,
            q3                    = ?,
            q4                    = ?,
            q5                    = ?,
            medical_history       = ?,
            plan_type             = ?,
            covered               = ?,
            deductible_rate       = ?,
            reimbursement_rate    = ?,
            term                  = ?,
            monthly_premium       = ?,
            total_monthly_premium = ?,
            monthly_extra         = ?,
            total_extra           = ?,
            comment               = ?,
            effective_date        = ?,
            cover_consultation    = ?,
            cover_rabies_vax      = ?,
            cover_dhppil          = ?,
            cover_corona_vax      = ?,
            cover_lyme_vax        = ?,
            cover_bordetella      = ?
          WHERE id = ?
        """
        c.execute(sql, params + (row[0],))
    else:
        # INSERT
        placeholders = ",".join("?" for _ in params)
        sql = f"""
        INSERT INTO application (
            owner, wechat_id, phone, email,
            pet_name, pet_type, pet_sex, chipped, breed, age, weight, color, neuter,
            q1, q2, q3, q4, q5, medical_history,
            plan_type, covered,
            deductible_rate, reimbursement_rate, term,
            monthly_premium, total_monthly_premium, monthly_extra, total_extra,
            effective_date, comment,
            cover_consultation, cover_rabies_vax, cover_dhppil, cover_corona_vax, cover_lyme_vax, cover_bordetella
        ) VALUES ({placeholders})
        """
        c.execute(sql, params)

    conn.commit()
    conn.close()

def is_existing_chip(chip_id: str, db_path: str = db_path) -> bool:
    """
    Check if the given chip ID already exists in the database.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM application WHERE chipped = ?", (chip_id,))
    exists = c.fetchone()[0] > 0
    conn.close()
    return exists


    """
    Insert a new application record or update an existing one by chip ID.
    """
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Check if this chip already exists
    c.execute("SELECT id FROM application WHERE chipped = ?", (record['chipped'],))
    row = c.fetchone()

    # Prepare parameters in the correct order
    params = (
        record['owner'],
        record['pet_name'],
        record['pet_type'],
        record['breed'],
        record['age'],
        record['covered'],
        record['plan_type'],
        record['deductible_rate'],
        record['reimbursement_rate'],
        record['term'],
        record['monthly_premium'],
        record['total_monthly_premium'],
        record['monthly_extra'],
        record['total_extra'],
        record['chipped'],
        record['phone'],
        record['email'],
        record['comment'],
        record['wechat_id'],
        record.get('cover_consultation', 0),
        record.get('cover_rabies_vax', 0),
        record.get('cover_dhppil', 0),
        record.get('cover_corona_vax', 0),
        record.get('cover_lyme_vax', 0),
        record.get('cover_bordetella', 0),
    )

    if row:
        # UPDATE existing record
        sql = """
        UPDATE application
           SET owner                  = ?,
               pet_name               = ?,
               pet_type               = ?,
               breed                  = ?,
               age                    = ?,
               covered                = ?,
               deductible_rate        = ?,
               reimbursement_rate     = ?,
               term                   = ?,
               plan_type              = ?,
               monthly_premium        = ?,
               total_monthly_premium  = ?,
               monthly_extra          = ?,
               total_extra            = ?,
               chipped                = ?,
               phone                  = ?,
               email                  = ?,
               comment                = ?,
               wechat_id              = ?,
               cover_consultation     = ?,
               cover_rabies_vax       = ?,
               cover_dhppil           = ?,
               cover_corona_vax       = ?,
               cover_lyme_vax         = ?,
               cover_bordetella       = ?
         WHERE id = ?
        """
        c.execute(sql, params + (row[0],))

    else:
        # INSERT new record
        placeholders = ','.join('?' for _ in range(len(params)))
        sql = f"""
        INSERT INTO application (
            owner, pet_name, pet_type, breed, age, covered,
            deductible_rate, reimbursement_rate, term,
            monthly_premium, total_monthly_premium, monthly_extra, total_extra, plan_type,
            chipped, phone, email, comment, wechat_id,
            cover_consultation, cover_rabies_vax, cover_dhppil,
            cover_corona_vax, cover_lyme_vax, cover_bordetella
        ) VALUES ({placeholders})
        """
        c.execute(sql, params)

    conn.commit()
    conn.close()



funeral_rates = [.00033, .00017, .0005, .00083, .0025]
humane_destruction = 750
humane_destruction_public = 300
cremation = [750, 1250, 3000]
cremation_public = [300, 500, 1200]
cremation_rates = [.0005, .0025, .0001]
corpse = [375, 500, 2500]
corpse_public = [150, 200, 1000]
corpse_rates = [.0005, .0025, .0001]
staycation = [875, 1000, 1125]
staycation_public = [140, 160, 180]
staycation_rate = [.002, .001, .0025, .004, .006]
beauty1 = [200, 220, 240]
beauty1_public = [100, 110, 120]
beauty1_rate = [.15, .12, .1]
beauty2 = [140, 160, 180]
beauty2_public = [70, 80, 90]
beauty2_rate = .25
consultation = 300; consultation_public = 150
follow_up = 160; follow_up_public = 80
quarantine = 100; quarantine_public = 50
vaccination = [600/12, 900/12, 800/12, 800/12, 800/12]
vaccination_public = [50/12, 400/12, 400/12, 400/12, 400/12]
surgery = [321, 993.32, 1519.75, 2085.79, 2700]
surgery_public = [75.8, 55.1, 74.6, 102.8, 133.24]
sterilization_male = [1048.35, 104.835, 20.967, 10.4835, 4.1934]
sterilization_female = [1129.85, 112.985, 22.597, 11.2985, 4.5194]
sterilization_male_public = [230.45,	23.045,	4.609,	2.3045,	0.9218]
sterilization_female_public = [268.7,	26.87,	5.374,	2.687,	1.0748]

def premium_calculation_private(weight, age, pet_sex = None,
                        pet_type = None, neuter = None,
                        term = None, deductible_rate = None, reimbursement_rate = None,
                        cover_consultation = None, cover_rabies_vax = None, cover_dhppil = None,
                        cover_corona_vax = None, cover_lyme_vax = None, cover_bordetella = None):
    if age <= 1:
        age_idx = 0
    elif 2 <= age <= 4:
        age_idx = 1
    elif 5 <= age <= 6:
        age_idx = 2
    elif 7 <= age <= 8:
        age_idx = 3
    else: 
        age_idx = 4

    if weight <= 15:
        weight_idx1 = 0
    elif 16 <= weight <= 50:
        weight_idx1 = 1
    else:
        weight_idx1 = 2

    if weight <= 10:
        weight_idx2 = 0
    elif 11 <= weight <= 20:
        weight_idx2 = 1
    else:
        weight_idx2 = 2

    funeral_fee = (humane_destruction * funeral_rates[age_idx] + 
                   cremation[weight_idx1] * cremation_rates[weight_idx1] + 
                   corpse[weight_idx1] * corpse_rates[weight_idx1])
    staycation_fee = staycation[weight_idx1] * staycation_rate[age_idx] * 3
    beauty_fee = (beauty1[weight_idx2] * beauty1_rate[weight_idx2] + 
                  beauty2[weight_idx2] * beauty2_rate)
    surgery_fee = surgery[age_idx]

    # Covered for consultation and vaccination
    # for staycation, since there will be tier, so need to decide what days for tier, then have the fee * days
    # default it 5 days per month
    base_premium = (funeral_fee
                  + staycation_fee
                  + beauty_fee
                  + surgery_fee)

    net_premium = base_premium * (1 - deductible_rate) * reimbursement_rate

    if cover_consultation:
        net_premium += consultation   + follow_up*0.4 \
                     + quarantine     + 60*0.05
    if cover_rabies_vax:
        net_premium += vaccination[0]
    if cover_dhppil:
        net_premium += vaccination[1]
    if cover_corona_vax:
        net_premium += vaccination[2]
    if cover_lyme_vax:
        net_premium += vaccination[3]
    if cover_bordetella:
        net_premium += vaccination[4]
    if neuter == '是':
        if [pet_sex] == '男仔':
            net_premium -= sterilization_male
        else:
            net_premium -= sterilization_female

    if term == 12:
        total_monthly_premium = net_premium * 1.0 * term
        extra_premium = net_premium * 0
        total_extra_premium = extra_premium * term
    elif term == 6:
        total_monthly_premium = net_premium * 1.05 * term
        extra_premium = net_premium * .05
        total_extra_premium = extra_premium * term
    else:
        total_monthly_premium = net_premium * 1.1 * term
        extra_premium = net_premium * .1
        total_extra_premium = extra_premium * term

    return round(total_monthly_premium, 2), round(extra_premium, 2), round(total_extra_premium, 2)



def premium_calculation_public(weight = None, age = None, pet_sex = None,
                        pet_type = None, neuter = None,
                        term = None, deductible_rate = None, reimbursement_rate = None,
                        cover_consultation = None, cover_rabies_vax = None, cover_dhppil = None,
                        cover_corona_vax = None, cover_lyme_vax = None, cover_bordetella = None):
    if age <= 1:
        age_idx = 0
    elif 2 <= age <= 4:
        age_idx = 1
    elif 5 <= age <= 6:
        age_idx = 2
    elif 7 <= age <= 8:
        age_idx = 3
    else: 
        age_idx = 4

    if weight <= 15:
        weight_idx1 = 0
    elif 16 <= weight <= 50:
        weight_idx1 = 1
    else:
        weight_idx1 = 2

    if weight <= 10:
        weight_idx2 = 0
    elif 11 <= weight <= 20:
        weight_idx2 = 1
    else:
        weight_idx2 = 2

    funeral_fee = (humane_destruction_public * funeral_rates[age_idx] + 
                   cremation_public[weight_idx1] * cremation_rates[weight_idx1] + 
                   corpse_public[weight_idx1] * corpse_rates[weight_idx1])
    staycation_fee = staycation_public[weight_idx1] * staycation_rate[age_idx] * 3
    beauty_fee = (beauty1_public[weight_idx2] * beauty1_rate[weight_idx2] + 
                  beauty2_public[weight_idx2] * beauty2_rate)
    surgery_fee = surgery_public[age_idx]

    # Covered for consultation and vaccination
    # for staycation, since there will be tier, so need to decide what days for tier, then have the fee * days
    # default it 5 days per month
    base_premium = (funeral_fee
                  + staycation_fee
                  + beauty_fee
                  + surgery_fee)

    net_premium = base_premium * (1 - deductible_rate) * reimbursement_rate

    if cover_consultation:
        net_premium += consultation   + follow_up*0.4 \
                     + quarantine     + 30*0.05
    if cover_rabies_vax:
        net_premium += vaccination[0]
    if cover_dhppil:
        net_premium += vaccination[1]
    if cover_corona_vax:
        net_premium += vaccination[2]
    if cover_lyme_vax:
        net_premium += vaccination[3]
    if cover_bordetella:
        net_premium += vaccination[4]
    if neuter == '是':
        if [pet_sex] == '男仔':
            net_premium -= sterilization_male
        else:
            net_premium -= sterilization_female

    
    if term == 12:
        total_monthly_premium = net_premium * 1.0 * term
        extra_premium = net_premium * 0
        total_extra_premium = extra_premium * term
    elif term == 6:
        total_monthly_premium = net_premium * 1.05 * term
        extra_premium = net_premium * .05
        total_extra_premium = extra_premium * term
    else:
        total_monthly_premium = net_premium * 1.1 * term
        extra_premium = net_premium * .1
        total_extra_premium = extra_premium * term


    return round(total_monthly_premium, 2), round(extra_premium, 2), round(total_extra_premium, 2)



# Work on Public_plan premium calculation
# Work on cat maybe? See if there's any data about the fee
# Work on QR code, ads, picture, icon, add some photo to the button, maybe some gif?
# Set Regulations
# Seasonal factors
# Claims after purchasing immediately? No
# Marketing Stratergies:
# Multiple Pets discounts, refer discounts, 
# Adjust the premium? May or May not, increase or decrease, based on everything
# First 300 member have some special benefits?
# Claim forms! Very important, recall how to prevent fraud, maybe use creditibility model
