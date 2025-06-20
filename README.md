#  DRAG – Distributed Retrieval-Augmented Generation Platform
**DRAG** is a distributed, cloud-native platform designed to help enterprise users unlock the power of Retrieval-Augmented Generation (RAG) across large custom datasets. It streamlines data vectorization, distributed inference, and seamless integration of chat and search capabilities through simple API endpoints.

---

## Purpose

The purpose of DRAG is to provide a platform to enterprise users with large data corpuses to integrate RAG functionality into their existing products through RAG API endpoints.

The platform simplifies the process involved in large-scale inference and vectorization by offering:

- A user-friendly frontend for setting up GPU resources and configuring inference parameters
- A robust backend powered by AWS SageMaker to perform distributed inference
- A streamlined pipeline that exposes chat and search API endpoints over your processed data

---

##  Tech Stack

- **Cloud & Infrastructure:** AWS (SageMaker, Bedrock, API Gateway, S3, RDS, SQS, Cognito, CloudWatch, SNS), Terraform  
- **Backend:** Python, Flask, Boto3  
- **Frontend:** Svelte  
- **Vector Store:** Pinecone  
- **Database:** PostgreSQL  

---

## Features

- Upload documents from your local machine for processing  
- Customize inference settings: model type, GPU count, batch size, and worker nodes  
- Perform fast, distributed inference using AWS SageMaker (~40,000 vectors/min)  
- Vectorize documents and store them in Pinecone for semantic search  
- Expose chat and search API endpoints for easy integration into other apps  
- Manage everything through a simple web interface built with Flask and Svelte  
- Scalable, cloud-native deployment using AWS and Terraform

---

## License
This project is for portfolio and demonstration purposes only.  
View the full license [here](./LICENSE).

---

## Copyright

© 2025 Zeta Solution. All rights reserved.

This repository is intended for educational, non-commercial, and reference purposes only.  
No part of this codebase may be used, copied, modified, or distributed for commercial use without explicit written permission.



