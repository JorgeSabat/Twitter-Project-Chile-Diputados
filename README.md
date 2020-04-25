# Documentation
### Setup Instructions
1. Create Virtual Environment
```
python3 -m venv venv
```

2. Activate virtual environment
```
source venv/bin/activate
```

3. Install required python packages
```
pip install -r requirements.txt
```

### How to run the ID Generator
1. If needed, update `id_ranges` in the code
2. If needed, update `PARTITION_SIZE` in the code
3. Run the ID Generator
```
python id_generator.py
```

### How to run the scraper

1. Activate virtual environment
```
source venv/bin/activate
```
2. Add ids to _input.txt_
3. Run the scraper
```
python scraper.py input.txt output.csv
```
