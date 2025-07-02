# nipun_adapter.py

"""
Nipun Adapter

A simple adapter for your project.
This version can:
- Echo normal text
- Evaluate simple modulo expressions like "25%4"
- Be expanded to handle real tasks later
"""

class NipunAdapter:
    def __init__(self):
        """
        Initialize your adapter.
        """
        print("[NipunAdapter] Initialized.")

    def analyze_prompt(self, text):
        """
        Analyze the input prompt.
        If the text looks like a modulo expression (e.g., '25%4'), evaluate it.
        Otherwise, echo it back.
        """
        print(f"[NipunAdapter] Analyzing prompt: {text}")

        # Try to detect a modulo pattern like "25%4"
        if "%" in text:
            try:
                left, right = text.split("%")
                left = left.strip()
                right = right.strip()

                if left.isdigit() and right.isdigit():
                    result = int(left) % int(right)
                    return f"The result of {left} % {right} is: {result}"
                else:
                    return "Error: Invalid numbers for modulo operation."

            except Exception as e:
                return f"Error evaluating modulo: {e}"

        # Default fallback
        return f"The answer to this question is: {text}"

    def connect(self):
        """
        Example connect method — dummy.
        """
        print("[NipunAdapter] Connect called.")
        return True

    def disconnect(self):
        """
        Example disconnect method — dummy.
        """
        print("[NipunAdapter] Disconnect called.")
        return True


# ✅ Standalone test
if __name__ == "__main__":
    adapter = NipunAdapter()
    print(adapter.analyze_prompt("25%4"))
    print(adapter.analyze_prompt("Hello World"))
    adapter.connect()
    adapter.disconnect()
