# Week 4 - Telco Churn Assignment

## Task 1: Understand the Problem

This task was completed by first formulating the machine learning problem and inspecting the dataset before any modelling code was written.

### Problem formulation
- Feature space $X$: all customer attributes except `Churn`, including `gender`, `SeniorCitizen`, `Partner`, `Dependents`, `tenure`, `PhoneService`, `MultipleLines`, `InternetService`, `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`, `Contract`, `PaperlessBilling`, `PaymentMethod`, `MonthlyCharges`, and `TotalCharges`.
- Target variable $y$: `Churn` (`Yes` / `No`).
- Natural distribution for $y$: Bernoulli, because churn is a binary outcome.
- Loss function: binary cross-entropy / log loss, which is the negative log-likelihood for a Bernoulli target.

### Key assumptions
- Training and future customers come from the same distribution.
- `Churn` labels are correct and consistently defined.
- All features used for prediction are available before churn happens.
- Customer rows are approximately independent.

### Data uncertainty and quality issues
- `TotalCharges` contains 11 blank / non-numeric values, which appear to correspond to customers with `tenure = 0` and no billing history yet.
- `tenure` has a minimum of 0, which is valid but indicates brand-new customers.
- `MonthlyCharges` is plausible but depends on plan structure, add-ons, and discounts that are only partially captured in the dataset.
- `customerID` is an identifier and should not be used as a predictive feature.

### Distribution profiling
- `MonthlyCharges` is broadly spread and mildly left-skewed / roughly unimodal, with values ranging from 18.25 to 118.75.
- `tenure` is strongly right-skewed, with many customers in early tenure and a long tail up to 72 months.
- `TotalCharges` is strongly right-skewed with a long upper tail; after coercing blanks to missing, its numeric values range from 18.80 to 8684.80.
- Decision: keep `MonthlyCharges` and `tenure` as numeric features, and handle `TotalCharges` blanks explicitly in preprocessing rather than leaving them as raw strings.

### Naive baseline
- Majority class: `No` churn.
- Baseline accuracy: 5174 / 7043 = 73.46%.
- Why this is misleading: the class distribution is imbalanced, so accuracy hides the fact that the model never identifies churners.
- Why this is dangerous: it has zero recall for the minority class and provides no useful retention signal for the business.

### Notebook state
- The notebook includes the written response for Task 1 and a profiling cell that loads the CSV and prints the key summary statistics.

## Task 2: Classification Experiment - Who Will Churn?

This task is set up as a linear-model comparison experiment for predicting `Churn` on an imbalanced dataset.

### Models to compare
- `LogisticRegression`
- `RidgeClassifier`
- `SGDClassifier(loss='log_loss')`

### Evaluation plan
- Train each model on the training split and evaluate on a validation split.
- Compare models using metrics that are appropriate for class imbalance:
	- Accuracy
	- Precision
	- Recall
	- F1
	- ROC-AUC
	- PR-AUC
	- Log Loss
- Rank models primarily by PR-AUC and business usefulness, not by accuracy alone.

### Why these metrics matter
- Accuracy is misleading because the churn rate is only about 27%.
- Precision tells us how many customers flagged as churn-risk are actually likely to churn.
- Recall tells us how many true churners we successfully catch.
- F1 balances precision and recall.
- ROC-AUC measures ranking quality across thresholds.
- PR-AUC is especially informative for imbalanced data because it focuses on the positive class.
- Log loss rewards well-calibrated probabilities and penalises confident wrong predictions.

### Threshold decision under the 200-call budget
- The retention team can only call 200 customers per week.
- The model threshold should be chosen by sorting customers by predicted churn probability and selecting the top 200.
- The deployment threshold is therefore the score of the 200th highest-risk customer.
- This rule prioritises precision at the top of the ranked list and respects the operational budget.

### Coefficient inspection
- Inspect the coefficients of the chosen linear model to identify the strongest churn drivers.
- Check whether the sign and magnitude of each coefficient are consistent with business expectations.
- If a coefficient looks surprising, investigate whether it is caused by correlated features, encoding effects, or data quirks.

### Logistic Regression vs SGDClassifier
- Logistic Regression uses full-batch optimisation and is usually more stable.
- SGDClassifier uses stochastic updates and is usually faster on large datasets.
- They may not converge to exactly the same coefficients because SGD is noisy and more sensitive to learning rate, shuffling, and stopping criteria.
- In this dataset, the comparison should focus on whether SGD reaches a similar validation score faster, not whether the coefficients match exactly.

### Current notebook status
- The notebook contains the full Task 2 workflow: preprocessing, model comparison, ROC / PR curves, threshold tuning, coefficient inspection, and SGD comparison.
- The experiment was run on a stratified validation split.

### Validation results

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC | Log Loss | Fit Time (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Logistic Regression | 0.741477 | 0.507795 | 0.814286 | 0.625514 | 0.844797 | 0.631152 | 0.506153 | 0.120254 |
| Ridge Classifier | 0.729167 | 0.493506 | 0.814286 | 0.614555 | 0.841534 | 0.621803 | N/A | 0.069292 |
| SGD Classifier | 0.750947 | 0.520885 | 0.757143 | 0.617176 | 0.841023 | 0.617132 | 0.472970 | 0.103856 |

### Model choice
- `LogisticRegression` was chosen as the best overall linear classifier because it achieved the strongest ROC-AUC and PR-AUC, and it outputs calibrated probabilities needed for thresholding and log loss.
- `RidgeClassifier` was slightly faster, but it does not provide probabilities, so it is less useful for a retention workflow that depends on risk ranking.
- `SGDClassifier` was competitive but slightly weaker on ROC-AUC and PR-AUC, and its coefficients were not identical to the batch logistic solution.

### ROC / PR interpretation
- The ROC curve for the best model shows good separation from the diagonal, with ROC-AUC of 0.844797.
- The PR curve is more informative here because the data are imbalanced; the average precision is 0.631152, which is substantially above the churn prevalence baseline.

### 200-call threshold
- The retention team can call 200 customers per week.
- The best model’s deployment threshold is the score of the 200th highest-risk validation customer.
- Measured threshold: **0.774943**.
- At that operating point, the model achieves precision 0.6950, recall 0.4964, and F1 0.5792 on the validation split.

### Coefficient interpretation
- Strongest positive churn drivers: `InternetService_Fiber optic`, `TotalCharges`, `StreamingMovies_Yes`, `PaymentMethod_Electronic check`, and `PaperlessBilling_Yes`.
- Strongest negative coefficients: `Contract_Two year`, `tenure`, `Contract_One year`, `MonthlyCharges`, `OnlineSecurity_Yes`, and `TechSupport_Yes`.
- The signs are broadly sensible: long contracts, longer tenure, and support/security features reduce churn risk; fiber and electronic check are associated with higher churn risk.

### SGD vs batch gradient descent
- Logistic Regression fit time: 0.120254 s.
- SGDClassifier fit time: 0.103856 s.
- LogisticRegression ROC-AUC: 0.844797.
- SGDClassifier ROC-AUC: 0.841023.
- Approximate coefficient agreement: false.
- On this dataset, both methods are close in speed, but Logistic Regression is the safer choice because it is more stable and gives calibrated probabilities.
