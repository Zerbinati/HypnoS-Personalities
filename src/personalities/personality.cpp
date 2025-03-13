/*
  HypnoS, a UCI chess playing engine derived from Stockfish
  Copyright (C) 2004-2025 The Stockfish developers (see AUTHORS file)

  HypnoS is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  HypnoS is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <iostream>
#include <fstream>
#include <unordered_map>
#include <string>
#include "../nlohmann/json.hpp"

#include "../personalities/personality.h"

using json = nlohmann::json; // Alias for the JSON library

// Method to load a personality from a JSON file
bool Personality::load_from_file(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Unable to open file " << filename << std::endl;
        return false;
    }

    try {
        json j;
        file >> j; // Parsing the JSON file
        std::cout << "Debug: JSON file successfully loaded!" << std::endl;

        // Loading general parameters
        name = j.value("name", "Default");
        description = j.value("description", "No description provided");

        // Loading "Personality" and "Elo"
		personalityEnabled = j.value("Personality", true);  // Default: true
		Elo = j.value("Elo", 1320);                         // Default: 1320
		uci_elo = Elo;  // Synchronize directly with the class variable

        // Loading book parameters
        PersonalityBook = j.value("PersonalityBook", false);
        BookFile = j.value("BookFile", "<empty>");
        BookWidth = j.value("BookWidth", 5);
        BookDepth = j.value("BookDepth", 5);

        // Debug: Display loaded book parameters
        std::cout << "Debug: Loaded book parameters:\n";
        std::cout << "  PersonalityBook: " << (PersonalityBook ? "true" : "false") << "\n";
        std::cout << "  BookFile: " << BookFile << "\n";
        std::cout << "  BookWidth: " << BookWidth << "\n";
        std::cout << "  BookDepth: " << BookDepth << "\n";

        // Loading Elo parameter
		if (j.contains("Elo")) {
			evaluation["Elo"] = j["Elo"].get<int>();
			Elo = evaluation["Elo"];  // Keep the Elo value synchronized
			uci_elo = Elo;  // Ensure `uci_elo` is always up to date
			std::cout << "Debug: Loaded Elo parameter: " << Elo << "\n";
		} else {
			std::cout << "Debug: Elo parameter not found, using default value (1320).\n";
			evaluation["Elo"] = 1320;
			Elo = 1320;  
			uci_elo = 1320;  // Also synchronize `uci_elo`
		}

        // Loading evaluation parameters
        if (j.contains("evaluation") && j["evaluation"].is_object()) {
            std::cout << "Debug: Loading evaluation parameters..." << std::endl;
            for (const auto& [key, value] : j["evaluation"].items()) {
                evaluation[key] = value.get<int>();
                std::cout << "Debug: " << key << " = " << evaluation[key] << std::endl; // Print each loaded parameter
            }
        }

		std::cout << "info string Personality loaded successfully: " << name << std::endl;
		std::cout << "info string Personality: " << (personalityEnabled ? "true" : "false") << std::endl;
		std::cout << "info string Elo: " << Elo << std::endl;

        // Debug: Display loaded evaluation parameters
        std::cout << "Debug: Loaded evaluation parameters:\n";
        for (const auto& [key, value] : evaluation) {
            std::cout << "  " << key << " = " << value << "\n";
        }

        return true;

    } catch (const std::exception& e) {
        std::cerr << "Error while parsing the JSON file: " << e.what() << std::endl;
        return false;
    }
}

// Method to print a summary of the personality
void Personality::print_summary() const {
	std::cout << "Name: " << name << "\nDescription: " << description << "\n";

	// Print Elo
	std::cout << "Elo: " << get_elo() << "\n\n";

    std::cout << "[Book]\n";
    std::cout << "  PersonalityBook: " << (PersonalityBook ? "true" : "false") << "\n";
    std::cout << "  BookFile: " << BookFile << "\n";
    std::cout << "  BookWidth: " << BookWidth << "\n";
    std::cout << "  BookDepth: " << BookDepth << "\n\n";

    std::cout << "[Evaluation Parameters]\n";
    for (const auto& [key, value] : evaluation) {
        std::cout << "  " << key << " = " << value << "\n";
    }
}

// Method to update a parameter in the evaluation map
void Personality::set_param(const std::string& key, int value) {
    // Update the value in the evaluation map
    evaluation[key] = value;
    std::cout << "Debug: Parameter '" << key << "' updated to: " << value << std::endl;
}

// Method to retrieve an evaluation parameter. Returns the associated value
// or a default value if the parameter does not exist.
int Personality::get_evaluation_param(const std::string& key, int default_value) const {
    auto it = evaluation.find(key);
    if (it == evaluation.end()) {
        return default_value; // If the parameter does not exist, return the default value
    }
    return it->second; // Return the value associated with the parameter
}
