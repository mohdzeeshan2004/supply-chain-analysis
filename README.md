# Supply Chain Analytics

An interactive data analytics project for exploring supply-chain revenue, profitability, customer value, product/category performance, and discount impact.

## 🔗 Live Dashboard

**Streamlit:** https://supplychainanalysis.streamlit.app/

The dashboard uses an upload-based workflow. The cleaned dataset is **not stored in the repository**, avoiding large-file/repository size issues.

## 📌 Project Overview

This project analyzes an APL Logistics supply-chain dataset containing more than 180,000 transaction records.

The analysis focuses on:
- Revenue and profit performance
- Profit margins
- Customer value and customer segments
- Product and category performance
- Discount and profitability relationships
- What-if discount scenarios

## 🎯 Objectives

1. Analyze overall supply-chain revenue and profitability.
2. Compare performance across markets and categories.
3. Identify high- and low-value customers.
4. Evaluate product-level and category-level profitability.
5. Examine the relationship between discounts and profit margins.
6. Build an interactive dashboard for business analysis.
7. Generate insights and practical recommendations.

## 🛠️ Technologies

- Python
- Pandas
- NumPy
- Plotly
- Streamlit
- Exploratory Data Analysis (EDA)
- Data Visualization

## 📊 Dashboard Modules

### 1. Revenue & Profit Overview
- Total Sales
- Total Profit
- Profit Margin
- Transactions
- Units Sold
- Average Order Value
- Revenue by Market
- Profit by Market
- Category profitability

### 2. Customer Value Dashboard
- Total Customers
- Average Customer Revenue
- Average Customer Profit
- Top and bottom customers by profit
- Customer segment revenue and profit
- Customer Value Matrix

### 3. Product & Category Performance
- Product revenue and profit
- Product margins
- Top products
- Category profitability
- Category profitability heatmap
- Category performance matrix

### 4. Discount Impact Analyzer
- Discount vs Profit
- Discount vs Profit Margin
- Discount-band analysis
- Discount/profit correlation
- Discount/margin correlation
- What-if discount scenarios

## 📁 Dataset

The cleaned APL Logistics dataset is uploaded directly through the Streamlit application.

The application validates required fields before starting the analysis.

The dataset is intentionally **not included in this GitHub repository** because of its large file size.

## 🔬 Methodology

```text
Dataset
   ↓
Data Cleaning
   ↓
Data Validation
   ↓
Exploratory Data Analysis
   ↓
Business Analysis
   ↓
Interactive Visualization
   ↓
Insights
   ↓
Recommendations
```

## 📝 Project Outputs

- Research Paper
- Executive Analysis
- Interactive Streamlit Dashboard

The Research Paper covers the methodology, EDA, insights, recommendations, limitations, and conclusion.

The Executive Analysis summarizes the major findings and their implications for business decision-makers.

## ⚠️ Limitations

- The analysis is based on the variables available in the supplied dataset.
- The dataset does not contain a suitable order-date field for reliable monthly time-series analysis.
- Correlation does not establish causation.
- The discount what-if analysis is an analytical scenario estimate, not a financial forecast.
- External factors such as fuel costs, infrastructure conditions, macroeconomic factors, and supplier performance are not included unless represented in the dataset.

## 🚀 Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Upload the cleaned CSV when prompted.

## 📦 Repository Structure

```text
Supply-Chain-Analytics/
│
├── app.py
├── requirements.txt
└── README.md
```

## 📈 Project Outcome

The project demonstrates how exploratory data analysis and interactive visualization can transform a large supply-chain dataset into an accessible decision-support tool.

The dashboard enables users to explore revenue, profitability, customer value, product/category performance, and discount-related patterns interactively.

## 👤 Project

**Supply Chain Analytics — Data Science Project**

Built using Python, Pandas, NumPy, Plotly, and Streamlit.
