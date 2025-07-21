import streamlit as st
from langchain_experimental.agents import create_csv_agent
from langchain_openai import ChatOpenAI
import os
import tempfile
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set page title
st.title("📊 Data Chat - Talk to Your Data")

# Function to preprocess and save uploaded file
def preprocess_and_save(uploaded_file):
    try:
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_extension == '.csv':
            # Read CSV
            df = pd.read_csv(uploaded_file,encoding='utf-8')
        elif file_extension == '.xlsx':
            # Read Excel
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None, None
        
        # Save cleaned DataFrame to a temporary CSV
        temp_path = os.path.join(os.getcwd(), "uploaded_data.csv")
        df.to_csv(temp_path, index=False, encoding='utf-8')

        return temp_path, df
    
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None, None

# Sidebar info
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📌 How to Use")
    st.markdown("""
    1. Upload a CSV or Excel file.
    2. Ask a question in plain English.
    3. The AI will analyze the data and give you an answer.
    
    Example Questions:
    - What's the total sales?
    - Show average value of column X
    - How many rows are there?
    """)

# File uploader
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

# Initialize session state for conversation history
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'df' not in st.session_state:
    st.session_state.df = None

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle file upload
if uploaded_file is not None:
    temp_path, df = preprocess_and_save(uploaded_file)
    if df is not None:
        st.session_state.df = df
        st.write("📄 **First 2 Rows of Uploaded Data:**")
        st.write(temp_path," **File Name:**")
        st.dataframe(df.head(2))  # 👈 This now shows the first 2 rows

# Chat input
if st.session_state.df is not None:
    if prompt := st.chat_input("Ask a question about your data"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message("assistant"):
            response_container = st.empty()
            try:
                # Check API key
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not found in environment variables")

                # Setup agent
                llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
                agent = create_csv_agent(llm,"uploaded_data.csv",verbose=True,allow_dangerous_code=True)  
                # Run query
                response = agent.invoke({"input": prompt})['output']
            except Exception as e:
                response = f"⚠️ Error: {str(e)}"

            # Display and save response
            response_container.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.info("📂 Please upload a CSV or Excel file to get started.")

# Footer
st.markdown("---")
st.caption("🧠 Powered by LangChain | 🤖 GPT-3.5 Turbo | 📊 Streamlit")
