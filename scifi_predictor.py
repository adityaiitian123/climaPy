import os
import groq
from dotenv import load_dotenv
import xarray as xr
import numpy as np
import streamlit as st

load_dotenv()

class ScifiPredictor:
    """AI module for climate intelligence briefings using Groq."""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment.")
        self.client = groq.Groq(api_key=self.api_key)

    def generate_intelligence_briefing(self, ds: xr.Dataset, variable: str, stats: dict):
        """Generates an intelligence briefing with persona adapted to ui_mode."""
        ui_mode = st.session_state.get("ui_mode", "public")
        
        if ui_mode == "public":
            persona = "You are 'Clima-Bot', a friendly planetary companion. Objective: Explain climate data to a curious citizen using analogies."
            task_instr = "Provide a 'Quick Tip' (2 sentences) using friendly analogies. Identify 'What this means for you'. projecting 'Our Path Forward'. Keep it warm and hopeful."
        else:
            persona = "You are 'PyClima-Core', a high-level tactical intelligence AI. Objective: Analyze climate telemetry and provide a tactical intelligence briefing."
            task_instr = "Provide a 'Tactical Summary' (2-3 sentences) in a cold, professional, scifi tone. Identify 'Critical Anomalies'. Project a 'Future Trajectory'. Use technical jargon."

        prompt = f"""
        System: {persona}

        TELEMETRY DATA:
        Variable: {variable}
        Global Mean: {stats.get('mean', 'N/A')}
        Max Recorded: {stats.get('max', 'N/A')}
        Min Recorded: {stats.get('min', 'N/A')}
        Std Dev: {stats.get('std', 'N/A')}

        TASK:
        {task_instr}
        """

        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"SYSTEM ERROR: Failed to interface with AI Core. Detail: {str(e)}"

    def generate_story_narrative(self, variable, title, stats):
        """Generates an immersive story narrative for a specific climate event."""
        ui_mode = st.session_state.get("ui_mode", "public")
        
        if ui_mode == "public":
            persona = "Climate Storyteller"
            ctx_instr = "You are narrating a guided tour of Earth's changing climate for a general audience. Be engaging, clear, and hopeful."
            task_instr = "Explain the significance of this data point as part of a larger story. Use one striking analogy."
        else:
            persona = "Planetary Historian"
            ctx_instr = "You are recording a high-fidelity historical record of planetary shifts. Be objective, precise, and use a slightly formal, archival tone."
            task_instr = "Document the structural significance of this change in the context of the 21st-century climate transition."

        prompt = f"""
        System Persona: {persona}
        Context: {ctx_instr}
        
        DATA POINT:
        Insight Title: {title}
        Variable: {variable}
        Mean Intensity: {stats.get('mean', 'N/A')}
        
        TASK:
        {task_instr}
        """
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=300
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Transmissions garbled. Manual override required. (Error: {str(e)})"

    def get_future_projection(self, ds: xr.Dataset, variable: str):
        """Simulates a future projection for the variable (AI-augmented placeholder)."""
        # For a real implementation, we might use the LLM to hypothesize or a statistical model.
        # Here we'll generate a projected trend based on existing mean trajectory.
        timeseries = ds[variable].mean(dim=['lat', 'lon'], skipna=True).values
        last_val = float(timeseries[-1])
        trend = np.mean(np.diff(timeseries))
        
        # Project 20 steps into the future
        projections = []
        current = last_val
        for i in range(20):
            noise = np.random.normal(0, abs(trend * 0.5) if trend != 0 else 0.1)
            current += trend + noise
            projections.append(float(current))
            
        return projections
