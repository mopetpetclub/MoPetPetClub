import pandas as pd


data_sources = {
    "funeral": {
        "人道毀滅": 750,
        "火化": {
            "體重15公斤或以下的動物": 750,
            "體重16公斤至50公斤的動物": 1250,
            "體重50公斤以上的動物": 3000,
        },
        "垃圾及廢料的收集及處理": {
            "15公斤或以下": 375,
            "16公斤至50公斤": 500,
            "50公斤以上": 2500,
        }
    },
    "staycation": {
        "15日或以下": {
            "犬隻": {
                "10公斤或以下": 200,
                "11公斤至20公斤": 225,
                "21公斤或以上": 250,
            },
            "貓隻": 150
        },
        "15日或以上": {
            "犬隻": {
                "10公斤或以下": 150,
                "11公斤至20公斤": 175,
                "21公斤或以上": 200,
            },
            "貓隻": 125
        },
        "因無法飼養而將動物交予民政總署": 2500
    },
    "beauty": {
        "沐浴/剪毛": {
            "犬隻": {
                "10公斤或以下": 200,
                "11公斤至20公斤": 220,
                "21公斤或以上": 240,
            },
            "貓隻": 500,
        },
        "刷毛/梳毛": {
            "犬隻": {
                "10公斤或以下": 140,
                "11公斤至20公斤": 160,
                "21公斤或以上": 180,
            },
            "貓隻": 500,
        },
        "修甲": 80,
        "清潔牙齒": 960,
        "運送動物（以無需特別車輛運送為限）": 60,
        "晶片植入": 200
    },
    "consultation": {
        "初診": 300,
        "複診（每次）": 160,
        "隔離檢疫（每日）": {
            "犬隻（每隻）": 100,
            "貓隻（每隻）": 60
        }
    },
    "vaccination": {
        "狂犬病預防疫苗（每劑）": 600,
        "DHPPIL五合一（每劑）": 800,
        "冠狀病毒疫苗": 800,
        "萊姆病": 800,
        "犬咳": 800
    },
    "inspection": {
        "解剖屍體作局部檢查": 5000,
        "動物組織病理診斷": 3000,
        "病歷及檢查報告列印": 1500,
        "X光": 1500,
        "超聲波檢查": 2500,
        "尿液檢查": 2000,
        "糞便檢查": 1500,
        "毛皮檢查": 2000,
        "心電圖檢查": 2500,
        "內窺鏡檢查": 7500,
        "血壓檢查": 1250, 
        "血液檢驗": 4000,
        "病毒/寄生蟲快速檢驗":2500,
        "眼部檢查": 2000
    },
    "treatment": {
        "治療及各種藥物": 1200,
        "鎮靜": 3000,
        "麻醉": 600,
        "輸液治療": 3000,
        "輸血治療": 600,
        "噴霧治療": 2400,
        "導管放置": 1500,
        "傷口包紮": 1500,
        "針灸": 1200,
        "剪修甲": 2400,
        "其他治療": 2400,
    },
    "surgery": {
        "雄犬閹割": 2800,
        "雄貓閹割": 2100,
        "雌犬絕育（卵巢子宮切除）": 3200,
        "雌貓絕育（卵巢子宮切除）": 2400,
        "剖腹產手術": 7000,
        "犬貓子宮蓄膿": 7000,
        "子宮脫垂": 3500,
        "腫瘤切除術": 14000,
        "小手術": 4200,
        "疝復位術": 12600,
        "骨科手術": 35000,
        "眼部手術": 7000,
        "耳部手術": 7000,
        "口腔護理": 7000,
        "鼻臉部矯形手術": 7000,
        "開腹探查": 7000,
        "軟顎過長切除術": 7000,
        "胃腸手術": 14000,
        "泌尿系統手術": 14000,
        "其他外科手術": 35000,
    }
}

def flatten_category(entry):
    rows = []
    def recurse(keys, val):
        if isinstance(val, dict) and not all(isinstance(v, (int, float)) for v in val.values()):
            # 還有更深一層
            for k, v in val.items():
                recurse(keys + [k], v)
        else:
            if isinstance(val, dict):
                for opt, cost in val.items():
                    rows.append({
                        **{f"Level{i+1}": keys[i] for i in range(len(keys))},
                        "Option": opt,
                        "Cost": cost
                    })
            else:
                rows.append({
                    **{f"Level{i+1}": keys[i] for i in range(len(keys))},
                    "Option": keys[-1],
                    "Cost": val
                })
    recurse([], entry)
    return pd.DataFrame(rows)

# 建立每個服務分類的 DataFrame
dfs = {}
for category, content in data_sources.items():
    df = flatten_category(content)
    dfs[category] = df

# 如果要寫成多張表的 Excel
output_path = "services_each_sheet.xlsx"
with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
    for name, df in dfs.items():
        df.to_excel(writer, sheet_name=name, index=False)