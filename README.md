# Tool Window Usage Analysis
## A data analysis project for JetBrains Internship task, focusing on analyzing tool window usage patterns in IDEs based on event log data.

### Instalation and Setup
#### Prerequisites
- Python 3.8+
- pip package manager
  
#### Installation Steps
1. Clone the repository

```
git clone https://github.com/Drake3001/JetBrains-Internship-task.git
```

2. Install dependencies
```
pip install -r requirements.txt
```

### Usage 
1. Base analysis- generates most of the files used in the report 
```
python main.py 
```
2. Additional analysis- generates time_window_analysis.txt
```
python time_window_selection.py
```
### Project structure
```
JetBrains-Internship-task/
│
├── .gitignore               # Git ignore file
├── ToolWindow_report.pdf    # Report of finding and analysis
├── main.py                  # Executes data transformation and outputs most of the visualizations and statistics used 
├── time_window_selection.py # Creates dataframes, for diffrent time_windows, and outputs into generated/csv/time_window_analysis.csv 
├── requirements.txt         # Python dependencies
├── toolwindow_data.csv      # Starting dataset
│
├── generated/               # Directory for generated outputs (CSV, stats, plots)
│   ├── csv/
│   ├── orinal_dataset/
│   └──processed_dataset/
│
└── README.md                # This file
```

### Dependencies
- contourpy==1.3.3
- cycler==0.12.1
- fonttools==4.60.1
- kiwisolver==1.4.9
- matplotlib==3.10.7
- numpy==2.3.4
- packaging==25.0
- pandas==2.3.3
- pillow==12.0.0
- pyparsing==3.2.5
- python-dateutil==2.9.0.post0
- pytz==2025.2
- scipy==1.16.3
- seaborn==0.13.2
- six==1.17.0
- tzdata==2025.2

