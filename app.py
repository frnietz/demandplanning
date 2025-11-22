import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="SCM Pro | Demand & Supply Planner", layout="wide", page_icon="🏭")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
    }
    .stDataFrame { width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS (THE ENGINE) ---

def generate_mock_data():
    """Generates sample data for the MVP demonstration."""
    products = ['SKU-101 (Industrial Pump)', 'SKU-102 (Filter Assembly)', 'SKU-103 (Control Valve)']
    accounts = ['Region North', 'Region South', 'Region East']
    
    # 1. Historical Sales Data
    dates = pd.date_range(start='2024-01-01', periods=12, freq='M')
    sales_data = []
    for p in products:
        base_demand = np.random.randint(50, 150)
        trend = np.linspace(1, 1.2, 12) # Slight upward trend
        seasonality = np.random.normal(1, 0.1, 12)
        sales = (base_demand * trend * seasonality).astype(int)
        for d, s in zip(dates, sales):
            sales_data.append({'Date': d, 'Product': p, 'Sales_Qty': s})
            
    # 2. Inventory Snapshots (Current State)
    inventory_data = []
    for p in products:
        inventory_data.append({
            'Product': p,
            'On_Hand_DC': np.random.randint(200, 500), # Central Warehouse
            'On_Order_PO': np.random.randint(0, 200),  # Coming from Supplier
            'Lead_Time_Days': np.random.randint(15, 45),
            'Unit_Cost': np.random.randint(50, 200)
        })

    # 3. Account Demand (For Allocation)
    allocation_data = []
    for p in products:
        for acc in accounts:
            allocation_data.append({
                'Product': p,
                'Account': acc,
                'Current_Stock_at_Account': np.random.randint(10, 50),
                'Forecast_Next_30_Days': np.random.randint(30, 80)
            })

    return pd.DataFrame(sales_data), pd.DataFrame(inventory_data), pd.DataFrame(allocation_data)

def calculate_forecast(df_sales, horizon_months=3):
    """Simple Moving Average Forecast for MVP."""
    forecasts = []
    products = df_sales['Product'].unique()
    
    for p in products:
        p_data = df_sales[df_sales['Product'] == p].sort_values('Date')
        # Simple 3-month moving average
        last_3_avg = p_data['Sales_Qty'].tail(3).mean()
        
        # Generate future dates
        last_date = p_data['Date'].max()
        future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=horizon_months, freq='M')
        
        for d in future_dates:
            forecasts.append({'Date': d, 'Product': p, 'Forecast_Qty': int(last_3_avg)})
            
    return pd.DataFrame(forecasts)

def supply_planning_logic(inventory_df, forecast_df, target_dos):
    """
    Calculates Net Requirements based on Target Days of Supply (DOS).
    Logic: Target Stock = (Daily Demand * Target DOS)
    """
    # Get total forecasted demand next 30 days (approx)
    monthly_forecast = forecast_df.groupby('Product')['Forecast_Qty'].mean().reset_index()
    monthly_forecast.rename(columns={'Forecast_Qty': 'Avg_Monthly_Demand'}, inplace=True)
    
    merged = pd.merge(inventory_df, monthly_forecast, on='Product')
    
    # Industrial Engineering Math
    merged['Daily_Demand'] = merged['Avg_Monthly_Demand'] / 30
    merged['Target_Stock_Qty'] = (merged['Daily_Demand'] * target_dos).astype(int)
    merged['Total_Pipeline'] = merged['On_Hand_DC'] + merged['On_Order_PO']
    
    # The "Net Requirement" Formula
    merged['Net_Requirement'] = merged['Target_Stock_Qty'] - merged['Total_Pipeline']
    merged['Net_Requirement'] = merged['Net_Requirement'].apply(lambda x: max(0, x)) # No negative orders
    
    merged['Inventory_Health'] = np.where(merged['Total_Pipeline'] < merged['Target_Stock_Qty'], 'Understocked', 
                                 np.where(merged['Total_Pipeline'] > merged['Target_Stock_Qty'] * 1.5, 'Overstocked', 'Healthy'))
    
    return merged

def allocation_logic(allocation_df, product_selected, available_to_allocate):
    """
    Allocates limited stock to accounts based on keeping them equal in Days of Supply (Fair Share).
    """
    df = allocation_df[allocation_df['Product'] == product_selected].copy()
    
    # Calculate Needs
    df['Daily_Burn_Rate'] = df['Forecast_Next_30_Days'] / 30
    df['Current_DOS'] = df['Current_Stock_at_Account'] / df['Daily_Burn_Rate']
    
    total_forecast = df['Forecast_Next_30_Days'].sum()
    
    # Proportional Allocation Strategy (Simple version)
    # Share = (Account Forecast / Total Forecast) * Available Qty
    df['Allocated_Qty'] = (df['Forecast_Next_30_Days'] / total_forecast) * available_to_allocate
    df['Allocated_Qty'] = df['Allocated_Qty'].astype(int)
    
    # Projected DOS after allocation
    df['Projected_Stock'] = df['Current_Stock_at_Account'] + df['Allocated_Qty']
    df['Projected_DOS'] = df['Projected_Stock'] / df['Daily_Burn_Rate']
    
    return df

# --- MAIN APP UI ---

st.sidebar.title("📦 SupplyChain.ai")
module = st.sidebar.radio("Navigate Module", ["Dashboard", "1. Demand Planning", "2. Supply Planning", "3. Inventory Allocation"])

# Load Data
df_sales, df_inv, df_alloc = generate_mock_data()

if module == "Dashboard":
    st.title("Executive S&OP Dashboard")
    st.markdown("### High Level Overview")
    
    col1, col2, col3 = st.columns(3)
    total_inv_value = (df_inv['On_Hand_DC'] * df_inv['Unit_Cost']).sum()
    total_demand = calculate_forecast(df_sales)['Forecast_Qty'].sum()
    
    with col1:
        st.metric(label="Total Inventory Value", value=f"${total_inv_value:,.0f}")
    with col2:
        st.metric(label="Forecasted Demand (3 Mo)", value=f"{total_demand:,.0f} Units")
    with col3:
        st.metric(label="Active SKUs", value=len(df_inv))
        
    st.markdown("---")
    st.subheader("Sales History vs Forecast Trend")
    
    # Generate forecast for chart
    df_fcst = calculate_forecast(df_sales)
    
    # Combine for chart
    hist_chart = df_sales.groupby('Date')['Sales_Qty'].sum().reset_index()
    hist_chart['Type'] = 'Historical'
    fcst_chart = df_fcst.groupby('Date')['Forecast_Qty'].sum().reset_index().rename(columns={'Forecast_Qty': 'Sales_Qty'})
    fcst_chart['Type'] = 'Forecast'
    
    chart_df = pd.concat([hist_chart, fcst_chart])
    
    fig = px.line(chart_df, x='Date', y='Sales_Qty', color='Type', markers=True, 
                  color_discrete_map={'Historical': '#1f77b4', 'Forecast': '#ff7f0e'})
    st.plotly_chart(fig, use_container_width=True)

elif module == "1. Demand Planning":
    st.title("📈 Demand Planning Module")
    st.info("Uses Moving Average logic to project future demand based on historical trends.")
    
    selected_sku = st.selectbox("Select Product to Forecast", df_sales['Product'].unique())
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        sku_hist = df_sales[df_sales['Product'] == selected_sku]
        sku_fcst = calculate_forecast(df_sales[df_sales['Product'] == selected_sku])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=sku_hist['Date'], y=sku_hist['Sales_Qty'], name='History', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=sku_fcst['Date'], y=sku_fcst['Forecast_Qty'], name='Forecast', line=dict(color='orange', dash='dash')))
        fig.update_layout(title=f"Demand Signal: {selected_sku}", xaxis_title="Date", yaxis_title="Quantity")
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.write("### Forecast Data")
        st.dataframe(sku_fcst[['Date', 'Forecast_Qty']].style.format({'Forecast_Qty': '{:.0f}'}))
        
        adjustment = st.slider("Manual Override (%)", -20, 20, 0)
        st.caption(f"Planner Adjustment: {adjustment}%")
        st.metric("Final Forecast (Next Month)", f"{int(sku_fcst.iloc[0]['Forecast_Qty'] * (1 + adjustment/100))}")

elif module == "2. Supply Planning":
    st.title("🚚 Supply Planning & Purchasing")
    st.markdown("Calculates **Net Requirements** to generate Purchase Orders.")
    
    # Inputs
    target_dos = st.slider("Global Target Inventory Days", min_value=15, max_value=90, value=45, step=5)
    
    # Calculation
    df_fcst = calculate_forecast(df_sales)
    supply_plan = supply_planning_logic(df_inv, df_fcst, target_dos)
    
    # KPIs
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Items Understocked", len(supply_plan[supply_plan['Inventory_Health'] == 'Understocked']), delta_color="inverse")
    kpi2.metric("Total Net Requirement", f"{supply_plan['Net_Requirement'].sum():,.0f} Units")
    kpi3.metric("Estimated PO Cost", f"${(supply_plan['Net_Requirement'] * supply_plan['Unit_Cost']).sum():,.0f}")
    
    # Detailed Table
    st.subheader("Purchase Order Recommendations")
    
    def color_health(val):
        color = 'red' if val == 'Understocked' else 'green' if val == 'Healthy' else 'orange'
        return f'color: {color}; font-weight: bold'

    st.dataframe(supply_plan[[
        'Product', 'On_Hand_DC', 'On_Order_PO', 'Daily_Demand', 
        'Target_Stock_Qty', 'Net_Requirement', 'Inventory_Health'
    ]].style.applymap(color_health, subset=['Inventory_Health'])
      .format({'Daily_Demand': '{:.1f}', 'Net_Requirement': '{:.0f}'}))
    
    st.download_button("Download PO CSV", supply_plan.to_csv(), "purchase_orders.csv")

elif module == "3. Inventory Allocation":
    st.title("📦 Inventory Allocation & Replenishment")
    st.markdown("Distribute scarce inventory from the DC to Regional Accounts based on **Fair Share**.")
    
    selected_sku_alloc = st.selectbox("Select Product to Allocate", df_alloc['Product'].unique())
    
    # Context
    current_dc_stock = df_inv[df_inv['Product'] == selected_sku_alloc]['On_Hand_DC'].values[0]
    st.write(f"**Available Quantity at DC:** {current_dc_stock} units")
    
    allocate_qty = st.number_input("Quantity to Release for Shipment", min_value=0, max_value=int(current_dc_stock), value=int(current_dc_stock*0.5))
    
    # Run Algorithm
    allocation_results = allocation_logic(df_alloc, selected_sku_alloc, allocate_qty)
    
    # Visualization
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Projected Coverage (Days)")
        # Bar chart comparing Current DOS vs Projected DOS
        
        fig = go.Figure(data=[
            go.Bar(name='Current DOS', x=allocation_results['Account'], y=allocation_results['Current_DOS']),
            go.Bar(name='Projected DOS (After Alloc)', x=allocation_results['Account'], y=allocation_results['Projected_DOS'])
        ])
        fig.update_layout(barmode='group', title="Impact of Allocation on Inventory Health")
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Replenishment Orders")
        st.dataframe(allocation_results[['Account', 'Forecast_Next_30_Days', 'Current_Stock_at_Account', 'Allocated_Qty']].style.background_gradient(subset=['Allocated_Qty'], cmap='Greens'))
        
        if st.button("Confirm Allocation Release"):
            st.success(f"Successfully created Transfer Orders for {allocate_qty} units.")
