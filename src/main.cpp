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
#include<stdio.h>
#include <fstream>

#include "bitboard.h"
#include "endgame.h"
#include "misc.h"
#include "polybook.h"
#include "position.h"
#include "psqt.h"
#include "search.h"
#include "thread.h"
#include "tt.h"
#include "uci.h"
#include "personalities/personality.h"

using namespace Stockfish;

namespace Stockfish::UCI {
    void sync_uci_options();
}

// Global object for the active personality
Personality activePersonality;

int main(int argc, char* argv[]) {

    SysInfo::init();
    show_logo();

    std::cout << engine_info() << std::endl;

    CommandLine::init(argc, argv);

    // Show system information
    std::cout
        << "Operating System (OS) : " << SysInfo::os_info() << std::endl
        << "CPU Brand             : " << SysInfo::processor_brand() << std::endl
        << "NUMA Nodes            : " << SysInfo::numa_nodes() << std::endl
        << "Cores                 : " << SysInfo::physical_cores() << std::endl
        << "Threads               : " << SysInfo::logical_cores() << std::endl
        << "Hyper-Threading       : " << SysInfo::is_hyper_threading() << std::endl
        << "L1/L2/L3 cache size   : " << SysInfo::cache_info(0) << "/" << SysInfo::cache_info(1)
        << "/" << SysInfo::cache_info(2) << std::endl
        << "Memory installed (RAM): " << SysInfo::total_memory() << std::endl << std::endl;

    // Initialization of options
    UCI::init(Options);

    // Determine the personality file from the UCI option or use the default file
    std::string personalityDir = "perGM"; // Personality directory
    std::string personalityFile = (std::string)Options["Load Personality"] == "<empty>"
                                      ? personalityDir + "/default.json"
                                      : personalityDir + "/" + (std::string)Options["Load Personality"];

    std::cerr << "Info: Trying to load personality file: " << personalityFile << std::endl;

    // Load the personality file
    if (!activePersonality.load_from_file(personalityFile)) {
        std::cerr << "Error: Could not load personality file: " << personalityFile
                  << ". Falling back to default parameters." << std::endl;
    } else {
        std::cerr << "Info: Personality loaded successfully from: " << personalityFile << std::endl;
        activePersonality.print_summary(); // Print a summary of the loaded personality
    }

    // Engine initializations
    Tune::init();
    PSQT::init();
    Bitboards::init();
    Position::init();
    Bitbases::init();
    Endgames::init();
    Threads.set(size_t(Options["Threads"]));
    Search::clear(); 

    // Start the UCI loop
    UCI::loop(argc, argv);

    Threads.set(0);
    return 0;
}
