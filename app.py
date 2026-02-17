import streamlit as st
import json
import csv
import io
from datetime import date, time, timedelta
from tasks import Task

TASKS_FILE = "tasks.json"

def save_tasks(tasks):
    data = [
        {
            "title": t.title,
            "done": t.done,
            "day": t.day.isoformat() if t.day else None,
            "start_time": t.start_time.strftime("%H:%M") if t.start_time else None,
            "end_time": t.end_time.strftime("%H:%M") if t.end_time else None
        }
        for t in tasks
    ]
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_tasks():
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            tasks = []
            for d in data:
                day_value = d.get("day")
                day = date.fromisoformat(day_value) if day_value else None

                start_value = d.get("start_time")
                start_time = time.fromisoformat(start_value) if start_value else None

                end_value = d.get("end_time")
                end_time = time.fromisoformat(end_value) if end_value else None

                done_value = d.get("done", False)
                tasks.append(Task(d["title"], done_value, day, start_time, end_time))
            save_tasks(tasks)
            return tasks
    except FileNotFoundError:
        return []

if "tasks" not in st.session_state:
    st.session_state["tasks"] = load_tasks()

st.title("Gerenciador de Tarefas com Agenda")

title = st.text_input("Digite uma tarefa:")

start_time = st.time_input("Horário inicial:")
end_time = st.time_input("Horário final:")
day = st.date_input("Escolha o dia:", value=date.today())

st.write(f"Data escolhida: {day.strftime('%d/%m/%Y')}")

if st.button("Adicionar tarefa"):
    if title:
        st.session_state["tasks"].append(Task(title, False, day, start_time, end_time))
        save_tasks(st.session_state["tasks"])
        st.success(
            f"Tarefa adicionada: {title} em {day.strftime('%d/%m/%Y')} "
            f"das {start_time.strftime('%H:%M')} às {end_time.strftime('%H:%M')}"
        )
        st.rerun()

# ---------------- FILTROS ----------------
st.subheader("Filtros")
opcao = st.radio("Mostrar tarefas de:", ["Todas", "Hoje", "Escolher dia", "Semana", "Mês"])

dia_escolhido = None
intervalo_inicio = None
intervalo_fim = None

if opcao == "Hoje":
    dia_escolhido = date.today()
elif opcao == "Escolher dia":
    dia_escolhido = st.date_input("Selecione o dia para filtrar:")
elif opcao == "Semana":
    intervalo_inicio = date.today()
    intervalo_fim = date.today() + timedelta(days=7)
elif opcao == "Mês":
    intervalo_inicio = date.today().replace(day=1)
    if intervalo_inicio.month == 12:
        intervalo_fim = intervalo_inicio.replace(year=intervalo_inicio.year+1, month=1, day=1) - timedelta(days=1)
    else:
        intervalo_fim = intervalo_inicio.replace(month=intervalo_inicio.month+1, day=1) - timedelta(days=1)

# ---------------- LISTA DE TAREFAS ----------------
st.session_state["tasks"].sort(
    key=lambda t: (
        t.day if t.day else date.max,
        t.start_time if t.start_time else time.max
    )
)

st.subheader("Lista de Tarefas")
filtered_tasks = []
for i, t in enumerate(st.session_state["tasks"]):
    if dia_escolhido and t.day != dia_escolhido:
        continue
    if intervalo_inicio and intervalo_fim:
        if not (t.day and intervalo_inicio <= t.day <= intervalo_fim):
            continue

    filtered_tasks.append(t)

    col1, col2, col3 = st.columns([3,1,1])
    with col1:
        status = "✔️" if t.done else "❌"
        day_str = t.day.strftime("%d/%m/%Y") if t.day else "Sem data"
        start_str = t.start_time.strftime("%H:%M") if t.start_time else "??:??"
        end_str = t.end_time.strftime("%H:%M") if t.end_time else "??:??"
        st.write(f"{status} {t.title} - {day_str} {start_str} às {end_str}")
    with col2:
        if st.button("Concluir", key=f"done_{i}"):
            st.session_state["tasks"][i].done = True
            save_tasks(st.session_state["tasks"])
            st.success(f"Tarefa concluída: {t.title}")
            st.rerun()
    with col3:
        if st.button("Remover", key=f"remove_{i}"):
            st.session_state["tasks"].pop(i)
            save_tasks(st.session_state["tasks"])
            st.warning(f"Tarefa removida: {t.title}")
            st.rerun()

# ---------------- EXPORTAR PARA CSV COM DOWNLOAD ----------------
if filtered_tasks:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Título", "Concluída", "Data", "Hora inicial", "Hora final"])
    for t in filtered_tasks:
        writer.writerow([
            t.title,
            "✔️" if t.done else "❌",
            t.day.strftime("%d/%m/%Y") if t.day else "Sem data",
            t.start_time.strftime("%H:%M") if t.start_time else "??:??",
            t.end_time.strftime("%H:%M") if t.end_time else "??:??"
        ])
    csv_data = output.getvalue()

    if st.download_button(
        label="📥 Baixar tarefas filtradas em CSV",
        data=csv_data,
        file_name="tarefas_exportadas.csv",
        mime="text/csv"
    ):
        st.success("Exportação concluída e servidor atualizado!")
        st.rerun()

# ---------------- IMPORTAR CSV ----------------
st.subheader("Importar tarefas de CSV")
st.info("⚠️ Observação: Sempre faça o download/exportação antes de importar. Esse arquivo servirá como backup caso queira reverter.")

uploaded_file = st.file_uploader("Selecione um arquivo CSV", type=["csv"])
if uploaded_file is not None:
    stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
    reader = csv.DictReader(stringio)

    expected_fields = ["Título", "Concluída", "Data", "Hora inicial", "Hora final"]
    if reader.fieldnames != expected_fields:
        st.error("Formato de CSV inválido. Use apenas arquivos exportados pelo sistema.")
    else:
        imported_tasks = []
        for row in reader:
            title = row.get("Título")
            done = True if row.get("Concluída") == "✔️" else False

            day_str = row.get("Data")
            day = None
            if day_str and day_str != "Sem data":
                try:
                    d, m, y = day_str.split("/")
                    day = date(int(y), int(m), int(d))
                except Exception:
                    pass

            start_str = row.get("Hora inicial")
            end_str = row.get("Hora final")
            start_time = None
            end_time = None
            try:
                if start_str and start_str != "??:??":
                    start_time = time.fromisoformat(start_str)
                if end_str and end_str != "??:??":
                    end_time = time.fromisoformat(end_str)
            except Exception:
                pass

            imported_tasks.append(Task(title, done, day, start_time, end_time))

        st.session_state["tasks"] = imported_tasks
        save_tasks(st.session_state["tasks"])
        st.success("Tarefas importadas com sucesso do CSV! (substituiu as existentes)")

        # Botão de atualização manual (tipo F5)
        if st.button("🔄 Atualizar após import"):
            st.rerun()

       