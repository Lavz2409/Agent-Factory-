"""
Minimal chat-style reasoning viewer for Agent Factory (debugging UI).
Run: streamlit run ui_app.py
"""

from __future__ import annotations

import os

import streamlit as st

from dotenv import load_dotenv


load_dotenv()

print("LOCAL_MODE:", os.environ.get("LOCAL_MODE"))

from main import run_pipeline_from_ui

st.set_page_config(
    page_title="Agent Factory — Reasoning Viewer",
    page_icon="🏭",
    layout="centered",
)

# Light, readable defaults
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; max-width: 720px; }
    div[data-testid="stVerticalBlock"] > div { gap: 0.75rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _box():
    """Soft message block (Streamlit 1.29+ has border= on container)."""
    try:
        return st.container(border=True)
    except TypeError:
        return st.container()


def _render_guardrails(g: dict) -> None:
    st.markdown("### 🛡 Quality Checks")

    dv = g.get("design_validation", {})
    if dv.get("passed"):
        st.markdown("✔ **PASS** — Design validation")
    else:
        st.markdown("✖ **FAIL** — Design validation")
        for i in dv.get("issues") or []:
            st.caption(f"↳ {i}")

    cv = g.get("code_validation", {})
    if cv.get("passed"):
        st.markdown("✔ **PASS** — Code validation")
    else:
        st.markdown("✖ **FAIL** — Code validation")
        for i in cv.get("issues") or []:
            st.caption(f"↳ {i}")

    ss = g.get("security_scan", {})
    if ss.get("passed"):
        st.markdown("✔ **PASS** — Security scan")
    else:
        st.markdown("⚠ **WARNING** — Security scan")
        for w in ss.get("warnings") or []:
            st.caption(f"↳ {w}")

    sla = g.get("sla_enforcement", {})
    if sla.get("passed"):
        st.markdown(f"✔ **PASS** — SLA ({sla.get('message', '')})")
    else:
        st.markdown(f"✖ **FAIL** — SLA ({sla.get('message', '')})")


def _render_flow(result: dict) -> None:
    """Vertical step-by-step walkthrough."""
    text = result.get("user_input") or ""
    st.markdown(f"**User:** {text}")

    st.divider()

    with _box():
        st.markdown("### 🧾 Input Layer — Understanding the request")
        pi = result.get("parsed_input") or {}
        st.json(pi)

    st.divider()

    with _box():
        st.markdown("### 🧠 Planner — Creating execution strategy")
        plan = result.get("plan") or {}
        st.markdown("**Strategy**")
        st.markdown(f"> {plan.get('strategy', '—')}")
        tasks = plan.get("tasks") or []
        st.markdown("**Tasks**")
        for t in tasks:
            agent = str(t.get("agent", "")).title()
            st.markdown(f"- **{agent}** → {t.get('task', '')}")

    st.divider()

    with _box():
        st.markdown("### 🏗 Architect — Designing system")
        arch = result.get("architecture") or {}
        st.markdown("**Components**")
        for c in arch.get("components") or []:
            if isinstance(c, dict):
                st.markdown(f"- **{c.get('name', '?')}** — {c.get('responsibility', '')}")
        st.markdown("**Data flow**")
        st.write(arch.get("data_flow", "—"))
        st.markdown("**Entry point**")
        st.write(arch.get("entry_point", "—"))

    st.divider()

    with _box():
        st.markdown("### 💻 Coder — Generating code")
        co = result.get("code_output") or {}
        st.write("**Filename:**", co.get("filename", "—"))
        st.code(co.get("code") or "# (no code)", language="python")

    st.divider()

    with _box():
        _render_guardrails(result.get("guardrails") or {})

    st.divider()

    with _box():
        st.markdown("### ✅ Final Result")
        fn = (result.get("code_output") or {}).get("filename", "output.py")
        how = (result.get("code_output") or {}).get("how_to_run", "python main.py")
        st.write(f"**File saved:** `outputs/{fn}`")
        st.write(f"**How to run:** `{how}`")


def main() -> None:
    st.title("🏭 Agent Factory — Reasoning Viewer")
    st.caption("Watch how agents think, plan, and build")

    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    if st.session_state.last_result is not None:
        st.success("Pipeline completed successfully")
        _render_flow(st.session_state.last_result)
        st.divider()
    else:
        st.info("Enter a request below and click **Run** to see step-by-step reasoning.")

    st.markdown("##### Run")
    c1, c2 = st.columns([5, 1])
    with c1:
        q = st.text_input(
            "Request",
            value="Build a FastAPI CRUD API",
            label_visibility="collapsed",
            placeholder="Describe what to build…",
            key="user_request_field",
        )
    with c2:
        st.write("")
        run = st.button("Run", type="primary", use_container_width=True)

    if run:
        prompt = (q or "").strip() or "Build a FastAPI CRUD API"
        with st.spinner("Agents are working..."):
            try:
                st.session_state.last_result = run_pipeline_from_ui(prompt)
            except Exception as e:
                st.error(f"Pipeline failed: {e}")
                st.session_state.last_result = None
            else:
                st.rerun()


if __name__ == "__main__":
    main()
