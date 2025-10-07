"""
Epic #127 Python Enhancement Bridge Example

This demonstrates the new Python injection capabilities that allow
seamless integration of kinda-lang constructs into Python code.
"""

# This is a regular Python file that can be enhanced with kinda-lang constructs


def calculate_score(base_score):
    """Calculate a score with some fuzzy logic"""
    bonus = 10  # This could become kinda_int(10)
    multiplier = 1.5  # This could become kinda_float(1.5)

    print(f"Calculating score from base: {base_score}")  # Could become sorta_print

    # Traditional calculation
    final_score = (base_score + bonus) * multiplier

    return int(final_score)


class GameEngine:
    """A simple game engine that could benefit from probabilistic behavior"""

    def __init__(self):
        self.player_health = 100
        self.enemy_health = 80

    def player_attack(self):
        """Player attack with potential for enhancement"""
        damage = 20  # Could become kinda_int(20) for fuzzy damage
        print(f"Player deals {damage} damage!")  # Could become sorta_print

        self.enemy_health -= damage
        return damage

    def enemy_attack(self):
        """Enemy attack that could be made probabilistic"""
        damage = 15  # Could become kinda_int(15)

        # This conditional could become ~sometimes
        if self.enemy_health > 50:
            print(f"Enemy deals {damage} damage!")
            self.player_health -= damage
        else:
            print("Enemy is too weak to attack!")

        return damage if self.enemy_health > 50 else 0


def demonstrate_enhancement():
    """Show how the code works before and after enhancement"""
    print("=== Original Python Code ===")
    print("Running with standard Python behavior...")

    # Run a few calculations
    for i in range(3):
        score = calculate_score(100)
        print(f"  Run {i+1}: Score = {score}")

    print("\n=== Game Engine Demo ===")
    game = GameEngine()

    for round_num in range(3):
        print(f"\nRound {round_num + 1}:")
        player_dmg = game.player_attack()
        enemy_dmg = game.enemy_attack()

        print(f"  Player Health: {game.player_health}")
        print(f"  Enemy Health: {game.enemy_health}")

        if game.enemy_health <= 0:
            print("  Enemy defeated!")
            break
        if game.player_health <= 0:
            print("  Player defeated!")
            break

    print("\n=== Enhancement Instructions ===")
    print("To enhance this file with kinda-lang constructs:")
    print("1. kinda inject analyze epic_127_example.py")
    print("2. kinda inject convert epic_127_example.py --level basic")
    print("3. kinda inject run epic_127_example_enhanced.py")
    print("")
    print("Or use decorators directly:")
    print("@kinda.enhance(patterns=['kinda_int', 'sorta_print'])")
    print("def calculate_score(base_score):")
    print("    # Function becomes probabilistically enhanced")


if __name__ == "__main__":
    demonstrate_enhancement()
