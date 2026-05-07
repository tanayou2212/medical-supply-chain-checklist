# Supply Chain Risk Assessment Checklist Generator

A tool that automatically generates procurement risk assessment checklists in Markdown format by entering a component category. Includes automatic numerical risk scoring.

---

## Features

- Generates risk assessment checklists tailored to the component category
- Combines category-specific items with common items
- **Automatic numerical risk scoring** — answer y/n for each item to get a weighted total score (0–100)
- Displays output in Markdown and optionally saves to a file

### Risk Areas Covered

| Risk Area | Description |
|-----------|-------------|
| Geographic Concentration Risk | Dependency on specific countries or regions |
| Single-Supplier Dependency Risk | Number of suppliers and their financial health |
| Transportation Route Risk | Alternative routes and tariff/customs risks |
| Alternative Sourcing | Qualification status of alternative suppliers |
| Inventory & Lead Time Risk | Safety stock levels and procurement lead times |

---

## Requirements

- Python 3.8 or later (no additional libraries required)

---

## Usage

### Method 1: Interactive mode

```bash
python supply_chain_checklist.py
```

You will be prompted to enter a category name, then choose whether to calculate a risk score.

```
==================================================
Supply Chain Risk Assessment Checklist Generator
==================================================

Supported categories: Semiconductors, Sensors, Electronic Components
  (Other categories are also accepted)

Enter component category: Semiconductors

Calculate risk score automatically? (y/n): y
```

If you choose `y`, the tool walks through every checklist item and asks you to answer `y` (addressed) or `n` (not addressed). A numerical score is computed at the end.

### Method 2: Command-line argument

```bash
python supply_chain_checklist.py 半導体
python supply_chain_checklist.py センサー
python supply_chain_checklist.py 電子部品
python supply_chain_checklist.py パワーデバイス
```

---

## Risk Scoring

Each checklist item is answered as:

| Answer | Meaning | Risk contribution |
|--------|---------|-------------------|
| `y` | Addressed | None |
| `n` | Not addressed | Increases score |

**Area score** = (number of "n" answers ÷ total items) × 100

**Total score** = weighted average of all area scores

| Risk Area | Weight |
|-----------|--------|
| Geographic Concentration Risk | 25% |
| Single-Supplier Dependency Risk | 25% |
| Alternative Sourcing | 20% |
| Transportation Route Risk | 15% |
| Inventory & Lead Time Risk | 15% |

**Score interpretation:**

| Score | Level |
|-------|-------|
| 0 – 30 | Low |
| 31 – 60 | Medium |
| 61 – 100 | High |

---

## Sample Output

```markdown
# Supply Chain Risk Assessment Checklist

**Category:** Semiconductors
**Date:** 2026-05-07

---

## Risk Score Summary

**Total Risk Score: 42.3 / 100  (Medium)**

| Risk Area | Score | Level | Not Addressed / Total |
|-----------|-------|-------|-----------------------|
| Geographic Concentration Risk | 50.0 | Medium | 4 / 8 |
| Single-Supplier Dependency Risk | 33.3 | Medium | 2 / 6 |
| Transportation Route Risk | 50.0 | Medium | 3 / 6 |
| Alternative Sourcing | 25.0 | Low | 2 / 8 |
| Inventory & Lead Time Risk | 40.0 | Medium | 4 / 10 |

---

## Geographic Concentration Risk

- [ ] Confirmed degree of manufacturing concentration in Taiwan, South Korea, and Japan
- [ ] Assessed the impact of geopolitical risks (Taiwan Strait situation) on procurement
...

## Overall Assessment

| Risk Area | Assessment (High / Medium / Low) | Action / Comment |
|-----------|----------------------------------|-----------------|
| Geographic Concentration Risk | Medium | |
...

**Total Risk Level:** Medium (Score: 42.3)
```

After the checklist is displayed, press `y` to save it as a file:

```
checklist_半導体_20260507_143022.md
```

---

## Supported Categories

The following categories include detailed category-specific checklist items. Other inputs will display common items only.

| Category | Recognized Keywords |
|----------|---------------------|
| Semiconductors | 半導体, IC, チップ, LSI, マイコン, CPU, GPU, FPGA, メモリ |
| Sensors | センサー, センサ, sensor, 検出器, 検知器 |
| Electronic Components | 電子部品, 部品, コンデンサ, 抵抗, コイル, MLCC, 受動部品, 能動部品 |

---

## File Structure

```
business-automation/
├── supply_chain_checklist.py   # Main script
├── README.md                   # This file (English)
├── README_ja.md                # Japanese version
└── checklist_*.md              # Generated checklists (created at runtime)
```

---

## Customization

Edit the following dictionaries in the script to add or modify checklist items:

- **`CATEGORY_SPECIFIC_ITEMS`** — Category-specific checklist items
- **`COMMON_ITEMS`** — Common items applied to all categories
- **`CATEGORY_ALIASES`** — Keyword aliases for category recognition
- **`RISK_WEIGHTS`** — Weight assigned to each risk area (must sum to 1.0)

Example: to add a "Battery" category, add the following to `CATEGORY_SPECIFIC_ITEMS`:

```python
"バッテリー": {
    "調達先の地域集中リスク": [
        "中国のリチウム・コバルト生産への依存度を確認したか",
        ...
    ],
    ...
}
```

---

## Contact

For questions, please contact the internal person in charge.
