"""
サプライチェーンリスク評価チェックリスト生成ツール
部品カテゴリを入力すると、リスク評価チェックリストをMarkdown形式で出力する
"""

import sys
import os
from datetime import datetime

# Windowsのコンソールでの文字化けを防ぐ
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

# カテゴリ別の追加チェック項目
CATEGORY_SPECIFIC_ITEMS = {
    "半導体": {
        "調達先の地域集中リスク": [
            "台湾・韓国・日本への製造集中度を確認したか",
            "先端ロジック半導体（TSMC・Samsung）への依存度を把握しているか",
            "地政学的リスク（台湾海峡情勢）が調達に与える影響を評価したか",
            "米国輸出規制・対中規制の影響を確認したか",
        ],
        "単一サプライヤー依存リスク": [
            "特定ファウンドリ（TSMC・Intel・Samsung）への依存率を把握しているか",
            "設計会社（Fabless）と製造委託先の両方のリスクを評価したか",
            "EOL（製品生産終了）予定品の在庫確保状況を確認したか",
        ],
        "輸送ルートリスク": [
            "半導体製造装置・材料の調達ルートを確認したか",
            "航空輸送依存品の代替輸送手段を検討したか",
        ],
        "代替調達先の有無": [
            "セカンドソース品・代替品のリストを作成しているか",
            "国内調達（日本製半導体）の選択肢を評価したか",
            "オープンソースIPを活用したカスタム設計の可能性を検討したか",
        ],
        "在庫・リードタイムリスク": [
            "リードタイム（通常52〜104週）を考慮した発注計画があるか",
            "シリコンサイクルに応じた需給変動リスクを評価したか",
            "長期購入契約（LTA）の締結状況を確認したか",
        ],
    },
    "センサー": {
        "調達先の地域集中リスク": [
            "中国・東南アジアの製造拠点への依存度を確認したか",
            "MEMS製造の集中地域（中国・米国・欧州）のリスクを評価したか",
            "日本国内サプライヤーの対応能力を把握しているか",
        ],
        "単一サプライヤー依存リスク": [
            "特定センサーメーカー（Bosch・STMicro・TDK）への依存率を確認したか",
            "カスタム仕様品の場合、代替製造先を特定しているか",
        ],
        "輸送ルートリスク": [
            "精密部品の梱包・輸送基準を満たしているか",
            "温度・湿度管理が必要な品の輸送条件を確認したか",
        ],
        "代替調達先の有無": [
            "同等スペックの代替センサーを事前に評価・認定しているか",
            "評価・認定に必要なリードタイムを考慮した代替計画があるか",
        ],
        "在庫・リードタイムリスク": [
            "キャリブレーション済みセンサーのリードタイムを把握しているか",
            "季節・需要変動に対応した安全在庫水準を設定しているか",
        ],
    },
    "電子部品": {
        "調達先の地域集中リスク": [
            "受動部品（コンデンサ・抵抗）の主要製造国（中国・日本・台湾）を把握しているか",
            "中国製部品への依存度と規制リスクを評価したか",
            "村田製作所・TDK・太陽誘電等の日本メーカーの供給能力を確認したか",
        ],
        "単一サプライヤー依存リスク": [
            "積層セラミックコンデンサ（MLCC）の調達先を複数確保しているか",
            "特定グレード・サイズでの入手難リスクを評価したか",
        ],
        "輸送ルートリスク": [
            "海上輸送・航空輸送のコスト比較と最適化を行っているか",
            "港湾ストライキ・自然災害による遅延リスクを想定しているか",
        ],
        "代替調達先の有無": [
            "主要部品の承認済み代替品（AML: Approved Manufacturers List）を整備しているか",
            "スポット購入の際の信頼できる商社・代理店リストがあるか",
            "偽造品混入リスクへの対策（認定流通チャネルの利用）があるか",
        ],
        "在庫・リードタイムリスク": [
            "部品ごとの適正在庫水準（安全在庫・発注点）を設定しているか",
            "EOL（製品生産終了）情報を定期的に収集しているか",
            "急需対応のためのバッファ在庫を確保しているか",
        ],
    },
}

# 全カテゴリ共通チェック項目
COMMON_ITEMS = {
    "調達先の地域集中リスク": [
        "特定の国・地域に調達が集中していないか確認したか",
        "地政学的リスク（紛争・経済制裁・自然災害）を評価したか",
        "各地域の政治・経済情勢を定期的にモニタリングしているか",
        "カントリーリスクスコアを用いた定量評価を実施しているか",
    ],
    "単一サプライヤー依存リスク": [
        "特定サプライヤーへの依存率（金額ベース・数量ベース）を把握しているか",
        "サプライヤーの財務健全性を定期的に確認しているか",
        "サプライヤーの生産拠点・BCP（事業継続計画）を確認しているか",
        "サプライヤーとの契約に供給保証条項が含まれているか",
    ],
    "輸送ルートリスク": [
        "主要輸送ルートの代替ルートを事前に特定しているか",
        "複数の物流会社・輸送手段を利用しているか",
        "輸送保険の適用範囲と補償額を確認しているか",
        "通関・関税リスク（追加関税・輸出規制）を評価したか",
    ],
    "代替調達先の有無": [
        "メインサプライヤーとは異なる地域に代替調達先を確保しているか",
        "代替調達先の品質認定・評価は完了しているか",
        "緊急調達時の価格・納期条件を事前に確認しているか",
        "代替品への切替に必要な設計変更・認定期間を把握しているか",
    ],
    "在庫・リードタイムリスク": [
        "標準リードタイムと最長リードタイムの両方を把握しているか",
        "需要変動（±何%）に対応できる在庫水準を設定しているか",
        "在庫の陳腐化リスク（有効期限・技術仕様変更）を評価したか",
        "サプライチェーン全体の可視化（Tier2・Tier3まで）ができているか",
    ],
}

# リスクエリアの定義（順序保持のためリストで管理）
RISK_AREAS = [
    "調達先の地域集中リスク",
    "単一サプライヤー依存リスク",
    "輸送ルートリスク",
    "代替調達先の有無",
    "在庫・リードタイムリスク",
]

# 各リスクエリアの重み（合計1.0）
RISK_WEIGHTS = {
    "調達先の地域集中リスク":     0.25,
    "単一サプライヤー依存リスク": 0.25,
    "輸送ルートリスク":           0.15,
    "代替調達先の有無":           0.20,
    "在庫・リードタイムリスク":   0.15,
}

# カテゴリの別名マッピング（入力の柔軟性向上）
CATEGORY_ALIASES = {
    "半導体": ["半導体", "IC", "チップ", "LSI", "マイコン", "CPU", "GPU", "FPGA", "メモリ"],
    "センサー": ["センサー", "センサ", "sensor", "検出器", "検知器"],
    "電子部品": ["電子部品", "部品", "コンデンサ", "抵抗", "コイル", "MLCC", "受動部品", "能動部品"],
}


def get_risk_level(score: float) -> str:
    """スコア（0〜100）をリスクレベル（高・中・低）に変換する"""
    if score <= 30:
        return "低"
    elif score <= 60:
        return "中"
    else:
        return "高"


def score_checklist(category: str) -> dict:
    """各チェック項目にy/nで回答させ、リスクスコアを計算する。

    戻り値の構造:
        {
            "areas": {エリア名: {"score": 0-100, "not_done": int, "total": int}},
            "total": 0-100（重み付き総合スコア）
        }
    スコアは「未対応率 × 100」なので、高いほど高リスク。
    """
    canonical = normalize_category(category)
    specific = CATEGORY_SPECIFIC_ITEMS.get(canonical, {})

    area_scores = {}

    print()
    print("=" * 50)
    print("リスクスコア自動計算モード")
    print("=" * 50)
    print("各項目に対して回答してください：")
    print("  y = 対応済み（リスク低）")
    print("  n = 未対応  （リスク高）")
    print()

    for area in RISK_AREAS:
        items = []
        if area in specific:
            items.extend(specific[area])
        items.extend(COMMON_ITEMS.get(area, []))

        if not items:
            area_scores[area] = {"score": 0.0, "not_done": 0, "total": 0}
            continue

        print(f"【{area}】")
        not_done = 0
        for i, item in enumerate(items, 1):
            while True:
                ans = input(f"  {i}. {item}\n     → (y/n): ").strip().lower()
                if ans in ("y", "yes", "n", "no"):
                    break
                print("     ※ y または n で入力してください")
            if ans in ("n", "no"):
                not_done += 1
        print()

        area_score = (not_done / len(items)) * 100
        area_scores[area] = {
            "score": area_score,
            "not_done": not_done,
            "total": len(items),
        }

    # 重み付き総合スコア
    total_score = sum(
        area_scores[area]["score"] * RISK_WEIGHTS.get(area, 0)
        for area in RISK_AREAS
    )

    return {"areas": area_scores, "total": total_score}


def normalize_category(input_category: str) -> str:
    """入力カテゴリを正規化する"""
    input_lower = input_category.strip()
    for canonical, aliases in CATEGORY_ALIASES.items():
        if any(alias in input_lower for alias in aliases):
            return canonical
    return input_lower


def generate_checklist(category: str, scores: dict = None) -> str:
    """チェックリストのMarkdownを生成する。

    scores: score_checklist() の戻り値。指定するとスコアを総合評価テーブルに埋め込む。
    """
    canonical = normalize_category(category)
    specific = CATEGORY_SPECIFIC_ITEMS.get(canonical, {})

    today = datetime.now().strftime("%Y年%m月%d日")
    lines = [
        f"# サプライチェーンリスク評価チェックリスト",
        f"",
        f"**対象カテゴリ：** {category}",
        f"**作成日：** {today}",
        f"",
        f"---",
        f"",
        f"> このチェックリストは調達リスクの洗い出しを目的としています。",
        f"> 各項目を確認し、問題がある場合は対応策を検討してください。",
        f"",
    ]

    # スコアがある場合はサマリーバナーを先頭に追加
    if scores:
        total = scores["total"]
        level = get_risk_level(total)
        lines += [
            f"## リスクスコアサマリー",
            f"",
            f"**総合リスクスコア：{total:.1f} / 100　（{level}リスク）**",
            f"",
            f"| リスク区分 | スコア | レベル | 未対応数 / 全項目数 |",
            f"|-----------|--------|--------|-------------------|",
        ]
        for area in RISK_AREAS:
            a = scores["areas"].get(area, {})
            s = a.get("score", 0.0)
            lv = get_risk_level(s)
            nd = a.get("not_done", 0)
            tot = a.get("total", 0)
            lines.append(f"| {area} | {s:.1f} | {lv} | {nd} / {tot} |")
        lines += ["", "---", ""]

    for area in RISK_AREAS:
        lines.append(f"## {area}")
        lines.append("")

        # カテゴリ固有の項目を先に追加
        if area in specific:
            for item in specific[area]:
                lines.append(f"- [ ] {item}")

        # 共通項目を追加
        for item in COMMON_ITEMS.get(area, []):
            lines.append(f"- [ ] {item}")

        lines.append("")

    # 総合評価テーブル（スコアがある場合は自動入力）
    if scores:
        table_rows = []
        for area in RISK_AREAS:
            a = scores["areas"].get(area, {})
            lv = get_risk_level(a.get("score", 0.0))
            table_rows.append(f"| {area} | {lv} | |")
        total_level = get_risk_level(scores["total"])
        total_label = f"{total_level}（スコア：{scores['total']:.1f}）"
    else:
        table_rows = [
            "| 調達先の地域集中リスク | | |",
            "| 単一サプライヤー依存リスク | | |",
            "| 輸送ルートリスク | | |",
            "| 代替調達先の有無 | | |",
            "| 在庫・リードタイムリスク | | |",
        ]
        total_label = "（高・中・低）"

    lines += [
        "---",
        "",
        "## 総合評価",
        "",
        "| リスク区分 | 評価（高・中・低） | 対応策・コメント |",
        "|-----------|-----------------|----------------|",
    ]
    lines.extend(table_rows)
    lines += [
        "",
        f"**総合リスクレベル：** {total_label}",
        "",
        "**次回レビュー予定日：**",
        "",
        "**担当者：**",
        "",
    ]

    return "\n".join(lines)


def save_checklist(content: str, category: str, output_dir: str = ".") -> str:
    """チェックリストをファイルに保存する"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_category = category.replace("/", "_").replace("\\", "_").replace(" ", "_")
    filename = f"checklist_{safe_category}_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


def main():
    # コマンドライン引数またはインタラクティブ入力でカテゴリを受け取る
    if len(sys.argv) > 1:
        category = " ".join(sys.argv[1:])
    else:
        print("=" * 50)
        print("サプライチェーンリスク評価チェックリスト生成ツール")
        print("=" * 50)
        print()
        print("対応カテゴリ例：半導体、センサー、電子部品")
        print("  （上記以外のカテゴリも入力可能です）")
        print()
        category = input("部品カテゴリを入力してください: ").strip()

    if not category:
        print("エラー：カテゴリが入力されていません。")
        sys.exit(1)

    # スコアリングモードの選択
    print()
    mode_input = input("リスクスコアを自動計算しますか？ (y/n): ").strip().lower()
    scores = None
    if mode_input in ("y", "yes", ""):
        scores = score_checklist(category)
        print("-" * 50)
        print(f"総合リスクスコア：{scores['total']:.1f} / 100　（{get_risk_level(scores['total'])}リスク）")
        print("-" * 50)

    # チェックリスト生成
    checklist = generate_checklist(category, scores=scores)

    # 画面出力
    print()
    print(checklist)

    # ファイル保存の確認
    print()
    save_input = input("ファイルに保存しますか？ (y/n): ").strip().lower()
    if save_input in ("y", "yes", ""):
        filepath = save_checklist(checklist, category)
        print(f"保存しました：{filepath}")


if __name__ == "__main__":
    main()
