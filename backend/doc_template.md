## Endpoints Documentation for

#### Search Endpoint

The **search** endpoint is designed to only return the top n most likely matches from the vector database given the query.
You may also filter the results through this endpoint.

URL: {SEARCH_ENDPOINT}
Method: POST

| Parameter | Data Type | Description                                                                                                                 |
| --------- | --------- | --------------------------------------------------------------------------------------------------------------------------- |
| n         | int       | Determines the number of search results returned                                                                            |
| query     | string    | Query string to vectorize and perform a similarity search on                                                                |
| filters   | object    | object with key value pairs, where each key is the attribute to filter on, and value is the filter value for that attribute |

Returns:

Array of matches, where each item is an object/dictionary with the following key-value pairs:

- id: Indicates the file and chunk in one identifier string
- metadata: object
  - chunk_id: int id of the chunk of the document
  - name: source document filename
  - text: text corresponding to chunk
- score: float representing similarity score of chunk with the query, from 0 to 1

#### Chat Endpoint

The **chat** endpoint is designed to use the search results to feed to an LLM from OpenAI and obtain an answer using RAG.
You may also filter the results through this endpoint.

URL: {CHAT_ENDPOINT}
Method: POST

| Parameter      | Data Type | Description                                                                                                                 |
| -------------- | --------- | --------------------------------------------------------------------------------------------------------------------------- |
| n              | int       | Determines the number of search results returned                                                                            |
| search_query   | string    | Query that will be used for the similarity search for retrieval purposes                                                    |
| chat_query     | string    | Query that will be fed to the LLM to get a response based on the retrieved context                                          |
| system_message | string    | System Message for the LLM for customization purposes, defaults to empty string                                             |
| api_key        | string    | The API key used for authentication with the service                                                                        |
| model          | string    | one of 'gpt-3.5-turbo' or 'gpt-4' (only OpenAI models are supported for now)                                                |
| filters        | object    | object with key value pairs, where each key is the attribute to filter on, and value is the filter value for that attribute |

Returns:

An object/dictionary with the following keys:

- matches: Array of all matches where each item is an object/dictionary with the following key-value pairs:
  - id: Indicates the file and chunk in one identifier string
  - metadata: object
    - chunk_id: int id of the chunk of the document
    - name: source document filename
    - text: text corresponding to chunk
- messages: Array of the message history with the LLM, where the last item is the response returned by the LLM. Each element contains:
  - content: The string sent to and received by the LLM in that message
  - role: string identifier that determines whether message was created by user, was a system message, or was a response by the LLM. Can take one of three values: "system", "user", "assistant"
