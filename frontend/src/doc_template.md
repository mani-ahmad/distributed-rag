## Endpoints Documentation for {JOB_NAME}

#### Search Endpoint

The **search** endpoint is designed to only return the top n most likely matches from the vector database given the query.
You may also filter the results through this endpoint.

URL: {SEARCH_ENDPOINT} \
Method: POST

| Parameter | Data Type | Description                                                                                                                 |
|-----------|-----------|-----------------------------------------------------------------------------------------------------------------------------|
| n         | int       | Determines the number of search results returned                                                                            |
| query     | string    | Query string to vectorize and perform a similarity search on                                                                |
| filters   | object    | object with key value pairs, where each key is the attribute to filter on, and value is the filter value for that attribute |

#### Chat Endpoint

The **chat** endpoint is designed to use the search results to feed to an LLM from OpenAI and obtain an answer using RAG.
You may also filter the results through this endpoint.

URL: {CHAT_ENDPOINT} \
Method: POST

| Parameter      | Data Type | Description                                                                                                                 |
|----------------|-----------|-----------------------------------------------------------------------------------------------------------------------------|
| n              | int       | Determines the number of search results returned                                                                            |
| search_query   | string    | Query that will be used for the similarity search for retrieval purposes                                                    |
| chat_query     | string    | Query that will be fed to the LLM to get a response based on the retrieved context                                          |
| system_message | string    | System Message for the LLM for customization purposes, defaults to empty string                                             |
| model          | string    | one of 'gpt-3.5' or 'gpt-4' (only OpenAI models are supported for now)                                                      |
| filters        | object    | object with key value pairs, where each key is the attribute to filter on, and value is the filter value for that attribute |