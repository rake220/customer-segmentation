#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[ ]:


from langchain_community.llms import Ollama
from langchain.agents import Tool, initialize_agent
import requests

# Initialize the LLM
llm = Ollama(model="mistral")

# Tool to fetch a single customer by ID
def get_full_customer_info(customer_id: str):
    customer_id_clean = customer_id.strip("'\" ")
    url = f"http://127.0.0.1:8080/customer/{customer_id_clean}"
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
        return f"Customer {customer_id_clean} not found"
    else:
        return f"Error fetching data for customer {customer_id_clean}, status {response.status_code}"

# Tool to fetch customers in a segment
def get_customers_in_segment(segment_id: str):
    # forcibly clean all weird agent formatting
    cleaned_id = (
        str(segment_id)
        .replace("segment_id=", "")
        .replace("(", "")
        .replace(")", "")
        .replace("\"", "")
        .replace("'", "")
        .strip()
    )

    print(f">>> Calling segment lookup with cleaned segment_id: {cleaned_id}")

    url = f"http://127.0.0.1:8080/segment/{cleaned_id}"
    response = requests.get(url)
    print(f">>> Segment lookup status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if not data:
            return f"No customers found in segment {cleaned_id}"
        result = "\n".join(
            f"ID: {cust['CustomerID']}, Gender: {cust['Gender']}, Age: {cust['Age']}"
            for cust in data
        )
        return result
    elif response.status_code == 404:
        return f"No customers found in segment {cleaned_id}"
    else:
        return f"Error fetching customers for segment {cleaned_id}, status {response.status_code}"

# define the tools
tools = [
    Tool(
        name="FullCustomerInfoLookup",
        func=get_full_customer_info,
        description="Get all available info about a customer by their ID."
    ),
    Tool(
        name="CustomersInSegmentLookup",
        func=get_customers_in_segment,
        description="Get a list of customers with their ID, gender, and age in a specified segment by segment ID (e.g., '1')."
    )
]

# initialize the agent
agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True
)

# entry point
if __name__ == "__main__":
    print("Ask your questions about customers or segments. Type 'exit' to quit.")
    while True:
        user_input = input("Ask about a customer or segment: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
        response = agent.run(user_input)
        print("\n" + response + "\n")


# In[ ]:




