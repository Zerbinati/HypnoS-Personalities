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

#ifndef EVALUATE_H_INCLUDED
#define EVALUATE_H_INCLUDED

#include <string>
#include "types.h"
#include "personalities/personality.h"

namespace Stockfish {

class Position;

namespace Eval {

  // Declaration of the function **trace**
  std::string trace(Position& pos);
  
  extern Personality activePersonality;

  // Function to print a debug message about classical evaluation
  void print_classical_eval_message();

  // Main function to compute the evaluation of a position
  Value evaluate(const Position& pos);

  extern int loss_streak;  // Make loss_streak accessible

} // namespace Eval

} // namespace Stockfish

#endif // #ifndef EVALUATE_H_INCLUDED
