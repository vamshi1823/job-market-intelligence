import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import os

DB_PATH = "Data/jobs.db"
CHARTS_DIR = "charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

print("Running analysis...\n")

# Insight 1: Top 10 highest paying roles
df1 = pd.read_sql("""
    SELECT job_title,
           ROUND(AVG(salary_in_usd), 0) AS avg_salary,
           COUNT(*) AS job_count
    from jobs
    GROUP BY job_title
    HAVING job_count >= 30
    ORDER BY avg_salary DESC
    LIMIT 10
""", conn)
print("Top 10 highest paying roles:")
print(df1.to_string(index=False))

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(df1['job_title'][::-1], df1['avg_salary'][::-1], color='#2563EB')
ax.set_xlabel('Average Salary (USD)')
ax.set_title('Top 10 Highest Paying AI/Data Roles')
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
plt.tight_layout()
plt.savefig(f'{CHARTS_DIR}/top_paying_roles.png', dpi=150)
plt.close()
print("ok Saved: top_paying_roles.png\n")

# Insight 2: Salary by experience level
df2 = pd.read_sql("""
    SELECT experience_level,
           ROUND(AVG(salary_in_usd), 0) AS avg_salary,
           COUNT(*) AS count
    from jobs
    GROUP BY experience_level
    ORDER BY avg_salary
""", conn)
print("Salary by experience level:")
print(df2.to_string(index=False))

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(df2['experience_level'], df2['avg_salary'],
       color=['#93C5FD', '#3B82F6', '#1D4ED8', '#1E3A8A'])
ax.set_xlabel('Experience Level')
ax.set_ylabel('Average Salary (USD)')
ax.set_title('Average Salary by Experience Level')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
plt.tight_layout()
plt.savefig(f'{CHARTS_DIR}/salary_by_experience.png', dpi=150)
plt.close()
print("ok Saved: salary_by_experience.png\n")

# Insight 3: Remote work vs salary
df3 = pd.read_sql("""
    SELECT
        CASE remote_ratio
            WHEN 0   THEN 'On-site'
            WHEN 50  THEN 'Hybrid'
            WHEN 100 THEN 'Fully Remote'
        END AS work_type,
        ROUND(AVG(salary_in_usd), 0) AS avg_salary,
        COUNT(*) AS count
    from jobs
    GROUP BY remote_ratio
    ORDER BY remote_ratio
""", conn)
print("Salary by remote work type:")
print(df3.to_string(index=False))

fig, ax = plt.subplots(figsize=(7, 5))
ax.bar(df3['work_type'], df3['avg_salary'],
       color=['#F87171', '#FB923C', '#4ADE80'])
ax.set_xlabel('Work Type')
ax.set_ylabel('Average Salary (USD)')
ax.set_title('Average Salary: On-site vs Hybrid vs Remote')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
plt.tight_layout()
plt.savefig(f'{CHARTS_DIR}/salary_by_remote.png', dpi=150)
plt.close()
print("ok Saved: salary_by_remote.png\n")

# Insight 4: Salary growth over years
df4 = pd.read_sql("""
    SELECT work_year,
           ROUND(AVG(salary_in_usd), 0) AS avg_salary,
           COUNT(*) AS count
    from jobs
    WHERE work_year >= 2020
    GROUP BY work_year
    ORDER BY work_year
""", conn)
print("Salary trend by year:")
print(df4.to_string(index=False))

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(df4['work_year'], df4['avg_salary'], marker='o',
        linewidth=2.5, color='#7C3AED', markersize=8)
ax.fill_between(df4['work_year'], df4['avg_salary'], alpha=0.1, color='#7C3AED')
ax.set_xlabel('Year')
ax.set_ylabel('Average Salary (USD)')
ax.set_title('AI/Data Salary Trend 2020-2025')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
plt.tight_layout()
plt.savefig(f'{CHARTS_DIR}/salary_trend.png', dpi=150)
plt.close()
print("ok Saved: salary_trend.png\n")

# Insight 5: Top 10 countries by avg salary
df5 = pd.read_sql("""
    SELECT company_location,
           ROUND(AVG(salary_in_usd), 0) AS avg_salary,
           COUNT(*) AS count
    from jobs
    GROUP BY company_location
    HAVING count >= 20
    ORDER BY avg_salary DESC
    LIMIT 10
""", conn)
print("Top 10 countries by average salary:")
print(df5.to_string(index=False))

fig, ax = plt.subplots(figsize=(9, 5))
ax.barh(df5['company_location'][::-1], df5['avg_salary'][::-1], color='#0891B2')
ax.set_xlabel('Average Salary (USD)')
ax.set_title('Top 10 Countries by Average AI/Data Salary')
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
plt.tight_layout()
plt.savefig(f'{CHARTS_DIR}/salary_by_country.png', dpi=150)
plt.close()
print("ok Saved: salary_by_country.png\n")

conn.close()
print("ok All 5 charts generated successfully!")