# Git Commands — CodeAlpha_DataVisualization
# Run these from the PARENT folder of CodeAlpha_DataVisualization/
# Replace YOUR_USERNAME with your actual GitHub username

# ─── Step 1: Navigate into the project folder ────────────────────────────────
cd CodeAlpha_DataVisualization

# ─── Step 2: Initialize git repo ─────────────────────────────────────────────
git init

# ─── Step 3: Set your identity (if not already configured globally) ──────────
git config user.name "Suvam Suryakanta Nayak"
git config user.email "your.email@example.com"

# ─── Step 4: Stage all files ─────────────────────────────────────────────────
git add .

# ─── Step 5: Initial commit ───────────────────────────────────────────────────
git commit -m "Initial commit: Netflix Data Visualization — CodeAlpha Task 3

- Jupyter notebook with 12 charts + dashboard
- Standalone Python script (src/generate_figures.py)
- 5 business questions answered with data
- README, requirements.txt, submission checklist
- Colorblind-friendly palette, 300 dpi exports"

# ─── Step 6: Create the GitHub repo ─────────────────────────────────────────
# Go to https://github.com/new
# Repository name: CodeAlpha_DataVisualization
# Description:     Netflix Movies & TV Shows Data Visualization — CodeAlpha Internship Task 3
# Visibility:      Public
# Do NOT initialize with README (we already have one)
# Click "Create repository"

# ─── Step 7: Add remote and push ─────────────────────────────────────────────
git remote add origin https://github.com/YOUR_USERNAME/CodeAlpha_DataVisualization.git
git branch -M main
git push -u origin main

# ─── Step 8: After running the notebook/script, commit the visuals ───────────
# (Run notebook or: py src/generate_figures.py)
# Then:
git add visuals/
git commit -m "Add generated visuals (12 charts + dashboard at 300 dpi)"
git push

# ─── Done! ───────────────────────────────────────────────────────────────────
# Your repo will be at:
# https://github.com/YOUR_USERNAME/CodeAlpha_DataVisualization
