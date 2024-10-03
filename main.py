import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from func import DataAnalyzer
from babel.numbers import format_currency
sns.set(style='dark')
#st.set_option('deprecation.showPyplotGlobalUse', False)

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("/workspaces/Proyek-Analisis-Data/all_data.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar
with st.sidebar:
    # Title
    st.title("Adilla Rifqi Muhammad")

    # Logo Image
    st.image("/workspaces/Proyek-Analisis-Data/ShopCart.png")

    # Date Range
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Main
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                 (all_df["order_approved_at"] <= str(end_date))]

function = DataAnalyzer(main_df)

daily_orders_df = function.create_daily_orders_df()
sum_spend_df = function.create_sum_spend_df()
sum_order_items_df = function.create_sum_order_items_df()
review_score, common_score = function.review_score_df()
state, most_common_state = function.create_bystate_df()
order_status, common_status = function.create_order_status()

# Title
st.header("E-Commerce Dashboard")

# Daily Orders
st.subheader("Daily Orders")

col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.markdown(f"Total Order: **{total_order}**")

with col2:
    total_revenue = format_currency(daily_orders_df["revenue"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Revenue: **{total_revenue}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Order Items
st.subheader("Order Items")
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Items: **{total_items}**")

with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"Average Items: **{avg_items}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Produk Paling Banyak Terjual", loc="center", fontsize=35)
ax[0].tick_params(axis='y', labelsize=20)

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].yaxis.set_label_position("right")  # Posisikan label di sisi kanan
ax[1].yaxis.tick_right()  # Posisikan tick di sisi kanan
ax[1].set_title("Produk Paling Sedikit Terjual", loc="center", fontsize=35)
ax[1].tick_params(axis='y', labelsize=20)

st.pyplot(fig)

# Review Score
st.subheader("Review Score")
col1,col2 = st.columns(2)

with col1:
    avg_review_score = review_score.mean()
    st.markdown(f"Average Review Score: **{avg_review_score}**")

with col2:
    most_common_review_score = review_score.value_counts().index[0]
    st.markdown(f"Most Common Review Score: **{most_common_review_score}**")

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x=review_score.index, 
            y=review_score.values, 
            order=review_score.index,
            palette=["#068DA9" if score == common_score else "#D3D3D3" for score in review_score.index]
            )

plt.title("Rating by customers for service", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Count")
plt.xticks(fontsize=12)
st.pyplot(fig)

# Number of Orders per Month
st.subheader("Number of Orders per Month")

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

# Buat monthly_df
monthly_df = all_df.resample(rule='ME', on='order_approved_at').agg({
    "order_id": "nunique",
})
monthly_df.index = monthly_df.index.strftime('%B')  # Mengubah format menjadi nama bulan
monthly_df = monthly_df.reset_index()
monthly_df.rename(columns={"order_id": "order_count"}, inplace=True)

# Urutkan bulan
monthly_df = monthly_df.sort_values('order_count').drop_duplicates('order_approved_at', keep='last')
month_mapping = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5,
    "June": 6, "July": 7, "August": 8, "September": 9, "October": 10,
    "November": 11, "December": 12
}
monthly_df["month_numeric"] = monthly_df["order_approved_at"].map(month_mapping)
monthly_df = monthly_df.sort_values("month_numeric")
monthly_df = monthly_df.drop("month_numeric", axis=1)

# Buat plot
fig, ax = plt.subplots(figsize=(12, 6))

# Plot dengan penyesuaian visual
ax.plot(
    monthly_df["order_approved_at"],
    monthly_df["order_count"],
    marker='o',
    markersize=8,  # Ukuran marker
    linewidth=3,   # Lebar garis
    color="#4A90E2",  # Warna garis
    markerfacecolor="#F5A623",  # Warna isi marker
    markeredgewidth=2,  # Ketebalan garis luar marker
    markeredgecolor="#FF6F61"  # Warna garis luar marker
)

# Tambahkan grid
ax.grid(True, which="both", linestyle='--', linewidth=0.7, alpha=0.7)

# Set judul dan label sumbu dengan penyesuaian visual
ax.set_xlabel("Month", fontsize=14, labelpad=10)
ax.set_ylabel("Number of Orders", fontsize=14, labelpad=10)

# Set tampilan sumbu x dan y
ax.tick_params(axis='x', labelsize=12, rotation=30, labelcolor="#333", labelright=False)
ax.tick_params(axis='y', labelsize=12, labelcolor="#333")

# Tampilkan plot dalam Streamlit
st.pyplot(fig)