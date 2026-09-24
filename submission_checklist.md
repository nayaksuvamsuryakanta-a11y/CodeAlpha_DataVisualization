# CodeAlpha Internship — Task 3 Submission Checklist
## Netflix Data Visualization | Suvam Suryakanta Nayak

---

### Deliverable Checklist

- [ ] **Task 3 completed within the internship time frame**
      - Notebook runs end-to-end without errors
      - Script `src/generate_figures.py` runs without errors
      - All 13 figures saved to `visuals/` at 300 dpi
      - Dashboard PNG (`visuals/00_dashboard.png`) generated

- [ ] **GitHub repository named `CodeAlpha_DataVisualization`** (format: CodeAlpha_ProjectName)
      - Full source code uploaded (notebook + script + README + requirements.txt)
      - `.gitignore` excludes large data files
      - `data/` folder contains a `.gitkeep` and setup instructions in README

- [ ] **LinkedIn: Internship status post** tagging @CodeAlpha
      - Post text prepared (see `linkedin_content.md`)
      - Posted publicly on LinkedIn

- [ ] **LinkedIn: Project video post**
      - 2–3 minute walkthrough video recorded
      - Post includes GitHub repo link and @CodeAlpha tag
      - Post text prepared (see `linkedin_content.md`)

- [ ] **Official submission form submitted**
      - Use the form link shared in the CodeAlpha WhatsApp group
      - Submit before the deadline

---

### Certificate Requirement Reminder
> ⚠️ The CodeAlpha completion certificate requires **at least 2 tasks completed**.
> Task 3 alone is NOT sufficient. Ensure at least one other task is also submitted.

| Task | Status |
|------|--------|
| Task 1 | [ ] Complete |
| Task 2 | [ ] Complete |
| Task 3 — Data Visualization | [x] Complete |

---

### Quick Verification Commands
```bash
# Confirm all figures generated
ls visuals/

# Re-run script to verify no errors
python src/generate_figures.py

# Validate notebook runs clean
jupyter nbconvert --to notebook --execute notebooks/netflix_visualization.ipynb --output notebooks/netflix_visualization_executed.ipynb
```

---
_Generated as part of CodeAlpha Data Analytics Internship — Task 3_
