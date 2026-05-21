import streamlit as st
import pandas as pd
from components.sidebar import draw_sidebar
from utils.db_manager import get_prodotti_raw
from core_ai.market_explorer import interroga_orchestratore

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

if "azienda_id" not in st.session_state:
    st.session_state.azienda_id = None

if "nome_azienda" not in st.session_state:
    st.session_state.nome_azienda = "La Tua Azienda"

if st.session_state.azienda_id is None:
    st.error("❌ Errore: ID azienda non trovato. Per favore, fai login di nuovo.")
    st.switch_page("app.py")

draw_sidebar(st.session_state.nome_azienda)

st.title("📈 Analisi di Mercato ")

try:
    df_magazzino = get_prodotti_raw(st.session_state.azienda_id)
except Exception as e:
    st.error(f"❌ Errore nel caricamento del magazzino: {e}")
    df_magazzino = pd.DataFrame()

st.markdown("---")


if "mercato_chat" not in st.session_state:
    st.session_state.mercato_chat = [
        {
            "role": "assistant",
            "content": "👋 Ciao! Sono il tuo consulente di mercato personale, come posso aiutarti?",
            "azioni": [],
            "contesto": None
        }
    ]

def costruisci_contesto_conversazione():
    """
    Estrae l'ultimo scambio completo (domanda utente + risposta agente).
    Questo è il contesto che passa ai bottoni suggeriti.
    """
    contesto = []
    
    for i in range(len(st.session_state.mercato_chat) - 1, -1, -1):
        msg = st.session_state.mercato_chat[i]
        
        if msg["role"] == "assistant" and msg.get("content"):
            contesto.insert(0, f"Assistant: {msg['content']}")
            
            if i > 0 and st.session_state.mercato_chat[i-1]["role"] == "user":
                contesto.insert(0, f"You: {st.session_state.mercato_chat[i-1]['content']}")
                break
    
    return " | ".join(contesto) if contesto else None


for idx, msg in enumerate(st.session_state.mercato_chat):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        if msg["role"] == "assistant" and msg.get("azioni"):
            st.markdown("---")
            st.write("💡 **Azioni suggerite:**")
            
            cols = st.columns(len(msg["azioni"]))
            
            for col_idx, azione in enumerate(msg["azioni"]):
                with cols[col_idx]:
                    if azione["tipo"] == "button":
                        btn_key = f"btn_msg_{idx}_action_{col_idx}"
                        
                        if st.button(azione["label"], use_container_width=True, key=btn_key):
                            user_msg_precedente = None
                            if idx > 0 and st.session_state.mercato_chat[idx-1]["role"] == "user":
                                user_msg_precedente = st.session_state.mercato_chat[idx-1]["content"]
                            
                            if user_msg_precedente:
                                contesto_completo = (
                                    f"Domanda precedente: '{user_msg_precedente}'\n"
                                    f"Risposta agente: '{msg['content'][:300]}...'\n" 
                                    f"\nNuova azione: {azione['azione']}"
                                )
                            else:
                                contesto_completo = azione['azione']
                            st.session_state.mercato_chat.append({
                                "role": "user",
                                "content": contesto_completo,
                                "contesto": f"You: {user_msg_precedente}\n\nAssistant: {msg['content'][:200]}..." if user_msg_precedente else None,
                                "azione_bottone": azione['azione']
                            })
                            st.rerun()


if prompt := st.chat_input("Scrivi la tua domanda..."):

    st.session_state.mercato_chat.append({
        "role": "user",
        "content": prompt,
        "contesto": None,
        "azione_bottone": None
    })
    st.rerun()

ultimo_msg = st.session_state.mercato_chat[-1] if st.session_state.mercato_chat else None

if ultimo_msg and ultimo_msg["role"] == "user" and "elaborato" not in ultimo_msg:
    ultimo_msg["elaborato"] = True
    
    with st.chat_message("assistant"):
        with st.spinner("🧠 analisi per una risposta adeguata..."):
            try:
                prompt_da_elaborare = ultimo_msg["content"]
                contesto_msg = ultimo_msg.get("contesto", None)
                
                if contesto_msg:
                    print(f"📌 Contesto includente risposta precedente:\n{contesto_msg[:200]}...")
                
                risposta = interroga_orchestratore(
                    messaggio_utente=prompt_da_elaborare,
                    df_magazzino=df_magazzino,
                    contesto_completo=contesto_msg 
                )
                
                st.markdown(risposta["messaggio"])
                
                st.session_state.mercato_chat.append({
                    "role": "assistant",
                    "content": risposta["messaggio"],
                    "azioni": risposta.get("azioni_suggerite", []),
                    "contesto": contesto_msg
                })
                
            except Exception as e:
                st.error(f"❌ Errore durante l'elaborazione: {str(e)}")
                print(f"Debug error: {e}")
                
                st.session_state.mercato_chat.append({
                    "role": "assistant",
                    "content": f"Scusa, ho avuto un problema: {str(e)}",
                    "azioni": [],
                    "contesto": ultimo_msg.get("contesto", None)
                })
    
    st.rerun()