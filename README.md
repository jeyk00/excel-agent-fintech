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
*   **Web Application (v2.0)**:
    *   **Streamlit Interface**: User-friendly drag-and-drop UI for uploading PDFs.
    *   **Interactive Charts**: Visualize revenue forecasts and historical trends directly in the browser.
    *   **State Persistence**: Analysis results are saved across sessions.
*   **AI Forecasting (v2.0)**:
    *   **Revenue Prediction**: Uses Linear Regression (`scikit-learn`) to forecast revenue for the next 5 years.
    *   **DCF Ready**: Includes placeholders for WACC and Terminal Growth Rate assumptions.
*   **"Glass Box" DCF Valuation**:
    *   **Transparent Models**: Generates a fully functional Discounted Cash Flow (DCF) model in Excel using native formulas (not hardcoded values).
    *   **Interactive Assumptions**: Users can modify WACC, Terminal Growth, and Margins directly in Excel to see real-time valuation updates.
    *   **Valuation Bridge**: Automatically calculates **Enterprise Value**, **Equity Value**, and **Implied Share Price** (PLN).
*   **Expanded Format Support**:
    *   **XHTML Support**: Now supports parsing of `.xhtml` financial reports (e.g., ESEF filings) using `BeautifulSoup`.
*   **Investor-Grade Dashboard**:
    *   **Native Excel Charts**: Includes a dedicated Revenue Forecast chart (Historical + 5Y Projection).
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

### Web App (Recommended)

Start the Streamlit interface:

```bash
uv run streamlit run src/app.py
```

### CLI Mode

Run the agent on a PDF financial report via command line:

```bash
uv run python main.py "path/to/report.pdf"
```

### CLI Options

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
