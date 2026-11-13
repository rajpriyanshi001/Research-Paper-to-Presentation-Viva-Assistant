# PaperMate AI – Research Paper to Presentation & Viva Assistant

An Agentic AI-powered academic assistant that transforms research papers into structured summaries, presentation slides, concept explanations, and viva questions with model answers.

## 1. Project Overview

PaperMate AI is an intelligent academic assistant designed to help students and faculty understand research papers and prepare for academic presentations and viva examinations.

The application uses Large Language Models (LLMs), LangChain, Agentic RAG, and ChromaDB to retrieve relevant information from uploaded research papers and generate context-aware responses.

## 2. Problem Statement

Preparing presentations, understanding complex research concepts, and anticipating viva questions from research papers is time-consuming for students and faculty.

PaperMate AI simplifies this process by automating research-paper summarization, concept extraction, presentation generation, and viva preparation.

## 3. Objectives

- Generate structured summaries of research papers.
- Extract important concepts, contributions, methods, and results.
- Generate presentation-ready slides.
- Explain technical concepts in simple language.
- Generate likely viva questions with model answers.
- Provide context-aware responses using Agentic RAG.

## 4. Features

### Summarizer Agent
Generates concise, structured summaries of uploaded research papers.

### Concept Extractor Agent
Identifies key contributions, methodologies, technologies, and research findings.

### Slide Generator Agent
Converts research-paper content into presentation-ready slides.

### Viva Agent
Generates potential examiner questions with suggested model answers.

### Intelligent Intent Router
Identifies user requests and directs them to the appropriate agent.

### Agentic RAG
Retrieves relevant sections from the uploaded research paper to provide grounded responses.

## 5. Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Programming Language | Python |
| LLM | Google Gemini API |
| AI Framework | LangChain |
| Prompt Engineering | LangChain PromptTemplate |
| Chain Processing | LangChain Expression Language (LCEL) |
| PDF Processing | PyPDF |
| Vector Database | ChromaDB |
| Embeddings | Google Generative AI Embeddings |

## 6. System Architecture

User → Streamlit GUI → Intent Detection & Routing → Selected Agent → Agentic RAG → ChromaDB Retrieval → Gemini LLM → Generated Response.

The application uses four logical agents:

1. Summarizer Agent
2. Concept Extractor Agent
3. Slide Generator Agent
4. Viva Agent

A central intent router determines which agent should handle each request.

## 7. Agentic RAG Workflow

1. User uploads a research paper in PDF format.
2. Text is extracted from the PDF.
3. The extracted text is divided into smaller chunks.
4. Embeddings are generated for the document chunks.
5. Embeddings are stored in ChromaDB.
6. The intent router identifies the user's request.
7. The application retrieves relevant document chunks when required.
8. Retrieved context is passed to the selected LangChain prompt chain.
9. Gemini generates a context-aware response.
10. The generated result is displayed in the Streamlit interface.

## 8. Prompt Engineering

The application uses a system prompt to define the role of the academic assistant and separate prompts for each agent.

Prompt engineering techniques include:

- Role-based prompting.
- Zero-shot prompting.
- Task-specific prompt templates.
- Context-grounded prompting.
- Response verification.

LangChain LCEL connects prompts, the Gemini model, and output parsers into processing chains.

## 9. Installation and Execution

### Prerequisites
- Python 3.10 or later (depending on package compatibility).
- Google Gemini API key.
- Internet connection for API access.

### Step 1: Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd PaperMate-AI
```

### Step 2: Create a virtual environment

```bash
python -m venv .venv
```

### Step 3: Activate the environment

Windows:

```powershell
.venv\Scripts\activate
```

### Step 4: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure API key

Create a `.env` file:

```env
GOOGLE_API_KEY=your_api_key
```

### Step 6: Run the application

```bash
streamlit run app.py
```

## 10. Mandatory Acceptance Criteria

| No. | Criterion | Implementation |
|---|---|---|
| 1 | LLM Integration | Google Gemini API |
| 2 | Interactive GUI | Streamlit |
| 3 | Prompt Engineering | System and agent-specific prompts |
| 4 | LangChain Core Components | PromptTemplate and LCEL |
| 5 | Agentic RAG | Context retrieval and generation |
| 6 | Intent Detection and Routing | Intelligent request router |
| 7 | Vector Database | ChromaDB |

## 11. Project Structure

```text
PaperMate-AI/
│
├── app.py
├── agents.py
├── rag_pipeline.py
├── prompts.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── uploads/
├── chroma_db/
└── assets/
```

## 12. Expected Output

The application provides:

- Structured research paper summaries.
- Extracted research concepts and contributions.
- Presentation-ready slides.
- Beginner-friendly concept explanations.
- Viva questions with suggested answers.

## 13. Future Enhancements

- Support for multiple research papers.
- More advanced viva simulation.
- Export summaries as PDF and DOCX.
- Presentation theme customization.
- Multi-language explanations.

## 14. Conclusion

PaperMate AI demonstrates how Agentic AI, Large Language Models, LangChain, and Retrieval-Augmented Generation can be combined to simplify academic research and presentation preparation.

The system helps students understand research papers, prepare presentations, and improve their confidence during viva examinations.
