# KCSF Shipping Report Dashboard

A clean, focused Streamlit application for analyzing shipping data from NetSuite.

## Overview

This application provides a single-page dashboard that displays shipping data from NetSuite with interactive filters and visualizations. It fetches data from NetSuite RESTlets and presents it in an easy-to-use interface for shipping operations management.

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure secrets**:
   Create `.streamlit/secrets.toml` with your NetSuite credentials:
   ```toml
   consumer_key = "your_consumer_key"
   consumer_secret = "your_consumer_secret"
   token_key = "your_token_key"
   token_secret = "your_token_secret"
   realm = "your_netsuite_realm"
   url_restlet = "your_restlet_url"
   ```

3. **Run the application**:
   ```bash
   streamlit run streamlit_app.py
   ```

## Application Structure

```
kcsf_streamlit/
├── streamlit_app.py              # Main application entry point
├── pages/
│   └── Shipping_Report.py        # Shipping dashboard page
├── utils/
│   └── restlet.py                # NetSuite data fetching utility
├── requirements.txt              # Python dependencies
└── README.md                     # This documentation
```

## Features

### Data Sources
- **Open Orders** (customsearch5190): Sales orders with ship dates
- **Pick Tasks** (customsearch5457): Task assignments for fulfillment
- **Our Truck Orders** (customsearch5147): Company truck delivery orders

### Interactive Filters
- **Sales Representative**: Filter by specific reps or view all
- **Shipping Method**: Group by type (Small Package, LTL, Truckload, Our Truck, Pick Ups)
- **Ship Date**: Filter by time periods or custom date ranges
- **Task Status**: Filter by tasked or untasked orders

### Visualizations
- **Metrics Dashboard**: Key performance indicators
- **Line Chart**: Orders over time by ship date
- **Pie Chart**: Tasked vs untasked order distribution
- **Weekly Calendar**: Visual calendar view of scheduled shipments
- **Data Tables**: Interactive tables with filtered results

## Dependencies

```txt
streamlit
requests
pandas
plotly
requests-oauthlib
```

## Data Flow

1. **Authentication**: OAuth1 authentication with NetSuite
2. **Data Fetching**: RESTlet calls to retrieve saved search data
3. **Data Processing**: Pandas operations for merging and filtering
4. **User Interface**: Streamlit components for interaction
5. **Visualization**: Plotly charts for data presentation

## Performance Features

- **Caching**: Data is cached for 2 minutes to reduce API calls
- **Error Handling**: Graceful handling of network and data issues
- **Responsive UI**: Optimized for smooth user interaction

## Security

- NetSuite credentials stored in Streamlit secrets
- OAuth1 authentication for secure API access
- No sensitive data logged or displayed

## Troubleshooting

- **Authentication Errors**: Check NetSuite credentials in secrets
- **No Data**: Verify RESTlet URLs are accessible
- **Performance Issues**: Monitor application logs for errors

---

**Note**: This application has been cleaned to include only the Shipping Report functionality for streamlined deployment and maintenance.
