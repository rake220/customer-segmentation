#!/usr/bin/env python
# coding: utf-8

# In[7]:


from fastapi import FastAPI, HTTPException
import pandas as pd

app = FastAPI()

# Load the CSV
df = pd.read_csv("segmented_customers.csv")

@app.get("/customer/{customer_id}")
def get_customer_info(customer_id: int):
    customer = df[df["CustomerID"] == customer_id]
    if customer.empty:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer.iloc[0].to_dict()

@app.get("/segment/{segment_id}")
def get_customers_in_segment(segment_id: int):
    customers = df[df["Segment"].astype(str) == str(segment_id)]
    if customers.empty:
        raise HTTPException(status_code=404, detail=f"No customers found in segment {segment_id}")
    return customers[["CustomerID", "Gender", "Age"]].to_dict(orient="records")


# In[ ]:





# In[ ]:




