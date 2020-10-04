## Usage
1. `git clone https://github.com/nus-se-instructors/pdf-annotation.git`
2. `cd pdf-annotation && virtualenv .env`
3. `source ./.env/bin/activate` (on Windows, use `".env/Scripts/activate.bat"` -- note the double quotes)
4. `pip install -r requirements.txt`
5. Download chromedriver from https://chromedriver.chromium.org/downloads and place the binary in the `enhance_textbook` directory (if a new copy of the textbook has to be downloaded)
6. Go to `enhance_textbook` directory and run the `main.py`. 
   No input required. Will create a copy of the textbook with table of contents etc and output it into the outputs directory

### Fine-tuning Index Generation
The terms listed in the index are extracted from HTML headings in the textbook website. There are optionally two files, `include.csv` and `exclude.csv` in `enhance_textbook/inputs` that allow you to specify what index terms to include or exclude if need be.
1. Open up the respective csv file (`include.csv` or `exclude.csv`) in a text editor
2. Enter any index terms that you wish to be included or excluded (preferably one term per line for readability)
3. Run the program as usual
   
