
import matplotlib.pyplot as plt 
import seaborn as sns
import numpy as np
import ast
import statsmodels.api as sm
import pandas as pd
from sklearn.preprocessing import LabelEncoder

full_data = pd.read_csv("projects/hiring_cafe/job_listings_big.csv")

selected_df = pd.read_csv("projects/hiring_cafe/job_listings_selected_big.csv")

## plots

# salary

## basic plot
salary = selected_df['job_data.yearly_min_compensation']
plot_data = salary[salary.between(10_000, 500_000)]

plt.figure(figsize=(10, 6))
sns.histplot(plot_data, bins=30, kde=True, alpha=0.7)
plt.xlabel('Yearly Min Compensation ($)')
plt.ylabel('Density')
plt.title('Salary Distribution')
plt.tight_layout()
plt.show()

## salaries by sector
sector = (selected_df['job_data.company_sector_and_industry']
    .value_counts()
    .reset_index()
    .sort_values('count', ascending=False)
    .head(8)
    )

salary_sector = selected_df[['job_data.yearly_min_compensation', 'job_data.company_sector_and_industry']]
salary_sector_plot = salary_sector[
    (salary_sector['job_data.yearly_min_compensation'].between(10_000, 500_000)) &
    (salary_sector['job_data.company_sector_and_industry'].isin(sector['job_data.company_sector_and_industry']))
]
sector_order = salary_sector_plot['job_data.company_sector_and_industry'].value_counts().index.tolist()

sns.catplot(
    data=salary_sector_plot,
    x='job_data.company_sector_and_industry',
    y='job_data.yearly_min_compensation',
    kind='box',
    order=sector_order  # This orders by frequency
)
plt.xticks(rotation=90)
plt.xlabel('Sector')
plt.ylabel('Salary ($)')
plt.title('Salary by Sector (Ordered by Frequency)')
plt.tight_layout()
plt.show()


## by YoE/level

salary_yoe = selected_df[['job_data.yearly_min_compensation', 'job_data.seniority_level']]
salary_yoe_plot = salary_yoe[
    (salary_sector['job_data.yearly_min_compensation'].between(10_000, 500_000))
]
yoe_order = ['No Prior Experience Required', 'Entry Level', 'Mid Level', 'Senior Level']

sns.catplot(
    data=salary_yoe_plot,
    x='job_data.seniority_level',
    y='job_data.yearly_min_compensation',
    kind='box',
    order=yoe_order 
)
plt.xticks(rotation=90)
plt.xlabel('Seniority Level')
plt.ylabel('Salary ($)')
plt.title('Salary by Level of Seniority')
plt.tight_layout()
plt.show()


## by workplace state
salary_state = selected_df[['job_data.yearly_min_compensation', 'job_data.workplace_states']]

states = (selected_df[
    (selected_df['job_data.workplace_states'].notna()) & 
    (selected_df['job_data.workplace_states'] != "") &
    (selected_df['job_data.workplace_states'] != "[]")
]
    ['job_data.workplace_states']
    .value_counts()
    .head(10)
    .reset_index()
)

salary_state_plot = salary_state[
    (salary_sector['job_data.yearly_min_compensation'].between(10_000, 500_000)) &
    (salary_state['job_data.workplace_states'].isin(states['job_data.workplace_states']))
]

state_order = salary_state_plot['job_data.workplace_states'].value_counts().index.tolist()

salary_state_plot['job_data.workplace_states'] = salary_state_plot['job_data.workplace_states'].apply(
    lambda x: ', '.join(ast.literal_eval(x)) if isinstance(x, str) else x
)

state_order = salary_state_plot['job_data.workplace_states'].value_counts().index.tolist()

def parse_states(x):
    if not isinstance(x, str) or x in ['', '[]', 'nan']:
        return x
    try:
        return ', '.join(ast.literal_eval(x)).replace(', US', '')
    except (ValueError, SyntaxError):
        return x

salary_state_plot = salary_state_plot.copy()
salary_state_plot['job_data.workplace_states'] = salary_state_plot['job_data.workplace_states'].apply(parse_states)


sns.catplot(
    data=salary_state_plot,
    x='job_data.workplace_states',
    y='job_data.yearly_min_compensation',
    kind='box',
    order=state_order
)

plt.xticks(rotation=90)
plt.xlabel('State')
plt.ylabel('Salary ($)')
plt.title('Salary by State')
plt.tight_layout()
plt.show()

## salary ~ applications
selected_df['applicant_count'] = selected_df['job_info.appliedFromUsers'].apply(
    lambda x: len(ast.literal_eval(x)) if isinstance(x, str) and x not in ['', 'nan'] else 0
)

job_summary = selected_df.dropna(subset=['job_data.yearly_min_compensation'])
job_summary = job_summary[
    job_summary['job_data.yearly_min_compensation'].between(10_000, 500_000)
]

# Prepare the data
X = job_summary['job_data.yearly_min_compensation']
y = job_summary['applicant_count']

# Add constant for intercept
X = sm.add_constant(X)

# Fit Poisson regression
poisson_model = sm.GLM(y, X, family=sm.families.Poisson()).fit()

poisson_model.summary()

const = poisson_model.params['const']
salary_coef = poisson_model.params['job_data.yearly_min_compensation']

# Convert to IRR (exponentiate)
const_irr = np.exp(const)
salary_irr = np.exp(salary_coef)

# Percent change per unit increase
salary_pct_change = (salary_irr - 1) * 100

interpretable_results = {
    'intercept_irr': const_irr,
    'salary_irr': salary_irr,
    'applicant_pct_change_per_dollar': salary_pct_change,
    'applicant_pct_change_per_10k': (salary_irr**10000 - 1) * 100
}

interpretable_results

# remote vs. hybrid vs. in-office

workplace_salary = selected_df[['job_data.yearly_min_compensation', 'job_data.workplace_type']]
workplace_salary = workplace_salary[(salary_sector['job_data.yearly_min_compensation'].between(10_000, 500_000))]

workplace_type = (workplace_salary['job_data.workplace_type']
    .value_counts()
    .reset_index()
)

type_order = ['Remote', 'Hybrid', 'Onsite']

sns.catplot(
    data=workplace_salary,
    x='job_data.workplace_type',
    y='job_data.yearly_min_compensation',
    kind='box',
    order=type_order
)
plt.xticks(rotation=90)
plt.xlabel('Workplace Type')
plt.ylabel('Salary ($)')
plt.title('Salary by Workplace Type')
plt.tight_layout()
plt.show()

### job titles

job_titles_count = selected_df_unpacked['job_data.core_job_title'].value_counts().reset_index()

### skills

# Parse the string representation to actual lists
selected_df['job_data.technical_tools'] = selected_df['job_data.technical_tools'].apply(
    lambda x: ast.literal_eval(x) if isinstance(x, str) else x
)
selected_df['job_data.workplace_states'] = selected_df['job_data.workplace_states'].apply(
    lambda x: ast.literal_eval(x) if isinstance(x, str) else x
)

# Explode the list into separate rows
selected_df_unpacked = selected_df.explode('job_data.technical_tools')
selected_df_unpacked['job_data.technical_tools'] = selected_df_unpacked['job_data.technical_tools'].str.lower()
selected_df_unpacked = selected_df_unpacked.explode('job_data.workplace_states')
selected_df_unpacked['job_data.workplace_states'] = selected_df_unpacked['job_data.workplace_states'].str.lower()

technical_tools_count = selected_df_unpacked['job_data.technical_tools'].value_counts().reset_index()

technical_tools_count[technical_tools_count['count'] > 50]

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import StrOutputParser

unique_skills = technical_tools_count[technical_tools_count['count'] > 5].sort_values(['job_data.technical_tools']).reset_index()

llm = OllamaLLM(model="qwen2.5:7b", temperature=0)

prompt_template = ChatPromptTemplate.from_template(
    """Standardize these technical skills to common names. 
    For each skill, provide ONLY a more generalized skill. For specific applications or software packages (e.g., transformers, tensorflow, tableau), retain the original name.

    For instance: 'R programming' --> 'R', 'statistical modeling' --> 'statistics', 'statsmodels' --> 'statsmodels', 'unix' --> 'unix', 'tensorflow' --> 'tensorflow'
    
    Skills to standardize:
    {skills}
    
    Return as a Python dictionary mapping original -> standardized name. Example:
    {{'python 3': 'python', 'py': 'python'}}"""
)

chain = prompt_template | llm | StrOutputParser()
result = chain.invoke({"skills": "python 3\njs\nreact.js"})


import json
import re

batch_size = 50
skills = unique_skills['job_data.technical_tools']
all_mappings = []

for i in range(0, len(skills), batch_size):
    batch = skills[i:i+batch_size]
    result = chain.invoke({"skills": str(batch)})
    match = re.search(r'```(?:python)?\s*(\{.*?\})\s*```', result, re.DOTALL)
    result_clean = match.group(1)
    try:
        batch_mapping = ast.literal_eval(result_clean)
        for original, standardized in batch_mapping.items():
            all_mappings.append({'original': original, 'standardized': standardized})
    except (ValueError, SyntaxError) as e:
        print(f"Skipped batch at index {i}: {e}")
        continue
    print(i)



skill_mappings_df = pd.DataFrame(all_mappings)

selected_df_unpacked = (selected_df_unpacked.merge(
    skill_mappings_df,
    left_on='job_data.technical_tools',
    right_on='original',
    how='inner'
).rename(columns={'standardized': 'job_data.technical_tools'})
.drop('original', axis=1)
)

## 

## model

# Prepare the data
model_df = selected_df_unpacked[[
    'job_data.yearly_min_compensation',
    'job_data.workplace_type',
    'job_data.workplace_states',
    'job_data.seniority_level',
    'job_data.min_industry_and_role_yoe',
    'job_data.technical_tools'
]].copy()

# Remove rows with missing values
model_df = model_df.dropna()

# Filter salary to reasonable range
model_df = model_df[
    model_df['job_data.yearly_min_compensation'].between(10_000, 500_000)
]

# Create dummy variables for categorical features
model_df_encoded = pd.get_dummies(
    model_df,
    columns=[
        'job_data.workplace_type',
        'job_data.workplace_states',
        'job_data.seniority_level',
        'job_data.technical_tools'
    ],
    drop_first=True
)

# Prepare X and y
X = model_df_encoded.drop('job_data.yearly_min_compensation', axis=1).astype(float)
y = np.log(model_df_encoded['job_data.yearly_min_compensation'].astype(float))

# Fit OLS model
X = model_df_encoded.drop('job_data.yearly_min_compensation', axis=1).astype(float)
X = sm.add_constant(X)

salary_model = sm.OLS(y, X).fit()

salary_model.summary()

## save model
import pickle

# Save model
with open('projects/hiring_cafe/salary_model.pkl', 'wb') as f:
    pickle.dump(salary_model, f)

# Save column names (needed for prediction)
with open('projects/hiring_cafe/model_columns.pkl', 'wb') as f:
    pickle.dump(X.columns.tolist(), f)

# Save residual standard deviation (for confidence intervals)
residuals = y - salary_model.predict(X)
residual_std = residuals.std()

with open('projects/hiring_cafe/model_residual_std.pkl', 'wb') as f:
    pickle.dump(residual_std, f)


import matplotlib.pyplot as plt
import numpy as np

# Extract coefficients and confidence intervals
coefs = salary_model.params[1:]  # exclude constant
conf_int = salary_model.conf_int().iloc[1:]  # exclude constant

mask = coefs.index.str.contains('technical_tools')
coefs = coefs[mask]
conf_int = conf_int[mask]

# Calculate errors as distance from coef to each CI bound
lower = conf_int.iloc[:, 0].values
upper = conf_int.iloc[:, 1].values
errors = np.array([coefs.values - lower, upper - coefs.values])

# Sort by coefficient value (ascending)
sorted_idx = np.argsort(coefs.values)

# Get 10 lowest and 10 highest
n_display = 10
lowest_idx = sorted_idx[:n_display]
highest_idx = sorted_idx[-n_display:]
combined_idx = np.concatenate([lowest_idx, highest_idx])

coefs_plot = coefs.iloc[combined_idx]
errors_plot = errors[:, combined_idx]

fig, ax = plt.subplots(figsize=(10, 8))
y_pos = np.arange(len(coefs_plot))

ax.errorbar(coefs_plot.values, y_pos, xerr=errors_plot, fmt='o', markersize=6, capsize=5)
ax.axvline(x=0, color='red', linestyle='--', linewidth=1)
ax.set_yticks(y_pos)
ax.set_yticklabels(coefs_plot.index, fontsize=9)
ax.set_xlabel('Coefficient (log scale)')
ax.set_title('Forest Plot: 10 Lowest and 10 Highest Salary Predictors')
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.show()
