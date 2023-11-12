import subprocess
import getopt
import sys
import time
import os
try:
    import requests
except ImportError:
    subprocess.check_call(["pip", "install", "requests-2.31.0.tar.gz"])
    sistema_operativo = os.name
    print(sistema_operativo)
    if sistema_operativo == 'nt':  # Windows
        os.system('cls')
    else:  # Linux, macOS, etc.
        os.system('clear')
    import requests

# Función para obtener los datos de fabricación de una tarjeta de red por IP
def obtener_datos_por_ip(ip):
    diccionario_arp = obtener_tabla_arp() 
    ip_rango = ip.split(".")
    ip_rango_bool = "192" == ip_rango[0] and "168" == ip_rango[1] and "1" == ip_rango[2]
    if(ip_rango_bool):
        if(ip in diccionario_arp):
            mac = diccionario_arp[ip]
            vendor,tiempo = obtener_datos_por_api(mac)
            print(f"MAC Address : {mac}\nFabricante : {vendor}\nTiempo de respuesta: {tiempo}ms")
        else:
            print(f"Error: Not found in arp table")
    else:
        print(f"Error: ip is outside the host network")

# Función para obtener los datos de fabricación de una tarjeta de red por MAC
def obtener_datos_por_api(mac):
    url = f"https://api.maclookup.app/v2/macs/{mac}/company/name?apiKey=01hexea024hba2yb7fqt7jkqmp01hexnkmgj9gffg4nzbtm1t3qfbqsm99zphjiw"
    inicio=time.time()
    response = requests.get(url)
    fin = time.time()
    if response.status_code == 200:
        #data = response.json()
        if(response.text == "*NO COMPANY*" or response.text == "*PRIVATE*"):
            return "Not Found",round((fin-inicio) * 1000)
        else:
            return response.text,round((fin-inicio) * 1000)
    else:
        print(f"Error al leer la api: {response.status_code}")
        return None

# Función para obtener la tabla ARP
def obtener_tabla_arp():
    dicc = {}
    try:
        tabla_arp = subprocess.check_output(['arp', '-a'], universal_newlines=True)
        arp_itt = tabla_arp.split('\n')
        for linea in arp_itt:
            if 'Internet Address' in linea or 'Interfaz' in linea or 'Direcci¢n' in linea or 'Direccion' in linea or 'Interface' in linea:  # Ignorar las 2 primeras líneas
                continue
            if linea.strip():
                parts = linea.split()
                if len(parts) >= 2:
                    cortado = parts[1]
                    cortado = cortado.split("-")
                    cortado = ":".join(cortado)
                    cortado = cortado.upper()
                    dicc[parts[0]] = cortado
        return dicc
    except subprocess.CalledProcessError as e:
        print(f"Error al obtener la tabla ARP: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None 

def main(argv):
    # Inicializar variables
    ayuda = """
Use: ./OUILookup --ip <IP> | --mac <MAC> | --arp | [--help]
--ip : IP del host a consultar.
--mac: MAC a consultar. P.e. aa:bb:cc:00:00:00.
--arp: muestra los fabricantes de los host disponibles en la tabla arp.
--help: muestra este mensaje y termina.
"""
    if len(argv) == 0:
        print(ayuda)
        sys.exit()
    # Leer --argumentos
    try:
        opts, args = getopt.getopt(argv, "i:m:ah", ["ip=", "mac=","arp","help"])
    except getopt.GetoptError:
        print(ayuda)
        sys.exit(2)
    # Iniciar lectura de argumentos
    for opt, arg in opts:
        # Ejecutar comando --help
        if opt == '--help':
            print(ayuda)
            sys.exit()
        # Comando --ip
        elif opt in ("-i", "--ip"):
            if arg == '':
                print("La opción -i/--input no puede estar vacía.")
                sys.exit(2)
            obtener_datos_por_ip(arg)
        # Comando --mac
        elif opt in ("-m", "--mac"):
            if arg == '':
                print("La opción -o/--output no puede estar vacía.")
                sys.exit(2)
            
            vendor,tiempo = obtener_datos_por_api(arg)
            print(f"MAC Address : {arg}\nFabricante : {vendor}\nTiempo de respuesta: {tiempo}ms")
        # Comando --arp
        elif opt in ("-a", "--arp"):
            diccionario_arp = obtener_tabla_arp()
            print("IP\t/\tMAC\t/\t/Vendor")
            for ip in diccionario_arp:
                vendor,time = obtener_datos_por_api(diccionario_arp[ip])
                print(f"{ip}\t {diccionario_arp[ip]}, {vendor}")
                      

if __name__ == "__main__":
    main(sys.argv[1:])
 
