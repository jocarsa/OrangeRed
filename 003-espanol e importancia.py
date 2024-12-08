import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time

def fetch_page(url):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        load_time = time.time() - start_time
        return response.text, load_time
    except requests.RequestException as e:
        print(f"Error al acceder a {url}: {e}")
        return None, None

def analyze_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    seo_results = {}

    # Títulos y meta etiquetas
    seo_results['Título'] = soup.title.string if soup.title else "No encontrado"
    seo_results['Meta Descripción'] = (soup.find('meta', attrs={'name': 'description'}) or {}).get('content', 'No encontrada')
    seo_results['Meta Keywords'] = (soup.find('meta', attrs={'name': 'keywords'}) or {}).get('content', 'No encontradas')

    # Etiquetas de encabezado
    seo_results['Encabezados'] = {f"h{i}": len(soup.find_all(f"h{i}")) for i in range(1, 7)}

    # Atributos ALT en imágenes
    images = soup.find_all('img')
    alt_count = sum(1 for img in images if img.get('alt'))
    seo_results['Imágenes con ALT'] = alt_count
    seo_results['Total Imágenes'] = len(images)

    # Enlaces internos y externos
    internal_links = []
    external_links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if urlparse(href).netloc:
            external_links.append(href)
        else:
            internal_links.append(href)
    seo_results['Enlaces Internos'] = len(internal_links)
    seo_results['Enlaces Externos'] = len(external_links)

    # Etiquetas fuertes
    seo_results['Uso de <strong>'] = len(soup.find_all('strong'))

    # Etiqueta canonical
    canonical_tag = soup.find('link', attrs={'rel': 'canonical'})
    seo_results['Etiqueta Canonical'] = canonical_tag['href'] if canonical_tag else "No encontrada"

    return seo_results

def analyze_css_and_js(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    css_js_results = {}

    # Archivos CSS y JS enlazados
    css_links = soup.find_all('link', attrs={'rel': 'stylesheet'})
    js_links = soup.find_all('script', attrs={'src': True})

    css_js_results['Archivos CSS'] = [urljoin(base_url, css.get('href')) for css in css_links if css.get('href')]
    css_js_results['Archivos JS'] = [urljoin(base_url, js.get('src')) for js in js_links if js.get('src')]

    # CSS y JS en línea
    css_js_results['CSS en Línea'] = "Presente" if soup.find('style') else "No encontrado"
    css_js_results['JS en Línea'] = "Presente" if soup.find('script', attrs={'type': 'text/javascript'}) else "No encontrado"

    return css_js_results

def check_responsiveness(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
    return "Responsive (etiqueta viewport encontrada)" if viewport_tag else "No responsive (sin etiqueta viewport)"

def render_report(results):
    print("\n" + "=" * 60)
    print("                  Informe de Análisis SEO")
    print("=" * 60 + "\n")

    # Información general
    print(f"Título del Sitio: {results.get('Título')}")
    print(f"Meta Descripción: {results.get('Meta Descripción')}")
    print(f"Meta Keywords: {results.get('Meta Keywords')}\n")

    # Encabezados
    print("Encabezados (Importancia: Alta):")
    for tag, count in results.get('Encabezados', {}).items():
        print(f"  - {tag.upper()}: {count}")
    print()

    # Imágenes
    print("Imágenes (Importancia: Media):")
    print(f"  - Total Imágenes: {results.get('Total Imágenes')}")
    print(f"  - Imágenes con Atributo ALT: {results.get('Imágenes con ALT')}\n")

    # Enlaces
    print("Enlaces (Importancia: Media):")
    print(f"  - Enlaces Internos: {results.get('Enlaces Internos')}")
    print(f"  - Enlaces Externos: {results.get('Enlaces Externos')}\n")

    # CSS y JavaScript
    print("CSS y JavaScript (Importancia: Media):")
    print(f"  - Archivos CSS Enlazados: {', '.join(results.get('Archivos CSS', [])) or 'Ninguno'}")
    print(f"  - Archivos JS Enlazados: {', '.join(results.get('Archivos JS', [])) or 'Ninguno'}")
    print(f"  - CSS en Línea: {results.get('CSS en Línea')}")
    print(f"  - JS en Línea: {results.get('JS en Línea')}\n")

    # Etiquetas y optimización
    print("Optimización (Importancia: Alta):")
    print(f"  - Página Responsive: {results.get('Responsive')}")
    print(f"  - Uso de <strong>: {results.get('Uso de <strong>')}")
    print(f"  - Etiqueta Canonical: {results.get('Etiqueta Canonical')}\n")

    print("=" * 60 + "\n")

def seo_analysis(url):
    print(f"Analizando el sitio web: {url}...\n")
    html_content, load_time = fetch_page(url)
    if not html_content:
        return

    # Análisis HTML
    html_results = analyze_html(html_content)

    # Análisis de CSS y JS
    css_js_results = analyze_css_and_js(html_content, url)

    # Verificar responsividad
    responsive = check_responsiveness(html_content)

    # Resultados combinados
    full_results = {
        **html_results,
        **css_js_results,
        "Tiempo de Carga (segundos)": f"{load_time:.2f}" if load_time else "No medido",
        "Responsive": responsive,
    }

    # Renderizar informe
    render_report(full_results)

if __name__ == "__main__":
    target_url = input("Introduce la URL del sitio web a analizar: ")
    if not target_url.startswith(('http://', 'https://')):
        target_url = f"http://{target_url}"
    seo_analysis(target_url)
