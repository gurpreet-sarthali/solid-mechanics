import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="Stress Lab")
st.title("Stress Lab: Transformation & Mohr's Circle")

# --- Formula Display ---
st.latex(r"\sigma_{x'} = \frac{\sigma_x + \sigma_y}{2} + \frac{\sigma_x - \sigma_y}{2} \cos(2\theta) + \tau_{xy} \sin(2\theta)")
st.latex(r"\tau_{x'y'} = -\frac{\sigma_x - \sigma_y}{2} \sin(2\theta) + \tau_{xy} \cos(2\theta)")

# --- Sidebar Inputs ---
st.sidebar.header("1. Define Stress State")
# Using the values from your screenshot as defaults
s_x = st.sidebar.number_input("σx (Normal X)", value=-89.0)
s_y = st.sidebar.number_input("σy (Normal Y)", value=20.0)
t_xy = st.sidebar.number_input("τxy (Shear XY)", value=40.0)

st.sidebar.header("2. Rotate Element")
theta_input = st.sidebar.slider("Rotation Angle (θ)", 0, 180, 67)

# --- Math Logic ---
# 1. Average Stress and Radius
sig_avg = (s_x + s_y) / 2
sig_diff = (s_x - s_y) / 2
radius = np.sqrt(sig_diff**2 + t_xy**2)

# 2. Data Arrays (CRITICAL FIX: We will convert these to lists later)
theta_deg = np.linspace(0, 360, 360) 
theta_rad = np.radians(theta_deg)

# Calculate curve data
sig_x_dash_all = sig_avg + sig_diff * np.cos(2 * theta_rad) + t_xy * np.sin(2 * theta_rad)

# 3. Single Point Calculation (Current Slider State)
c_rad = np.radians(theta_input)
cur_sx = sig_avg + sig_diff * np.cos(2*c_rad) + t_xy * np.sin(2*c_rad)
cur_tau = -sig_diff * np.sin(2*c_rad) + t_xy * np.cos(2*c_rad)

# --- Layout ---
col1, col2 = st.columns(2)

# ==========================================
# COLUMN 1: Stress Transformation Plot
# ==========================================
with col1:
    fig_line = go.Figure()

    # The Curve (FIX: Added .tolist() to ensure it renders)
    fig_line.add_trace(go.Scatter(
        x=theta_deg.tolist(), 
        y=sig_x_dash_all.tolist(), 
        mode='lines',
        name="σx'", 
        line=dict(color='#636EFA', width=4)
    ))

    # Current Angle Indicator
    fig_line.add_vline(x=theta_input, line_dash="dash", line_color="red", opacity=0.7)
    fig_line.add_trace(go.Scatter(
        x=[theta_input], 
        y=[cur_sx],
        mode='markers',
        marker=dict(size=12, color='red', line=dict(width=2, color='white')),
        name="Current State"
    ))

    # Dynamic Y-axis range to handle negative values properly
    y_min, y_max = np.min(sig_x_dash_all), np.max(sig_x_dash_all)
    y_pad = (y_max - y_min) * 0.1

    fig_line.update_layout(
        title="<b>Normal Stress Transformation</b>",
        xaxis_title="Rotation Angle θ (°)",
        yaxis_title="Normal Stress (σx')",
        xaxis=dict(range=[0, 180], tickmode='linear', dtick=30),
        yaxis=dict(range=[y_min - y_pad, y_max + y_pad]),
        hovermode="x unified",
        template="plotly_dark",
        height=500
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
    st.info(f"**Current State (θ = {theta_input}°)**\n\n"
            f"σx': {cur_sx:.2f} | τx'y': {cur_tau:.2f}")

# ==========================================
# COLUMN 2: Mohr's Circle
# ==========================================
with col2:
    fig_mohr = go.Figure()

    # 1. Circle Perimeter (FIX: Added .tolist())
    beta = np.linspace(0, 2*np.pi, 360)
    circle_x = (sig_avg + radius * np.cos(beta)).tolist()
    circle_y = (radius * np.sin(beta)).tolist()

    fig_mohr.add_trace(go.Scatter(
        x=circle_x, 
        y=circle_y,
        mode='lines',
        name="Mohr's Circle",
        line=dict(color='#E5E7EB', width=3),
        fill='toself',
        fillcolor='rgba(148,163,184,0.1)'
    ))

    # 2. Axes and Center
    fig_mohr.add_hline(y=0, line_color="gray", line_width=1)
    fig_mohr.add_vline(x=0, line_color="gray", line_width=1)
    
    # 3. Reference State (Original X-Face)
    fig_mohr.add_trace(go.Scatter(
        x=[s_x], y=[t_xy],
        mode='markers',
        marker=dict(size=8, color='gray', symbol='x'),
        name="Original Face (θ=0)"
    ))

    # 4. Current State Radius Arm
    fig_mohr.add_trace(go.Scatter(
        x=[sig_avg, cur_sx], 
        y=[0, cur_tau],
        mode='lines',
        line=dict(color='red', width=2, dash='dot'),
        showlegend=False
    ))

    # 5. Current Rotated Point
    fig_mohr.add_trace(go.Scatter(
        x=[cur_sx], 
        y=[cur_tau],
        mode='markers',
        marker=dict(size=12, color='red', line=dict(width=2, color='white')),
        name="Rotated Face"
    ))

    # 6. Principal Stresses
    sigma_1, sigma_2 = sig_avg + radius, sig_avg - radius
    fig_mohr.add_trace(go.Scatter(
        x=[sigma_1, sigma_2],
        y=[0, 0],
        mode='markers',
        marker=dict(size=8, color='green'),
        name="Principal Stresses"
    ))

    # We ensure the range covers the entire circle (Center +/- Radius) plus padding
    x_margin = radius * 1.3
    
    fig_mohr.update_layout(
        title="<b>Mohr's Circle</b>",
        xaxis_title="Normal Stress (σ)",
        yaxis_title="Shear Stress (τ)",
        # Centering the view on the Average Stress ensures we see the whole circle
        xaxis=dict(range=[sig_avg - x_margin, sig_avg + x_margin]),
        yaxis=dict(range=[-x_margin, x_margin], scaleanchor="x", scaleratio=1),
        template="plotly_dark",
        height=500
    )
    
    st.plotly_chart(fig_mohr, use_container_width=True)

    st.success(f"**Principal Stresses**\n\n"
               f"σ1 (Max): {sigma_1:.2f} | σ2 (Min): {sigma_2:.2f} | τ_max: {radius:.2f}")
