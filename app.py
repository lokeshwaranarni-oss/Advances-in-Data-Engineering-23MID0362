import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt

# Import custom core modules
from core.profiler import profile_data
from core.decision_engine import select_best_method
from core.monitoring import monitor_compression
from storage.feedback_db import FeedbackDB

# Setup the page
st.set_page_config(
    page_title="Intelligent Compression Engine",
    page_icon="🗜️",
    layout="wide"
)

# Initialize database
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "storage", "history.db")
db = FeedbackDB(DB_PATH)

# Ensure output directory exists
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT_DIR = os.path.join(DATA_DIR, "compressed")
os.makedirs(OUTPUT_DIR, exist_ok=True)

st.title("🗜️ Adaptive Intelligent Data Compression Engine")
st.markdown("Dynamically profiles data, selects the best compression strategy, and monitors real-time performance.")

# --- Sidebar ---
st.sidebar.header("Input Configuration")

# Selection Mode
input_mode = st.sidebar.radio("Data Source:", ["Select Sample Dataset", "Upload Dataset"])

if "target_file" not in st.session_state:
    st.session_state.target_file = None

if input_mode == "Select Sample Dataset":
    samples = {
        "1MB CSV (High Repetition)": os.path.join(DATA_DIR, "sample_1mb.csv"),
        "5MB JSON (Structural)": os.path.join(DATA_DIR, "sample_5mb.json"),
        "10MB Log (High Entropy)": os.path.join(DATA_DIR, "sample_10mb.log")
    }
    selected_sample = st.sidebar.selectbox("Choose a sample file:", list(samples.keys()))
    if st.sidebar.button("Load Sample Data"):
        st.session_state.target_file = samples[selected_sample]

elif input_mode == "Upload Dataset":
    uploaded_file = st.sidebar.file_uploader("Upload any file (CSV, JSON, TXT, etc.)")
    if uploaded_file is not None:
        # Save temp file
        temp_path = os.path.join(DATA_DIR, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.sidebar.success(f"Uploaded {uploaded_file.name} successfully!")
        if st.sidebar.button("Analyze & Compress"):
            st.session_state.target_file = temp_path

# --- Main Dashboard ---
target_file = st.session_state.target_file
if target_file and os.path.exists(target_file):
    
    st.header("1. Data Profiling & Characteristics")
    with st.spinner("Profiling dataset (Calculating Entropy and Repetition Ratio)..."):
        profile = profile_data(target_file)
        
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("File Name", profile["file_name"])
    col2.metric("Size", f"{profile['size_mb']:.2f} MB")
    col3.metric("Entropy (0-8)", f"{profile['entropy']:.2f}")
    col4.metric("Repetition Ratio", f"{profile['repetition_ratio']:.2%}")

    st.header("2. Intelligent Decision Engine")
    decision = select_best_method(profile)
    
    st.info(f"**Recommended Algorithm:** `{decision['method'].upper()}`")
    st.success(f"**Engine Rationale:** {decision['reason']}")
    
    # Allow user override
    st.markdown("### Compression Execution")
    override = st.checkbox("Override recommendation?")
    selected_method = decision["method"]
    if override:
        selected_method = st.selectbox("Select method manually:", ["gzip", "lz4", "zstd", "none"], index=["gzip", "lz4", "zstd", "none"].index(decision["method"]))
    
    if st.button("Execute Compression Pipeline", type="primary"):
        with st.spinner(f"Compressing using {selected_method.upper()}..."):
            metrics = monitor_compression(target_file, selected_method, OUTPUT_DIR)
            
            # Log to DB
            db.log_run(profile, metrics, selected_method)
            
            st.header("3. Performance Results")
            r_col1, r_col2, r_col3, r_col4 = st.columns(4)
            r_col1.metric("Compressed Size", f"{(metrics['compressed_size_bytes'] / (1024*1024)):.2f} MB", f"-{metrics['storage_savings_percent']:.1f}%")
            r_col2.metric("Compression Ratio", f"{metrics['compression_ratio']:.2f}x")
            r_col3.metric("Execution Time", f"{metrics['compression_time_seconds']*1000:.2f} ms")
            r_col4.metric("CPU Overhead", f"{metrics['cpu_usage_percent']}%")
            
        st.subheader("Size Reduction Visualized")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(["Original Size", "Compressed Size"], 
               [metrics['original_size_bytes'] / (1024*1024), metrics['compressed_size_bytes'] / (1024*1024)],
               color=['#ff9999','#66b3ff'])
        ax.set_ylabel("Size (MB)")
        st.pyplot(fig)

st.divider()
st.header("4. Feedback Learning Loop (History)")

# Retrieve historical runs
history = db.get_all_runs()

if history:
    df_history = pd.DataFrame(history)
    st.dataframe(df_history[["timestamp", "file_name", "algorithm_used", "original_size_mb", "compressed_size_mb", "compression_ratio", "savings_percent", "compression_time_seconds"]], use_container_width=True)
    
    st.subheader("Algorithm Performance Averages")
    averages = db.get_average_performance_by_algorithm()
    if averages:
        df_avg = pd.DataFrame(averages)
        st.bar_chart(df_avg.set_index("algorithm")[["avg_ratio"]], use_container_width=True)
else:
    st.markdown("No historical runs recorded yet. Execute a compression job to populate this dashboard.")
