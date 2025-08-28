import streamlit as st
import ollama
import time
from typing import List, Dict

# Page configuration
st.set_page_config(
    page_title="AI Chat App with Ollama",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #f0f2f6;
        border-left: 4px solid #4e79a7;
    }
    .assistant-message {
        background-color: #e6f7ff;
        border-left: 4px solid #1890ff;
    }
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
    }
    /* Make text gray with 60% transparency */
    .user-message, .assistant-message {
        color: rgba(128, 128, 128, 0.6) !important;
    }
    /* Keep the strong elements slightly darker for better readability */
    .user-message strong, .assistant-message strong {
        color: rgba(96, 96, 96, 0.8) !important;
    }
</style>
""", unsafe_allow_html=True)


class OllamaChatApp:
    def __init__(self):
        self.setup_session_state()

    def setup_session_state(self):
        """Initialize session state variables"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'model' not in st.session_state:
            st.session_state.model = "llama2"  # Default model
        if 'available_models' not in st.session_state:
            st.session_state.available_models = self.get_available_models()

    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            models = ollama.list()
            return [model['model'] for model in models['models']]
        except Exception as e:
            st.error(f"Error fetching models: {e}")
            return ["llama2", "mistral", "gemma"]  # Fallback models

    def send_message(self, message: str) -> str:
        """Send message to Ollama and get response"""
        try:
            # Add user message to conversation history
            st.session_state.messages.append({"role": "user", "content": message})

            # Generate response using Ollama
            response = ollama.chat(
                model=st.session_state.model,
                messages=st.session_state.messages
            )

            assistant_response = response['message']['content']

            # Add assistant response to conversation history
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})

            return assistant_response

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.error(error_msg)
            return error_msg

    def clear_chat(self):
        """Clear the chat history"""
        st.session_state.messages = []

    def display_chat(self):
        """Display the chat messages"""
        st.markdown("### 💬 Chat Conversation")

        # Create a container for chat messages
        chat_container = st.container()

        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(
                        f"""
                        <div class="stChatMessage user-message">
                            <strong>👤 You:</strong><br>
                            {message["content"]}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="stChatMessage assistant-message">
                            <strong>🤖 Assistant:</strong><br>
                            {message["content"]}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    def run(self):
        """Run the main application"""
        # Sidebar for settings
        with st.sidebar:
            st.title("⚙️ Settings")

            # Model selection
            st.session_state.model = st.selectbox(
                "Select Model:",
                options=st.session_state.available_models,
                index=0
            )

            # Clear chat button
            if st.button("🗑️ Clear Chat", use_container_width=True):
                self.clear_chat()
                st.rerun()

            # Display model information
            st.markdown("---")
            st.markdown("### ℹ️ About")
            st.info(
                f"Using model: **{st.session_state.model}**\n\n"
                "Make sure Ollama is running on your system with:\n"
                "```bash\nollama serve\n```"
            )

        # Main chat area
        st.title("🤖 AI Chat App with Ollama")
        st.markdown("Chat with various AI models powered by Ollama")

        # Display chat messages
        self.display_chat()

        # Chat input
        user_input = st.chat_input("Type your message here...")

        if user_input:
            # Display user message immediately
            with st.chat_message("user"):
                st.markdown(user_input)

            # Generate and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = self.send_message(user_input)
                    st.markdown(response)

            # Rerun to update the chat display
            st.rerun()


def main():
    # Check if Ollama is running
    try:
        ollama.list()
    except Exception as e:
        st.error(
            "Ollama is not running or not installed!\n\n"
            "Please make sure to:\n"
            "1. Install Ollama from https://ollama.ai/\n"
            "2. Run `ollama serve` in your terminal\n"
            "3. Pull some models: `ollama pull llama2`\n\n"
            f"Error details: {e}"
        )
        return

    # Initialize and run the app
    app = OllamaChatApp()
    app.run()


if __name__ == "__main__":
    main()