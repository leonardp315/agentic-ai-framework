 
"""
Agentic AI Framework - Main Dashboard
Interactive web interface for the integrated framework
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
import numpy as np
from aas_integration import aas_connector

# Page configuration
st.set_page_config(
    page_title="Agentic AI Framework",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title
st.title("🤖 Agentic AI Framework for Future of Work")
st.markdown("**Integrated LLMs, Digital Twins & Asset Administration Shells**")

# Sidebar
with st.sidebar:
    st.header("Framework Components")
    
    # Component selector
    component = st.selectbox(
        "Select Component",
        ["Overview", "Asset Administration Shell", "Digital Twin", "Agentic AI", "LLM Orchestration"]
    )
    
    st.markdown("---")
    st.markdown("### Status")
    st.success("✅ AAS Online")
    st.warning("⚠️ Digital Twin Loading")
    st.info("ℹ️ LLM Ready")
    st.error("❌ Agents Offline")

# Main content based on selection
if component == "Overview":
    st.header("System Overview")
    
    # Get real metrics from AAS
    metrics = aas_connector.get_system_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Assets", metrics["total_assets"])
    with col2:
        st.metric("Active Assets", metrics["active_assets"], 
                 f"+{metrics['active_assets'] - metrics['maintenance_assets']}")
    with col3:
        st.metric("In Maintenance", metrics["maintenance_assets"])
    with col4:
        st.metric("Avg Efficiency", f"{metrics['average_efficiency']}%")
    
    # Real alerts
    st.subheader("System Alerts")
    alerts = aas_connector.get_maintenance_alerts()
    
    if alerts:
        for alert in alerts:
            alert_type = "🔴" if alert["severity"] == "high" else "🟡"
            st.warning(f"{alert_type} **{alert['asset']}**: {alert['message']}")
    else:
        st.success("✅ All systems operating normally")
    
    # Assets overview chart
    st.subheader("Assets Status Distribution")
    
    status_data = {
        'Active': metrics["active_assets"],
        'Maintenance': metrics["maintenance_assets"], 
        'Offline': metrics.get("offline_assets", 0)
    }
    
    fig = px.pie(values=list(status_data.values()), names=list(status_data.keys()), 
                title="Asset Status Distribution")
    st.plotly_chart(fig, use_container_width=True)

elif component == "Asset Administration Shell":
    st.header("Asset Administration Shell")
    st.markdown("Semantic representation and metadata management")
    
    # Real AAS Explorer
    st.subheader("AAS Explorer")
    
    # Get real assets data
    assets_df = aas_connector.get_assets_summary()
    st.dataframe(assets_df, use_container_width=True)
    
    # Asset details
    asset_names = assets_df['ID'].tolist()
    selected_asset = st.selectbox("Select Asset for Details", asset_names)
    
    if selected_asset:
        details = aas_connector.get_asset_details(selected_asset)
        if details:
            st.subheader(f"Details: {details['name']}")
            
            # Basic info
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Status:** {details['status'].title()}")
                st.write(f"**Created:** {details['created']}")
            with col2:
                st.write(f"**Asset ID:** {selected_asset}")
                st.write(f"**Last Modified:** {details['last_modified']}")
            
            # Submodels
            st.subheader("Submodels")
            for sm_name, sm_data in details['submodels'].items():
                with st.expander(f"📋 {sm_name}"):
                    for elem_name, elem_data in sm_data.items():
                        st.write(f"**{elem_name}:** {elem_data['value']} ({elem_data['type']})")
                        if elem_data['description']:
                            st.caption(elem_data['description'])
                        st.caption(f"Last updated: {elem_data['last_updated']}")

elif component == "Digital Twin":
    st.header("Digital Twin Simulation")
    st.markdown("Virtual environment for testing and validation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Simulation Environment")
        
        # Placeholder for 3D visualization
        st.info("📊 3D Digital Twin Visualization Would Appear Here")
        st.markdown("*In a real implementation, this would show an interactive 3D model*")
        
        # Simulation controls
        st.subheader("Simulation Controls")
        
        scenario = st.selectbox("Select Scenario", [
            "Normal Operations",
            "Maintenance Window", 
            "Equipment Failure",
            "Peak Production"
        ])
        
        if st.button("Run Simulation"):
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)
            st.success(f"Simulation '{scenario}' completed successfully!")
    
    with col2:
        st.subheader("Simulation Results")
        
        # Mock simulation metrics
        st.metric("Efficiency", "89.2%", "↑ 2.1%")
        st.metric("Throughput", "145 units/h", "↓ 3")
        st.metric("Energy Usage", "2.4 kWh", "↑ 0.2")
        st.metric("Risk Score", "Low", "stable")

elif component == "Agentic AI":
    st.header("Autonomous Agents")
    st.markdown("Intelligent agents performing specialized tasks")
    
    # Agent status
    agents = [
        {"Name": "Maintenance Agent", "Status": "Active", "Tasks": 12, "Success Rate": "94%"},
        {"Name": "Quality Agent", "Status": "Idle", "Tasks": 8, "Success Rate": "98%"},
        {"Name": "Resource Agent", "Status": "Active", "Tasks": 15, "Success Rate": "91%"},
        {"Name": "Safety Agent", "Status": "Active", "Tasks": 3, "Success Rate": "100%"}
    ]
    
    df_agents = pd.DataFrame(agents)
    st.dataframe(df_agents, use_container_width=True)
    
    # Agent interaction
    st.subheader("Agent Communication")
    
    user_input = st.text_input("Send message to agents:", 
                              placeholder="e.g., 'Schedule maintenance for Robot R-47'")
    
    if st.button("Send Message") and user_input:
        st.chat_message("user").write(user_input)
        
        # Simulate agent response
        time.sleep(1)
        response = f"🤖 **Maintenance Agent**: I've analyzed Robot R-47's condition. Scheduling maintenance window for Tuesday 14:00-18:00. Estimated impact: 0.3% production loss."
        st.chat_message("assistant").write(response)

elif component == "LLM Orchestration":
    st.header("LLM Orchestration Layer")
    st.markdown("Cognitive coordination and natural language interface")
    
    # LLM Status
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Model", "Llama-2-7B", "Fine-tuned")
    with col2:
        st.metric("Tokens/min", "1.2K", "↑ 5%")
    with col3:
        st.metric("Accuracy", "92.1%", "↑ 1.2%")
    
    # Chat interface
    st.subheader("Natural Language Interface")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask anything about your factory..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            response = f"I understand you're asking about: '{prompt}'. Based on current system status, here's what I recommend: [This would be generated by the fine-tuned LLM in a real implementation]"
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.markdown("**Agentic AI Framework** | Built with Streamlit | Apache 2.0 License")
