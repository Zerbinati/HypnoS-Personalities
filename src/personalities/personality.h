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

#ifndef PERSONALITY_H_INCLUDED
#define PERSONALITY_H_INCLUDED

#include <string>
#include <unordered_map>
#include <iostream> // Required for std::cout in the print_summary method
#include "../nlohmann/json.hpp"

class Personality {
public:

    // Default constructor
    Personality() = default;
    
	// Updated variables to reflect the new JSON names
	bool personalityEnabled = true;  // Indicates whether to use the personality (default: true)
	int Elo = 1320;                  // Personality's Elo rating (default: 1320)
	int uci_elo = 1320;               // Variable to synchronize Elo with the Skill structure

	void set_param(const std::string& key, int value);

	// Method to retrieve an evaluation parameter. Returns the associated value  
	// or a default value if the parameter does not exist.
	int get_evaluation_param(const std::string& key, int default_value = 0) const;
	int get_elo() const { return personalityEnabled ? Elo : 1320; }  // Returns Elo only if the personality is enabled

    // Method to set an evaluation parameter
    void set_evaluation_param(const std::string& key, int value);

    // Method to load personality parameters from a file (e.g., JSON or text)
    bool load_from_file(const std::string& filename);

    // Method to print a summary of the personality (useful for debugging)
    void print_summary() const;

    // General parameters
    std::string name = "Default";          // Personality name
    std::string description = "No description provided"; // Personality description

    // Book parameters
    bool PersonalityBook = false;         // Enable/disable the opening book
    std::string BookFile = "<empty>";     // Opening book file name
    int BookWidth = 5;                    // Book width
    int BookDepth = 5;                    // Book depth

    // Map for evaluation parameters (e.g., Aggressiveness, RiskTaking, etc.)
    std::unordered_map<std::string, int> evaluation;

private:
    // Private methods and members for future integrations
    // e.g., advanced parsing or parameter limit management
};

#endif // PERSONALITY_H_INCLUDED
