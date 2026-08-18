import streamlit as st
import sqlite3
import os
import time
from datetime import datetime

SQLITE_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coding_prep.db")

def init_db():
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            problem_id INTEGER,
            problem_title TEXT,
            difficulty TEXT,
            category TEXT,
            status TEXT,
            code TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def record_submission(user_id, problem_id, problem_title, difficulty, category, status, code):
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO submissions (user_id, problem_id, problem_title, difficulty, category, status, code, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, problem_id, problem_title, difficulty, category, status, code, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

# Problems Bank
PROBLEMS = [
    {
        "id": 1,
        "title": "Two Sum",
        "difficulty": "Easy",
        "category": "Array & Hashing",
        "description": "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.",
        "example": "Input: nums = [2,7,11,15], target = 9\nOutput: [0, 1]",
        "starter_code": """def twoSum(nums, target):
    # Write your solution here
    hashmap = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in hashmap:
            return [hashmap[diff], i]
        hashmap[num] = i
    return []

# Test execution
print(twoSum([2, 7, 11, 15], 9))""",
        "starter_code_java": """import java.util.*;

public class Main {
    public static int[] twoSum(int[] nums, int target) {
        // Write your solution here
        Map<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int diff = target - nums[i];
            if (map.containsKey(diff)) {
                return new int[]{map.get(diff), i};
            }
            map.put(nums[i], i);
        }
        return new int[]{};
    }

    public static void main(String[] args) {
        int[] result = twoSum(new int[]{2, 7, 11, 15}, 9);
        System.out.println(Arrays.toString(result));
    }
}""",
        "starter_code_cpp": """#include <bits/stdc++.h>
using namespace std;

vector<int> twoSum(vector<int>& nums, int target) {
    // Write your solution here
    unordered_map<int, int> hashmap;
    for (int i = 0; i < (int)nums.size(); i++) {
        int diff = target - nums[i];
        if (hashmap.count(diff)) return {hashmap[diff], i};
        hashmap[nums[i]] = i;
    }
    return {};
}

int main() {
    vector<int> nums = {2, 7, 11, 15};
    vector<int> result = twoSum(nums, 9);
    cout << "[" << result[0] << ", " << result[1] << "]" << endl;
    return 0;
}""",
        "expected_output": "[0, 1]"
    },
    {
        "id": 2,
        "title": "Valid Anagram",
        "difficulty": "Easy",
        "category": "Array & Hashing",
        "description": "Given two strings `s` and `t`, return `True` if `t` is an anagram of `s`, and `False` otherwise.",
        "example": "Input: s = \"anagram\", t = \"nagaram\"\nOutput: True",
        "starter_code": """def isAnagram(s, t):
    # Write your solution here
    return sorted(s) == sorted(t)

print(isAnagram('anagram', 'nagaram'))""",
        "starter_code_java": """import java.util.*;

public class Main {
    public static boolean isAnagram(String s, String t) {
        // Write your solution here
        char[] sc = s.toCharArray();
        char[] tc = t.toCharArray();
        Arrays.sort(sc);
        Arrays.sort(tc);
        return Arrays.equals(sc, tc);
    }

    public static void main(String[] args) {
        boolean result = isAnagram("anagram", "nagaram");
        System.out.println(result ? "True" : "False");
    }
}""",
        "starter_code_cpp": """#include <bits/stdc++.h>
using namespace std;

bool isAnagram(string s, string t) {
    // Write your solution here
    sort(s.begin(), s.end());
    sort(t.begin(), t.end());
    return s == t;
}

int main() {
    bool result = isAnagram("anagram", "nagaram");
    cout << (result ? "True" : "False") << endl;
    return 0;
}""",
        "expected_output": "True"
    },
    {
        "id": 3,
        "title": "Container With Most Water",
        "difficulty": "Medium",
        "category": "Two Pointers",
        "description": "You are given an integer array `height` of length `n`. Find two lines that together with the x-axis form a container, such that the container contains the most water.",
        "example": "Input: height = [1,8,6,2,5,4,8,3,7]\nOutput: 49",
        "starter_code": """def maxArea(height):
    left, right = 0, len(height) - 1
    max_water = 0
    while left < right:
        w = right - left
        h = min(height[left], height[right])
        max_water = max(max_water, w * h)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return max_water

print(maxArea([1,8,6,2,5,4,8,3,7]))""",
        "starter_code_java": """public class Main {
    public static int maxArea(int[] height) {
        int left = 0, right = height.length - 1, maxWater = 0;
        while (left < right) {
            int w = right - left;
            int h = Math.min(height[left], height[right]);
            maxWater = Math.max(maxWater, w * h);
            if (height[left] < height[right]) left++;
            else right--;
        }
        return maxWater;
    }

    public static void main(String[] args) {
        int[] height = {1, 8, 6, 2, 5, 4, 8, 3, 7};
        System.out.println(maxArea(height));
    }
}""",
        "starter_code_cpp": """#include <bits/stdc++.h>
using namespace std;

int maxArea(vector<int>& height) {
    int left = 0, right = (int)height.size() - 1, maxWater = 0;
    while (left < right) {
        int w = right - left;
        int h = min(height[left], height[right]);
        maxWater = max(maxWater, w * h);
        if (height[left] < height[right]) left++;
        else right--;
    }
    return maxWater;
}

int main() {
    vector<int> height = {1, 8, 6, 2, 5, 4, 8, 3, 7};
    cout << maxArea(height) << endl;
    return 0;
}""",
        "expected_output": "49"
    },
    {
        "id": 4,
        "title": "Valid Parentheses",
        "difficulty": "Easy",
        "category": "Stack",
        "description": "Given a string `s` containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
        "example": "Input: s = \"()[]{}\"\nOutput: True",
        "starter_code": """def isValid(s):
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in mapping:
            top = stack.pop() if stack else '#'
            if mapping[char] != top:
                return False
        else:
            stack.append(char)
    return not stack

print(isValid('()[]{}'))""",
        "starter_code_java": """import java.util.*;

public class Main {
    public static boolean isValid(String s) {
        Deque<Character> stack = new ArrayDeque<>();
        Map<Character, Character> mapping = new HashMap<>();
        mapping.put(')', '(');
        mapping.put('}', '{');
        mapping.put(']', '[');
        for (char c : s.toCharArray()) {
            if (mapping.containsKey(c)) {
                char top = stack.isEmpty() ? '#' : stack.pop();
                if (top != mapping.get(c)) return false;
            } else {
                stack.push(c);
            }
        }
        return stack.isEmpty();
    }

    public static void main(String[] args) {
        boolean result = isValid("()[]{}");
        System.out.println(result ? "True" : "False");
    }
}""",
        "starter_code_cpp": """#include <bits/stdc++.h>
using namespace std;

bool isValid(string s) {
    stack<char> st;
    unordered_map<char, char> mapping = {{')','('},{'}','{'},{']','['}};
    for (char c : s) {
        if (mapping.count(c)) {
            char top = st.empty() ? '#' : st.top();
            if (!st.empty()) st.pop();
            if (top != mapping[c]) return false;
        } else {
            st.push(c);
        }
    }
    return st.empty();
}

int main() {
    bool result = isValid("()[]{}");
    cout << (result ? "True" : "False") << endl;
    return 0;
}""",
        "expected_output": "True"
    },
    {
        "id": 5,
        "title": "Binary Search",
        "difficulty": "Easy",
        "category": "Binary Search",
        "description": "Given an array of integers `nums` which is sorted in ascending order, and an integer `target`, write a function to search `target` in `nums`.",
        "example": "Input: nums = [-1,0,3,5,9,12], target = 9\nOutput: 4",
        "starter_code": """def search(nums, target):
    l, r = 0, len(nums) - 1
    while l <= r:
        m = (l + r) // 2
        if nums[m] == target:
            return m
        elif nums[m] < target:
            l = m + 1
        else:
            r = m - 1
    return -1

print(search([-1,0,3,5,9,12], 9))""",
        "starter_code_java": """public class Main {
    public static int search(int[] nums, int target) {
        int l = 0, r = nums.length - 1;
        while (l <= r) {
            int m = (l + r) / 2;
            if (nums[m] == target) return m;
            else if (nums[m] < target) l = m + 1;
            else r = m - 1;
        }
        return -1;
    }

    public static void main(String[] args) {
        int[] nums = {-1, 0, 3, 5, 9, 12};
        System.out.println(search(nums, 9));
    }
}""",
        "starter_code_cpp": """#include <bits/stdc++.h>
using namespace std;

int search(vector<int>& nums, int target) {
    int l = 0, r = (int)nums.size() - 1;
    while (l <= r) {
        int m = (l + r) / 2;
        if (nums[m] == target) return m;
        else if (nums[m] < target) l = m + 1;
        else r = m - 1;
    }
    return -1;
}

int main() {
    vector<int> nums = {-1, 0, 3, 5, 9, 12};
    cout << search(nums, 9) << endl;
    return 0;
}""",
        "expected_output": "4"
    }
]

# High-Contrast Theme Styling
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #0f172a 100%) !important;
        color: #f8fafc !important;
    }
    h1, h2, h3, h4, h5, h6, p, label, span, div, .stMarkdown, .stMarkdown p {
        color: #f8fafc !important;
    }
    .stTextInput label, .stTextArea label, .stSelectbox label {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #0f172a !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        border-radius: 10px !important;
        font-family: 'Consolas', 'Fira Code', monospace !important;
        font-size: 1.05rem !important;
    }
    ::placeholder {
        color: #94a3b8 !important;
        opacity: 1 !important;
    }
    .badge-easy { background: rgba(16, 185, 129, 0.25); color: #6ee7b7 !important; padding: 5px 12px; border-radius: 14px; font-weight: 700; }
    .badge-med { background: rgba(245, 158, 11, 0.25); color: #fde68a !important; padding: 5px 12px; border-radius: 14px; font-weight: 700; }
    .badge-hard { background: rgba(239, 68, 68, 0.25); color: #fca5a5 !important; padding: 5px 12px; border-radius: 14px; font-weight: 700; }
    
    .stButton button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("💻 DSA Coding Practice Platform")
st.caption("Sharpen Data Structures & Algorithms problem-solving skills.")

with st.sidebar:
    st.header("👤 Candidate Settings")
    user_id = st.text_input("Username / Candidate ID:", value="candidate1")
    cat_filter = st.selectbox("Filter Category:", ["All"] + list(set([p["category"] for p in PROBLEMS])))
    diff_filter = st.selectbox("Filter Difficulty:", ["All", "Easy", "Medium", "Hard"])

filtered_problems = PROBLEMS
if cat_filter != "All":
    filtered_problems = [p for p in filtered_problems if p["category"] == cat_filter]
if diff_filter != "All":
    filtered_problems = [p for p in filtered_problems if p["difficulty"] == diff_filter]

st.markdown("### 🧩 Select Problem Prompt")
prob_titles = [f"#{p['id']} - {p['title']} ({p['difficulty']})" for p in filtered_problems]

if not prob_titles:
    st.warning("No problems match the selected filter criteria.")
else:
    selected_idx = st.selectbox("Choose Problem Prompt:", range(len(filtered_problems)), format_func=lambda i: prob_titles[i])
    prob = filtered_problems[selected_idx]

    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader(f"#{prob['id']}. {prob['title']}")
        diff_class = "badge-easy" if prob["difficulty"] == "Easy" else ("badge-med" if prob["difficulty"] == "Medium" else "badge-hard")
        st.markdown(f'<span class="{diff_class}">{prob["difficulty"]}</span> • **{prob["category"]}**', unsafe_allow_html=True)
        st.markdown(f"\n{prob['description']}")
        st.info(f"**Example:**\n```text\n{prob['example']}\n```")

    with c2:
        st.markdown("### ⏱️ Code Sandbox")
        lang = st.selectbox("Language:", ["Python 3", "Java", "C++", "JavaScript"])
        if lang == "JavaScript":
            st.caption("⚠️ Only Python 3, Java and C++ can currently be executed & judged.")

    st.markdown("### ✍️ Solution Editor & Code Input")

    placeholder_map = {
        "Python 3": "# Write your Python solution here...",
        "Java": "// Write your Java solution here (must include a public class with a main method)...",
        "C++": "// Write your C++ solution here (must include an int main() function)...",
        "JavaScript": "// Write your JavaScript solution here...",
    }

    user_code = st.text_area(
        "Write solution code below:",
        value="",
        placeholder=placeholder_map[lang],
        height=260,
        key=f"code_{prob['id']}_{lang}"
    )

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        run_submitted = st.button("🚀 Run Code & Submit")

    if run_submitted:
        if not user_code.strip():
            st.warning("⚠️ Please write your solution code before submitting — the editor is empty.")
        elif lang == "JavaScript":
            st.warning(f"⚠️ Running **{lang}** isn't supported yet — only **Python 3**, **Java** and **C++** can be executed right now. Please switch the language dropdown to try your solution.")
        else:
            with st.spinner("Executing test cases..."):
                time.sleep(0.3)
                exec_status = "Accepted"
                output_val = ""

                if lang == "Python 3":
                    import io
                    import sys

                    old_stdout = sys.stdout
                    redirected_output = io.StringIO()
                    sys.stdout = redirected_output

                    try:
                        exec(user_code, {})
                        output_val = redirected_output.getvalue().strip()
                    except Exception as e:
                        exec_status = "Runtime Error"
                        output_val = str(e)
                    finally:
                        sys.stdout = old_stdout

                elif lang == "Java":
                    import subprocess
                    import re
                    import tempfile

                    class_match = re.search(r'public\s+class\s+(\w+)', user_code)
                    class_name = class_match.group(1) if class_match else "Main"

                    try:
                        with tempfile.TemporaryDirectory() as tmpdir:
                            java_file = os.path.join(tmpdir, f"{class_name}.java")
                            with open(java_file, "w", encoding="utf-8") as jf:
                                jf.write(user_code)

                            compile_proc = subprocess.run(
                                ["javac", java_file],
                                cwd=tmpdir, capture_output=True, text=True, timeout=15
                            )

                            if compile_proc.returncode != 0:
                                exec_status = "Compilation Error"
                                output_val = compile_proc.stderr.strip()
                            else:
                                run_proc = subprocess.run(
                                    ["java", "-cp", tmpdir, class_name],
                                    capture_output=True, text=True, timeout=10
                                )
                                if run_proc.returncode != 0:
                                    exec_status = "Runtime Error"
                                    output_val = (run_proc.stderr or run_proc.stdout).strip()
                                else:
                                    output_val = run_proc.stdout.strip()
                    except FileNotFoundError:
                        exec_status = "Environment Error"
                        output_val = (
                            "Java JDK not found on this system. Install a JDK (e.g. from "
                            "https://adoptium.net) and make sure 'javac' and 'java' are on your PATH, "
                            "then restart the app."
                        )
                    except subprocess.TimeoutExpired:
                        exec_status = "Time Limit Exceeded"
                        output_val = "Code execution timed out (limit: 15s)."

                elif lang == "C++":
                    import subprocess
                    import tempfile

                    try:
                        with tempfile.TemporaryDirectory() as tmpdir:
                            cpp_file = os.path.join(tmpdir, "solution.cpp")
                            bin_file = os.path.join(tmpdir, "solution.out")
                            with open(cpp_file, "w", encoding="utf-8") as cf:
                                cf.write(user_code)

                            compile_proc = subprocess.run(
                                ["g++", "-O2", "-std=c++17", cpp_file, "-o", bin_file],
                                cwd=tmpdir, capture_output=True, text=True, timeout=15
                            )

                            if compile_proc.returncode != 0:
                                exec_status = "Compilation Error"
                                output_val = compile_proc.stderr.strip()
                            else:
                                run_proc = subprocess.run(
                                    [bin_file],
                                    capture_output=True, text=True, timeout=10
                                )
                                if run_proc.returncode != 0:
                                    exec_status = "Runtime Error"
                                    output_val = (run_proc.stderr or run_proc.stdout).strip()
                                else:
                                    output_val = run_proc.stdout.strip()
                    except FileNotFoundError:
                        exec_status = "Environment Error"
                        output_val = (
                            "C++ compiler (g++) not found on this system. Install a C++ toolchain "
                            "(e.g. build-essential / MinGW) and make sure 'g++' is on your PATH, "
                            "then restart the app."
                        )
                    except subprocess.TimeoutExpired:
                        exec_status = "Time Limit Exceeded"
                        output_val = "Code execution timed out (limit: 15s)."

                if exec_status == "Accepted" and output_val == prob["expected_output"]:
                    st.success(f"🎉 **Accepted!** Test cases passed.\n\n**Output:** `{output_val}`")
                elif exec_status == "Accepted":
                    exec_status = "Wrong Answer"
                    st.error(f"❌ **Wrong Answer**.\n\n**Expected:** `{prob['expected_output']}`\n\n**Got:** `{output_val}`")
                else:
                    st.error(f"⚠️ **{exec_status}**:\n```\n{output_val}\n```")

                record_submission(user_id, prob["id"], prob["title"], prob["difficulty"], prob["category"], exec_status, user_code)
