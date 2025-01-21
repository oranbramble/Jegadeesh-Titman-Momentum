
# Jegadeesh-Titman Momentum Strategy

This project implements and evaluates the **[Jegadeesh-Titman Momentum Strategy](https://www.bauer.uh.edu/rsusmel/phd/jegadeesh-titman93.pdf)**, a widely studied financial trading strategy that aims to capitalize on market trends. The project uses Python to analyze historical stock data and simulate portfolio returns based on momentum signals.

## Features

- **Momentum Signal Generation**: Identifies assets with strong recent performance.
- **Portfolio Construction**: Constructs a diversified portfolio based on momentum rankings.
- **Performance Evaluation**: Analyzes returns and compares them to benchmarks.
- **Data Handling**: Efficiently processes financial datasets.

## Project Structure

```
Jegadeesh-Titman-Momentum-Git/
├── data/               # Historical stock data files
├── src/                # Source code for momentum strategy
├── tests/              # Unit tests for the project
├── venv/               # Python virtual environment
├── .gitignore          # Git ignored files
├── LICENSE             # Project license
├── NOTES               # Project notes and insights
└── README.md           # Project documentation
```

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/Jegadeesh-Titman-Momentum.git
   cd Jegadeesh-Titman-Momentum
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Prepare Data**: Ensure your data is in the `data/` folder.
2. **Run Analysis**:
   ```bash
   python src/main.py
   ```
3. **View Results**: Analyze performance metrics in the output.

## Roadmap

- [ ] Improve data preprocessing.
- [ ] Add visualization for portfolio performance.
- [ ] Optimize signal generation.
- [ ] Extend to other financial markets.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for improvements.

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
