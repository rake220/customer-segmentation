#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[ ]:


import gradio as gr

# Import your LangChain agent setup (adjust import as needed)
from agent import agent  # or from your_agent_module import agent

# Store chat history as a list of tuples (user, bot)
chat_history = []

def chatbot_response(user_message):
    global chat_history
    # Append user message to history
    chat_history.append(("User", user_message))
    
    # Combine chat history into a single string for context (optional)
    # Or pass messages list if your agent supports it
    # Here, just sending current user message to agent
    response = agent.run(user_message)
    
    # Append bot response to history
    chat_history.append(("Agent", response))
    
    # Prepare display chat log
    display = ""
    for speaker, msg in chat_history:
        display += f"{speaker}: {msg}\n\n"
    return display

iface = gr.Interface(
    fn=chatbot_response,
    inputs=gr.Textbox(lines=2, placeholder="Ask about customer segments..."),
    outputs=gr.Textbox(lines=20),
    title="Customer Segmentation Chatbot",
    description="Chat with the agent to get customer segmentation info."
)

if __name__ == "__main__":
    iface.launch()

