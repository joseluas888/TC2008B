# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python server to interact with Unity
# Sergio. Julio 2021

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json

from mesa import Agent, Model
from mesa.space import SingleGrid
from mesa import Agent, Model
from mesa.space import SingleGrid
from mesa.time import SimultaneousActivation
import pandas as pd
import time
import datetime
import random
import numpy as np

#################################################################


def lane_with_more_traffic(model):
    pass


class Semaforo(Agent):
    def __init__(self, unique_id, model, direccion):
        super().__init__(unique_id, model)
        self.direccion = direccion
        self.color = 'Verde' if self.direccion in ['Norte', 'Sur'] else 'Rojo'
        self.pasos = 0

    def step(self):
        colores = {'Verde': ('Amarillo', 7), 'Amarillo': ('Rojo', 13), 'Rojo': ('Verde', 22)}
        if self.pasos == colores[self.color][1]:
            self.color = colores[self.color][0]
            self.pasos = 0
        else:
            self.pasos += 1



class Auto(Agent):
    def __init__(self,unique_id, model):
        super().__init__(unique_id, model)
        self.waiting = False
        self.origen  = None

        self.posiciones = {}
        for i in range(25, 31):
            self.posiciones[(49, i)] = 'Sur'
        for i in range(17, 23):
            self.posiciones[(0, i)] = 'Norte'
        for i in range(19, 25):
            self.posiciones[(i, 49)] = 'Oeste'
        for i in range(27, 33):
            self.posiciones[(i, 0)] = 'Este'

        self.carriles = {}
        for i in range(19, 25):
            self.carriles[(i, 33)] = 'Este'
        for i in range(27, 33):
            self.carriles[(i, 14)] = 'Oeste'
        for i in range(25, 31):
            self.carriles[(35, i)] = 'Norte'
        for i in range(17, 23):
            self.carriles[(16, i)] = 'Sur'

        # Lista de posiciones en las que los agentes deben ser removidos
        self.posiciones_para_remover = []
        for i in range(25, 31):
            self.posiciones_para_remover.append((0, i))
        for i in range(17, 23):
            self.posiciones_para_remover.append((49, i))
        for i in range(19, 25):
            self.posiciones_para_remover.append((i, 0))
        for i in range(27, 33):
            self.posiciones_para_remover.append((i, 49))

    def step(self):
        # Comportamiento del agente en cada paso de tiempo
        if self.origen is None:
            self.origen = self.posiciones.get(self.pos)

        if self.pos in self.carriles:
            semaforo_asociado = [a for a in self.model.schedule.agents if isinstance(a, Semaforo) and a.direccion == self.origen][0]
            if semaforo_asociado.color == 'Rojo' or semaforo_asociado.color == 'Amarillo':
                self.waiting = True
            else:
                self.waiting = False

        direcciones = {'Norte': (1, 0), 'Sur': (-1, 0), 'Este': (0, 1), 'Oeste': (0, -1)}
        if not self.waiting:
            nueva_posicion = (self.pos[0] + direcciones[self.origen][0], self.pos[1] + direcciones[self.origen][1])
        else:
            nueva_posicion = self.pos

        # Verificar si la nueva posición está en la lista de posiciones para remover
        if nueva_posicion in self.posiciones_para_remover:
            # Eliminar el agente de la grilla
            self.model.grid.remove_agent(self)
            # Eliminar el agente del horario
            self.model.schedule.remove(self)
            self.model.autosEliminados += 1
        elif self.model.grid.is_cell_empty(nueva_posicion):
            # Mover al agente a la nueva posición
            self.model.grid.move_agent(self, nueva_posicion)




class Peaton(Agent):
    def __init__(self,unique_id, model):
        pass

    def step():
        pass


################################################################
class SimulacionCruce(Model):
    def __init__(self):
        self.grid = SingleGrid(50, 50, False)
        self.schedule = SimultaneousActivation(self)
        self.current_id = 0
        self.autosEliminados = 0

        # Norte - límite izquierdo
        for i in range(17):
            for j in range(15, 17):
                self.grid[i][j] = 1
        # Norte - línea de división
        for i in range(17):
            for j in range(23, 25):
                self.grid[i][j] = 1
        # Norte - límite derecho
        for i in range(17):
            for j in range(31, 33):
                self.grid[i][j] = 1
        # Oeste - límite superior
        for i in range(17, 19):
            for j in range(15):
                self.grid[i][j] = 1
        # Oeste - línea de división
        for i in range(25, 27):
            for j in range(15):
                self.grid[i][j] = 1
        # Oeste - límite inferior
        for i in range(33, 35):
            for j in range(15): #17
                self.grid[i][j] = 1
        # Este - límite superior
        for i in range(17, 19):
            for j in range(33, 50):
                self.grid[i][j] = 1
        # Este - línea de división
        for i in range(25, 27):
            for j in range(33, 50):
                self.grid[i][j] = 1
        # Este - límite inferior
        for i in range(33, 35):
            for j in range(33, 50):
                self.grid[i][j] = 1
        # Sur - límite izquierdo
        for i in range(35, 50):
            for j in range(15, 17):
                self.grid[i][j] = 1
        # Sur - línea de división
        for i in range(35, 50):
            for j in range(23, 25):
                self.grid[i][j] = 1
        # Sur - límite derecho
        for i in range(35, 50):
            for j in range(31, 33):
                self.grid[i][j] = 1


        posiciones_semaforos = {
            'Norte': (18,31),
            'Sur': (33,16),
            'Este': (18,16),
            'Oeste': (33,32)
        }

        for direccion, posicion in posiciones_semaforos.items():
                    semaforo = Semaforo(self.current_id, self, direccion)
                    self.schedule.add(semaforo)
                    self.grid.place_agent(semaforo, posicion)
                    self.current_id += 1

    def step(self):

        # Decidir cuántos autos nuevos crear (entre 0 y 5)
        num_autos_nuevos = random.randint(0, 3)

        for _ in range(num_autos_nuevos):
            # Crear un nuevo agente Auto y agregarlo al modelo
            print("Generando ", num_autos_nuevos, " Autos")
            auto = Auto(self.current_id, self)
            self.schedule.add(auto)
            self.current_id += 1

            # Definir la posición inicial del vehículo
            #Sur: (49,25),(49,26),(49,27),(49,28),(49,29),(49,30)
            #Norte: (0,17),(0,18),(0,19),(0,20),(0,21),(0,22)
            #Este:(32,0),(31,0),(30,0),(29,0),(28,0),(27,0)
            #Oeste:(24,49),(23,49),(22,49),(21,49),(20,49),(19,49)


            initial_positions = [(49,25),(49,26),(49,27),(49,28),(49,29),(49,30),(0,17),(0,18),(0,19),(0,20),(0,21),(0,22),(32,0),(31,0),(30,0),(29,0),(28,0),(27,0),(24,49),(23,49),(22,49),(21,49),(20,49),(19,49)]
            initial_position = random.choice(initial_positions)
            while not self.grid.is_cell_empty(initial_position):
                initial_position = random.choice(initial_positions)
            self.grid.place_agent(auto, initial_position)

            print(initial_position)
            origen = auto.posiciones.get(initial_position)
            print(origen)

        # Actualizar el estado del modelo
        self.schedule.step()

modelo = SimulacionCruce()

escalado = 2.5

def updatePositions():  
    modelo.step()
    
    positions = []
    
    agentesGenerados = 0
    
    print('autos eliminados: ' + str(modelo.autosEliminados))
    
    for i in range(modelo.autosEliminados):
        positions.append([20, 20, -10])
        agentesGenerados += 1
    
    for agente in modelo.schedule.agents:
            if isinstance(agente, Auto):
                positions.append([agente.pos[0]*escalado, agente.pos[1]*escalado, 0])
                agentesGenerados += 1
    
    while agentesGenerados < 300:
        positions.append([20, 20, -10])
        agentesGenerados += 1
    
    return positions

def positionsToJSON(ps):
    posDICT = []
    for p in ps:
        pos = {
            "x" : p[0],
            "z" : p[1],
            "y" : p[2]
        }
        posDICT.append(pos)
    return json.dumps(posDICT)


class Server(BaseHTTPRequestHandler):
    
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        #post_data = self.rfile.read(content_length)
        post_data = json.loads(self.rfile.read(content_length))
        #logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                     #str(self.path), str(self.headers), post_data.decode('utf-8'))
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                     str(self.path), str(self.headers), json.dumps(post_data))
        
        positions = updatePositions()
        #print(positions)
        self._set_response()
        resp = "{\"data\":" + positionsToJSON(positions) + "}"
        #print(resp)
        self.wfile.write(resp.encode('utf-8'))


def run(server_class=HTTPServer, handler_class=Server, port=8585):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info("Starting httpd...\n") # HTTPD is HTTP Daemon!
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:   # CTRL+C stops the server
        pass
    httpd.server_close()
    logging.info("Stopping httpd...\n")

if __name__ == '__main__':
    from sys import argv
    
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
