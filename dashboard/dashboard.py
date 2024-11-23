import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Helper Functions

#fungsi untuk mengembalikan data penggunaan harian sepeda
def create_daily_usage_df(df):

    daily_usage_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum",   #count
        "temp": "mean", #temperature
        "hum": "mean"   #humidity
    }).reset_index()
    daily_usage_df.rename(columns={
        "cnt": "total_rentals",
        "temp": "avg_temp",
        "hum": "avg_humidity"
    }, inplace=True)
    
    return daily_usage_df

# fungsi untuk mengembalikan data penggunaan sepeda musiman
def create_seasonal_usage_df(df):

    seasonal_usage_df = df.groupby("season", as_index=False).agg({
        "cnt": "mean"
    })
    seasonal_usage_df.rename(columns={"cnt": "avg_rentals"}, inplace=True)
    #mapping untuk memberikan label nama musim
    seasonal_usage_df["season_name"] = seasonal_usage_df["season"].map({
        1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"
    })
    
    return seasonal_usage_df

# penggunaan sepeda tahunan
def create_yearly_usage_df(df):

    yearly_usage_df = df.groupby("yr", as_index=False).agg({
        "cnt": "sum",
        "temp": "mean"
    })
    yearly_usage_df.rename(columns={
        "cnt": "total_rentals",
        "temp": "avg_temp"
    }, inplace=True)
    
    return yearly_usage_df

# penggunaan berdasarkan hari libur / tidak
def create_holiday_usage_df(df):
    
    holiday_usage_df = df.groupby("holiday", as_index=False).agg({
        "cnt": "mean"
    })
    holiday_usage_df.rename(columns={"cnt": "avg_rentals"}, inplace=True)
    # pelabelan, 0 menunjukan bukan hari libur, 1 menunjukan hari libur
    holiday_usage_df["holiday_type"] = holiday_usage_df["holiday"].map({
        0: "Non-Holiday",
        1: "Holiday"
    })
    
    return holiday_usage_df

# penggunaan mingguan
def create_weekday_usage_df(df):
    
    weekday_usage_df = df.groupby("weekday", as_index=False).agg({
        "cnt": "mean"
    })
    weekday_usage_df.rename(columns={"cnt": "avg_rentals"}, inplace=True)
    #pelabelan hari
    weekday_usage_df["weekday_name"] = weekday_usage_df["weekday"].map({
        0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday",
        4: "Thursday", 5: "Friday", 6: "Saturday"
    })
    
    return weekday_usage_df


# Visualization Functions

# Fungsi untuk menampilkan tren harian
def plot_daily_usage(df):

    st.subheader('Daily Bike Usage')

    total_rentals = df['total_rentals'].sum()
    avg_temp = round(df['avg_temp'].mean(), 2)
    avg_humidity = round(df['avg_humidity'].mean(), 2)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rentals", value=total_rentals)
    with col2:
        st.metric("Average Temperature", value=f"{avg_temp} °C")
    with col3:
        st.metric("Average Humidity", value=f"{avg_humidity}")
    
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(df["dteday"], df["total_rentals"], marker='o', linewidth=2, color="#90CAF9")
    ax.set_title("Daily Bike Rentals Over Time", fontsize=20)
    ax.set_xlabel("Date", fontsize=15)
    ax.set_ylabel("Total Rentals", fontsize=15)
    st.pyplot(fig)

# Fungsi untuk visualisasi penggunaan berdasarkan musim
def plot_seasonal_usage(df):
    st.subheader('Seasonal Bike Usage')

    #sorting berdasarkan musim dengan penggunaan paling banyak
    df = df.sort_values(by='avg_rentals', ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        y='season_name', x='avg_rentals', 
        data=df, palette="viridis", ax=ax
    )

    ax.set_title("Average Rentals by Season", fontsize=20)
    ax.set_ylabel("Season", fontsize=15)
    ax.set_xlabel("Average Rentals", fontsize=15)
    st.pyplot(fig)

# Fungsi untuk visualisasi penggunaan berdasarkan hari libur
def plot_holiday_usage(df):

    st.subheader('Holiday vs Non-Holiday Usage')
    fig, ax = plt.subplots(figsize=(8, 5))

    sns.barplot(
        x='holiday_type', y='avg_rentals', 
        data=df, palette="coolwarm", ax=ax
    )

    ax.set_title("Average Rentals: Holiday vs Non-Holiday", fontsize=20)
    ax.set_xlabel("Holiday Type", fontsize=15)
    ax.set_ylabel("Average Rentals", fontsize=15)
    st.pyplot(fig)

# Fungsi untuk menampilkan visualisasi penggunaan berdasarkan hari dalam seminggu
def plot_weekday_usage(df):
    st.subheader('Weekday Bike Usage')

    #sorting berdasarkan penggunaan harian paling banyak
    df = df.sort_values(by='avg_rentals', ascending=False)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(
        y='weekday_name', x='avg_rentals', 
        data=df, palette="muted", ax=ax
    )
    
    ax.set_title("Average Rentals by Weekday", fontsize=20)
    ax.set_ylabel("Weekday", fontsize=15)
    ax.set_xlabel("Average Rentals", fontsize=15)
    st.pyplot(fig)


# MAIN 

#load data
df = pd.read_csv("./main_data.csv")

#mengubah tipe data
df["dteday"] = pd.to_datetime(df["dteday"])

#mencari tanggal paling awal dan akhir
min_date = df["dteday"].min()
max_date = df["dteday"].max()

#Sidebar untuk filter berdasarkan rentang tanggal
with st.sidebar:
    
    st.image("https://raw.githubusercontent.com/dickifathurohman/submission_analisis_data/main/dashboard/logo.jpg")

    start_date, end_date = st.date_input(
    label='Rentang Waktu',min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
    )

main_df = df[(df["dteday"] >= str(start_date)) & 
                (df["dteday"] <= str(end_date))]

# menerapkan helper functions untuk mendapatkan data yang dibutuhkan
daily_usage = create_daily_usage_df(main_df)
seasonal_usage = create_seasonal_usage_df(main_df)
yearly_usage = create_yearly_usage_df(main_df)
holiday_usage = create_holiday_usage_df(main_df)
weekday_usage = create_weekday_usage_df(main_df)

st.header('Dicoding Project: Rental Bike Dashboards')

# memanggil fungsi-fungsi untuk menampilkan visualisasi
plot_daily_usage(daily_usage)
plot_seasonal_usage(seasonal_usage)
plot_holiday_usage(holiday_usage)
plot_weekday_usage(weekday_usage)

st.caption('Copyright (c) Dicki Fathurohman 2024')
