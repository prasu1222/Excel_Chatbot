import streamlit as st
import pandas as pd
import os
import tempfile
from langchain_community.chat_models import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

# Set page title
st.title("📊 Data Chat - Talk to Your Data")

# Function to preprocess and save uploaded file
def preprocess_and_save(uploaded_file):
    try:
        # Create a temporary file
        temp_dir = tempfile.mkdtemp()
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_extension == '.csv':
            # For CSV files
            temp_path = os.path.join(temp_dir, "uploaded_data.csv")
            df = pd.read_csv(uploaded_file)
            df.to_csv(temp_path, index=False)
        elif file_extension == '.xlsx':
            # For Excel files
            temp_path = os.path.join(temp_dir, "uploaded_data.xlsx")
            df = pd.read_excel(uploaded_file)
            df.to_excel(temp_path, index=False)
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None, None, None
        
        # Get column names
        columns = df.columns.tolist()
        
        return temp_path, columns, df
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None, None, None

# Add OpenAI API key input in sidebar
with st.sidebar:
    # st.header("Configuration")
    # api_key = st.text_input("Enter your OpenAI API key", type="password")
    st.markdown("---")
    st.markdown("### Data Analysis Tips")
    st.markdown("""
    - Upload a CSV or Excel file to get started
    - Ask questions in natural language
    - Try questions like:
        - "What's the average of column X?"
        - "Show me the distribution of Y"
        - "Find correlations between A and B"
    """)

# File uploader
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

# Initialize session state for conversation history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if uploaded_file is not None:
    # Preprocess and save the uploaded file
    temp_path, columns, df = preprocess_and_save(uploaded_file)
    
    if temp_path and columns and df is not None:
        # Display the uploaded data as a table
        st.write("Uploaded Data:")
        st.dataframe(df)  # Use st.dataframe for an interactive table
        
        # Display the columns of the uploaded data
        st.write("Columns in your data:", ", ".join(columns))
        
        # Create a chat input
        if prompt := st.chat_input("Ask a question about your data"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                response_container = st.empty()
                
                # if not api_key:
                #     response = "Please enter your OpenAI API key in the sidebar to enable the chat functionality."
                # else:
                try:
                        # Set OpenAI API key
                    os.environ["OPENAI_API_KEY"] = "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"
                        
                    # Create a pandas agent to answer questions about the dataframe
                    agent = create_pandas_dataframe_agent(ChatOpenAI(temperature=0, model="gpt-4"),
                            df,
                            verbose=True,
                            agent_type=AgentType.OPENAI_FUNCTIONS,
                            allow_dangerous_code=True)
                        
                    # Get response from the agent
                    response = agent.run(prompt)
                except Exception as e:
                        response = f"Error: {str(e)}"
                
                # Display the response
                response_container.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.info("Please upload a CSV or Excel file to get started.")

# Add footer
st.markdown("---")
st.caption("Data Chat App - Powered by LangChain and OpenAI")