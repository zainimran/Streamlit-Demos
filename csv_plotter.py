# csv_plotter.py
import streamlit as st
import pandas as pd

# Use cache for loading data
@st.cache_data
def load_csv(file_obj):
    return pd.read_csv(file_obj)

st.title("📊 CSV Quick Plotter")

uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

# Initialize df in session state to None if not already there
if 'df' not in st.session_state:
    st.session_state.df = None
if 'data_source_name' not in st.session_state:
    st.session_state.data_source_name = None

if uploaded_file is not None:
    # To prevent reloading and reprocessing if other widgets change
    if st.session_state.data_source_name != uploaded_file.name:
        st.session_state.df = load_csv(uploaded_file)
        st.session_state.data_source_name = uploaded_file.name
    df = st.session_state.df # work with the dataframe from session state
    st.sidebar.success(f"'{uploaded_file.name}' loaded!")
else:
    # Provide a way to load sample data if no file is uploaded
    if st.sidebar.button("Load Sample Data"):
        try:
            st.session_state.df = load_csv("sample_data.csv") # Assuming sample_data.csv is in the same directory
            st.session_state.data_source_name = "Sample Data"
            st.sidebar.success("Sample data loaded!")
        except FileNotFoundError:
            st.sidebar.error("sample_data.csv not found.")
            st.session_state.df = None # Ensure df is None if sample loading fails
    df = st.session_state.df # Re-assign df from session state

if df is not None:
    st.header("Data Preview (First 5 rows)")
    st.dataframe(df.head())
    # Add this inside the `if df is not None:` block

    st.header("📊 Create a Plot")
    columns = df.columns.tolist()
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()

    if not numeric_columns:
        st.warning("No numeric columns found in the CSV for plotting the Y-axis.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            x_axis = st.selectbox("Select X-axis:", columns, index=0 if columns else None)
        with col2:
            y_axis = st.selectbox("Select Y-axis (must be numeric):", numeric_columns, index=0 if numeric_columns else None)

        plot_type = st.radio("Select Plot Type:", ("Bar Chart", "Line Chart"), horizontal=True)

        if x_axis and y_axis:
            st.subheader(f"{plot_type} of {y_axis} vs {x_axis}")
            try:
                if plot_type == "Bar Chart":
                    if df[x_axis].dtype == 'object' and df[x_axis].nunique() < 20: # Heuristic for categorical
                        st.bar_chart(df.groupby(x_axis)[y_axis].mean()) # Show mean as an example
                        st.caption(f"Showing mean of {y_axis} for each {x_axis}")
                    else: # If X is numeric or too many categories, plot directly
                        st.bar_chart(df.set_index(x_axis)[y_axis])
                elif plot_type == "Line Chart":
                    # Line charts often benefit from a sorted X-axis
                    chart_data = df.sort_values(by=x_axis) if pd.api.types.is_numeric_dtype(df[x_axis]) or pd.api.types.is_datetime64_any_dtype(df[x_axis]) else df
                    st.line_chart(chart_data.set_index(x_axis)[y_axis])
            except Exception as e:
                st.error(f"Could not generate plot. Error: {e}")
                st.error("Ensure X and Y axes are compatible for the selected plot type.")
        else:
            st.info("Please select X and Y axes to generate a plot.")

    with st.expander("View Data Summary"):
        st.write("**Shape:**", df.shape)
        st.write("**Columns:**", df.columns.tolist())
        st.write("**Data Types:**")
        st.dataframe(df.dtypes.reset_index().rename(columns={'index': 'Column', 0: 'Data Type'}))
        if st.checkbox("Show Descriptive Statistics"):
            st.dataframe(df.describe(include='all'))
else:
    st.info("Upload a CSV file or load sample data to get started.")