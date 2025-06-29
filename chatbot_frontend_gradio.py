#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[ ]:


import gradio as gr
import requests

def get_customer_info(customer_id):
    if not customer_id.isdigit():
        return "Please enter a valid numeric Customer ID."
    try:
        url = f"http://127.0.0.1:8080/customer/{customer_id}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            info = (
                f"Customer ID: {data.get('CustomerID')}\n"
                f"Gender: {data.get('Gender')}\n"
                f"Age: {data.get('Age')}\n"
                f"Annual Income (k$): {data.get('Annual Income (k$)')}\n"
                f"Spending Score (1-100): {data.get('Spending Score (1-100)')}\n"
                f"Segment: {data.get('Segment')}"
            )
            return info
        elif response.status_code == 404:
            return f"Customer ID {customer_id} not found."
        else:
            return "Error fetching customer data."
    except Exception as e:
        return f"Request failed: {e}"

iface = gr.Interface(
    fn=get_customer_info,
    inputs=gr.Textbox(label="Enter Customer ID"),
    outputs=gr.Textbox(label="Customer Information"),
    title="Customer Segmentation Chatbot",
    description="Enter a customer ID to get full customer info and segment."
)

if __name__ == "__main__":
    iface.launch()


# In[ ]:




