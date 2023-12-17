import pandas as pd
import plotly.express as px
import streamlit as st
import openpyxl

st.set_page_config(page_title='Sales Dashboard', page_icon=":chart_increasing:", layout='wide')

@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(io="supermarkt_sales.xlsx", engine='openpyxl', sheet_name='Sales', skiprows=3, usecols='B:R', nrows=1000)
    # -- hour column in the dataframe
    df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
    return df
df = get_data_from_excel()

st.sidebar.header("Please Filter Here:")

city = st.sidebar.multiselect("select the city",
                              options=df['City'].unique(),
                              default=df['City'].unique()
                              )
customer_type = st.sidebar.multiselect("select the city",
                                       options=df['Customer_type'].unique(),
                                       default=df['Customer_type'].unique()
                                       )
gender = st.sidebar.multiselect("select the city",
                                options=df['Gender'].unique(),
                                default=df['Gender'].unique()
                                )
filtered_df = df.query(
    "City == @city & Customer_type == @customer_type & Gender == @gender"
)
# -- Main page --
st.title(":bar_chart: Sales Dashboard")
st.markdown("##")

# --- KPI's

total_sales = int(filtered_df["Total"].sum())
avg_rating = round(filtered_df["Rating"].mean(), 1)
star_rating = ":star:" * int(round(avg_rating, 0))
avg_sale_by_transaction = round(filtered_df["Total"].mean(), 2)

col1, col2, col3 = st.columns(3)
# col1.metric("Total Sale", f"US ${total_sales}")
# col2.metric("Avg.Rating", f"{avg_rating} {star_rating}")
# col3.metric("Avg.Sales Per Transaction", f"US ${avg_sale_by_transaction}", "4%")

with col1:
    st.subheader("Total Sale")
    st.subheader(f"US ${total_sales:,}")
with col2:
    st.subheader("Avg.Rating")
    st.subheader(f"{avg_rating} {star_rating}")
with col3:
    st.subheader("Avg.Sales Per Transaction")
    st.subheader(f"US ${avg_sale_by_transaction}")

st.markdown("---")

# sales by product line [bar / line chart]

# -- ['Health and beauty' 'Electronic accessories' 'Home and lifestyle' 'Sports and travel' 'Food and beverages' 'Fashion accessories']
sales_by_product_line = (
    # filtered_df.groupby(by=["Product line"]).sum()[["Total"]].sort_values(by="Total")
    filtered_df.groupby(by=["Product line"])[["Total"]].sum().sort_values(by="Total")

)
r1_chart_col1, r1_chart_col2 = st.columns([3,3])
fig_product_sales = px.bar(sales_by_product_line,
                           x="Total",
                           y=sales_by_product_line.index,
                           orientation="h",
                           title="<b>Sales By Product Line</b>",
                           color_discrete_sequence=["#2D9596"] * len(sales_by_product_line),
                           template="plotly_white",
                           width = 450
                           )
# - sales by hour
sales_by_hour = filtered_df.groupby(by=["hour"])[["Total"]].sum()

r1_chart_col1.plotly_chart(fig_product_sales)
r1_chart_col2.plotly_chart(px.bar(
    sales_by_hour,
    x=sales_by_hour.index,
    y="Total",
    title="<b>Sales By Hour</b>",
    color_discrete_sequence=["#2D9596"] * len(sales_by_hour),
    template="plotly_white",
    width = 450
))

# Visualization 1: Sales Trends Over Time
filtered_df['Date_Formatted'] = filtered_df['Date'].dt.strftime('%y-%m-%d')
filtered_df = filtered_df.sort_values(by="Date_Formatted")
fig1 = px.line(filtered_df, x='Date_Formatted', y="Total", title="Sales Trends Over Time", width = 550)
r1_chart_col1.plotly_chart(fig1)

# Visualization 2: Sales by Product Line
fig2 = px.bar(filtered_df, x="Product line", y="Total", color="Product line", title="Sales by Product Line", width = 650)
r1_chart_col2.plotly_chart(fig2)

# Visualization 3: Customer Type Analysis
fig3 = px.pie(filtered_df, names="Customer_type", title="Customer Type Distribution", width = 450)
r1_chart_col1.plotly_chart(fig3)

# Visualization 4: Branch Comparison
fig4 = px.bar(filtered_df, x="Branch", y="Total", color="Branch",title="Branch-wise Sales Comparison", width = 650)
r1_chart_col2.plotly_chart(fig4)

# Visualization 5: Gender-based Analysis
df_pie = px.data.tips() # replace with your own data source
fig5 = px.pie(filtered_df, names="Gender", values='Total', title="Gender-based Sales Distribution", width = 450)
fig5.update_traces(textposition='inside', textinfo='percent+label')
r1_chart_col1.plotly_chart(fig5)

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
