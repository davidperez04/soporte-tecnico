"""
Modelo de datos: clase Ticket.
"""


class Ticket:
    def __init__(self, id, nombre, descripcion, categoria, horaLlegada):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.categoria = categoria
        self.prioridad = None
        self.horaLlegada = horaLlegada
        self.horaInicioAtencion = None
        self.horaSolucion = None
        self.solucion = None
        self.estado = "en espera"
