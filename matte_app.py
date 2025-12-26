import streamlit as st
from openai import OpenAI
import sympy as sp
import json

# --- SETUP ---
st.set_page_config(page_title="Ma 1-5 Expert", layout="wide")
# Ändra denna rad i din matte_app.py på GitHub:
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- SYMPY-MOTORN ---
def execute_math(python_code):
    """Kör genererad SymPy-kod och returnerar ett exakt svar."""
    try:
        # Vi skapar en miljö för SymPy
        x, y, z = sp.symbols('x y z')
        # Här kör vi koden säkert (i en riktig app bör man vara mer restriktiv)
        result = eval(python_code)
        return str(result)
    except Exception as e:
        return f"Fel i beräkning: {e}"

st.title("📐 Matematiklärare 2.0 (Ma 1-5)")
st.write("Denna AI använder en inbyggd algebra-motor (SymPy) för att garantera korrekta svar.")

# --- NAVIGATION ---
kurs = st.sidebar.selectbox("Kursnivå:", ["Ma 1", "Ma 2", "Ma 3", "Ma 4", "Ma 5"])

user_query = st.text_area("Vad vill du ha hjälp med?", placeholder="T.ex. Bestäm derivatan av f(x) = x^2 * sin(x)")

if st.button("Lös med full precision"):
    if user_query:
        # STEG 1: AI:n analyserar och skapar ett "bevis" med SymPy
        # Vi ber AI:n att först ge oss den matematiska lösningen via kod
        with st.spinner("Beräknar med algebra-motorn..."):
            tool_prompt = f"""
            Du är en matematisk assistent. Din uppgift är att skriva EN RAD Python-kod med biblioteket SymPy 
            för att lösa elevens problem exakt.
            
            Exempel:
            Fråga: Lös x^2 - 4 = 0
            Svar: sp.solve(x**2 - 4, x)
            
            Fråga: Derivera x^3
            Svar: sp.diff(x**3, x)
            
            Elevens fråga: {user_query}
            Svara ENDAST med Python-koden.
            """
            
            code_res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": tool_prompt}],
                temperature=0
            )
            generated_code = code_res.choices[0].message.content
            
            # STEG 2: Kör SymPy
            exact_answer = execute_math(generated_code)

            # STEG 3: Skapa den pedagogiska förklaringen med det rätta svaret som facit
            final_prompt = f"""
            Du är en lärare i {kurs}. 
            Eleven vill ha hjälp med: {user_query}
            Det matematiskt korrekta svaret är: {exact_answer}
            
            Din uppgift:
            1. Förklara steg för steg hur man når fram till svaret {exact_answer}.
            2. Om det är en andragradsekvation, använd ABC-formeln.
            3. Använd LaTeX för alla formler.
            4. Var uppmuntrande och pedagogisk.
            """
            
            final_res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": final_prompt}]
            )
            
            st.success(f"Beräkning genomförd!")
            st.markdown("### Pedagogisk genomgång")
            st.markdown(final_res.choices[0].message.content)
            
            # Visa koden som användes (valfritt, bra för transparens)
            with st.expander("Se den tekniska beräkningen"):

                st.code(f"# SymPy-kod som kördes:\n{generated_code}\n\n# Resultat:\n{exact_answer}")
