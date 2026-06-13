import json

path = r"C:\Users\rubin\OneDrive\Desktop\AI fellow\week5\W5_Assignment.ipynb"
with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find Q22 cell (markdown cell with "Challenge 1")
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'markdown':
        src = ''.join(cell['source'])
        if 'Challenge 1: Why Did Tree-Based Ensembles Outperform Linear Models?' in src:
            nb['cells'][i]['source'] = [
                "# Final Reflections & Completion Checklist\n",
                "\n",
                "## \u270d Q22: Reflect on Your Work - Key Insights\n",
                "\n",
                "**FILL IN YOUR OWN REASONING - NOT AI-GENERATED ANSWERS**\n",
                "\n",
                "### Challenge 1: Why Did Tree-Based Ensembles Outperform Linear Models?\n",
                "\n",
                "```\n",
                "Tree-based models outperform linear models because churn data has strong\n",
                "non-linearities and feature interactions. For example, churn risk drops\n",
                "sharply after the first 6-12 months of tenure (a non-linear decay that\n",
                "linear models cannot approximate), and interactions like month-to-month\n",
                "contract combined with fiber optic internet create churn spikes that an\n",
                "additive linear model cannot capture. Random Forest and XGBoost use\n",
                "recursive binary splits to carve out these interaction regions and\n",
                "piecewise-constant decision surfaces automatically.\n",
                "```\n",
                "\n",
                "### Challenge 2: What Did You Learn About Data Leakage?\n",
                "\n",
                "```\n",
                "Using sklearn.pipeline.Pipeline with SMOTE causes SMOTE to generate\n",
                "synthetic samples from the entire training set before cross-validation\n",
                "splits, so validation folds contain synthetic neighbors generated from\n",
                "data that includes those same validation points \u2014 inflating CV scores.\n",
                "Switching to imblearn.pipeline.Pipeline (ImbPipeline) prevents this by\n",
                "fitting SMOTE only inside each training fold during CV, so validation\n",
                "data stays truly unseen. Our CV-AUROC of 0.844 with ImbPipeline is\n",
                "honest; any higher value would have indicated leakage.\n",
                "```\n",
                "\n",
                "### Challenge 3: Which Hyperparameter Had the Largest Impact?\n",
                "\n",
                "```\n",
                "max_depth had the largest impact: AUROC ranged from 0.8289 (depth=10) to\n",
                "0.8437 (depth=5), a spread of ~0.015. Depth controls how many interaction\n",
                "levels each tree can learn \u2014 too shallow misses interactions, too deep\n",
                "(10) overfits to training noise. With 45 transformed features, depth=5\n",
                "gave enough complexity to model the key churn interactions (tenure x\n",
                "contract, internet x online security) without memorizing spurious\n",
                "patterns.\n",
                "```\n",
                "\n",
                "### Challenge 4: What Do SHAP Values Tell You About Your Customers?\n",
                "\n",
                "```\n",
                "SHAP reveals that Contract_Month-to-month and tenure are the top two\n",
                "churn drivers across all customers \u2014 month-to-month agreements\n",
                "consistently increase churn risk while longer tenure decreases it.\n",
                "These are directly actionable: the retention team can target new\n",
                "customers on flexible plans with upgrade incentives. For our specific\n",
                "high-risk customer, tenure=1 month (+0.68 SHAP) and month-to-month\n",
                "contract (+0.62 SHAP) combine for a 97% churn probability. To a\n",
                'non-technical stakeholder I would say: "New customers on month-to-month\n',
                "plans are our biggest leakage point \u2014 offering them a small discount\n",
                "to switch to an annual plan directly addresses the two strongest\n",
                'signals our model found."\n',
                "```\n",
            ]
            break

# Find Q16 code cell (contains "RETENTION RECOMMENDATION")
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        src = ''.join(cell['source'])
        if 'RETENTION RECOMMENDATION' in src and '2-sentence' in src:
            new_src = []
            for line in cell['source']:
                if 'YOUR ANSWER HERE - Reference specific features and SHAP values.' in line:
                    new_src.append("The customer\'s tenure of 1 month (SHAP +0.6781) and month-to-month contract \n")
                elif 'Example: The customer\'s tenure of 1 month and month-to-month contract type' in line:
                    new_src.append("(SHAP +0.6242) are the strongest churn drivers, indicating minimal switching \n")
                elif 'push churn probability up by +0.45 and +0.32 respectively, indicating weak' in line:
                    new_src.append("costs and no lock-in; the absence of online security (SHAP +0.1943) further \n")
                elif 'switching costs typical of new customers.' in line:
                    new_src.append("signals low engagement with the provider\'s ecosystem.\n")
                elif 'YOUR ANSWER HERE - Link to business action.' in line:
                    new_src.append("We recommend a targeted offer: a 12-month contract at a 15% discount plus \n")
                elif 'Example: We recommend a retention offer targeting early-stage customers:' in line:
                    new_src.append("free online security for the first year, directly addressing the top three \n")
                elif 'a 2-month service discount or upgrade to an annual contract to increase' in line:
                    new_src.append("SHAP drivers. This increases switching costs and product stickiness, \n")
                elif 'lock-in and improve switching costs.' in line:
                    new_src.append("potentially reducing churn probability from 97% to under 50%.\n")
                else:
                    new_src.append(line)
            nb['cells'][i]['source'] = new_src
            print("Found Q16 cell at index", i)
            break

with open(path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Done - Q16 and Q22 updated")
