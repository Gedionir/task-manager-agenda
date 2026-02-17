from tasks import Task
from storage import save_tasks, load_tasks

def menu():
    print("\n--- Gerenciador de Tarefas ---")
    print("1. Adicionar tarefa")
    print("2. Listar tarefas")
    print("3. Concluir tarefa")
    print("4. Remover tarefa")
    print("5. Sair")

def main():
    tasks = load_tasks()

    while True:
        menu()
        choice = input("Escolha uma opção: ")

        if choice == "1":
            title = input("Digite a tarefa: ")
            tasks.append(Task(title))
        elif choice == "2":
            for i, t in enumerate(tasks):
                print(f"{i+1}. {t}")
        elif choice == "3":
            idx = int(input("Número da tarefa: ")) - 1
            if 0 <= idx < len(tasks):
                tasks[idx].mark_done()
        elif choice == "4":
            idx = int(input("Número da tarefa: ")) - 1
            if 0 <= idx < len(tasks):
                tasks.pop(idx)
        elif choice == "5":
            save_tasks(tasks)
            print("Tarefas salvas. Até mais!")
            break

if __name__ == "__main__":
    main()