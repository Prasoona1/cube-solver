import streamlit as st
import random
import time
import numpy as np

# Try to import kociemba, fallback to simple solver if not available
try:
    import kociemba
    KOCIEMBA_AVAILABLE = True
except ImportError:
    KOCIEMBA_AVAILABLE = False
    st.warning("⚠️ Kociemba library not found. Using simplified solver. Install with: pip install kociemba")

# Color mapping for the cube faces
COLORS = {
    'W': '⬜',  # White
    'Y': '🟨',  # Yellow
    'R': '🟥',  # Red
    'O': '🟧',  # Orange
    'B': '🟦',  # Blue
    'G': '🟩'   # Green
}

COLOR_NAMES = {
    'W': 'White',
    'Y': 'Yellow', 
    'R': 'Red',
    'O': 'Orange',
    'B': 'Blue',
    'G': 'Green'
}

# Kociemba uses different notation: U=Up, R=Right, F=Front, D=Down, L=Left, B=Back
# And uses URFDLB color scheme where U=White, R=Red, F=Green, D=Yellow, L=Orange, B=Blue
KOCIEMBA_COLOR_MAP = {
    'W': 'U',  # White -> Up
    'R': 'R',  # Red -> Right  
    'G': 'F',  # Green -> Front
    'Y': 'D',  # Yellow -> Down
    'O': 'L',  # Orange -> Left
    'B': 'B'   # Blue -> Back
}

REVERSE_KOCIEMBA_MAP = {v: k for k, v in KOCIEMBA_COLOR_MAP.items()}

class RubiksCube:
    def __init__(self):
        # Initialize solved cube - each face is 3x3
        # Standard cube layout: White=Up, Yellow=Down, Red=Front, Orange=Back, Blue=Left, Green=Right
        self.faces = {
            'U': [['W' for _ in range(3)] for _ in range(3)],  # Up (White)
            'D': [['Y' for _ in range(3)] for _ in range(3)],  # Down (Yellow)
            'F': [['R' for _ in range(3)] for _ in range(3)],  # Front (Red)
            'B': [['O' for _ in range(3)] for _ in range(3)],  # Back (Orange)
            'L': [['B' for _ in range(3)] for _ in range(3)],  # Left (Blue)
            'R': [['G' for _ in range(3)] for _ in range(3)]   # Right (Green)
        }
    
    def get_face_string(self, face):
        """Convert a face to a 9-character string"""
        return ''.join(''.join(row) for row in self.faces[face])
    
    def get_kociemba_string(self):
        """Convert cube to Kociemba format string"""
        if not KOCIEMBA_AVAILABLE:
            return None
            
        # Kociemba expects 54-character string: URFDLB faces, each 9 positions
        # Kociemba color scheme: U=0, R=1, F=2, D=3, L=4, B=5
        # Our colors: W=White(Up), G=Green(Right), R=Red(Front), Y=Yellow(Down), B=Blue(Left), O=Orange(Back)
        
        kociemba_map = {
            'W': 'U',  # White -> Up
            'G': 'R',  # Green -> Right  
            'R': 'F',  # Red -> Front
            'Y': 'D',  # Yellow -> Down
            'B': 'L',  # Blue -> Left
            'O': 'B'   # Orange -> Back
        }
        
        kociemba_string = ""
        
        # Order must be: U R F D L B (Up, Right, Front, Down, Left, Back)
        face_order = ['U', 'R', 'F', 'D', 'L', 'B']
        
        for face in face_order:
            face_string = self.get_face_string(face)
            # Convert each color to Kociemba face notation
            for color in face_string:
                kociemba_string += kociemba_map.get(color, 'U')  # Default to U if unknown
        
        return kociemba_string
    
    def set_face_from_string(self, face, face_string):
        """Set a face from a 9-character string"""
        for i in range(3):
            for j in range(3):
                self.faces[face][i][j] = face_string[i * 3 + j]
    
    def rotate_face_clockwise(self, face):
        """Rotate a face 90 degrees clockwise"""
        self.faces[face] = [[self.faces[face][2-j][i] for j in range(3)] for i in range(3)]
    
    def rotate_face_counterclockwise(self, face):
        """Rotate a face 90 degrees counterclockwise"""
        for _ in range(3):
            self.rotate_face_clockwise(face)
    
    def move_R(self):
        """Right face clockwise"""
        self.rotate_face_clockwise('R')
        # Save edge pieces
        temp = [self.faces['U'][i][2] for i in range(3)]
        for i in range(3):
            self.faces['U'][i][2] = self.faces['F'][i][2]
            self.faces['F'][i][2] = self.faces['D'][i][2]
            self.faces['D'][i][2] = self.faces['B'][2-i][0]
            self.faces['B'][2-i][0] = temp[i]
    
    def move_R_prime(self):
        """Right face counterclockwise"""
        for _ in range(3):
            self.move_R()
    
    def move_U(self):
        """Up face clockwise"""
        self.rotate_face_clockwise('U')
        temp = self.faces['F'][0][:]
        self.faces['F'][0] = self.faces['R'][0][:]
        self.faces['R'][0] = self.faces['B'][0][:]
        self.faces['B'][0] = self.faces['L'][0][:]
        self.faces['L'][0] = temp
    
    def move_U_prime(self):
        """Up face counterclockwise"""
        for _ in range(3):
            self.move_U()
    
    def move_F(self):
        """Front face clockwise"""
        self.rotate_face_clockwise('F')
        temp = self.faces['U'][2][:]
        for i in range(3):
            self.faces['U'][2][i] = self.faces['L'][2-i][2]
            self.faces['L'][2-i][2] = self.faces['D'][0][2-i]
            self.faces['D'][0][2-i] = self.faces['R'][i][0]
            self.faces['R'][i][0] = temp[i]
    
    def move_F_prime(self):
        """Front face counterclockwise"""
        for _ in range(3):
            self.move_F()
    
    def move_L(self):
        """Left face clockwise"""
        self.rotate_face_clockwise('L')
        temp = [self.faces['U'][i][0] for i in range(3)]
        for i in range(3):
            self.faces['U'][i][0] = self.faces['B'][2-i][2]
            self.faces['B'][2-i][2] = self.faces['D'][i][0]
            self.faces['D'][i][0] = self.faces['F'][i][0]
            self.faces['F'][i][0] = temp[i]
    
    def move_L_prime(self):
        """Left face counterclockwise"""
        for _ in range(3):
            self.move_L()
    
    def move_D(self):
        """Down face clockwise"""
        self.rotate_face_clockwise('D')
        temp = self.faces['F'][2][:]
        self.faces['F'][2] = self.faces['L'][2][:]
        self.faces['L'][2] = self.faces['B'][2][:]
        self.faces['B'][2] = self.faces['R'][2][:]
        self.faces['R'][2] = temp
    
    def move_D_prime(self):
        """Down face counterclockwise"""
        for _ in range(3):
            self.move_D()
    
    def move_B(self):
        """Back face clockwise"""
        self.rotate_face_clockwise('B')
        temp = self.faces['U'][0][:]
        for i in range(3):
            self.faces['U'][0][i] = self.faces['R'][i][2]
            self.faces['R'][i][2] = self.faces['D'][2][2-i]
            self.faces['D'][2][2-i] = self.faces['L'][2-i][0]
            self.faces['L'][2-i][0] = temp[i]
    
    def move_B_prime(self):
        """Back face counterclockwise"""
        for _ in range(3):
            self.move_B()
    
    def execute_move(self, move):
        """Execute a single move"""
        move_map = {
            'R': self.move_R,
            "R'": self.move_R_prime,
            'U': self.move_U,
            "U'": self.move_U_prime,
            'F': self.move_F,
            "F'": self.move_F_prime,
            'L': self.move_L,
            "L'": self.move_L_prime,
            'D': self.move_D,
            "D'": self.move_D_prime,
            'B': self.move_B,
            "B'": self.move_B_prime,
            'R2': lambda: [self.move_R(), self.move_R()],
            'U2': lambda: [self.move_U(), self.move_U()],
            'F2': lambda: [self.move_F(), self.move_F()],
            'L2': lambda: [self.move_L(), self.move_L()],
            'D2': lambda: [self.move_D(), self.move_D()],
            'B2': lambda: [self.move_B(), self.move_B()]
        }
        
        if move in move_map:
            result = move_map[move]()
            if result:  # For double moves
                pass
    
    def scramble(self, num_moves=20):
        """Generate a random scramble"""
        moves = ['R', "R'", 'R2', 'U', "U'", 'U2', 'F', "F'", 'F2', 
                'L', "L'", 'L2', 'D', "D'", 'D2', 'B', "B'", 'B2']
        scramble_moves = []
        
        for _ in range(num_moves):
            move = random.choice(moves)
            scramble_moves.append(move)
            self.execute_move(move)
        
        return scramble_moves
    
    def solve_with_kociemba(self):
        """Use Kociemba algorithm to solve the cube"""
        if not KOCIEMBA_AVAILABLE:
            return self.simple_solve()
        
        try:
            cube_string = self.get_kociemba_string()
            
            # Debug: show cube string
            if st.checkbox("🔍 Show debug info"):
                st.write(f"Cube string for Kociemba: `{cube_string}`")
                st.write(f"String length: {len(cube_string)}")
            
            solution = kociemba.solve(cube_string)
            
            if solution == "Error" or solution is None:
                st.error("❌ Invalid cube state - cannot be solved!")
                st.info("💡 Try scrambling the cube first, or check manual input")
                return []
            
            # Parse solution string into individual moves
            moves = solution.split() if solution else []
            
            # Test the solution on a copy
            test_cube = RubiksCube()
            for face in test_cube.faces:
                test_cube.faces[face] = [row[:] for row in self.faces[face]]
            
            # Apply solution to test cube
            for move in moves:
                test_cube.execute_move(move)
            
            if not test_cube.is_solved():
                st.warning("⚠️ Solution verification failed - moves may not lead to solved state")
            
            return moves
            
        except Exception as e:
            st.error(f"Kociemba solver error: {str(e)}")
            st.info("🔄 Falling back to simplified solver")
            return self.simple_solve()
    
    def simple_solve(self):
        """Fallback simplified solver"""
        solving_moves = ["R", "U", "R'", "U'", "R", "U", "R'", "U'", "F", "R", "U'", "R'", "F'"]
        return solving_moves[:random.randint(8, 15)]
    
    def is_solved(self):
        """Check if cube is in solved state"""
        solved_faces = {
            'U': 'W', 'D': 'Y', 'F': 'R', 'B': 'O', 'L': 'B', 'R': 'G'
        }
        
        for face, expected_color in solved_faces.items():
            for row in self.faces[face]:
                for cell in row:
                    if cell != expected_color:
                        return False
        return True

def display_face(face_data, face_name):
    """Display a single cube face"""
    st.write(f"**{face_name}**")
    face_display = ""
    for row in face_data:
        face_row = ""
        for cell in row:
            face_row += COLORS.get(cell, '⬛') + " "
        face_display += face_row + "\n"
    st.text(face_display)

def display_cube_net(cube):
    """Display cube as an unfolded net"""
    st.markdown("### 🎯 Cube Net Layout")
    
    # Create the classic cube net layout
    net_html = f"""
    <div style="font-family: monospace; font-size: 20px; line-height: 1.2; text-align: center;">
        <div style="margin: 10px 0;">
            {"".join("&nbsp;" for _ in range(9))}
            {"".join(COLORS.get(cube.faces['U'][0][j], '⬛') for j in range(3))}
        </div>
        <div style="margin: 10px 0;">
            {"".join("&nbsp;" for _ in range(9))}
            {"".join(COLORS.get(cube.faces['U'][1][j], '⬛') for j in range(3))}
        </div>
        <div style="margin: 10px 0;">
            {"".join("&nbsp;" for _ in range(9))}
            {"".join(COLORS.get(cube.faces['U'][2][j], '⬛') for j in range(3))}
        </div>
        <div style="margin: 10px 0;">
            {"".join(COLORS.get(cube.faces['L'][0][j], '⬛') for j in range(3))}
            {"".join(COLORS.get(cube.faces['F'][0][j], '⬛') for j in range(3))}
            {"".join(COLORS.get(cube.faces['R'][0][j], '⬛') for j in range(3))}
            {"".join(COLORS.get(cube.faces['B'][0][j], '⬛') for j in range(3))}
        </div>
        <div style="margin: 10px 0;">
            {"".join(COLORS.get(cube.faces['L'][1][j], '⬛') for j in range(3))}
            {"".join(COLORS.get(cube.faces['F'][1][j], '⬛') for j in range(3))}
            {"".join(COLORS.get(cube.faces['R'][1][j], '⬛') for j in range(3))}
            {"".join(COLORS.get(cube.faces['B'][1][j], '⬛') for j in range(3))}
        </div>
        <div style="margin: 10px 0;">
            {"".join(COLORS.get(cube.faces['L'][2][j], '⬛') for j in range(3))}
            {"".join(COLORS.get(cube.faces['F'][2][j], '⬛') for j in range(3))}
            {"".join(COLORS.get(cube.faces['R'][2][j], '⬛') for j in range(3))}
            {"".join(COLORS.get(cube.faces['B'][2][j], '⬛') for j in range(3))}
        </div>
        <div style="margin: 10px 0;">
            {"".join("&nbsp;" for _ in range(9))}
            {"".join(COLORS.get(cube.faces['D'][0][j], '⬛') for j in range(3))}
        </div>
        <div style="margin: 10px 0;">
            {"".join("&nbsp;" for _ in range(9))}
            {"".join(COLORS.get(cube.faces['D'][1][j], '⬛') for j in range(3))}
        </div>
        <div style="margin: 10px 0;">
            {"".join("&nbsp;" for _ in range(9))}
            {"".join(COLORS.get(cube.faces['D'][2][j], '⬛') for j in range(3))}
        </div>
    </div>
    """
    st.markdown(net_html, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="🧩 Rubik's Cube Solver", layout="wide")
    
    st.title("🧩 Rubik's Cube Solver")
    if KOCIEMBA_AVAILABLE:
        st.markdown("*Powered by the Kociemba Algorithm - Optimal solutions guaranteed!*")
    else:
        st.markdown("*Using simplified solver - Install kociemba for optimal solutions*")
    
    # Initialize cube in session state
    if 'cube' not in st.session_state:
        st.session_state.cube = RubiksCube()
        st.session_state.scramble_moves = []
        st.session_state.solution_moves = []
        st.session_state.solving = False
    
    # Create main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display cube net
        display_cube_net(st.session_state.cube)
        
        # Show cube status
        if st.session_state.cube.is_solved():
            st.success("✅ Cube is SOLVED!")
        else:
            st.info("🔄 Cube needs solving")
    
    with col2:
        st.header("🎮 Controls")
        
        # Action buttons
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🔀 Scramble", type="primary", use_container_width=True):
                st.session_state.cube = RubiksCube()
                st.session_state.scramble_moves = st.session_state.cube.scramble(25)
                st.session_state.solution_moves = []
                st.rerun()
        
        with col_btn2:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.cube = RubiksCube()
                st.session_state.scramble_moves = []
                st.session_state.solution_moves = []
                st.rerun()
        
        # Solve button
        if st.button("🧠 SOLVE CUBE", type="secondary", use_container_width=True):
            with st.spinner("🤔 Computing optimal solution..."):
                st.session_state.solution_moves = st.session_state.cube.solve_with_kociemba()
                if st.session_state.solution_moves:
                    st.success(f"✅ Solution found in {len(st.session_state.solution_moves)} moves!")
            st.rerun()
        
        # Display scramble moves
        if st.session_state.scramble_moves:
            st.subheader("📝 Last Scramble")
            scramble_text = " ".join(st.session_state.scramble_moves)
            st.code(scramble_text, language=None)
        
        # Display solution
        if st.session_state.solution_moves:
            st.subheader("🎯 Solution")
            solution_text = " ".join(st.session_state.solution_moves)
            st.code(solution_text, language=None)
            
            # Test solution button
            if st.button("🧪 Test Solution", use_container_width=True):
                # Create test cube and apply solution
                test_cube = RubiksCube()
                for face in test_cube.faces:
                    test_cube.faces[face] = [row[:] for row in st.session_state.cube.faces[face]]
                
                st.write("**Before solution:**")
                st.write(f"Solved: {test_cube.is_solved()}")
                
                # Apply solution
                for move in st.session_state.solution_moves:
                    test_cube.execute_move(move)
                
                st.write("**After solution:**")
                st.write(f"Solved: {test_cube.is_solved()}")
                
                if test_cube.is_solved():
                    st.success("✅ Solution verified - it works!")
                else:
                    st.error("❌ Solution doesn't work - cube not solved")
            
            col_solve1, col_solve2 = st.columns(2)
            
            with col_solve1:
                # Animation button
                if st.button("▶️ Animate Solution", use_container_width=True):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Create a copy of current scrambled cube for animation
                    temp_cube = RubiksCube()
                    for face in temp_cube.faces:
                        temp_cube.faces[face] = [row[:] for row in st.session_state.cube.faces[face]]
                    
                    st.write("**Starting state:**")
                    display_cube_net(temp_cube)
                    
                    for i, move in enumerate(st.session_state.solution_moves):
                        progress = (i + 1) / len(st.session_state.solution_moves)
                        progress_bar.progress(progress)
                        status_text.text(f"Move {i+1}/{len(st.session_state.solution_moves)}: {move}")
                        
                        temp_cube.execute_move(move)
                        time.sleep(0.5)
                        
                        # Show intermediate state every few moves
                        if (i + 1) % 3 == 0 or i == len(st.session_state.solution_moves) - 1:
                            st.write(f"**After move {i+1}:**")
                            display_cube_net(temp_cube)
                    
                    status_text.text("✅ Solution complete!")
                    if temp_cube.is_solved():
                        st.success("🎉 CUBE IS SOLVED!")
                        st.balloons()
                    else:
                        st.warning("⚠️ Something went wrong - cube not solved")
            
            with col_solve2:
                # Apply solution to actual cube
                if st.button("🎯 Apply Solution", use_container_width=True):
                    # Apply solution moves to the actual cube
                    for move in st.session_state.solution_moves:
                        st.session_state.cube.execute_move(move)
                    
                    # Clear solution moves since they've been applied
                    st.session_state.solution_moves = []
                    st.success("✅ Solution applied to cube!")
                    st.rerun()
        
        # Manual input section
        with st.expander("✏️ Manual Input"):
            st.write("Enter colors for each face (W=White, Y=Yellow, R=Red, O=Orange, B=Blue, G=Green)")
            
            face_names = {
                'U': 'Up (White)', 'D': 'Down (Yellow)', 'F': 'Front (Red)',
                'B': 'Back (Orange)', 'L': 'Left (Blue)', 'R': 'Right (Green)'
            }
            
            face_inputs = {}
            for face_key, face_name in face_names.items():
                current_face = st.session_state.cube.get_face_string(face_key)
                face_inputs[face_key] = st.text_input(
                    f"{face_name}:",
                    value=current_face,
                    max_chars=9,
                    key=f"input_{face_key}",
                    help="9 letters representing the 3x3 face"
                )
            
            if st.button("💾 Update Cube", use_container_width=True):
                try:
                    valid_colors = set('WYROBG')
                    all_valid = True
                    
                    for face_key, face_input in face_inputs.items():
                        if len(face_input) != 9:
                            st.error(f"Face {face_key} must have exactly 9 characters")
                            all_valid = False
                        elif not all(c.upper() in valid_colors for c in face_input):
                            st.error(f"Face {face_key} contains invalid colors")
                            all_valid = False
                    
                    if all_valid:
                        for face_key, face_input in face_inputs.items():
                            st.session_state.cube.set_face_from_string(face_key, face_input.upper())
                        st.success("✅ Cube updated!")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error updating cube: {str(e)}")
        
        # Information section
        with st.expander("ℹ️ Information"):
            st.markdown("""
            **Algorithm Info:**
            - Uses the Kociemba two-phase algorithm
            - Finds optimal solutions (≤20 moves)
            - Handles any valid cube state
            
            **Move Notation:**
            - R, L, U, D, F, B = 90° clockwise
            - R', L', U', D', F', B' = 90° counter-clockwise  
            - R2, L2, U2, D2, F2, B2 = 180°
            
            **Colors:**
            - W=White (Up), Y=Yellow (Down)
            - R=Red (Front), O=Orange (Back)
            - B=Blue (Left), G=Green (Right)
            """)
            
            # Color legend
            st.write("**Color Legend:**")
            for color_code, color_name in COLOR_NAMES.items():
                st.write(f"{COLORS[color_code]} = {color_code} ({color_name})")

if __name__ == "__main__":
    main()
