import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

st.set_page_config(
    page_title="Job Market Intelligence",
    layout="wide"
)

st.title("Job Market Intelligence Dashboard")
st.caption("Analyzing 71,913 real AI/Data salary records from 2020-2025 | Built with Python, SQLite and Streamlit")

DB_PATH = "Data/jobs.db"

conn = sqlite3.connect(DB_PATH, check_same_thread=False)

total = pd.read_sql("SELECT COUNT(*) AS n FROM jobs", conn).iloc[0, 0]
avg_sal = pd.read_sql("SELECT ROUND(AVG(salary_in_usd), 0) AS s FROM jobs", conn).iloc[0, 0]
remote_pct = pd.read_sql("""
    SELECT ROUND(100.0 * SUM(CASE WHEN remote_ratio=100 THEN 1 ELSE 0 END) / COUNT(*), 1) AS p
    FROM jobs
""", conn).iloc[0, 0]
top_role = pd.read_sql("""
    SELECT job_title FROM jobs
    GROUP BY job_title ORDER BY COUNT(*) DESC LIMIT 1
""", conn).iloc[0, 0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Records", f"{total:,}")
c2.metric("Avg Salary (USD)", f"${avg_sal:,.0f}")
c3.metric("Fully Remote %", f"{remote_pct}%")
c4.metric("Most Common Role", top_role)

st.divider()

tab1, tab2, tab3 = st.tabs(["Salary Insights", "Trends", "Explorer"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Highest Paying Roles")
        df1 = pd.read_sql("""
            SELECT job_title,
                   ROUND(AVG(salary_in_usd), 0) AS avg_salary,
                   COUNT(*) AS count
            FROM jobs
            GROUP BY job_title
            HAVING count >= 30
            ORDER BY avg_salary DESC
            LIMIT 10
        """, conn)
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh(df1['job_title'][::-1], df1['avg_salary'][::-1], color='#2563EB')
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
        ax.set_xlabel('Avg Salary (USD)')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.subheader("Salary by Experience Level")
        df2 = pd.read_sql("""
            SELECT experience_level,
                   ROUND(AVG(salary_in_usd), 0) AS avg_salary
            FROM jobs
            GROUP BY experience_level
            ORDER BY avg_salary
        """, conn)
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.bar(df2['experience_level'], df2['avg_salary'],
               color=['#93C5FD', '#3B82F6', '#1D4ED8', '#1E3A8A'])
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
        ax.set_ylabel('Avg Salary (USD)')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.subheader("Remote Work vs Salary")
    df3 = pd.read_sql("""
        SELECT
            CASE remote_ratio
                WHEN 0   THEN 'On-site'
                WHEN 50  THEN 'Hybrid'
                WHEN 100 THEN 'Fully Remote'
            END AS work_type,
            ROUND(AVG(salary_in_usd), 0) AS avg_salary,
            COUNT(*) AS count
        FROM jobs
        GROUP BY remote_ratio
        ORDER BY remote_ratio
    """, conn)
    st.dataframe(df3, hide_index=True)

with tab2:
    st.subheader("Average Salary Trend 2020-2025")
    df4 = pd.read_sql("""
        SELECT work_year,
               ROUND(AVG(salary_in_usd), 0) AS avg_salary,
               COUNT(*) AS count
        FROM jobs
        WHERE work_year >= 2020
        GROUP BY work_year
        ORDER BY work_year
    """, conn)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df4['work_year'], df4['avg_salary'],
            marker='o', linewidth=2.5, color='#7C3AED', markersize=9)
    ax.fill_between(df4['work_year'], df4['avg_salary'], alpha=0.1, color='#7C3AED')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.set_xlabel('Year')
    ax.set_ylabel('Avg Salary (USD)')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.subheader("Year by year breakdown")
    st.dataframe(df4, hide_index=True)

with tab3:
    st.subheader("Explore the data yourself")

    exp_levels = pd.read_sql("""
        SELECT DISTINCT experience_level FROM jobs ORDER BY experience_level
    """, conn)['experience_level'].tolist()

    selected_exp = st.multiselect(
        "Filter by experience level",
        exp_levels,
        default=exp_levels
    )

    remote_opts = ['On-site', 'Hybrid', 'Fully Remote']
    remote_map = {'On-site': 0, 'Hybrid': 50, 'Fully Remote': 100}
    selected_remote = st.multiselect(
        "Filter by work type",
        remote_opts,
        default=remote_opts
    )
    remote_vals = [remote_map[r] for r in selected_remote]

    if selected_exp and remote_vals:
        exp_str = ', '.join([f"'{e}'" for e in selected_exp])
        remote_str = ', '.join([str(r) for r in remote_vals])
        df_filtered = pd.read_sql(f"""
            SELECT job_title,
                   experience_level,
                   salary_in_usd,
                   work_year,
                   CASE remote_ratio
                       WHEN 0   THEN 'On-site'
                       WHEN 50  THEN 'Hybrid'
                       WHEN 100 THEN 'Remote'
                   END AS work_type,
                   company_location
            FROM jobs
            WHERE experience_level IN ({exp_str})
              AND remote_ratio IN ({remote_str})
            ORDER BY salary_in_usd DESC
            LIMIT 500
        """, conn)
        st.write(f"Showing top 500 results")
        st.dataframe(df_filtered, hide_index=True)
    else:
        st.info("Select at least one option from each filter above.")