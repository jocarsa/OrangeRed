import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time
import re

def fetch_page(url):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        load_time = time.time() - start_time
        return response.text, load_time
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None, None

def analyze_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    seo_results = {}

    # Check meta tags
    seo_results['Title'] = soup.title.string if soup.title else "No Title Found"
    seo_results['Meta Description'] = (soup.find('meta', attrs={'name': 'description'}) or {}).get('content', 'Not Found')
    seo_results['Meta Keywords'] = (soup.find('meta', attrs={'name': 'keywords'}) or {}).get('content', 'Not Found')

    # Check header tags
    seo_results['Header Tags'] = {f"h{i}": len(soup.find_all(f"h{i}")) for i in range(1, 7)}

    # Check image alt attributes
    images = soup.find_all('img')
    alt_count = sum(1 for img in images if img.get('alt'))
    seo_results['Images with Alt Text'] = alt_count
    seo_results['Total Images'] = len(images)

    return seo_results

def analyze_css_and_js(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    css_js_results = {}

    # Check linked CSS and JS
    css_links = soup.find_all('link', attrs={'rel': 'stylesheet'})
    js_links = soup.find_all('script', attrs={'src': True})

    css_js_results['CSS Files'] = [urljoin(base_url, css.get('href')) for css in css_links if css.get('href')]
    css_js_results['JavaScript Files'] = [urljoin(base_url, js.get('src')) for js in js_links if js.get('src')]

    # Check inline CSS and JS
    inline_css = bool(soup.find('style'))
    inline_js = bool(soup.find('script', attrs={'type': 'text/javascript'}) and not js_links)

    css_js_results['Inline CSS'] = "Present" if inline_css else "Not Found"
    css_js_results['Inline JS'] = "Present" if inline_js else "Not Found"

    return css_js_results

def check_responsiveness(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
    return "Responsive (Viewport meta tag found)" if viewport_tag else "Not Responsive (No viewport meta tag)"

def check_mobile_friendly(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Look for mobile-friendly indications in CSS
    linked_css = [link.get('href') for link in soup.find_all('link', attrs={'rel': 'stylesheet'})]
    if linked_css:
        mobile_friendly_indicators = any("mobile" in href.lower() for href in linked_css)
        if mobile_friendly_indicators:
            return "Mobile-Friendly (Detected mobile-specific CSS)"
    return "Not Mobile-Friendly"

def seo_analysis(url):
    print(f"Performing SEO analysis for {url}...")
    html_content, load_time = fetch_page(url)
    if not html_content:
        return

    # Analyze HTML structure
    html_results = analyze_html(html_content)

    # Analyze CSS and JavaScript usage
    css_js_results = analyze_css_and_js(html_content, url)

    # Check responsiveness
    responsiveness = check_responsiveness(html_content)

    # Check mobile-friendliness
    mobile_friendly = check_mobile_friendly(html_content)

    # Combine results
    full_results = {
        **html_results,
        **css_js_results,
        "Page Load Time (seconds)": f"{load_time:.2f}" if load_time else "Could not measure",
        "Responsiveness": responsiveness,
        "Mobile-Friendliness": mobile_friendly,
    }

    # Print results
    for key, value in full_results.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    target_url = input("Enter the website URL to analyze: ")
    if not target_url.startswith(('http://', 'https://')):
        target_url = f"http://{target_url}"
    seo_analysis(target_url)
