# AFilm Bot — Technical Architecture and System Design

## 1. Overall System Architecture

AFilm Bot is designed using a modular architecture. Its components are separated so that each one has a clearly defined responsibility, while communication between them takes place through well-defined interfaces.

In this architecture, the Telegram layer is responsible for user communication, the Conversation Manager handles conversation management, and LangGraph controls the Agent execution flow and its interactions with tools.

The system consists of several main components:

- **Telegram Interface:** Handles incoming and outgoing messages, commands, and user login processes.
- **Conversation Manager:** Manages conversation history, stores messages, and forwards user requests to the Agent.
- **Agent Layer:** Manages the decision-making process and tool execution using LangGraph.
- **LLM:** Analyzes user requests, decides whether tools are needed, and generates final responses.
- **Tools:** Specialized tools for movie recommendations, database access, and information retrieval.
- **Recommendation Engine:** A hybrid recommendation system for selecting suitable movies.
- **Database Layer:** Manages MySQL connectivity and database operations.

## 2. Agent, Language Model, and Tool Calling

The intelligent core of AFilm Bot is built around an Agent architecture using LangChain and LangGraph.

The Large Language Model (LLM) is responsible for analyzing user messages and deciding how to respond. Depending on the type of request, the model can either generate a response directly or determine that one of the system's specialized tools is required to provide a more accurate answer.

For this purpose, several tools are available to the Agent:

- **Recommendation Tool:** Communicates with the recommendation system and retrieves recommended movies.
- **Database Tools:** Provide access to information and data stored in the database.
- **Information Tools:** Retrieve information about movies and other relevant data. This category also includes specialized tools that allow the Agent to identify and explain AFilm Bot's capabilities and features, as well as provide information about its developer. These tools enable the bot to answer users' questions about itself and its developer.

The Agent execution process is managed using a `StateGraph` in LangGraph. After receiving a message, the model analyzes the request. If necessary, the appropriate tool is invoked, and its execution result is returned to the model to generate the final response.

This process continues until the model produces a final response or determines that no further tool execution is necessary.

The language model used in the system belongs to the Qwen family and is accessed through an OpenAI-compatible API.

## 3. Hybrid Recommendation System

One of the core components of AFilm Bot is its hybrid recommendation engine. This system combines three different approaches to select and rank suitable candidates through multiple stages.

The goal of this design is to use content similarity, user interaction patterns, and additional evaluation criteria together to improve recommendation quality.

### 3.1. Semantic Search

In the first stage, Sentence Transformers is used to convert movie text information into semantic vectors.

The generated vectors are stored and searched using FAISS to identify movies that are semantically closest to the user's request.

At this stage, the system retrieves 50 movies relevant to the user's request. The two highest-ranked movies are separated and preserved for final evaluation.

Movies that the user has already watched are also excluded from the recommendation candidates.

**Technologies:**

- Sentence Transformers
- FAISS
- NumPy

### 3.2. Collaborative Filtering with LightFM

In the second stage, the remaining candidates from the Semantic Search stage are passed to the LightFM model.

LightFM uses user interaction patterns to rank movies according to their relevance to the user's interaction history.

During model training, positive user interactions are assigned different weights:

- Like: Weight 2
- Seen: Weight 1

Dislike interactions are not directly included as training interactions. Instead, a custom method is implemented to identify movies disliked by the user and reduce their scores in the LightFM output.

Finally, the 10 highest-ranked movies are selected. The two highest-ranked movies are also preserved for final evaluation.

**Technology:**

- LightFM

### 3.3. Business Rules

In the third stage, the 10 movies selected by LightFM are passed to the Business Rules component.

This component evaluates and ranks movies using a set of predefined criteria.

To combine these criteria, each criterion's score is first normalized using Min-Max Normalization:

`(x - min) / (max - min)`

The normalized criteria then contribute equally to the final score.

Finally, the two highest-ranked movies from this stage are preserved for the final selection.

### 3.4. Final Recommendation Selection

After the three stages have been completed, their outputs are combined:

- The two highest-ranked movies from Semantic Search
- The two highest-ranked movies from LightFM
- The two highest-ranked movies from Business Rules

As a result, up to six movies are passed to the final stage.

At this stage, information about the selected movies, together with the User Profile, is provided to the bot's main LLM. Based on the user's current request and the available information, the model selects the most suitable options.

Under the current system configuration, the model typically recommends three movies to the user.

### 3.5. User Profile and Personalization

User-related information is retrieved from the database using the user's identifier and stored interaction history.

This information includes:

- Liked movies (Like)
- Disliked movies (Dislike)
- Watched movies (Seen)
- User interaction history

These data are used to personalize the recommendation process, manage restrictions related to watched and disliked movies, and support the LLM's final movie selection.

## 4. Database and Conversation Management

The project's database is designed using MySQL.

The database structure includes the following main tables:

- **Movie:** Stores movie information and the data required by the recommendation system.
- **Users:** Stores user information.
- **Interactions:** Records user interactions with movies.
- **Conversations:** Stores conversation information.
- **Messages:** Stores user messages and system responses.

DBUtils and Connection Pooling are used to manage database connectivity. This structure provides controlled access to database connections and avoids creating unnecessary connections for every request.

### Conversation Manager

The Conversation Manager is responsible for managing the lifecycle of user conversations.

Its responsibilities include:

- Receiving user messages and storing them in the database.
- Managing conversation identifiers and context.
- Forwarding requests to the Agent.
- Receiving and storing final responses.
- Delivering responses to the Telegram layer.
- Periodically summarizing conversation history to manage conversational context more efficiently.

To prevent the conversation history sent to the model from becoming excessively long, conversation summarization is performed after every 10 user messages.

## 5. Technology Stack

The main technologies and libraries used in the project are:

| Component | Technology |
|---|---|
| Programming Language | Python 3.11 |
| Telegram Interface | python-telegram-bot |
| Agent Architecture | LangChain |
| Agent Workflow Management | LangGraph |
| Language Model | Qwen (through an OpenAI-compatible API) |
| Semantic Search | Sentence Transformers |
| Vector Search | FAISS |
| Collaborative Filtering | LightFM |
| Data Processing | NumPy |
| Database | MySQL |
| Database Connection Management | DBUtils |
| Environment Management | Miniconda (Conda) |
| Version Control | Git |

## 6. Request Execution Flow

The normal message-processing flow in AFilm Bot is illustrated below:

```text
User
  |
  v
Telegram Bot
  |
  v
Conversation Manager
  |
  v
LangGraph
  |
  v
LLM
  |
  v
Tool Calling Decision
  |
  +----------------------+
  |                      |
  v                      v
Direct Response      Tool Execution
  |                      |
  |                      v
  |                    Tools
  |                      |
  |                      v
  |                 Tool Results
  |                      |
  |                      v
  |                    LangGraph
  |                      |
  |                      v
  |                    LLM
  |                      |
  +----------+-----------+
             |
             v
       Final Response
             |
             v
    Conversation Manager
             |
             v
       Telegram Bot
             |
             v
           User
```

In this workflow, the decision to invoke tools is made by the language model. Therefore, not every request necessarily results in tool execution. If the available information is sufficient, the model can generate a response directly.

## 7. User Login Process

The user login process is managed within the Telegram Interface layer and is not part of the LangGraph execution flow.

In this component, the user's status is checked, and the login or continuation of interaction with the bot is handled according to their status.

This separation keeps authentication responsibilities independent from conversation management and Agent execution.

## 8. Development Status

AFilm Bot has reached the initial usable release stage in version 0.1.

In this version, the main system components, including the Telegram interface, Agent architecture, specialized tools, hybrid recommendation engine, database, and conversation management, have been implemented and integrated.

The modular project structure also provides a foundation for adding new features, improving recommendation algorithms, and expanding system capabilities in future versions.

