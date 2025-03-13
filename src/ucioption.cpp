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

#include <algorithm>
#include <cassert>
#include <ostream>
#include <sstream>
#include <fstream>
#include "nlohmann/json.hpp"
#include <filesystem> // For std::filesystem::absolute

#include "evaluate.h"
#include "misc.h"
#include "search.h"
#include "thread.h"
#include "tt.h"
#include "uci.h"
#include "polybook.h"
#include "personalities/personality.h"


using std::string;

namespace Stockfish {

UCI::OptionsMap Options; // Global object for UCI options
Personality activePersonality; // Global object for the active personality
std::string previousBookFile = "<empty>"; // Tracks the last loaded book

namespace UCI {

void sync_uci_options(); // Declaration to avoid the warning

bool personalityChanged = true; // Global variable to track personality changes

void sync_uci_options() {
    std::cout << "info string Syncing UCI options with active personality..." << std::endl;

    Options["PersonalityBook"] = std::string(activePersonality.PersonalityBook ? "true" : "false");
    Options["Book File"] = activePersonality.BookFile;
    Options["Book Width"] = std::to_string(activePersonality.BookWidth);
    Options["Book Depth"] = std::to_string(activePersonality.BookDepth);

    // Synchronize personality parameters
    Options["Aggressiveness"]       = std::to_string(activePersonality.get_evaluation_param("Aggressiveness", 0));
    Options["RiskTaking"]           = std::to_string(activePersonality.get_evaluation_param("RiskTaking", 0));
    Options["KingSafety"]           = std::to_string(activePersonality.get_evaluation_param("KingSafety", 0));
    Options["PieceActivity"]        = std::to_string(activePersonality.get_evaluation_param("PieceActivity", 0));
    Options["PawnStructure"]        = std::to_string(activePersonality.get_evaluation_param("PawnStructure", 0));
    Options["KnightPair"]           = std::to_string(activePersonality.get_evaluation_param("KnightPair", 0));
    Options["BishopPair"]           = std::to_string(activePersonality.get_evaluation_param("BishopPair", 0));
    Options["Defense"]              = std::to_string(activePersonality.get_evaluation_param("Defense", 0));
    Options["CalculationDepth"]     = std::to_string(activePersonality.get_evaluation_param("CalculationDepth", 0));
    Options["EndgameKnowledge"]     = std::to_string(activePersonality.get_evaluation_param("EndgameKnowledge", 0));
    Options["PieceSacrifice"]       = std::to_string(activePersonality.get_evaluation_param("PieceSacrifice", 0));
    Options["CenterControl"]        = std::to_string(activePersonality.get_evaluation_param("CenterControl", 0));
    Options["PositionClosure"]      = std::to_string(activePersonality.get_evaluation_param("PositionClosure", 0));
    Options["PieceTrade"]           = std::to_string(activePersonality.get_evaluation_param("PieceTrade", 0));
    Options["KingAttack"]           = std::to_string(activePersonality.get_evaluation_param("KingAttack", 0));
    Options["PositionalSacrifice"]  = std::to_string(activePersonality.get_evaluation_param("PositionalSacrifice", 0));
    Options["KnightVsBishop"]       = std::to_string(activePersonality.get_evaluation_param("KnightVsBishop", 0));
    Options["PawnPush"]             = std::to_string(activePersonality.get_evaluation_param("PawnPush", 0));
    Options["OpenFileControl"]      = std::to_string(activePersonality.get_evaluation_param("OpenFileControl", 0));
    Options["RookActivity"]         = std::to_string(activePersonality.get_evaluation_param("RookActivity", 0));
    Options["PawnStorm"]            = std::to_string(activePersonality.get_evaluation_param("PawnStorm", 0));
    Options["SacrificeFrequency"]   = std::to_string(activePersonality.get_evaluation_param("SacrificeFrequency", 0));
    Options["KingMobility"]         = std::to_string(activePersonality.get_evaluation_param("KingMobility", 0));
    Options["PieceCoordination"]    = std::to_string(activePersonality.get_evaluation_param("PieceCoordination", 0));
    Options["HumanImperfection"]    = std::to_string(activePersonality.get_evaluation_param("HumanImperfection", 0));
    Options["LossStreak"]           = std::to_string(activePersonality.get_evaluation_param("LossStreak", 0));

    // Resend the values to ensure the GUI updates them
    std::cout << "info string UCI options updated:"          << std::endl;
    std::cout << "setoption name PersonalityBook value "     << Options["PersonalityBook"] << std::endl;
    std::cout << "setoption name Book File value "           << Options["Book File"] << std::endl;
    std::cout << "setoption name Book Width value "          << Options["Book Width"] << std::endl;
    std::cout << "setoption name Book Depth value "          << Options["Book Depth"] << std::endl;
    std::cout << "setoption name Aggressiveness value "      << Options["Aggressiveness"] << std::endl;
    std::cout << "setoption name RiskTaking value "          << Options["RiskTaking"] << std::endl;
    std::cout << "setoption name KingSafety value "          << Options["KingSafety"] << std::endl;
    std::cout << "setoption name PieceActivity value "       << Options["PieceActivity"] << std::endl;
    std::cout << "setoption name PawnStructure value "       << Options["PawnStructure"] << std::endl;
    std::cout << "setoption name KnightPair value "          << Options["KnightPair"] << std::endl;
    std::cout << "setoption name BishopPair value "          << Options["BishopPair"] << std::endl;
    std::cout << "setoption name Defense value "             << Options["Defense"] << std::endl;
    std::cout << "setoption name CalculationDepth value "    << Options["CalculationDepth"] << std::endl;
    std::cout << "setoption name EndgameKnowledge value "    << Options["EndgameKnowledge"] << std::endl;
    std::cout << "setoption name PieceSacrifice value "      << Options["PieceSacrifice"] << std::endl;
    std::cout << "setoption name CenterControl value "       << Options["CenterControl"] << std::endl;
    std::cout << "setoption name PositionClosure value "     << Options["PositionClosure"] << std::endl;
    std::cout << "setoption name PieceTrade value "          << Options["PieceTrade"] << std::endl;
    std::cout << "setoption name KingAttack value "          << Options["KingAttack"] << std::endl;
    std::cout << "setoption name PositionalSacrifice value " << Options["PositionalSacrifice"] << std::endl;
    std::cout << "setoption name KnightVsBishop value "      << Options["KnightVsBishop"] << std::endl;
    std::cout << "setoption name PawnPush value "            << Options["PawnPush"] << std::endl;
    std::cout << "setoption name OpenFileControl value "     << Options["OpenFileControl"] << std::endl;
    std::cout << "setoption name RookActivity value "        << Options["RookActivity"] << std::endl;
    std::cout << "setoption name PawnStorm value "           << Options["PawnStorm"] << std::endl;
    std::cout << "setoption name SacrificeFrequency value "  << Options["SacrificeFrequency"] << std::endl;
    std::cout << "setoption name KingMobility value "        << Options["KingMobility"] << std::endl;
    std::cout << "setoption name PieceCoordination value "   << Options["PieceCoordination"] << std::endl;
    std::cout << "setoption name HumanImperfection value "   << Options["HumanImperfection"] << std::endl;

    std::cout << "info string UCI options successfully synced." << std::endl;

    // Force the GUI to reload the updated options
    std::cout << "isready" << std::endl;
    std::cout << "uci" << std::endl;
}

/// 'On change' actions, triggered by an option's value change
static void on_clear_hash(const Option&) { Search::clear(); }
static void on_hash_size(const Option& o) { TT.resize(size_t(o)); }
static void on_logger(const Option& o) { start_logger(o); }
static void on_threads(const Option& o) { Threads.set(size_t(o)); }

static void on_book_file(const Option& o) {
    std::string newBookFile = static_cast<std::string>(o);
    
    std::cout << "info string Book file changed to: " << newBookFile << std::endl;
    
    if (newBookFile != previousBookFile) {
        activePersonality.BookFile = newBookFile; // UPDATE THE BOOK FILE!
        polybook[0].init(newBookFile);
        previousBookFile = newBookFile;
        std::cout << "info string Book loaded: " << newBookFile << std::endl;
    }
}

static void on_load_personality(const Option& o) {
    std::string personalityName = static_cast<std::string>(o);

    // If the option is `<empty>`, do not load anything
    if (personalityName == "<empty>") {
        std::cout << "info string No personality file selected. Using default engine parameters." << std::endl;
        return;
    }

    // Removes any trailing ".json" from the name
    if (personalityName.size() > 5 && personalityName.substr(personalityName.size() - 5) == ".json") {
        personalityName = personalityName.substr(0, personalityName.size() - 5);
    }

    // Constructs the correct path
    std::string personalityPath = "perGM/" + personalityName + ".json";

    // FIRST, print "uciok" for Arena!
    std::cout << "uciok" << std::endl;

    std::cout << "info string Attempting to load personality: " << personalityPath << std::endl;
    std::cout << "info string Absolute path: " << std::filesystem::absolute(personalityPath) << std::endl;

    if (activePersonality.load_from_file(personalityPath)) {
        // Synchronize the parameters BEFORE setting the flag
        sync_uci_options();

        Stockfish::UCI::personalityChanged = true; // Now set it after synchronization

        // FORCE the update of the global personality
        Stockfish::Eval::activePersonality = activePersonality;

        std::cout << "info string Personality loaded successfully: " << personalityName << std::endl;

        // FORCE the GUI to receive the new values
        std::cout << "setoption name PersonalityBook value " << (activePersonality.PersonalityBook ? "true" : "false") << std::endl;
        std::cout << "setoption name Book File value "       << activePersonality.BookFile << std::endl;
        std::cout << "setoption name Book Width value "      << activePersonality.BookWidth << std::endl;
        std::cout << "setoption name Book Depth value "      << activePersonality.BookDepth << std::endl;

        // Force the GUI to reload the updated options
        std::cout << "uci" << std::endl;
        std::cout << "isready" << std::endl;
 
       if (activePersonality.PersonalityBook) {
            std::cout << "info string Loading personality book: " << activePersonality.BookFile << std::endl;
            std::cout << "info string Book Width: "               << activePersonality.BookWidth << std::endl;
            std::cout << "info string Book Depth: "               << activePersonality.BookDepth << std::endl;
        } else {
            std::cout << "info string No personality book assigned." << std::endl;
        }

        // UCI output for personality parameters
        std::cout << "info string Personality Evaluation Parameters:" << std::endl;
        std::cout << "info string  - Aggressiveness: "       << activePersonality.get_evaluation_param("Aggressiveness", 0) << std::endl;
        std::cout << "info string  - RiskTaking: "           << activePersonality.get_evaluation_param("RiskTaking", 0) << std::endl;
        std::cout << "info string  - KingSafety: "           << activePersonality.get_evaluation_param("KingSafety", 0) << std::endl;
        std::cout << "info string  - PieceActivity: "        << activePersonality.get_evaluation_param("PieceActivity", 0) << std::endl;
        std::cout << "info string  - PawnStructure: "        << activePersonality.get_evaluation_param("PawnStructure", 0) << std::endl;
        std::cout << "info string  - KnightPair: "           << activePersonality.get_evaluation_param("KnightPair", 0) << std::endl;
        std::cout << "info string  - BishopPair: "           << activePersonality.get_evaluation_param("BishopPair", 0) << std::endl;
        std::cout << "info string  - Defense: "              << activePersonality.get_evaluation_param("Defense", 0) << std::endl;
        std::cout << "info string  - CalculationDepth: "     << activePersonality.get_evaluation_param("CalculationDepth", 0) << std::endl;
        std::cout << "info string  - EndgameKnowledge: "     << activePersonality.get_evaluation_param("EndgameKnowledge", 0) << std::endl;
        std::cout << "info string  - PieceSacrifice: "       << activePersonality.get_evaluation_param("PieceSacrifice", 0) << std::endl;
        std::cout << "info string  - CenterControl: "        << activePersonality.get_evaluation_param("CenterControl", 0) << std::endl;
        std::cout << "info string  - PositionClosure: "      << activePersonality.get_evaluation_param("PositionClosure", 0) << std::endl;
        std::cout << "info string  - PieceTrade: "           << activePersonality.get_evaluation_param("PieceTrade", 0) << std::endl;
        std::cout << "info string  - KingAttack: "           << activePersonality.get_evaluation_param("KingAttack", 0) << std::endl;
        std::cout << "info string  - PositionalSacrifice: "  << activePersonality.get_evaluation_param("PositionalSacrifice", 0) << std::endl;
        std::cout << "info string  - KnightVsBishop: "       << activePersonality.get_evaluation_param("KnightVsBishop", 0) << std::endl;
        std::cout << "info string  - PawnPush: "             << activePersonality.get_evaluation_param("PawnPush", 0) << std::endl;
        std::cout << "info string  - OpenFileControl: "      << activePersonality.get_evaluation_param("OpenFileControl", 0) << std::endl;
        std::cout << "info string  - RookActivity: "         << activePersonality.get_evaluation_param("RookActivity", 0) << std::endl;
        std::cout << "info string  - PawnStorm: "           << activePersonality.get_evaluation_param("PawnStorm", 0) << std::endl;
        std::cout << "info string  - SacrificeFrequency: "   << activePersonality.get_evaluation_param("SacrificeFrequency", 0) << std::endl;
        std::cout << "info string  - KingMobility: "         << activePersonality.get_evaluation_param("KingMobility", 0) << std::endl;
        std::cout << "info string  - PieceCoordination: "    << activePersonality.get_evaluation_param("PieceCoordination", 0) << std::endl;
        std::cout << "info string  - HumanImperfection: "    << activePersonality.get_evaluation_param("HumanImperfection", 0) << std::endl;

        // Confirm that options have been synced
        std::cout << "info string UCI options successfully synced with personality!" << std::endl;

        // Forces the GUI to reread the updated options
        std::cout << "isready" << std::endl;
        std::cout << "uci" << std::endl;

    } else {  
        std::cerr << "info string Could not load personality: " << personalityPath << std::endl;
    }
}

/// Our case insensitive less() function as required by UCI protocol
bool CaseInsensitiveLess::operator() (const string& s1, const string& s2) const {
    return std::lexicographical_compare(s1.begin(), s1.end(), s2.begin(), s2.end(),
         [](char c1, char c2) { return tolower(c1) < tolower(c2); });
}

/// UCI::init() initializes the UCI options to their hard-coded default values
void init(OptionsMap& o) {
    constexpr int MaxHashMB = Is64Bit ? 33554432 : 2048;

    o["Debug Log File"]        << Option("", on_logger);
    o["Threads"]               << Option(1, 1, 1024, on_threads);
    o["Hash"]                  << Option(16, 1, MaxHashMB, on_hash_size);
    o["Clear Hash"]            << Option(on_clear_hash);
    o["Ponder"]                << Option(false);
    o["MultiPV"]               << Option(1, 1, 500);
    o["Skill Level"]           << Option(20, 0, 20);
    o["Move Overhead"]         << Option(10, 0, 5000);
    o["Slow Mover"]            << Option(100, 10, 1000);
    o["nodestime"]             << Option(0, 0, 10000);
    o["UCI_Chess960"]          << Option(false);
    o["Personality"]           << Option(false);
    o["Elo"] << Option(1320, 1320, 3190, [](const Option& v) {
        int uci_elo = int(v);
        std::cout << "info string UCI Elo changed to " << uci_elo << std::endl;

        // Calculate HumanImperfection by Elo
        int humanImperfection = ((3190 - uci_elo) * 50) / (3190 - 1320);
        humanImperfection = std::clamp(humanImperfection, 0, 50); // Let's make sure it's in the correct range

        std::cout << "info string Calculated HumanImperfection: " << humanImperfection << std::endl;
        activePersonality.set_param("HumanImperfection", humanImperfection);
    });
    o["UCI_ShowWDL"]           << Option(false);
	#ifdef DEVELOPER_MODE
    // Advanced personality options (visible only in developer mode)
    o["Aggressiveness"]        << Option(0, 0, 30, [](const Option& v) { activePersonality.set_param("Aggressiveness", int(v)); });
    o["RiskTaking"]            << Option(0, 0, 30, [](const Option& v) { activePersonality.set_param("RiskTaking", int(v)); });
    o["KingSafety"]            << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("KingSafety", int(v)); });
    o["PieceActivity"]         << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("PieceActivity", int(v)); });
    o["PawnStructure"]         << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("PawnStructure", int(v)); });
    o["KnightPair"]            << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("KnightPair", int(v)); });
    o["BishopPair"]            << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("BishopPair", int(v)); });
    o["Defense"]               << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("Defense", int(v)); });
    o["CalculationDepth"]      << Option(0, 0, 18, [](const Option& v) { activePersonality.set_param("CalculationDepth", int(v)); }); 
    o["EndgameKnowledge"]      << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("EndgameKnowledge", int(v)); });
    o["PieceSacrifice"]        << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("PieceSacrifice", int(v)); });
    o["CenterControl"]         << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("CenterControl", int(v)); });
    o["PositionClosure"]       << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("PositionClosure", int(v)); });
    o["PieceTrade"]            << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("PieceTrade", int(v)); });
    o["KingAttack"]            << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("KingAttack", int(v)); });
    o["PositionalSacrifice"]   << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("PositionalSacrifice", int(v)); });
    o["KnightVsBishop"]        << Option(0, -50, 50, [](const Option& v) { activePersonality.set_param("KnightVsBishop", int(v)); });
    o["PawnPush"]              << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("PawnPush", int(v)); });
    o["OpenFileControl"]       << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("OpenFileControl", int(v)); });
    o["RookActivity"]          << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("RookActivity", int(v)); });
    o["PawnStorm"]             << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("PawnStorm", int(v)); });
    o["SacrificeFrequency"]    << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("SacrificeFrequency", int(v)); });
    o["KingMobility"]          << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("KingMobility", int(v)); });
    o["PieceCoordination"]     << Option(0, 0, 50, [](const Option& v) { activePersonality.set_param("PieceCoordination", int(v)); });
    o["HumanImperfection"]     << Option(0, 0, 50, [](const Option& v) {  activePersonality.set_param("HumanImperfection", int(v)); 
    });
    #endif
    // Book Options (PersonalityBook and associated parameters)
    o["PersonalityBook"]       << Option(false, [](const Option& v) { activePersonality.PersonalityBook = bool(v); });
    o["Book File"]             << Option("<empty>", on_book_file);
    o["Book Width"]            << Option(1, 1, 20, [](const Option& v) { activePersonality.BookWidth = int(v); });
    o["Book Depth"]            << Option(1, 1, 30, [](const Option& v) { activePersonality.BookDepth = int(v); });

    o["Load Personality"]      << Option("<empty>", on_load_personality);
}


/// operator<<() is used to print all the options default values in chronological
/// insertion order (the idx field) and in the format defined by the UCI protocol.

std::ostream& operator<<(std::ostream& os, const OptionsMap& om) {

  for (size_t idx = 0; idx < om.size(); ++idx)
      for (const auto& it : om)
          if (it.second.idx == idx)
          {
              const Option& o = it.second;
              os << "\noption name " << it.first << " type " << o.type;

              if (o.type == "string" || o.type == "check" || o.type == "combo")
                  os << " default " << o.defaultValue;

              if (o.type == "spin")
                  os << " default " << int(stof(o.defaultValue))
                     << " min "     << o.min
                     << " max "     << o.max;

              break;
          }

  return os;
}


/// Option class constructors and conversion operators

Option::Option(const char* v, OnChange f) : type("string"), min(0), max(0), on_change(f)
{ defaultValue = currentValue = v; }

Option::Option(bool v, OnChange f) : type("check"), min(0), max(0), on_change(f)
{ defaultValue = currentValue = (v ? "true" : "false"); }

Option::Option(OnChange f) : type("button"), min(0), max(0), on_change(f)
{}

Option::Option(double v, int minv, int maxv, OnChange f) : type("spin"), min(minv), max(maxv), on_change(f)
{ defaultValue = currentValue = std::to_string(v); }

Option::Option(const char* v, const char* cur, OnChange f) : type("combo"), min(0), max(0), on_change(f)
{ defaultValue = v; currentValue = cur; }

Option::operator int() const {
  assert(type == "check" || type == "spin");
  return (type == "spin" ? std::stoi(currentValue) : currentValue == "true");
}

Option::operator std::string() const {
  assert(type == "string");
  return currentValue;
}

bool Option::operator==(const char* s) const {
  assert(type == "combo");
  return   !CaseInsensitiveLess()(currentValue, s)
        && !CaseInsensitiveLess()(s, currentValue);
}


/// operator<<() inits options and assigns idx in the correct printing order

void Option::operator<<(const Option& o) {

  static size_t insert_order = 0;

  *this = o;
  idx = insert_order++;
}


/// operator=() updates currentValue and triggers on_change() action. It's up to
/// the GUI to check for option's limits, but we could receive the new value
/// from the user by console window, so let's check the bounds anyway.

Option& Option::operator=(const string& v) {

  assert(!type.empty());

  if (   (type != "button" && type != "string" && v.empty())
      || (type == "check" && v != "true" && v != "false")
      || (type == "spin" && (stof(v) < min || stof(v) > max)))
      return *this;

  if (type == "combo")
  {
      OptionsMap comboMap; // To have case insensitive compare
      string token;
      std::istringstream ss(defaultValue);
      while (ss >> token)
          comboMap[token] << Option();
      if (!comboMap.count(v) || v == "var")
          return *this;
  }

  if (type != "button")
      currentValue = v;

  if (on_change)
      on_change(*this);

  return *this;
}

} // namespace UCI

} // namespace Stockfish
