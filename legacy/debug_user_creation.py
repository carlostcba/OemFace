#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debugging para identificar diferencias entre usuario de prueba y usuario real
"""

import requests
import json
from requests.auth import HTTPDigestAuth
import urllib3

# Suprimir warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_session():
    """Crear sesión con autenticación Digest"""
    session = requests.Session()
    session.auth = HTTPDigestAuth("admin", "Oem2017*")
    session.headers.update({
        'User-Agent': 'Hikvision Client',
        'Accept': 'application/xml, application/json',
        'Connection': 'keep-alive'
    })
    session.verify = False
    return session

def test_user_creation(session, employee_no, name, test_name):
    """Probar creación de usuario con datos específicos"""
    print(f"\n{'='*60}")
    print(f"PROBANDO: {test_name}")
    print(f"{'='*60}")
    print(f"Employee No: {employee_no}")
    print(f"Name: '{name}'")
    print(f"Name length: {len(name)}")
    
    url = "http://192.168.0.222/ISAPI/AccessControl/UserInfo/Record?format=json"
    
    user_data = {
        "UserInfo": {
            "employeeNo": str(employee_no),
            "name": name,
            "userType": "normal",
            "Valid": {
                "enable": False,  # Deshabilitado para prueba
                "beginTime": "2024-01-01T00:00:00",
                "endTime": "2030-12-31T23:59:59"
            },
            "doorRight": "1",
            "RightPlan": [{
                "doorNo": 1,
                "planTemplateNo": "1"
            }],
            "maxFingerPrintNum": 0,
            "maxFaceNum": 5
        }
    }
    
    # Mostrar JSON que se enviará
    print(f"JSON a enviar:")
    print(json.dumps(user_data, indent=2, ensure_ascii=False))
    
    # Configurar headers para JSON
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    try:
        response = session.post(url, json=user_data, timeout=30)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code in [200, 201]:
            print(f"✅ EXITOSO: {test_name}")
            return True, employee_no
        elif response.status_code == 409:
            print(f"⚠️ USUARIO YA EXISTE: {test_name}")
            return True, employee_no
        else:
            print(f"❌ ERROR: {test_name}")
            return False, None
            
    except Exception as e:
        print(f"❌ EXCEPCIÓN: {e}")
        return False, None

def delete_user(session, employee_no):
    """Eliminar usuario de prueba"""
    if not employee_no:
        return
        
    url = "http://192.168.0.222/ISAPI/AccessControl/UserInfo/Delete?format=json"
    
    delete_data = {
        "UserInfoDelCond": {
            "EmployeeNoList": [
                {"employeeNo": str(employee_no)}
            ]
        }
    }
    
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    try:
        response = session.delete(url, json=delete_data, timeout=30)
        print(f"Eliminación: {response.status_code}")
    except:
        pass

def main():
    """Función principal de debugging"""
    print("🔍 DEBUG: CREACIÓN DE USUARIOS HIKVISION")
    print("Comparando usuario de prueba vs usuario real")
    
    session = create_session()
    created_users = []
    
    # Test 1: Usuario de prueba que sabemos que funciona
    success, user_id = test_user_creation(
        session, 
        "99999", 
        "Test User", 
        "Usuario de prueba (funciona)"
    )
    if success:
        created_users.append(user_id)
    
    # Test 2: Usuario real con datos originales
    success, user_id = test_user_creation(
        session, 
        "111500", 
        "MARIA TERESA  BENITEZ", 
        "Usuario real original (falla)"
    )
    if success:
        created_users.append(user_id)
    
    # Test 3: Usuario real con nombre limpio
    success, user_id = test_user_creation(
        session, 
        "111500", 
        "MARIA TERESA BENITEZ", 
        "Usuario real con nombre limpio"
    )
    if success:
        created_users.append(user_id)
    
    # Test 4: Usuario real con nombre más corto
    success, user_id = test_user_creation(
        session, 
        "111500", 
        "MARIA BENITEZ", 
        "Usuario real con nombre corto"
    )
    if success:
        created_users.append(user_id)
    
    # Test 5: Usuario real con ID diferente pero mismo nombre
    success, user_id = test_user_creation(
        session, 
        "11150", 
        "MARIA TERESA BENITEZ", 
        "ID más corto, mismo nombre"
    )
    if success:
        created_users.append(user_id)
    
    # Test 6: Usuario real con ID diferente y nombre corto
    success, user_id = test_user_creation(
        session, 
        "1115", 
        "MARIA BENITEZ", 
        "ID y nombre cortos"
    )
    if success:
        created_users.append(user_id)
    
    # Test 7: Verificar límites del employeeNo
    success, user_id = test_user_creation(
        session, 
        "999999", 
        "Test User", 
        "ID de 6 dígitos"
    )
    if success:
        created_users.append(user_id)
    
    # Test 8: Verificar formato de employeeNo
    success, user_id = test_user_creation(
        session, 
        "000111500", 
        "MARIA BENITEZ", 
        "ID con ceros a la izquierda"
    )
    if success:
        created_users.append(user_id)
    
    # Limpieza: Eliminar usuarios de prueba creados
    print(f"\n{'='*60}")
    print("LIMPIEZA: Eliminando usuarios de prueba")
    print(f"{'='*60}")
    
    for user_id in created_users:
        if user_id and str(user_id) != "111500":  # No eliminar el usuario real si se creó
            delete_user(session, user_id)
    
    print(f"\n🎯 ANÁLISIS COMPLETADO")
    print(f"Revisa los resultados para identificar qué formato funciona")

if __name__ == "__main__":
    main()