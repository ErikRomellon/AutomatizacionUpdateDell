#Programa realizado por Erik Jesús Romellón Lorenzana

import paramiko, os, re, time
from time import sleep
from datetime import datetime

listaACTUALIZADOS=[]
listaIP = []
listaNUEVAIOS = []
listaUSERNAME = []
listaPASSWORD = []
listaNUEVAIOSTAM = []
i = 0
ip = input(f"Ingresa IP del equipo #{i+1} o fin para dejar de agregar elementos: ")
ip = ip.lower()
while ip != 'fin':
    print("\n\n")
    listaIP.append(ip)
    username = input(f"Ingresa username de {ip}: ")
    password = input(f"Ingresa password de {ip}: ")
    nuevaIos = input(f"Ingresa nombre de el ios del equipo #{i + 1}(incluye extension de archivo ej. c3550X-iojajd23423.bin: ")
    nuevaIosTam = input(f"Ingresa el tamaño de la nueva Ios en Bytes ej.3745093: ")

    listaUSERNAME.append(username)
    listaPASSWORD.append(password)
    listaNUEVAIOS.append(nuevaIos)
    listaNUEVAIOSTAM.append(nuevaIosTam)

    i = i + 1
    ip = input(f"Ingresa IP del equipo #{i + 1} o fin para dejar de agregar elementos: ")

copyTo = "backup"
tiempoEspera = 85
copyFrom = "tftp://"
servidorTftpIp =input("Ingresa dir Ip del servidor Tftp: ")
final = b""
newMatch = []


logs = r'logs.txt'
comandos = r'comandos.txt'

f = open(logs, "w+")
f.write("")
f.write("\n")
f.close()

f = open(comandos, "w+")
f.write("")
f.write("\n")
f.close()

def updateDell():
    print("Ejecucion iniciada, informacion almacenada en logs")
    print("\n\tNO CERRAR HASTA QUE LA EJECUCUION CONCLUYA")
    pos = 0

    # conexion por SSH
    for ip in listaIP:
        try:
            now = datetime.now()
            tiempo = now.strftime("%H:%M:%S")
            f = open(logs, "a")
            f.write(tiempo + " : " + ip + " estableciendo conexion via SSH\n")
            f.close()
            remote_conn_pre = paramiko.SSHClient()
            remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            remote_conn_pre.connect(ip,22, username=listaUSERNAME[pos], password=listaPASSWORD[pos],look_for_keys=False, allow_agent=False)
            remote_conn = remote_conn_pre.invoke_shell()
            now = datetime.now()
            tiempo = now.strftime("%H:%M:%S")
            f = open(logs, "a")
            f.write(tiempo + " : " + ip + f" conexion establecida con exito\n")
            f.close()
            remote_conn.send("en")
            remote_conn.send("\n")
            remote_conn.send(listaPASSWORD[pos]+"\n")
            remote_conn.send("\n")
            remote_conn.send("dir\n")
            sleep(.3)

            while True:

                global final
                remote_conn.send("\n")
                data = remote_conn.recv(100)
                remote_conn.send("\n")
                if b'Bytes Free' in final:
                    global memoria
                    outputConv = final.decode("utf-8")
                    now = datetime.now()
                    tiempo = now.strftime("%H:%M:%S")
                    f = open(comandos, "a")
                    f.write(tiempo + " : " + ip + outputConv+"\n")
                    f.close()
                    memoria = re.findall('Bytes Free: \d+', outputConv)
                    for match in memoria:
                        newMatch.append(match[-8:])
                    memoria = "".join(newMatch)
                    break
                else:
                    final += data

            now = datetime.now()
            tiempo = now.strftime("%H:%M:%S")
            f = open(logs, "a")
            f.write(tiempo +" : " +ip +" memoria disponible " + memoria +"\n")
            f.close()
            print(tiempo +" : " +ip +" memoria disponible " + memoria)

            if(int(memoria) > int(listaNUEVAIOSTAM[pos])):
                now = datetime.now()
                tiempo = now.strftime("%H:%M:%S")
                f = open(logs, "a")
                f.write(tiempo + " : " + ip + " comando de transferencia enviado \n")
                f.close()
                print(tiempo + " : " + ip + " realizando transferencia con el servidor " + servidorTftpIp)
                #comando copy tfttp://servidor/archivo flash:
                sleep(1)
                remote_conn.send("copy "+copyFrom+""+servidorTftpIp+"/"+listaNUEVAIOS[pos]+" backup\n")
                sleep(1)
                now = datetime.now()
                tiempo = now.strftime("%H:%M:%S")
                f = open(logs, "a")
                f.write(tiempo + " : " + ip + f" conectando al servidor tftp para la transferencia, tiempo de espera por {tiempoEspera} segundos \n")
                f.close()
                print(tiempo + " : " + ip +f" conectando al servidor tftp para la transferencia, tiempo de espera por {tiempoEspera} segundos")

                remote_conn.send("y")
                remote_conn.send("\n")
                remote_conn.send("\n")
                sleep(tiempoEspera)

                now = datetime.now()
                tiempo = now.strftime("%H:%M:%S")
                f = open(logs, "a")
                f.write(tiempo + " : " + ip + " tiempo de espera finalizado \n")
                f.close()
                print(tiempo + " : " + ip + " tiempo de espera finalizado \n")
                sleep(.3)

                output=remote_conn.recv(5000)
                outputConv = output.decode("utf-8")
                now = datetime.now()
                tiempo = now.strftime("%H:%M:%S")
                f = open(comandos, "a")
                f.write(tiempo + " : " + ip + outputConv+"\n")
                f.close()

                canceled = re.findall("Transfer Canceled!", outputConv)
                canceled = "".join(canceled)
                failed = re.findall("File transfer failed!", outputConv)
                failed = "".join(failed)
                successfully = re.findall("successfully", outputConv)
                successfully = "".join(successfully)


                if failed:
                    now = datetime.now()
                    tiempo = now.strftime("%H:%M:%S")
                    f = open(logs, "a")
                    f.write(tiempo + " : " + ip + " no se pudo actualizar por un error de transferencia, vuelve a intentar!!!\n")
                    f.close()
                    print(tiempo + " : " + ip + " no se pudo actualizar por un error de transferencia, vuelve a intentar!!!\n")
                if canceled:
                    now = datetime.now()
                    tiempo = now.strftime("%H:%M:%S")
                    f = open(logs, "a")
                    f.write(tiempo + " : " + ip + " la transferencia ha sido cancelada\n")
                    f.close()
                if successfully:
                    now = datetime.now()
                    tiempo = now.strftime("%H:%M:%S")
                    f = open(logs, "a")
                    f.write(tiempo + " : " + ip + " transferencia realizada con exito\n")
                    f.close()

                    sleep(1)
                    remote_conn.send("boot system backup\n")
                    sleep(5)
                    now = datetime.now()
                    tiempo = now.strftime("%H:%M:%S")
                    f = open(logs, "a")
                    f.write(tiempo + " : " + ip + " la nueva imagen ha sido booteada\n")
                    f.close()
                    remote_conn.send("wr\n")
                    sleep(5)
                    remote_conn.send("y")
                    remote_conn.send("\n")
                    sleep(20)
                    output = remote_conn.recv(3000)
                    outputConv = output.decode("utf-8")
                    now = datetime.now()
                    tiempo = now.strftime("%H:%M:%S")
                    f = open(comandos, "a")
                    f.write(tiempo + " : " + ip + outputConv + "\n")
                    f.close()

                    saved = re.findall("Configuration Saved!", outputConv)
                    saved = "".join(saved)
                    if saved:
                        now = datetime.now()
                        tiempo = now.strftime("%H:%M:%S")
                        f = open(logs, "a")
                        f.write(tiempo + " : " + ip + " comando wr aplicado con exito\n")
                        f.close()
                        remote_conn.send("reload\n")
                        sleep(1)
                        remote_conn.send("y")
                        sleep(1)
                        remote_conn.send("y")
                        sleep(1)
                        now = datetime.now()
                        tiempo = now.strftime("%H:%M:%S")
                        f = open(logs, "a")
                        f.write(tiempo + " : " + ip + " comando reload enviado\n")
                        f.write(tiempo + " : " + ip + " coniguracion finalizada\n")
                        f.write("-------------------------------------------------------------")
                        f.close()
                    else:
                        now = datetime.now()
                        tiempo = now.strftime("%H:%M:%S")
                        f = open(logs, "a")
                        f.write(tiempo + " : " + ip + " configuracion no guardada, no es posible reiniciar el switch, guarda y reinicia manualmente\n")
                        f.write("-------------------------------------------------------------")
                        f.close()
                else:
                    now = datetime.now()
                    tiempo = now.strftime("%H:%M:%S")
                    f = open(logs, "a")
                    f.write(tiempo + " : " + ip + " no fue posible continuar con el monitoreo, revisa la configuracion manualmente\n")
                    f.write("-------------------------------------------------------------")
                    f.close()



            else:
                now = datetime.now()
                tiempo = now.strftime("%H:%M:%S")
                f = open(logs, "a")
                f.write(tiempo + " : " + ip + " memoria insuficiente, imposible actualizar \n")
                f.write("-------------------------------------------------------------")
                f.close()


        except paramiko.ssh_exception.AuthenticationException:
            now = datetime.now()
            tiempo = now.strftime("%H:%M:%S")
            f = open(logs, "a")
            f.write(f"No fue posible hacer conexion con {ip}\n")
            f.write("-------------------------------------------------------------")
            f.close()
            print(f"No fue posible hacer conexion con {ip}")
            print("-------------------------------------------------------------")
        except TimeoutError:
            now = datetime.now()
            tiempo = now.strftime("%H:%M:%S")
            f = open(logs, "a")
            f.write(f"No fue posible hacer conexion con {ip}\n")
            f.write("-------------------------------------------------------------")
            f.close()
            print(f"No fue posible hacer conexion con {ip}")
            print("-------------------------------------------------------------")
        pos = pos + 1
updateDell()
print("\n\n\tConfiguracion finalizada")
terminar = input("\nPresiona enter para finalizar la ejecucion del programa ")
