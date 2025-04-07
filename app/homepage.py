import streamlit as st

# Sample agents data
agents = [
    {
        "agent_token": "AGENT_1",
        "current_system": "X1-DF55",
        "current_waypoint": "PLANET-01",
        "credit": 5000,
        "starting_faction": "COSMIC_LEGION",
    },
    {
        "agent_token": "AGENT_2",
        "current_system": "X2-AB89",
        "current_waypoint": "ASTEROID-04",
        "credit": 8000,
        "starting_faction": "GALACTIC_UNION",
    },
]

# Initialize session state
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = None

# If an agent is selected, show details page
if st.session_state.selected_agent:
    agent = next(
        a for a in agents if a["agent_token"] == st.session_state.selected_agent
    )

    st.title(f"🛰️ {agent['agent_token']} - Agent Details")
    st.markdown(
        f"""
        <div style="
            padding: 20px; 
            border-radius: 12px; 
            border: 2px solid #4CAF50; 
            background-color: #f9f9f9;
            text-align: center;">
            <h3>{agent["agent_token"]}</h3>
            <p><strong>System:</strong> {agent["current_system"]}</p>
            <p><strong>Waypoint:</strong> {agent["current_waypoint"]}</p>
            <p><strong>💰 Credit:</strong> {agent["credit"]}</p>
            <p><strong>🏴 Faction:</strong> {agent["starting_faction"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Back button
    if st.button("🔙 Back to Agents Overview"):
        st.session_state.selected_agent = None
        st.experimental_rerun()

else:
    # Show agent list
    st.title("🚀 Agents Overview")

    for agent in agents:
        # Create a button that updates session state
        if st.button(
            f"🛰️ {agent['agent_token']} - {agent['current_system']} | {agent['current_waypoint']} | 💰 {agent['credit']} | 🏴 {agent['starting_faction']}",
            key=agent["agent_token"],
        ):
            st.session_state.selected_agent = agent["agent_token"]
            st.experimental_rerun()
