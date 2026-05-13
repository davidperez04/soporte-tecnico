"""
Interfaz de línea de comandos del sistema.
"""
from datetime import datetime

from .ticket import Ticket
from .soporte_tecnico import SoporteTecnico


def menu():
    menu_principal = '''
    ================================
           SOPORTE TÉCNICO
    ================================
    1. Soy usuario
    2. Soy agente
    3. Ver resumen del sistema
    4. Ver estadísticas
    5. Salir
    '''

    menu_usuario = '''
    ---- MENÚ USUARIO ----
    1. Crear ticket
    2. Consultar posición de mi ticket
    3. Ver tiempo estimado de espera
    4. Cancelar mi ticket
    5. Volver
    '''

    menu_agente = '''
    ---- MENÚ AGENTE ----
    1. Ver cola de tickets
    2. Atender siguiente ticket
    3. Ver ticket en atención
    4. Registrar solución
    5. Verificar tiempo de atención
    6. Ver historial de resueltos
    7. Filtrar historial por categoría
    8. Filtrar historial por prioridad
    9. Ver tickets cancelados
    10. Volver
    '''

    menu_categorias = '''
    Categoría del problema:
    1. Hardware
    2. Software
    3. Red
    4. Cuenta de usuario
    5. Otro
    '''

    categorias = {1: "hardware", 2: "software", 3: "red",
                  4: "cuenta de usuario", 5: "otro"}

    state = True
    soporteTecnico = SoporteTecnico()

    while state:
        try:
            opcion = int(input(f"{menu_principal} Respuesta: "))
        except ValueError:
            print("Opción inválida, ingresá un número.")
            continue

        if opcion == 1:
            try:
                opcion_usuario = int(input(f"{menu_usuario} Respuesta: "))
            except ValueError:
                print("Opción inválida")
                continue

            if opcion_usuario == 1:
                nombre = input("Nombre: ")
                descripcion = input("Descripción: ")
                try:
                    categoria = categorias[int(input(f"{menu_categorias} Respuesta: "))]
                except (ValueError, KeyError):
                    print("Categoría inválida")
                    continue
                horaLlegada = datetime.now()
                ticket = Ticket(soporteTecnico.contador_id, nombre, descripcion, categoria, horaLlegada)
                soporteTecnico.agregar_ticket(ticket)
                soporteTecnico.contador_id += 1
            elif opcion_usuario == 2:
                soporteTecnico.posicion_ticket()
            elif opcion_usuario == 3:
                soporteTecnico.tiempo_de_espera()
            elif opcion_usuario == 4:
                soporteTecnico.cancelar_ticket()

        elif opcion == 2:
            try:
                opcion_agente = int(input(f"{menu_agente} Respuesta: "))
            except ValueError:
                print("Opción inválida")
                continue

            if opcion_agente == 1:
                soporteTecnico.ver_cola()
            elif opcion_agente == 2:
                soporteTecnico.atender_ticket()
            elif opcion_agente == 3:
                soporteTecnico.ver_ticket_en_atencion()
            elif opcion_agente == 4:
                soporteTecnico.ticket_atendido()
            elif opcion_agente == 5:
                soporteTecnico.verificar_tiempo_atencion()
            elif opcion_agente == 6:
                soporteTecnico.ver_historial_tickets_resueltos()
            elif opcion_agente == 7:
                soporteTecnico.historial_por_categoria()
            elif opcion_agente == 8:
                soporteTecnico.historial_por_prioridad()
            elif opcion_agente == 9:
                soporteTecnico.ver_tickets_cancelados()

        elif opcion == 3:
            soporteTecnico.resumen_sistema()

        elif opcion == 4:
            soporteTecnico.estadisticas()

        elif opcion == 5:
            print("Saliendo del sistema...")
            state = False
