import streamlit as st
import requests
import os
import re

st.set_page_config(
    page_title="AI Fitness Guide 45+",
    page_icon="💪",
    layout="centered"
)

st.title("💪 AI Fitness Guide for 45+")
st.write("📝 Fully automated recommendations — all tips displayed at once")

API_URL = "https://router.huggingface.co/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
    "Content-Type": "application/json"
}

# Fix common truncation errors
TRUNCATED_FIXES = {
    r"painn": "pain",
    r"downn": "down",
    r"cool downn": "cool down",
    r"furtherr": "further",
    r"repainr": "repair",
    r"\bexercise\.e\b": "exercise",
    r"\bexercis\b": "exercise",
    r"\bmachin\b": "machine",
    r"\benduran\b": "endurance",
}

def fix_truncation(text):
    for pattern, replacement in TRUNCATED_FIXES.items():
        text = re.sub(pattern, replacement, text)
    return text

with st.form("fitness_form"):
    user_input = st.text_input(
        "Describe your fitness needs (e.g., knee pain, mobility, lose weight, build strength):"
    )
    submitted = st.form_submit_button("Get Recommendations")

if submitted:
    if not user_input.strip():
        st.warning("⚠️ Please enter your fitness needs")
    else:
        st.subheader("💡 AI Recommendations")

        prompt = (
            f"You are a professional fitness coach for adults over 45. "
            f"Create 9 beginner-friendly, safe, and complete fitness tips for someone with these needs: {user_input}. "
            f"Include 2-3 actionable points per tip. Use full sentences. "
            f"Use emojis: 💧 for hydration, 🏋️ for strength, 🏃 for cardio, 🪑 for chair/support, 💡 for general advice. "
            f"Do not truncate your output. Ensure every sentence is complete."
        )

        payload = {
            "model": "meta-llama/Llama-3.1-8B-Instruct",
            "messages": [
                {"role": "system", "content": "You are a professional fitness coach for adults over 45."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            st.write("Status Code:", response.status_code)

            if response.status_code != 200:
                st.error(f"API returned an error: {response.text}")
            else:
                data = response.json()
                ai_text = data["choices"][0]["message"]["content"].strip()
                ai_text = fix_truncation(ai_text)

                # Split tips by "Tip" headings
                tips = re.split(r'(?:Tip\s*\d+[:\s]*)', ai_text)
                tips = [t.strip() for t in tips if t.strip()]

                # Display all tips fully
                for idx, tip in enumerate(tips, start=1):
                    st.markdown(f"### Tip {idx} 💡")
                    sub_points = re.split(r'\n|[-*•]', tip)
                    sub_points = [sp.strip(" *\n") for sp in sub_points if sp.strip(" *\n")]
                    for sp in sub_points:
                        if not sp.startswith(("💧", "🏋️", "🏃", "🪑", "💡")):
                            sp = "💡 " + sp
                        st.write(f"- {sp}")

        except Exception as e:
            st.error(f"Request failed: {e}")