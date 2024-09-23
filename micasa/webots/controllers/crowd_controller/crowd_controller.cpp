#include "CrowdAgent.cpp"

#define TIME_STEP 32


int main() {

    std::unordered_map<std::string, std::vector<std::string>> miGrafo = {
        {"WAYPOINT_1", {"WAYPOINT_2", "WAYPOINT_3", "WAYPOINT_10"}},
        {"WAYPOINT_2", {"WAYPOINT_1"}},// Terminal
        {"WAYPOINT_3", {"WAYPOINT_1", "WAYPOINT_5", "WAYPOINT_4", "WAYPOINT_9"}},
        {"WAYPOINT_4", {"WAYPOINT_3"}}, //Terminal
        {"WAYPOINT_5", {"WAYPOINT_3", "WAYPOINT_6", "WAYPOINT_7"}},
        {"WAYPOINT_6", {"WAYPOINT_5"}},//Terminal
        {"WAYPOINT_7", {"WAYPOINT_5", "WAYPOINT_8"}},
        {"WAYPOINT_8", {"WAYPOINT_7"}},//Termianl
        {"WAYPOINT_9", {"WAYPOINT_3"}},//Terminal
        {"WAYPOINT_10", {"WAYPOINT_1", "WAYPOINT_11", "WAYPOINT_12"}},
        {"WAYPOINT_11", {"WAYPOINT_10"}},//Terminal
        {"WAYPOINT_12", {"WAYPOINT_10", "WAYPOINT_13", "WAYPOINT_15", "WAYPOINT_16"}},
        {"WAYPOINT_13", {"WAYPOINT_12", "WAYPOINT_14"}},
        {"WAYPOINT_14", {"WAYPOINT_13"}},//Terminal
        {"WAYPOINT_15", {"WAYPOINT_12"}}, //Terminal
        {"WAYPOINT_16", {"WAYPOINT_12", "WAYPOINT_17"}},
        {"WAYPOINT_17", {"WAYPOINT_16"}}//Termianl

    };

    CrowdAgent* agent = new CrowdAgent(miGrafo);

    while (agent->step(TIME_STEP) != -1) {
    
        agent->update();
    }

    return 0;
}
