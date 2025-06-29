#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test rápido de métodos de autenticación Hikvision
Para determinar cuál método funciona realmente con requests
"""

import requests
import urllib.parse
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
import urllib3

# Suprimir warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_url_embedded():
    """Probar credenciales embebidas en URL"""
    print("="*50)
    print("TEST 1: CREDENCIALES EMBEBIDAS EN URL")
    print("="*50)
    
    ip = "192.168.0.222"
    username = "admin"
    password = "Oem2017*"
    
    # Método 1: URL directa (como en navegador)
    url_direct = f"http://{username}:{password}@{ip}/ISAPI/System/deviceInfo"
    print(f"URL directa: {url_direct}")
    
    try:
        response = requests.get(url_direct, timeout=10, verify=False)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ MÉTODO URL DIRECTA - FUNCIONA")
            return True, "url_direct"
        else:
            print(f"❌ URL directa falló: {response.status_code}")
            print(f"Respuesta: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error URL directa: {e}")
    
    # Método 2: URL con encoding (excepto asterisco)
    username_encoded = urllib.parse.quote(username, safe='')
    password_encoded = urllib.parse.quote(password, safe='*')
    url_encoded = f"http://{username_encoded}:{password_encoded}@{ip}/ISAPI/System/deviceInfo"
    print(f"\nURL encoded: {url_encoded}")
    
    try:
        response = requests.get(url_encoded, timeout=10, verify=False)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ MÉTODO URL ENCODED - FUNCIONA")
            return True, "url_encoded"
        else:
            print(f"❌ URL encoded falló: {response.status_code}")
    except Exception as e:
        print(f"❌ Error URL encoded: {e}")
    
    return False, None

def test_digest_auth():
    """Probar autenticación Digest HTTP"""
    print("\n" + "="*50)
    print("TEST 2: DIGEST HTTP AUTHENTICATION")
    print("="*50)
    
    ip = "192.168.0.222"
    username = "admin"
    password = "Oem2017*"
    
    session = requests.Session()
    session.auth = HTTPDigestAuth(username, password)
    session.headers.update({
        'User-Agent': 'Hikvision Client',
        'Accept': 'application/xml, application/json'
    })
    session.verify = False
    
    url = f"http://{ip}/ISAPI/System/deviceInfo"
    print(f"URL: {url}")
    print(f"Auth: Digest HTTP")
    
    try:
        response = session.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ MÉTODO DIGEST HTTP - FUNCIONA")
            return True, session
        else:
            print(f"❌ Digest HTTP falló: {response.status_code}")
    except Exception as e:
        print(f"❌ Error Digest HTTP: {e}")
    
    return False, None

def test_basic_auth():
    """Probar autenticación Basic HTTP"""
    print("\n" + "="*50)
    print("TEST 3: BASIC HTTP AUTHENTICATION")
    print("="*50)
    
    ip = "192.168.0.222"
    username = "admin"
    password = "Oem2017*"
    
    session = requests.Session()
    session.auth = HTTPBasicAuth(username, password)
    session.headers.update({
        'User-Agent': 'Hikvision Client',
        'Accept': 'application/xml, application/json'
    })
    session.verify = False
    
    url = f"http://{ip}/ISAPI/System/deviceInfo"
    print(f"URL: {url}")
    print(f"Auth: Basic HTTP")
    
    try:
        response = session.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ MÉTODO BASIC HTTP - FUNCIONA")
            return True, session
        else:
            print(f"❌ Basic HTTP falló: {response.status_code}")
    except Exception as e:
        print(f"❌ Error Basic HTTP: {e}")
    
    return False, None

def test_headers_variations():
    """Probar variaciones de headers con URL embebida"""
    print("\n" + "="*50)
    print("TEST 4: URL EMBEBIDA CON DIFERENTES HEADERS")
    print("="*50)
    
    ip = "192.168.0.222"
    username = "admin"
    password = "Oem2017*"
    
    url = f"http://{username}:{password}@{ip}/ISAPI/System/deviceInfo"
    
    headers_variations = [
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        {"User-Agent": "Hikvision Client", "Accept": "application/xml"},
        {"User-Agent": "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1)", "Accept": "*/*"},
        {}  # Sin headers especiales
    ]
    
    for i, headers in enumerate(headers_variations, 1):
        print(f"\nVariación {i}: {headers}")
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ VARIACIÓN {i} - FUNCIONA")
                return True, headers
            else:
                print(f"❌ Variación {i} falló: {response.status_code}")
        except Exception as e:
            print(f"❌ Error variación {i}: {e}")
    
    return False, None

def extract_device_info(response_text):
    """Extraer información del dispositivo de la respuesta XML"""
    info = {}
    
    fields = ['model', 'serialNumber', 'firmwareVersion', 'deviceName']
    for field in fields:
        start_tag = f"<{field}>"
        end_tag = f"</{field}>"
        if start_tag in response_text and end_tag in response_text:
            value = response_text.split(start_tag)[1].split(end_tag)[0]
            info[field] = value
    
    return info

def main():
    """Función principal"""
    print("🔍 DIAGNÓSTICO DE AUTENTICACIÓN HIKVISION DS-K1T344MBFWX-E1")
    print("Probando todos los métodos para encontrar el que funciona con requests")
    
    working_methods = []
    
    # Test 1: URL embebida
    success, method = test_url_embedded()
    if success:
        working_methods.append(("URL Embebida", method))
    
    # Test 2: Digest Auth
    success, session = test_digest_auth()
    if success:
        working_methods.append(("Digest HTTP", session))
    
    # Test 3: Basic Auth
    success, session = test_basic_auth()
    if success:
        working_methods.append(("Basic HTTP", session))
    
    # Test 4: Headers variations
    success, headers = test_headers_variations()
    if success:
        working_methods.append(("URL con Headers", headers))
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE MÉTODOS QUE FUNCIONAN")
    print("="*60)
    
    if working_methods:
        for i, (method_name, method_data) in enumerate(working_methods, 1):
            print(f"{i}. ✅ {method_name}")
            
            # Obtener información del dispositivo para confirmar
            if method_name == "Digest HTTP" and hasattr(method_data, 'get'):
                try:
                    response = method_data.get("http://192.168.0.222/ISAPI/System/deviceInfo", timeout=10)
                    if response.status_code == 200:
                        device_info = extract_device_info(response.text)
                        for key, value in device_info.items():
                            print(f"   {key}: {value}")
                except:
                    pass
        
        # Recomendación
        print(f"\n🎯 RECOMENDACIÓN:")
        best_method = working_methods[0][0]
        print(f"Usar: {best_method}")
        
        if "Digest" in best_method:
            print(f"\n📝 CÓDIGO RECOMENDADO:")
            print("""
import requests
from requests.auth import HTTPDigestAuth

session = requests.Session()
session.auth = HTTPDigestAuth('admin', 'Oem2017*')
session.headers.update({
    'User-Agent': 'Hikvision Client',
    'Accept': 'application/xml'
})
session.verify = False

response = session.get('http://192.168.0.222/ISAPI/System/deviceInfo')
print(response.text)
""")
    else:
        print("❌ NINGÚN MÉTODO FUNCIONÓ")
        print("\n🔧 VERIFICACIONES NECESARIAS:")
        print("1. Confirmar que esta URL funciona en navegador:")
        print("   http://admin:Oem2017*@192.168.0.222/ISAPI/System/deviceInfo")
        print("2. Verificar configuración de red del dispositivo")
        print("3. Revisar configuración ISAPI en el dispositivo")

if __name__ == "__main__":
    main()