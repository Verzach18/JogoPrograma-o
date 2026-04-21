import traceback
import threading
import ast
from config import *

class LineTracker(ast.NodeTransformer):
    def visit_stmt(self, node):
        # We only want to track top-level statements or statements in blocks
        # Inject: drone.current_line = <node.lineno>
        track_node = ast.Assign(
            targets=[ast.Attribute(
                value=ast.Name(id='drone', ctx=ast.Load()),
                attr='current_line',
                ctx=ast.Store()
            )],
            value=ast.Constant(value=node.lineno)
        )
        ast.copy_location(track_node, node)
        return [track_node, self.generic_visit(node)]

    def visit_FunctionDef(self, node):
        return self.generic_visit(node)

    def visit_While(self, node):
        return self.generic_visit(node)

    def visit_For(self, node):
        return self.generic_visit(node)

class ScriptExecutor:
    def __init__(self, drone, progression):
        self.drone = drone
        self.progression = progression
        self.drone.progression = progression # Link for internal checks
        self.thread = None
        self.stop_event = threading.Event()
        self.globals = {
            "drone": self.drone,
            "Entities": Entities,
            "Direction": Direction,
            "print": self.drone.log
        }

    def stop(self):
        self.stop_event.set()
        self.drone.stop() # Signal drone to stop waiting
        if self.thread:
            self.thread.join(timeout=0.1)
        self.drone.current_line = -1
        self.drone.log("Script Stopped")

    def execute(self, code: str):
        self.stop() # Stop any existing script
        self.stop_event.clear()
        self.drone.reset_sync()

        # Security/Progression Check
        if "while" in code or "for" in code:
            if not self.progression.can_use("loops"):
                self.drone.log("ERROR: Loops not unlocked!")
                return False
        
        if "if " in code:
            if not self.progression.can_use("if_statements"):
                self.drone.log("ERROR: Conditionals not unlocked!")
                return False

        if "def " in code:
            if not self.progression.can_use("functions"):
                self.drone.log("ERROR: Functions not unlocked!")
                return False

        # Transform code for line tracking
        try:
            tree = ast.parse(code)
            # We need to wrap statements. LineTracker.visit_stmt returns a list, 
            # so we need to fix the tree structure.
            # Simplified approach: Walk and insert.
            new_body = []
            for stmt in tree.body:
                # Inject line tracker before each statement
                tracker = ast.Assign(
                    targets=[ast.Attribute(
                        value=ast.Name(id='drone', ctx=ast.Load()),
                        attr='current_line',
                        ctx=ast.Store()
                    )],
                    value=ast.Constant(value=stmt.lineno)
                )
                new_body.append(tracker)
                
                # If it's a block statement, we need to recurse inside its body
                self._inject_into_block(stmt)
                new_body.append(stmt)
            
            tree.body = new_body
            ast.fix_missing_locations(tree)
            compiled_code = compile(tree, filename="<drone_script>", mode="exec")
        except Exception as e:
            self.drone.log(f"PARSE ERROR: {e}")
            return False

        def run_script():
            try:
                exec(compiled_code, self.globals.copy())
                self.drone.log("Script Finished")
                self.drone.current_line = -1
            except Exception as e:
                if not self.stop_event.is_set():
                    msg = traceback.format_exc().splitlines()[-1]
                    self.drone.log(f"PYTHON ERROR: {msg}")
                    self.drone.current_line = -1

        self.thread = threading.Thread(target=run_script, daemon=True)
        self.thread.start()
        self.drone.log("Script Started")
        return True

    def _inject_into_block(self, node):
        if hasattr(node, 'body') and isinstance(node.body, list):
            new_block_body = []
            for stmt in node.body:
                tracker = ast.Assign(
                    targets=[ast.Attribute(
                        value=ast.Name(id='drone', ctx=ast.Load()),
                        attr='current_line',
                        ctx=ast.Store()
                    )],
                    value=ast.Constant(value=stmt.lineno)
                )
                new_block_body.append(tracker)
                self._inject_into_block(stmt)
                new_block_body.append(stmt)
            node.body = new_block_body
        
        if hasattr(node, 'orelse') and isinstance(node.orelse, list):
            new_else_body = []
            for stmt in node.orelse:
                tracker = ast.Assign(
                    targets=[ast.Attribute(
                        value=ast.Name(id='drone', ctx=ast.Load()),
                        attr='current_line',
                        ctx=ast.Store()
                    )],
                    value=ast.Constant(value=stmt.lineno)
                )
                new_else_body.append(tracker)
                self._inject_into_block(stmt)
                new_else_body.append(stmt)
            node.orelse = new_else_body
