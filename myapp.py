import streamlit as st
import numpy as np

# Toggle switch for novelty mode
on = st.toggle("Novelty mode", key='novelty_mode')

# Mapping from mode name to novelty factor
mode_to_novelty = {
    "Classic": 0.1,
    "Surprise Me": 1
}

# Determine mode and novelty factor based on toggle
if on:
    mode = "Surprise Me"
else:
    mode = "Classic"

novelty_factor = mode_to_novelty[mode]

# Show confirmation
st.write(f"Mode: **{mode}**")
st.write(f"Novelty Factor: **{novelty_factor}**")
