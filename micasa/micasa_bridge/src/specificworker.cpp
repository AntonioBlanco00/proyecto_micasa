/*
 *    Copyright (C) 2024 by YOUR NAME HERE
 *
 *    This file is part of RoboComp
 *
 *    RoboComp is free software: you can redistribute it and/or modify
 *    it under the terms of the GNU General Public License as published by
 *    the Free Software Foundation, either version 3 of the License, or
 *    (at your option) any later version.
 *
 *    RoboComp is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU General Public License for more details.
 *
 *    You should have received a copy of the GNU General Public License
 *    along with RoboComp.  If not, see <http://www.gnu.org/licenses/>.
 */
#include "specificworker.h"

/**
* \brief Default constructor
*/
SpecificWorker::SpecificWorker(TuplePrx tprx, bool startup_check) : GenericWorker(tprx)
{
	this->startup_check_flag = startup_check;
	// Uncomment if there's too many debug messages
	// but it removes the possibility to see the messages
	// shown in the console with qDebug()
//	QLoggingCategory::setFilterRules("*.debug=false\n");
}

/**
* \brief Default destructor
*/
SpecificWorker::~SpecificWorker()
{
	std::cout << "Destroying SpecificWorker" << std::endl;
}

bool SpecificWorker::setParams(RoboCompCommonBehavior::ParameterList params)
{
//	THE FOLLOWING IS JUST AN EXAMPLE
//	To use innerModelPath parameter you should uncomment specificmonitor.cpp readConfig method content
//	try
//	{
//		RoboCompCommonBehavior::Parameter par = params.at("InnerModelPath");
//		std::string innermodel_path = par.value;
//		innerModel = std::make_shared(innermodel_path);
//	}
//	catch(const std::exception &e) { qFatal("Error reading config params"); }






	return true;
}

void SpecificWorker::initialize(int period)
{
	std::cout << "Initialize worker" << std::endl;
	this->Period = period;
	if(this->startup_check_flag)
	{
		this->startup_check();
	}
	else
	{
		timer.start(Period);
	}

    robot = new webots::Supervisor();

}

void SpecificWorker::compute()
{
	parseHumanObjects();

    robot->step(1);
}

int SpecificWorker::startup_check()
{
	std::cout << "Startup check" << std::endl;
	QTimer::singleShot(200, qApp, SLOT(quit()));
	return 0;
}

void SpecificWorker::parseHumanObjects() {

    webots::Node* crowdNode = robot->getFromDef("CROWD");

    if(!crowdNode){

        static bool ErrorFlag = false;
        if(!ErrorFlag){
            qInfo() << "CROWD Node not found.";
            ErrorFlag = true;
        }

        return;
    }

    webots::Field* childrenField = crowdNode->getField("children");
    for (int i = 0; i < childrenField->getCount(); ++i)
    {
        std::string nodeDEF = childrenField->getMFNode(i)->getDef();
        if(nodeDEF.find("HUMAN_") != std::string::npos)
            humanObjects[i] = childrenField->getMFNode(i)->getPosition();
    }
}


RoboCompVisualElements::TObjects SpecificWorker::VisualElements_getVisualObjects(RoboCompVisualElements::TObjects objects)
{
    RoboCompVisualElements::TObjects objectsList;

    for (const auto &entry : humanObjects) {
        RoboCompVisualElements::TObject object;

        int id = entry.first;
        const double *position = entry.second;

        object.id = id;
        object.x = position[0];
        object.y = position[1];

        objectsList.objects.push_back(object);

        std::cout << "ID: " << id << " position: " << object.x << " " << object.y << std::endl;
    }

    return objectsList;
}

void SpecificWorker::VisualElements_setVisualObjects(RoboCompVisualElements::TObjects objects)
{

}



/**************************************/
// From the RoboCompVisualElements you can use this types:
// RoboCompVisualElements::TRoi
// RoboCompVisualElements::TObject
// RoboCompVisualElements::TObjects

