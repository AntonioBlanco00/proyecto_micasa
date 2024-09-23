#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2024 by YOUR NAME HERE
#
#    This file is part of RoboComp
#
#    RoboComp is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    RoboComp is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RoboComp.  If not, see <http://www.gnu.org/licenses/>.
#

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication
from rich.console import Console
from genericworker import *
import interfaces as ifaces
import time
from collections import deque

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

from pydsr import *

###### Webots packages ######
sys.path.append('/usr/local/webots/lib/controller/python')
from controller import Supervisor, Robot
os.environ["WEBOTS_CONTROLLER_URL"] = "ipc://1234/robot"
# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel

class SupervisorWorker(Supervisor):
    def __init__(self):
        Robot.__init__(self)
        self.people_dict = {
            "Etiqueta_2_6e91" : self.getFromDef("Etiqueta_2_6e91").getField('translation'),
            "Etiqueta_1_973b" : self.getFromDef("Etiqueta_1_973b").getField('translation'),
            "Pulsera_1_59b1" : self.getFromDef("Pulsera_1_59b1").getField('translation'),
            "Pulsera_2_d126" : self.getFromDef("Pulsera_2_d126").getField('translation'),
            "Colgante_1_f192" : self.getFromDef("Colgante_1_f192").getField('translation'),
            "Colgante_2_a8cf" : self.getFromDef("Colgante_2_a8cf").getField('translation')
        }
        self.timeStep = int(self.getBasicTimeStep())
    def set_translation(self, name, x, y):
        print(name, x, y)
        # traslation_field = self.people_dict[name].getField('translation')
        self.people_dict[name].setSFVec3f([y/1000, -x/1000, 1])
        # print(traslation_field.getSFVec3f())


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000

        # YOU MUST SET AN UNIQUE ID FOR THIS AGENT IN YOUR DEPLOYMENT. "_CHANGE_THIS_ID_" for a valid unique integer
        self.agent_id = 2
        self.g = DSRGraph(0, "pythonAgent", self.agent_id)
        self.rt_api = rt_api(self.g)

        try:
            # signals.connect(self.g, signals.UPDATE_NODE_ATTR, self.update_node_att)
            # signals.connect(self.g, signals.UPDATE_NODE, self.update_node)
            # signals.connect(self.g, signals.DELETE_NODE, self.delete_node)
            # signals.connect(self.g, signals.UPDATE_EDGE, self.update_edge)
            signals.connect(self.g, signals.UPDATE_EDGE_ATTR, self.update_edge_att)
            # signals.connect(self.g, signals.DELETE_EDGE, self.delete_edge)
            console.print("signals connected")
        except RuntimeError as e:
            print(e)

        if startup_check:
            self.startup_check()
        else:
            self.supervisor = SupervisorWorker()
            self.translation_queue = deque()

            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

    def __del__(self):
        """Destructor"""

    def setParams(self, params):
        # try:
        #	self.innermodel = InnerModel(params["InnerModelPath"])
        # except:
        #	traceback.print_exc()
        #	print("Error reading config params")
        return True


    @QtCore.Slot()
    def compute(self):
        while self.supervisor.step(self.supervisor.timeStep) != -1:
            if self.translation_queue:
                person_node_name, tx, ty = self.translation_queue.pop()
                self.supervisor.set_translation(person_node_name, tx, ty)
            time.sleep(0)

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)






    # =============== DSR SLOTS  ================
    # =============================================

    def update_node_att(self, id: int, attribute_names: [str]):
        console.print(f"UPDATE NODE ATT: {id} {attribute_names}", style='green')

    def update_node(self, id: int, type: str):
        console.print(f"UPDATE NODE: {id} {type}", style='green')

    def delete_node(self, id: int):
        console.print(f"DELETE NODE:: {id} ", style='green')

    def update_edge(self, fr: int, to: int, type: str):
        person_node_name = self.g.get_node(to).name
        rt_edge = self.rt_api.get_edge_RT(self.g.get_node(fr), to)
        if rt_edge != None:
            tx, ty, _ = rt_edge.attrs['rt_translation'].value
            self.translation_queue.append([person_node_name, tx, ty])     

    def update_edge_att(self, fr: int, to: int, type: str, attribute_names: [str]):
        person_node_name = self.g.get_node(to).name
        rt_edge = self.rt_api.get_edge_RT(self.g.get_node(fr), to)
        if rt_edge != None:
            tx, ty, _ = rt_edge.attrs['rt_translation'].value
            self.translation_queue.append([person_node_name, tx, ty])


    def delete_edge(self, fr: int, to: int, type: str):
        console.print(f"DELETE EDGE: {fr} to {type} {type}", style='green')
