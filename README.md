# Facebook Marketplace Car Scraper

A Python-based web scraper that automates the process of collecting car listings from Facebook Marketplace and enriches them with VIN (Vehicle Identification Number) data from AutoTempest. The scraper exports the collected data to an Excel spreadsheet for easy analysis.

## Features

- **Automated Facebook Marketplace Scraping**: Scrapes car listings from Facebook Marketplace with customizable search parameters
- **Data Parsing**: Automatically extracts key vehicle information including:
  - Price
  - Year
  - Make (Brand)
  - Model
  - Location
  - Mileage
  - Listing URL
- **VIN Enrichment**: Cross-references listings with AutoTempest to find and append Vehicle Identification Numbers
- **Excel Export**: Outputs all collected data to a formatted Excel spreadsheet
- **Headless Operation**: Runs Chrome in headless mode for faster, background execution
- **Logging**: Comprehensive logging system for tracking scraper progress and debugging

## Requirements

### Dependencies

- Python 3.x
- Selenium WebDriver
- ChromeDriver
- pandas
- numpy
- openpyxl (for Excel writing)

### Python Packages

```
selenium
pandas
numpy
openpyxl
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/daviddeng0smm/fb_marketplace_car_scraper.git
   cd fb_marketplace_car_scraper
   ```

2. **Install required Python packages:**
   ```bash
   pip install selenium pandas numpy openpyxl
   ```

3. **Download ChromeDriver:**
   - Download ChromeDriver from https://chromedriver.chromium.org/
   - Make sure the ChromeDriver version matches your Chrome browser version
   - Note the path where you save ChromeDriver

4. **Update the ChromeDriver path:**
   - Open `marketplace_scraper.py`
   - Locate the `init_driver()` function (around line 24)
   - Update the `executable_path` to point to your ChromeDriver location:
     ```python
     service = ChromeService(executable_path="YOUR_PATH_TO_CHROMEDRIVER")
     ```

## Usage

### Basic Usage

Run the scraper with default settings:

```bash
python marketplace_scraper.py
```

This will:
1. Scrape car listings from the default Facebook Marketplace URL (Los Angeles area)
2. Cross-reference with AutoTempest to find VINs
3. Export results to `processed_titles.xlsx`

### Customizing Search Parameters

You can modify the search URL in the `facebookScraper()` function to customize your search:

```python
url = "https://www.facebook.com/marketplace/la/vehicles?minPrice=3000&maxMileage=70000&minYear=2016&topLevelVehicleType=car_truck&exact=false"
```

Available parameters:
- `minPrice`: Minimum price filter
- `maxPrice`: Maximum price filter
- `maxMileage`: Maximum mileage filter
- `minYear`: Minimum year filter
- `maxYear`: Maximum year filter
- `topLevelVehicleType`: Vehicle type (e.g., `car_truck`)

### Customizing Output Filename

You can specify a custom output filename:

```python
excelWriter(updated_parsed_title, filename='my_custom_output.xlsx')
```

## Configuration

### AutoTempest Settings

The scraper uses AutoTempest to find VINs. Default settings in `gettingAutoTempest()`:
- **ZIP Code**: 94579 (default search radius center)
- **Radius**: 500 miles
- **Mileage Range**: ±5,000 miles from listing mileage
- **Title Status**: Clean titles only

You can modify these parameters in the URL construction around line 196:

```python
url = (
    f"https://www.autotempest.com/results?"
    f"make={make.lower()}&model={model.lower()}&zip=YOUR_ZIP&radius=YOUR_RADIUS"
    f"&minyear={year}&maxyear={year}&minmiles={int(mileage - 5000)}&maxmiles={int(mileage)}"
    f"&title=clean"
)
```

### Logging

The scraper includes comprehensive logging. Logs display:
- Timestamp
- Log level (INFO, ERROR)
- Message

Logging is configured at line 21 and can be adjusted:

```python
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
```

## Output Format

The scraper generates an Excel file (`processed_titles.xlsx` by default) with the following columns:

| Column   | Description                                    |
|----------|------------------------------------------------|
| Price    | Listing price                                  |
| Year     | Vehicle year                                   |
| Make     | Vehicle manufacturer/brand                     |
| Model    | Vehicle model                                  |
| Location | Geographic location of the listing             |
| Mileage  | Vehicle mileage (in miles)                     |
| Link     | Direct URL to the Facebook Marketplace listing |
| VIN      | Vehicle Identification Number (if found)       |

## How It Works

1. **Facebook Marketplace Scraping** (`facebookScraper()`):
   - Initializes Chrome WebDriver in headless mode
   - Navigates to Facebook Marketplace with specified search parameters
   - Scrolls through the page to load all listings
   - Extracts listing data from page containers
   - Parses vehicle information from listing text

2. **Title Parsing** (`titleParser()`):
   - Processes raw listing text
   - Extracts structured data (price, year, make, model, location, mileage)
   - Filters and validates listings

3. **VIN Enrichment** (`gettingAutoTempest()`):
   - Searches AutoTempest for each vehicle
   - Attempts to extract VIN from matching listings
   - Appends VIN to vehicle data
   - Removes listings without VINs

4. **Data Export** (`excelWriter()`):
   - Converts parsed data to pandas DataFrame
   - Exports to Excel with proper column headers

## Notes and Limitations

- **ChromeDriver Path**: You must update the ChromeDriver path to match your system
- **Facebook Login**: This scraper does not handle Facebook login. Ensure you can access Facebook Marketplace without authentication, or modify the code to handle login
- **Rate Limiting**: Be mindful of making too many requests in a short time period. Consider adding delays if needed
- **Listing Format Changes**: If Facebook or AutoTempest change their page layouts, the CSS selectors may need to be updated
- **VIN Availability**: Not all listings on AutoTempest include VINs. Listings without VINs are removed from the final output
- **Headless Mode**: The scraper runs in headless mode by default. Set `options.headless = False` in `init_driver()` to see the browser in action

## Troubleshooting

### Common Issues

1. **ChromeDriver Version Mismatch**:
   - Error: "This version of ChromeDriver only supports Chrome version X"
   - Solution: Download the ChromeDriver version that matches your Chrome browser

2. **Element Not Found Errors**:
   - Facebook or AutoTempest may have updated their page structure
   - Check and update CSS selectors in the code

3. **No Data Scraped**:
   - Verify your Facebook Marketplace URL is correct
   - Check if Facebook requires login for your region
   - Review logs for specific error messages

4. **Excel File Not Created**:
   - Ensure you have write permissions in the directory
   - Verify `openpyxl` is installed: `pip install openpyxl`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is provided as-is for educational purposes. Be sure to comply with Facebook's Terms of Service and robots.txt when scraping their website.

## Disclaimer

This tool is for educational purposes only. Web scraping may violate the Terms of Service of websites. Use responsibly and at your own risk. Always respect rate limits and consider using official APIs when available.
