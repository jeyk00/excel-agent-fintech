# Excel Financial Agent 📊

**Automated Financial Spreading: From PDF to Investor-Grade Excel Dashboard.**

This agent automates the tedious process of "financial spreading" — converting unstructured PDF financial reports into structured, analytical Excel models. It uses advanced LLMs (Gemini 2.0 Flash / DeepSeek) and a robust Python pipeline to extract, validate, and visualize financial data.

## 🚀 Key Features

*   **Smart PDF Filter**: Intelligent pre-processing scans PDF pages for financial keywords, reducing API costs and noise by **~50%**.
*   **Robust Extraction**:
    *   Uses **Gemini 2.0 Flash** (via OpenAI compatibility) for high-speed, low-cost extraction.
    *   **Auto-Retry Mechanism**: Built-in exponential backoff (using `tenacity`) handles API rate limits (429 errors) gracefully.
    *   **Strict Validation**: Pydantic models enforce accounting equations (`Assets = Liabilities + Equity`) and data integrity.
*   **Financial Intelligence**:
    *   Automatically calculates **EBITDA**, **EBITDA Margin**, **Net Margin**, **ROE**, and **YoY Growth**.
    *   Handles reporting units (thousands/millions) and currencies.
*   **Investor-Grade Dashboard**:
    *   Generates a professional Excel report (`.xlsx`) using `XlsxWriter`.
    *   **Sparklines**: Visual trend lines for every metric.
    *   **Smart Formatting**: Auto-formats percentages, currencies, and negative values (red).
    *   **Robust Saving**: Auto-saves to a timestamped file if the target Excel file is open/locked.

## 🛠️ Requirements

*   **Python**: >= 3.13
*   **Package Manager**: `uv` (recommended) or `pip`
*   **API Keys**:
    *   `LLAMA_CLOUD_API_KEY` (for LlamaParse PDF parsing)
    *   `GEMINI_API_KEY` (or `OPENAI_API_KEY`) for data extraction

## 📦 Installation

This project uses `uv` for fast dependency management.

1.  **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd excel-financial-agent
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```

3.  **Configure Environment**:
    Create a `.env` file in the root directory:
    ```env
    LLAMA_CLOUD_API_KEY=llx-your-key-here
    GEMINI_API_KEY=your-gemini-key-here
    # Optional: OPENAI_API_KEY=sk-... (if using OpenAI models)
    ```

## 🏃 Usage

Run the agent on a PDF financial report:

```bash
uv run python main.py "path/to/report.pdf"
```

### Options

*   `--model`: Specify the LLM model (default: `gemini-2.0-flash`).
    ```bash
    uv run python main.py "report.pdf" --model gemini-2.0-flash
    ```
*   `--no-filter`: Disable the Smart PDF Filter (process the entire PDF).
    ```bash
    uv run python main.py "report.pdf" --no-filter
    ```

## 📂 Project Structure

*   `src/`: Source code
    *   `models.py`: Pydantic data models & validation.
    *   `filter.py`: Smart PDF filtering logic.
    *   `parser.py`: LlamaParse integration.
    *   `extractor.py`: LLM extraction with retries.
    *   `analyzer.py`: KPI calculation (EBITDA, etc.).
    *   `reporter.py`: Excel dashboard generation.
*   `data/`: Data directories (raw, temp, processed).
*   `tests/`: Unit tests.

## 🛡️ License

[MIT](LICENSE)
