# ollama-query-web

This project fetches web pages from a web search and summarises the results using Ollama.

---

## Features

### Web Crawler

- Fetches and processes web pages using **Selenium** and **BeautifulSoup**.
- Extracts text content and relevant metadata (e.g., URLs).

### Embedding System

- Uses **ChromaDB** to store and manage embeddings.

### Integration with Language Model

- Generates answers to user queries by combining web data with a language model.
---

## Requirements

### Python Libraries

Install the following dependencies using `pip`:

```bash
pip install selenium beautifulsoup4 chromadb requests ollama
```

---

## Usage

### Running the Program

```bash
python query_web.py "Your search query"
```

---

## License

This project is licensed under the GNU General Public License (GPL). See the `LICENSE` file for details.

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.

---

## Contact

For questions or feedback, please create an issue in the GitHub repository.

