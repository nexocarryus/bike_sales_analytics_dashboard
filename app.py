import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np

# ===== Konfigurasi halaman =====
st.set_page_config(page_title="Bike Sales Dashboard", layout="wide")
st.title("Bike Sales Analytics Dashboard")

# ===== Load dataset =====
DATA_PATH = "bike_sales_100k.csv"  
try:
    df = pd.read_csv(DATA_PATH)
except Exception as e:
    st.error(f"Gagal memuat dataset: {e}")
    st.stop()

# ===== Pranala data =====
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Month"] = df["Date"].dt.to_period("M").astype(str)
df["Year"] = df["Date"].dt.year
df["Total_Amount"] = df["Price"] * df["Quantity"]

# ===== Layout utama dengan Tabs =====
tabs = st.tabs([
    "Data Overview",
    "Sales Performance",
    "Store & Payment Analysis",
    "Customer & Product Insights",
    "Business Insights"
])

# =====================================================================
#  TAB 1 — Data Overview
# =====================================================================
with tabs[0]:
    st.header("Data Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transaksi", f"{len(df):,}")
    col2.metric("Total Pelanggan Unik", f"{df['Customer_ID'].nunique():,}")
    col3.metric("Total Model Sepeda", f"{df['Bike_Model'].nunique():,}")

    st.markdown("### 📦 Distribusi Kolom Kategorikal")
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    selected_cols = st.multiselect(
        "Pilih kolom kategorikal untuk divisualisasikan:",
        categorical_cols,
        default=["Store_Location", "Payment_Method"]
    )

    cols_per_row = 2
    for i, col in enumerate(selected_cols):
        if i % cols_per_row == 0:
            row = st.columns(cols_per_row)

        with row[i % cols_per_row]:
            cat_counts = df[col].value_counts().reset_index()
            cat_counts.columns = [col, "Count"]

        fig = px.bar(
            cat_counts,
            x=col,
            y="Count",
            color="Count",
            color_continuous_scale="viridis",
            title=f"Distribusi {col}",
            text_auto=True,
        )
        fig.update_layout(
            xaxis_title=col,
            yaxis_title="Jumlah",
            template="plotly_white",
            title_x=0.5,
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)
        
    st.markdown("Anggota kelompok:")
    st.markdown("- Naufal Dzakwan Zakianto")
    st.markdown("- Rafi Pratama Gunadi")
    st.markdown("- Muhammad Fatih Yumna")
    st.markdown("- Muhammad Alvito Naufal Hakim")
    st.markdown("- Mohammad Naufal Widi Pratama ")
        


# =====================================================================
# TAB 2 — Sales Performance
# =====================================================================
with tabs[1]:
    st.header("Sales Performance")
    st.markdown("Analisis tren penjualan dan performa salesperson berdasarkan waktu dan jenis sepeda.")

    # --- Filter tahun dan jenis sepeda ---
    available_years = sorted(df["Year"].dropna().unique())
    available_models = ["Semua"] + sorted(df["Bike_Model"].dropna().unique().tolist())

    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("Pilih Tahun:", available_years, index=len(available_years) - 1)
    with col2:
        selected_model = st.selectbox("Pilih Jenis Sepeda:", available_models)

    # --- Filter data berdasarkan pilihan ---
    filtered_df = df[df["Year"] == selected_year].copy()
    if selected_model != "Semua":
        filtered_df = filtered_df[filtered_df["Bike_Model"] == selected_model]

    # --- Tren Bulanan ---
    monthly_sales = (
        filtered_df.groupby("Month")["Total_Amount"]
        .sum()
        .reset_index()
        .sort_values("Month")
    )

    fig1 = px.line(
        monthly_sales,
        x="Month",
        y="Total_Amount",
        markers=True,
        title=f"📈 Tren Penjualan per Bulan ({selected_year}) — {selected_model}",
        color_discrete_sequence=["#1f77b4"],
    )
    fig1.update_layout(template="plotly_white", title_x=0.5)
    st.plotly_chart(fig1, use_container_width=True)

    # --- Tren Tahunan (selalu seluruh dataset, tapi bisa difilter per model) ---
    yearly_df = df.copy()
    if selected_model != "Semua":
        yearly_df = yearly_df[yearly_df["Bike_Model"] == selected_model]

    yearly_sales = (
        yearly_df.groupby("Year")["Total_Amount"]
        .sum()
        .reset_index()
        .sort_values("Year")
    )

    fig2 = px.bar(
        yearly_sales,
        x="Year",
        y="Total_Amount",
        color="Total_Amount",
        color_continuous_scale="Blues",
        text_auto=".2s",
        title=f"📅 Total Penjualan per Tahun — {selected_model}",
    )
    fig2.update_layout(template="plotly_white", title_x=0.5)
    st.plotly_chart(fig2, use_container_width=True)

    # --- Top Salesperson ---
    st.markdown("### 🧍‍♂️ Top Salesperson")

    if "Salesperson_ID" in df.columns:
        top_n = st.slider("Tampilkan Top-N Salesperson", 5, 50, 20)

        sales_by_person = (
            df["Salesperson_ID"]
            .value_counts()
            .reset_index()
            .rename(columns={"index": "Salesperson_ID", "count": "SalesCount"})
            .head(top_n)
        )

        fig3 = px.bar(
            sales_by_person,
            x="Salesperson_ID",
            y="SalesCount",
            color="SalesCount",
            color_continuous_scale="viridis",
            title=f"Top {top_n} Salesperson berdasarkan Jumlah Transaksi",
            text_auto=True,
        )
        fig3.update_layout(template="plotly_white", title_x=0.5)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("Kolom 'Salesperson_ID' tidak ditemukan dalam dataset.")
    
        # --- Top Customer ---
    st.markdown("### 👑 Top Customer (Berdasarkan Nilai Pembelian)")

    top_n_customer = st.slider("Tampilkan Top-N Customer", 5, 50, 10, key="top_customer_slider")

    top_customers = (
        df.groupby("Customer_ID")["Total_Amount"]
        .sum()
        .reset_index()
        .sort_values("Total_Amount", ascending=False)
        .head(top_n_customer)
    )

    fig4 = px.bar(
        top_customers,
        x="Customer_ID",
        y="Total_Amount",
        color="Total_Amount",
        color_continuous_scale="YlOrRd",
        text_auto=".2s",
        title=f"💰 Top {top_n_customer} Customer berdasarkan Total Pembelian",
    )
    fig4.update_layout(
        template="plotly_white",
        title_x=0.5,
        xaxis_title="Customer ID",
        yaxis_title="Total Pembelian",
    )
    st.plotly_chart(fig4, use_container_width=True)


# =====================================================================
# TAB 3 — Store & Payment Analysis
# =====================================================================
with tabs[2]:
    st.header(" Store & Payment Analysis")

    # --- Jumlah transaksi per lokasi ---
    per_store = df.groupby("Store_Location").size().reset_index(name="TransactionCount")
    fig_store = px.bar(per_store, x="Store_Location", y="TransactionCount",
                       color="TransactionCount", color_continuous_scale="Blues",
                       title="📍 Jumlah Transaksi per Lokasi Toko")
    st.plotly_chart(fig_store, use_container_width=True)

    # --- Lokasi & Metode Pembayaran ---
    location_payment = df.groupby(["Store_Location", "Payment_Method"]).size().reset_index(name="TransactionCount")
    fig_pay = px.bar(location_payment, x="Store_Location", y="TransactionCount",
                     color="Payment_Method", barmode="group",
                     title="💳 Jumlah Transaksi per Lokasi & Metode Pembayaran")
    st.plotly_chart(fig_pay, use_container_width=True)

    # --- Heatmap Distribusi Model Sepeda per Toko ---

# Buat pivot data
    pivot_table = (
        df.groupby(["Store_Location", "Bike_Model"])["Quantity"]
        .sum()
        .reset_index()
        .pivot(index="Store_Location", columns="Bike_Model", values="Quantity")
        .fillna(0)
    )

# Reset index agar cocok untuk Plotly
    heatmap_data = pivot_table.reset_index().melt(id_vars="Store_Location", var_name="Bike_Model", value_name="Quantity")

# Plotly heatmap
    fig_heatmap = px.density_heatmap(
        heatmap_data,
        x="Bike_Model",
        y="Store_Location",
        z="Quantity",
        color_continuous_scale="YlGnBu",
        title="Distribusi Model Sepeda per Lokasi Toko",
        nbinsx=len(df["Bike_Model"].unique()),
        nbinsy=len(df["Store_Location"].unique()),
    )

# Ubah style agar serasi dengan chart lainnya
    fig_heatmap.update_layout(
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(size=12),
        title=dict(font=dict(size=18, family="Arial Black")),
        xaxis=dict(showgrid=True, gridcolor="lightgrey", tickangle=45),
        yaxis=dict(showgrid=True, gridcolor="lightgrey"),
        coloraxis_colorbar=dict(title="Jumlah Terjual")
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)


    # --- Penjualan Jenis Sepeda Berdasarkan Lokasi ---
    st.markdown("### 🚴 Penjualan Jenis Sepeda Berdasarkan Lokasi Toko")

# Pilihan tipe visualisasi
    chart_type = st.radio(
        "Pilih jenis visualisasi:",
        ["Grouped Bar Chart", "Stacked Bar Chart"],
        horizontal=True
    )

# Hitung total penjualan per model dan lokasi
    bike_sales_location = (
        df.groupby(["Store_Location", "Bike_Model"])["Total_Amount"]
        .sum()
        .reset_index()
        .sort_values("Total_Amount", ascending=False)
    )

# Pilih lokasi tertentu untuk difokuskan
    store_options = ["Semua"] + df["Store_Location"].unique().tolist()
    selected_store = st.selectbox("Pilih Lokasi Toko:", store_options)

    if selected_store != "Semua":
        filtered_sales = bike_sales_location[bike_sales_location["Store_Location"] == selected_store]
    else:
        filtered_sales = bike_sales_location

# Visualisasi interaktif
    barmode = "group" if chart_type == "Grouped Bar Chart" else "stack"

    fig_sales = px.bar(
        filtered_sales,
        x="Bike_Model",
        y="Total_Amount",
        color="Store_Location",
        barmode=barmode,
        title=f"💰 Penjualan Jenis Sepeda Berdasarkan Lokasi {'(' + selected_store + ')' if selected_store != 'Semua' else ''}",
        text_auto=".2s",
    )

    fig_sales.update_layout(xaxis_title="Model Sepeda", yaxis_title="Total Penjualan (USD)")
    st.plotly_chart(fig_sales, use_container_width=True)


# =====================================================================
# TAB 4 — Customer & Product Insights
# =====================================================================
with tabs[3]:
    st.header("Customer & Product Insights")

    # Filter gender
    genders = ["Semua"] + sorted(df["Customer_Gender"].dropna().unique().tolist())
    selected_gender = st.selectbox("Pilih Jenis Kelamin:", genders)

    if selected_gender != "Semua":
        filtered_df = df[df["Customer_Gender"] == selected_gender]
    else:
        filtered_df = df.copy()

    col1, col2 = st.columns(2)

    # Distribusi transaksi per gender
    with col1:
        gender_sales = df["Customer_Gender"].value_counts().reset_index()
        gender_sales.columns = ["Gender", "SalesCount"]
        fig_bar = px.bar(gender_sales, x="Gender", y="SalesCount",
                         color="Gender", title="📊 Jumlah Transaksi Berdasarkan Gender",
                         text_auto=True)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Model sepeda favorit per gender
    with col2:
        if "Bike_Model" in df.columns:
            model_pref = (
                filtered_df.groupby("Bike_Model").size()
                .reset_index(name="SalesCount")
                .sort_values("SalesCount", ascending=False)
                .head(10)
            )
            fig_model = px.bar(model_pref, x="Bike_Model", y="SalesCount",
                               color="SalesCount", color_continuous_scale="teal",
                               title=f"🚴 Model Sepeda Favorit ({selected_gender})",
                               text_auto=True)
            st.plotly_chart(fig_model, use_container_width=True)
            
    st.markdown("### 💵 Distribusi Nilai Transaksi")

    fig_dist = px.histogram(
        df,
        x="Total_Amount",
        nbins=40,
        color_discrete_sequence=["#1f77b4"],
        title="Distribusi Nilai Transaksi per Pembelian"
    )
    fig_dist.update_layout(
        xaxis_title="Total Nilai Transaksi (USD)",
        yaxis_title="Jumlah Transaksi",
        template="plotly_white"
    )
    st.plotly_chart(fig_dist, use_container_width=True)
    
    st.markdown("### 👶🧓 Segmentasi Pelanggan Berdasarkan Umur")

    age_bins = [0, 18, 25, 35, 45, 55, 65, 100]
    age_labels = ["<18", "18-25", "26-35", "36-45", "46-55", "56-65", "65+"]
    df["Age_Group"] = pd.cut(df["Customer_Age"], bins=age_bins, labels=age_labels, right=False)

    age_group_sales = df.groupby("Age_Group")["Total_Amount"].sum().reset_index()

    fig_age = px.bar(
        age_group_sales,
        x="Age_Group",
        y="Total_Amount",
        color="Total_Amount",
        color_continuous_scale="teal",
        title="Total Penjualan Berdasarkan Kelompok Umur",
        text_auto=True
    )
    fig_age.update_layout(xaxis_title="Kelompok Umur", yaxis_title="Total Penjualan (USD)")
    st.plotly_chart(fig_age, use_container_width=True)
    
    st.markdown("### 🚴 Distribusi Banyaknya Pembelian Sepeda per Transaksi")

    # Hitung total quantity per transaksi
    quantity_per_transaction = (
        df.groupby("Sale_ID")["Quantity"]
        .sum()
        .reset_index()
    )


    fig_qty_dist = px.histogram(
        quantity_per_transaction,
        x="Quantity",
        nbins=20,
        color_discrete_sequence=["#1f77b4"],
        title="Distribusi Banyaknya Pembelian Sepeda per Transaksi",
    )

    fig_qty_dist.update_layout(
        xaxis_title="Jumlah Sepeda per Transaksi",
        yaxis_title="Jumlah Transaksi",
        template="plotly_white",
    )

    st.plotly_chart(fig_qty_dist, use_container_width=True)
    
    st.markdown("### 💹 Hubungan antara Harga dan Jumlah Pembelian (Price vs Quantity)")

# Scatter plot Price vs Quantity
    fig_price_qty = px.scatter(
        df,
        x="Price",
        y="Quantity",
        color="Bike_Model",  # Bisa ubah ke 'Store_Location' atau 'Customer_Gender' untuk analisis lain
        size="Quantity",
        hover_data=["Customer_ID", "Store_Location", "Payment_Method"],
        title="Hubungan antara Harga Sepeda dan Jumlah yang Dibeli",
    )

    fig_price_qty.update_layout(
        xaxis_title="Harga Sepeda (USD)",
        yaxis_title="Jumlah Pembelian (Quantity)",
        template="plotly_white",
        legend_title_text="Model Sepeda",
    )

    st.plotly_chart(fig_price_qty, use_container_width=True)




# =====================================================================
#  TAB 5 — Business Insights
# =====================================================================
with tabs[4]:
    st.header("Business Insights")

    col1, col2, col3 = st.columns(3)
    avg_order_value = df.groupby("Customer_ID")["Total_Amount"].sum().mean()
    repeat_ratio = (df["Customer_ID"].value_counts() > 1).mean() * 100
    total_revenue = df["Total_Amount"].sum()

    col1.metric("Average Order Value", f"USD {avg_order_value:,.0f}")
    col2.metric("Repeat Customer Ratio", f"{repeat_ratio:.2f}%")
    col3.metric("Total Revenue", f"USD {total_revenue:,.0f}")

    # AOV per gender
    avg_by_gender = df.groupby("Customer_Gender")["Total_Amount"].mean().reset_index()
    fig_aov = px.bar(avg_by_gender, x="Customer_Gender", y="Total_Amount",
                     color="Customer_Gender", title="Rata-rata Nilai Transaksi per Gender",
                     text_auto=".2s")
    st.plotly_chart(fig_aov, use_container_width=True)

    # Repeat vs New customer
    # Hitung jumlah transaksi per customer
    customer_counts = df.groupby("Customer_ID").size().reset_index(name="TransactionCount")

# Tandai pelanggan baru vs repeat
    customer_counts["Customer_Status"] = np.where(customer_counts["TransactionCount"] > 1, "Repeat", "New")
    



# Gabungkan kembali ke dataframe utama
    df = df.merge(customer_counts[["Customer_ID", "Customer_Status"]], on="Customer_ID", how="left")

# Hitung proporsinya
    customer_status_count = df.groupby("Customer_Status").Customer_ID.nunique().reset_index(name="CustomerCount")
    
    # --- Pisahkan pelanggan baru ---
    new_customers = customer_counts[customer_counts["Customer_Status"] == "New"]

    st.subheader("Daftar New Customers")
    st.dataframe(new_customers)

# Buat pie chart
    fig_repeat = px.pie(
    customer_status_count,
    values="CustomerCount",
    names="Customer_Status",
    title="🧍‍♂️ Proporsi New vs Repeat Customers",
    color="Customer_Status",
    color_discrete_map={"New": "#1f77b4", "Repeat": "#ff7f0e"}
    )
    fig_repeat.update_traces(
    textinfo='percent+label',
    texttemplate='%{percent:.2%}'  # dua angka di belakang koma
)

  
    st.plotly_chart(fig_repeat, use_container_width=True)


    # Penjualan per model
    model_sales = df.groupby("Bike_Model")["Total_Amount"].sum().reset_index().sort_values("Total_Amount", ascending=False)
    fig_model_sales = px.bar(model_sales, x="Bike_Model", y="Total_Amount",
                             color="Total_Amount", color_continuous_scale="sunset",
                             title="🚴 Total Penjualan per Model Sepeda",
                             text_auto=True)
    st.plotly_chart(fig_model_sales, use_container_width=True)
